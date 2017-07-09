// Copyright (C) 2017, Yu Sheng Lin, johnjohnlys@media.ee.ntu.edu.tw

// This file is part of Nicotb.

// Nicotb is free software: you can redistribute it and/or modify
// it under the terms of the GNU General Public License as published by
// the Free Software Foundation, either version 3 of the License, or
// (at your option) any later version.

// Nicotb is distributed in the hope that it will be useful,
// but WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
// GNU General Public License for more details.

// You should have received a copy of the GNU General Public License
// along with Nicotb.  If not, see <http://www.gnu.org/licenses/>.
#include "nicotb_python.h"
#include <cstdio>
#include <cstdlib>
#include <functional>
#include <vector>

namespace Nicotb {
namespace Python {

using namespace std;

static PyObject* PyInit_func();
static EventEntry e;
static BusEntry b;
static PyObject *p_set_event;
static PyObject *p_main_loop;

static PyObject* ReadBus(PyObject *dummy, PyObject *args)
{
	unsigned i;
	PyObject *v_list;
	PyObject *x_list;
	if (!PyArg_ParseTuple(args, "IOO", &i, &v_list, &x_list)) {
		return nullptr;
	}
	ReadBusExt(i, v_list, x_list);
	Py_INCREF(Py_None);
	return Py_None;
}

static PyObject* WriteBus(PyObject *dummy, PyObject *args)
{
	unsigned i;
	PyObject *v_list;
	PyObject *x_list;
	if (!PyArg_ParseTuple(args, "IOO", &i, &v_list, &x_list)) {
		return nullptr;
	}
	WriteBusExt(i, v_list, x_list);
	Py_INCREF(Py_None);
	return Py_None;
}

static void InitEvent(PyObject *&p_list, PyObject *&p_dict)
{
	p_list = PyList_New(e.size());
	p_dict = PyDict_New();
	for (auto &&event: e) {
		auto &name = event.first;
		auto &idx = event.second.first;
		auto &read_buses = event.second.second;
		PyObject *p_idx = PyLong_FromLong(idx);
		PyObject *p_read_buses = PyTuple_New(read_buses.size());
		for (size_t bidx = 0; bidx < read_buses.size(); ++bidx) {
			PyTuple_SET_ITEM(p_read_buses, bidx, PyLong_FromLong(read_buses[bidx]));
		}
		PyDict_SetItemString(p_dict, name.c_str(), p_idx);
		PyList_SET_ITEM(p_list, idx, p_read_buses);
		Py_DECREF(p_idx);
	}
}

static void InitBus(PyObject *&p_list, PyObject *&p_dict)
{
	p_list = PyList_New(b.size());
	p_dict = PyDict_New();
	for (auto &&bus: b) {
		auto &name = bus.first;
		auto &idx = bus.second.first;
		auto &sig = bus.second.second;
		PyObject *p_idx = PyLong_FromLong(idx);
		PyObject *p_v_tup = PyTuple_New(sig.size());
		PyObject *p_x_tup = PyTuple_New(sig.size());
		PyDict_SetItemString(p_dict, name.c_str(), p_idx);
		for (size_t sidx = 0; sidx < sig.size(); ++sidx) {
			vector<npy_intp> dim_intp(sig[sidx].d.begin(), sig[sidx].d.end());
			if (dim_intp.empty()) {
				dim_intp.push_back(1);
			}
			PyTuple_SET_ITEM(p_v_tup, sidx, PyArray_ZEROS(dim_intp.size(), dim_intp.data(), sig[sidx].t, 0));
			PyTuple_SET_ITEM(p_x_tup, sidx, PyArray_ZEROS(dim_intp.size(), dim_intp.data(), sig[sidx].t, 0));
		}
		PyList_SET_ITEM(p_list, idx, PyTuple_Pack(2, p_v_tup, p_x_tup));
		Py_DECREF(p_idx);
	}
}

static PyObject* InitBridgeModule()
{
	// TODO: Error when they are not static, why?
	static PyMethodDef nicotb_bridge_methods[] = {
		{"WriteBus", WriteBus, METH_VARARGS, ""},
		{"ReadBus", ReadBus, METH_VARARGS, ""},
		{nullptr, nullptr, 0, nullptr}
	};
	static PyModuleDef nicotb_bridge_module = {
		PyModuleDef_HEAD_INIT,
		"nicotb_bridge", nullptr, -1,
		nicotb_bridge_methods,
		nullptr, nullptr, nullptr, nullptr
	};
	PyObject *p_bridge_module = PyModule_Create(&nicotb_bridge_module);
	PyObject *p_events, *p_event_dict, *p_buses, *p_bus_dict;
	InitEvent(p_events, p_event_dict);
	InitBus(p_buses, p_bus_dict);
	PyModule_AddObject(p_bridge_module, "events", p_events);
	PyModule_AddObject(p_bridge_module, "event_dict", p_event_dict);
	PyModule_AddObject(p_bridge_module, "buses", p_buses);
	PyModule_AddObject(p_bridge_module, "bus_dict", p_bus_dict);
	return p_bridge_module;
}

static void ImportTest()
{
	PyObject *p_module_name = PyUnicode_FromString(GetEnv("TEST"));
	PyObject *p_module = PyImport_Import(p_module_name);
	PyErr_Print();
	p_set_event = PyObject_GetAttrString(p_module, "SetEvent");
	p_main_loop = PyObject_GetAttrString(p_module, "MainLoop");
	LOG_IF(FATAL, p_set_event == nullptr or p_main_loop == nullptr) <<
		"Cannot find necessary functions, did you from nicotb import * in your code?";
	Py_DECREF(p_module_name);
	Py_DECREF(p_module);
}

void TriggerEvent(size_t i)
{
	Py_XDECREF(PyObject_CallFunction(p_set_event, "n", Py_ssize_t(i)));
	Py_XDECREF(PyObject_CallFunction(p_main_loop, ""));
	PyErr_Print();
}

void Init(const EventEntry &_e, const BusEntry &_b)
{
	e = _e;
	b = _b;
	PyImport_AppendInittab("nicotb_bridge", InitBridgeModule);
	Py_Initialize();
	_import_array();
	ImportTest();
	PyErr_Print();
}

} // namespace Python
} // namespace Nicotb
