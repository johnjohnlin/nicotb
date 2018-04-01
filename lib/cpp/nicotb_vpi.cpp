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
#include "vpi_user.h"
#include "nicotb_python.h"
#include <numpy/ndarrayobject.h>
#include <fstream>

namespace Nicotb {

using namespace std;
static vector<vector<vpiHandle>> registered_handles;

namespace Vpi {

static inline vpiHandle HandleByName(char *hier, vpiHandle h);
static void ExtractSignal(vector<vpiHandle> &handles, const vector<int> &d, char *hier);

} // namespace Vpi

namespace Python {

#define ITER_ROUTINE_BEGIN(ITER_FLAG)\
	vector<vpiHandle> &handles = registered_handles[i];\
	CHECK_EQ(PyTuple_Size(value_list), PyTuple_Size(xxx_list)) << "Tuple length mismatch";\
	PyObject *p_it_v = CHECK_NOTNULL(PyObject_GetIter(value_list));\
	PyObject *p_it_x = CHECK_NOTNULL(PyObject_GetIter(xxx_list));\
	auto it = handles.begin();\
	for (\
		PyObject *_p_v = PyIter_Next(p_it_v), *_p_x = PyIter_Next(p_it_x);\
		_p_v;\
		_p_v = PyIter_Next(p_it_v), _p_x = PyIter_Next(p_it_x)\
	) {\
		PyArrayObject *p_v = (PyArrayObject*)_p_v, *p_x = (PyArrayObject*)_p_x;\
		CHECK(PyArray_CheckExact(p_v) and PyArray_CheckExact(p_x)) << "Inputs are not numpy array";\
		CHECK_EQ(PyArray_SIZE(p_v), PyArray_SIZE(p_x)) << "Array size mismatch";\
		CHECK_LE(PyArray_SIZE(p_v), handles.end()-it) << "No enough Verilog signal left";\
		if (PyArray_SIZE(p_v) == 0) {\
			LOG(WARNING) << "Ignore zero-sized array";\
			continue;\
		}\
		PyArrayObject *op[2]{p_v, p_x};\
		npy_uint32 op_flags[2]{(ITER_FLAG), (ITER_FLAG)};\
		NpyIter *iter = CHECK_NOTNULL(NpyIter_MultiNew(\
			2, op, NPY_ITER_EXTERNAL_LOOP,\
			NPY_KEEPORDER, NPY_NO_CASTING, op_flags, nullptr\
		));\
		NpyIter_IterNextFunc *iternext = NpyIter_GetIterNext(iter, nullptr);\
		npy_intp innerstride0 = NpyIter_GetInnerStrideArray(iter)[0],\
		         innerstride1 = NpyIter_GetInnerStrideArray(iter)[1],\
		         itemsize0 = NpyIter_GetDescrArray(iter)[0]->elsize,\
		         itemsize1 = NpyIter_GetDescrArray(iter)[0]->elsize,\
		         *innersizeptr = NpyIter_GetInnerLoopSizePtr(iter);\
		char **dataptrarray = NpyIter_GetDataPtrArray(iter);\
		CHECK_EQ(itemsize0, itemsize1) << "Array dtype mismatch";\
		do {\
			npy_intp size = *innersizeptr;\
			char *v_dat = dataptrarray[0], *x_dat = dataptrarray[1];\
			for(npy_intp i = 0; i < size; i++, v_dat += innerstride0, x_dat += innerstride1) {\
				s_vpi_value v;\
				v.format = vpiVectorVal;

#define ITER_ROUTINE_END\
				++it;\
			}\
		} while (iternext(iter));\
		Py_DECREF(_p_v);\
		Py_DECREF(_p_x);\
	}\
	CHECK(it == handles.end()) << "Tuple length mismatch";\
	Py_DECREF(p_it_v);\
	Py_DECREF(p_it_x);

void ReadBusExt(const size_t i, PyObject *value_list, PyObject *xxx_list)
{
	ITER_ROUTINE_BEGIN(NPY_ITER_WRITEONLY)
		vpi_get_value(*it, &v);
		memcpy(v_dat, &v.value.vector->aval, itemsize0);
		memcpy(x_dat, &v.value.vector->bval, itemsize0);
	ITER_ROUTINE_END
}

void WriteBusExt(const size_t i, PyObject *value_list, PyObject *xxx_list)
{
	static s_vpi_time tm {vpiSimTime, 0, 0, 0};
	ITER_ROUTINE_BEGIN(NPY_ITER_READONLY)
		s_vpi_vecval vecval;
		memcpy(&vecval.aval, v_dat, itemsize0);
		memcpy(&vecval.bval, x_dat, itemsize0);
		v.value.vector = &vecval;
		vpi_put_value(*it, &v, &tm, vpiInertialDelay);
	ITER_ROUTINE_END
}

void BindBusExt(const BusEntry &bus)
{
	registered_handles.emplace_back();
	for (auto &&s: bus) {
		Vpi::ExtractSignal(registered_handles.back(), s.second, s.first);
	}
}

void BindEventExt(const size_t i, char *hier)
{
	vpiHandle h = Vpi::HandleByName(hier, nullptr);
	s_vpi_value v;
	v.format = vpiIntVal;
	v.value.integer = i;
	vpi_put_value(h, &v, nullptr, vpiNoDelay);
	LOG(INFO) << "Set signal " << hier << " to " << i;
}

} // namespace Python

namespace Vpi {

static inline vpiHandle HandleByName(char *hier, vpiHandle h)
{
	vpiHandle ret = vpi_handle_by_name(hier, h);
	LOG_IF(FATAL, not ret) << "Cannot find " << hier;
	LOG(INFO) << "Found vpiHandle " << ret << " from " << hier << " of vpiHandle " << h;
	return ret;
}

static void ExtractSignal(vector<vpiHandle> &handles, const vector<int> &d, char *hier)
{
	auto hier_cs = ToCharUqPtr(hier);
	vector<vpiHandle> src, dst;
	src.push_back(vpi_handle_by_name(hier, nullptr));
	if (src.back()) {
		LOG(INFO) << hier << " founded: " << src.back();
	} else {
		LOG(FATAL) << hier << " not founded.";
	}
	for (int l: d) {
		dst.clear();
		for (auto &&h: src) {
			for (int i = 0; i < l; ++i) {
				dst.push_back(vpi_handle_by_index(h, i));
				if (dst.back()) {
					LOG(INFO) << "Index " << i << " of " << h << " found: " << dst.back();
				} else {
					LOG(FATAL) << "Index " << i << " of " << h << " not found.";
				}
			}
		}
		swap(src, dst);
	}
	handles.insert(handles.end(), src.begin(), src.end());
}

static PLI_INT32 Init(PLI_BYTE8 *args)
{
	Python::InitTest();
	return 0;
}

static PLI_INT32 Final(PLI_BYTE8 *args)
{
	Python::Final();
	return 0;
}

static PLI_INT32 UpdateWrite(PLI_BYTE8 *args)
{
	Python::UpdateWrite();
	return 0;
}

static PLI_INT32 TriggerEvent(PLI_BYTE8 *args)
{
	vpiHandle systfref, args_iter, argh;
	struct t_vpi_value argval;
	systfref = vpi_handle(vpiSysTfCall, nullptr);
	args_iter = vpi_iterate(vpiArgument, systfref);
	argh = vpi_scan(args_iter);
	argval.format = vpiIntVal;
	vpi_get_value(argh, &argval);
	vpi_free_object(args_iter);
	if (argval.value.integer >= 0) {
		argval.value.integer = Python::TriggerEvent(argval.value.integer);
		vpi_put_value(systfref, &argval, nullptr, vpiNoDelay);
	}
	return 0;
}

} // namespace Vpi
} // namespace Nicotb

extern "C" void VpiBoot()
{
	using namespace Nicotb::Vpi;
	static s_vpi_systf_data tasks[] = {
		{vpiSysFunc, vpiIntFunc, "$NicotbTriggerEvent", TriggerEvent, nullptr, nullptr, nullptr},
		{vpiSysTask, vpiSysTask, "$NicotbUpdateWrite", UpdateWrite, nullptr, nullptr, nullptr},
		{vpiSysTask, vpiSysTask, "$NicotbInit", Init, nullptr, nullptr, nullptr},
		{vpiSysTask, vpiSysTask, "$NicotbFinal", Final, nullptr, nullptr, nullptr}
	};
	for (auto&& task: tasks) {
		vpi_register_systf(&task);
	}
	google::InitGoogleLogging("nicotb");
	Nicotb::Python::Init();
	_import_array(); // this is required for each compile unit
}

// TODO: this is not recognized by ncverilog?
void (*vlog_startup_routines[])() = {
	VpiBoot,
	nullptr
};
