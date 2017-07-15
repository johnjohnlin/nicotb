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
static PyObject *p_set_event;
static PyObject *p_main_loop;
static PyObject *p_bridge_module;
static PyObject *p_test_module;

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

static PyObject* BindEvent(PyObject *dummy, PyObject *args)
{
	unsigned i;
	PyObject *p_hier;
	if (!PyArg_ParseTuple(args, "IO", &i, &p_hier)) {
		return nullptr;
	}
	BindEventExt(i, CHECK_NOTNULL(PyBytes_AsString(p_hier)));
	Py_INCREF(Py_None);
	return Py_None;
}

static PyObject* BindBus(PyObject *dummy, PyObject *args)
{
	BusEntry b;
	PyObject *p_lst;
	if (!PyArg_ParseTuple(args, "O", &p_lst)) {
		return nullptr;
	}
	PyObject *p_it = CHECK_NOTNULL(PyObject_GetIter(p_lst));
	for (PyObject *p_tup = PyIter_Next(p_it); p_tup; p_tup = PyIter_Next(p_it)) {
		PyObject *p_hier = CHECK_NOTNULL(PySequence_GetItem(p_tup, 0));
		PyObject *p_shape = CHECK_NOTNULL(PySequence_GetItem(p_tup, 1));
		// get hierarchy
		char *s = CHECK_NOTNULL(PyBytes_AsString(p_hier));
		b.emplace_back(s, vector<int>());
		// iterate shapes
		auto &shapes = b.back().second;
		PyObject *p_shape_it = CHECK_NOTNULL(PyObject_GetIter(p_shape));
		for (PyObject *p_int = PyIter_Next(p_shape_it); p_int; p_int = PyIter_Next(p_shape_it)) {
			shapes.push_back(PyLong_AsLong(p_int));
			// release current
			Py_DECREF(p_int);
		}
		Py_DECREF(p_shape_it);
		// release current
		Py_DECREF(p_tup);
	}
	Py_DECREF(p_it);
	BindBusExt(b);
	Py_INCREF(Py_None);
	return Py_None;
}

static PyObject* InitBridgeModule()
{
	// TODO: Error when they are not static, why?
	static PyMethodDef nicotb_bridge_methods[] = {
		{"WriteBus", WriteBus, METH_VARARGS, ""},
		{"ReadBus", ReadBus, METH_VARARGS, ""},
		{"BindEvent", BindEvent, METH_VARARGS, ""},
		{"BindBus", BindBus, METH_VARARGS, ""},
		{nullptr, nullptr, 0, nullptr}
	};
	static PyModuleDef nicotb_bridge_module = {
		PyModuleDef_HEAD_INIT,
		"nicotb_bridge", nullptr, -1,
		nicotb_bridge_methods,
		nullptr, nullptr, nullptr, nullptr
	};
	p_bridge_module = PyModule_Create(&nicotb_bridge_module);
	return p_bridge_module;
}

static void ImportTest()
{
	PyObject *p_module_name = PyUnicode_FromString(GetEnv("TEST"));
	p_test_module = PyImport_Import(p_module_name);
	PyErr_Print();
	CHECK_NOTNULL(p_test_module);
	p_set_event = PyObject_GetAttrString(p_test_module, "SetEvent");
	p_main_loop = PyObject_GetAttrString(p_test_module, "MainLoop");
	LOG_IF(FATAL, p_set_event == nullptr or p_main_loop == nullptr) <<
		"Cannot find necessary functions, did you from nicotb import * in your code?";
	Py_DECREF(p_module_name);
}

bool TriggerEvent(size_t i)
{
	PyObject *o1 = PyObject_CallFunction(p_set_event, "n", Py_ssize_t(i));
	PyObject *o2 = PyObject_CallFunction(p_main_loop, "");
	PyErr_Print();
	Py_XDECREF(o1);
	Py_XDECREF(o2);
	return o1 == nullptr or o2 == nullptr;
}

void Init()
{
	PyImport_AppendInittab("nicotb_bridge", InitBridgeModule);
	Py_Initialize();
	ImportTest();
	PyErr_Print();
}

void Final()
{
	PyObject *p_scb = PyObject_GetAttrString(p_test_module, "Scoreboard");
	if (p_scb != nullptr) {
		Py_XDECREF(CHECK_NOTNULL(
			PyObject_CallMethod(p_scb, "ReportAll", "")
		));
	}
	Py_DECREF(p_set_event);
	Py_DECREF(p_main_loop);
	Py_DECREF(p_bridge_module);
	Py_DECREF(p_test_module);
}

} // namespace Python
} // namespace Nicotb
