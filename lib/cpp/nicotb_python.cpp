// Copyright (C) 2017-2019, Yu Sheng Lin, johnjohnlys@media.ee.ntu.edu.tw

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
#include <numpy/ndarrayobject.h>
#include <cstdio>
#include <cstdlib>
#include <functional>
#include <vector>

namespace Nicotb {

bool ValueIterProxy::Next()
{
	PyArrayObject *&p_v = p_vx_[0], *&p_x = p_vx_[1];
	// This line use switch as generator
	switch (state_) { case INIT:
	for (
		_p_v_ = PyIter_Next(p_it_v_), _p_x_ = PyIter_Next(p_it_x_);
		_p_v_;
		_p_v_ = PyIter_Next(p_it_v_), _p_x_ = PyIter_Next(p_it_x_)
	) {
		p_v = (PyArrayObject*)_p_v_;
		p_x = (PyArrayObject*)_p_x_;
		CHECK(PyArray_CheckExact(p_v) and PyArray_CheckExact(p_x)) << "Inputs are not numpy array";
		CHECK_EQ(PyArray_SIZE(p_v), PyArray_SIZE(p_x)) << "Array size mismatch";
		if (PyArray_SIZE(p_v) == 0) {
			LOG(WARNING) << "Ignore zero-sized array";
			continue;
		}
		iter_ = CHECK_NOTNULL(NpyIter_MultiNew(
			2, p_vx_, NPY_ITER_EXTERNAL_LOOP,
			NPY_KEEPORDER, NPY_NO_CASTING, OP_FLAGS_, nullptr
		));
		IterNext_ = NpyIter_GetIterNext(iter_, nullptr);
		inner_stride0_ = NpyIter_GetInnerStrideArray(iter_)[0];
		inner_stride1_ = NpyIter_GetInnerStrideArray(iter_)[1];
		item_size0_ = NpyIter_GetDescrArray(iter_)[0]->elsize;
		item_size1_ = NpyIter_GetDescrArray(iter_)[0]->elsize;
		inner_size_ptr_ = NpyIter_GetInnerLoopSizePtr(iter_);
		data_ptr_array_ = NpyIter_GetDataPtrArray(iter_);
		do {
			inner_size_ = *inner_size_ptr_;
			v_dat_ = data_ptr_array_[0];
			x_dat_ = data_ptr_array_[1];
			for(
				inner_count_ = 0;
				inner_count_ < inner_size_;
				inner_count_++, v_dat_ += inner_stride0_, x_dat_ += inner_stride1_
			) {
				state_ = LOOP;
				return true;
				case LOOP: ;
				// NEXT_YIELD(LOOP, true);
			}
		} while (IterNext_(iter_));
		Py_DECREF(_p_v_);
		Py_DECREF(_p_x_);
	}
	state_ = DONE;
	case DONE: ;
	} // end switch
	return false;
}

namespace Python {

using namespace std;

static PyObject *p_set_event;
static PyObject *p_main_loop;
static PyObject *p_update_write;
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
	ReadBusExt(i, ValueIterProxy(v_list, x_list, NPY_ITER_WRITEONLY));
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
	WriteBusExt(i, ValueIterProxy(v_list, x_list, NPY_ITER_READONLY));
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
	static PyMethodDef nicotb_bridge_methods[] = {
		{"WriteBus", WriteBus, METH_VARARGS, ""},
		{"ReadBus", ReadBus, METH_VARARGS, ""},
		{"BindEvent", BindEvent, METH_VARARGS, ""},
		{"BindBus", BindBus, METH_VARARGS, ""},
		{nullptr, nullptr, 0, nullptr}
	};
	static PyModuleDef nicotb_bridge_module = {
		PyModuleDef_HEAD_INIT,
		NICOTB_MODULE_NAME,
		nullptr, -1,
		nicotb_bridge_methods,
		nullptr, nullptr, nullptr, nullptr
	};
	p_bridge_module = PyModule_Create(&nicotb_bridge_module);
	return p_bridge_module;
}

static bool ImportTest()
{
	PyObject *p_module_name = PyUnicode_FromString(GetEnv("TEST"));
	p_test_module = PyImport_Import(p_module_name);
	PyErr_Print();
	if (p_test_module == nullptr) {
		return true;
	}
	p_set_event = PyObject_GetAttrString(p_test_module, "SignalEvent");
	p_main_loop = PyObject_GetAttrString(p_test_module, "MainLoop");
	p_update_write = PyObject_GetAttrString(p_test_module, "FlushBusWrite");
	LOG_IF(ERROR, p_set_event == nullptr or p_main_loop == nullptr or p_update_write == nullptr) <<
		"Cannot find necessary functions, did you from nicotb import * in your code?";
	Py_DECREF(p_module_name);
	return false;
}

bool UpdateWrite()
{
	// FIXME: They are initialized only after ImportTest, we should prevent this
	if (p_update_write == nullptr) {
		return true;
	}
	PyObject *o = PyObject_CallFunction(p_update_write, "");
	PyErr_Print();
	Py_XDECREF(o);
	return o == nullptr;
}

bool TriggerEvent(size_t i)
{
	// FIXME: They are initialized only after ImportTest, we should prevent this
	if (p_set_event == nullptr or p_main_loop == nullptr) {
		return true;
	}
	PyObject *o1 = PyObject_CallFunction(p_set_event, "nO", Py_ssize_t(i), Py_True);
	PyObject *o2 = PyObject_CallFunction(p_main_loop, "");
	PyErr_Print();
	Py_XDECREF(o1);
	Py_XDECREF(o2);
	return o1 == nullptr or o2 == nullptr;
}

bool Init()
{
	PyImport_AppendInittab(NICOTB_MODULE_NAME, InitBridgeModule);
	Py_Initialize();
	auto Imp = []() -> int {
		// this is required for each compile unit
		// this macro make this function return 1 if failed
		import_array1(1);
		return 0;
	};
	CHECK_EQ(Imp(), 0) << "Import Numpy fails";
	return false;
}

bool InitTest()
{
	return ImportTest();
}

bool Final()
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
	return false;
}

} // namespace Python
} // namespace Nicotb
