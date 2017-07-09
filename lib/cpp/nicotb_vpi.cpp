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
#include "nicotb_config.pb.h"
#include <fstream>
#include <google/protobuf/text_format.h>
#include <google/protobuf/io/zero_copy_stream_impl.h>

namespace Nicotb {

using namespace std;
static vector<vector<vpiHandle>> registered_handles;

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
			LOG(ERROR) << "Ignore zero-sized array";\
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
	ITER_ROUTINE_BEGIN(NPY_ITER_READONLY)
		s_vpi_vecval vecval;
		memcpy(&vecval.aval, v_dat, itemsize0);
		memcpy(&vecval.bval, x_dat, itemsize0);
		v.value.vector = &vecval;
		vpi_put_value(*it, &v, nullptr, vpiNoDelay);
	ITER_ROUTINE_END
}

} // namespace Python

namespace Vpi {

using namespace google;
using namespace google::protobuf;

static inline vpiHandle HandleByName(char *hier, vpiHandle h)
{
	vpiHandle ret = vpi_handle_by_name(hier, h);
	LOG_IF(FATAL, not ret) << "Cannot find" << hier;
	LOG(INFO) << "Found vpiHandle " << ret << " from " << hier << " of vpiHandle " << h;
	return ret;
}

static void ExtractSignal(vector<vpiHandle> &handles, const vector<int> &d, const string &hier)
{
	auto hier_cs = ToCharUqPtr(hier);
	vector<vpiHandle> src, dst;
	src.push_back(vpi_handle_by_name(hier_cs.get(), nullptr));
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

static void ReadConfig(EventEntry &eent, BusEntry &bent)
{
	// read protobuf
	const char *cfg_file = GetEnv("CONNECT_CONFIG");

	ifstream ifs(cfg_file);
	LOG_IF(FATAL, not ifs.is_open()) << cfg_file << " is missing";

	io::IstreamInputStream iifs(&ifs);
	NicotbConfig::NicotbConfig config;
	const bool parse_success = TextFormat::Parse(&iifs, &config);
	LOG_IF(FATAL, not parse_success) << "Cannot parse " << cfg_file;

	ifs.close();

	// get vpi
	const string topm = string(GetEnv("TOPMODULE")) + '.';
	// signal groups
	unordered_map<string, vector<tuple<string, vector<int>, NPY_TYPES>>> siggrp_defs;
	static NPY_TYPES ToNp[] = {
		NPY_BOOL,
		NPY_BOOL, NPY_UBYTE, NPY_USHORT, NPY_UINT,
		NPY_BYTE, NPY_SHORT, NPY_INT
	};
	for (auto &&gd: config.siggrp_defs()) {
		const string &name = gd.name();
		const auto ins_result = siggrp_defs.emplace(name, decltype(siggrp_defs)::mapped_type());
		LOG_IF(ERROR, not ins_result.second) << "Signal group " << name << " is already defined.";
		auto &grp_vec = ins_result.first->second;
		if (ins_result.second) {
			for (auto &&s: gd.sigs()) {
				grp_vec.emplace_back(
					s.name(),
					vector<int>(s.shape().begin(), s.shape().end()),
					ToNp[s.np_type()]
				);
			}
		}
	}

	// buses
	for (auto&& b: config.buses()) {
		const string &name = b.name();
		const string &hier = topm + (b.hier().empty() ? string() : b.hier() + '.');
		auto ins_result = bent.emplace(name, BusEntry::mapped_type());
		LOG_IF(ERROR, not ins_result.second) << "Bus " << name << " is already inserted and thus ignored.";

		ins_result.first->second.first = bent.size() - 1;
		auto &bent_vec = ins_result.first->second.second;
		registered_handles.emplace_back();
		for (auto &&sg: b.sig_grps()) {
			const string &def_name = sg.grp_def_name();
			const string &prefix = sg.prefix();
			auto it = siggrp_defs.find(def_name);
			LOG_IF(FATAL, it == siggrp_defs.end()) << "Cannot find signal group definition " << def_name;
			for (auto &&sig: it->second) {
				SignalEntry bent;
				const string &s_hier = hier + prefix + get<0>(sig);
				bent.t = get<2>(sig);
				bent.d = get<1>(sig);
				ExtractSignal(registered_handles.back(), bent.d, s_hier);
				bent_vec.push_back(move(bent));
			}
		}
		for (auto &&s: b.sigs()) {
			SignalEntry bent;
			const string &s_hier = hier + s.name();
			bent.t = ToNp[s.np_type()];
			bent.d.insert(bent.d.end(), s.shape().begin(), s.shape().end());
			ExtractSignal(registered_handles.back(), bent.d, s_hier);
			bent_vec.push_back(move(bent));
		}
		LOG(INFO) << "There are " << registered_handles.back().size() << " handles in " << name;
	}

	// assign events
	for (auto &&e: config.events()) {
		const string &name = e.name();
		const string &hier = string(topm) + e.hier();
		const auto &ev_bound_buses = e.bound_buses();
		const auto ins_result = eent.emplace(name, EventEntry::mapped_type());
		if (not ins_result.second) {
			LOG(ERROR) << "Signal " << name << " is already inserted and thus ignored.";
			continue;
		}
		auto &target_entry = ins_result.first->second;
		target_entry.first = eent.size() - 1;
		if (e.has_hier()) {
			auto hier_cs = ToCharUqPtr(hier);
			LOG(INFO) << "Name: " << name << ", event = " << hier;
			vpiHandle h = HandleByName(hier_cs.get(), nullptr);
			s_vpi_value v;
			const unsigned writev = target_entry.first;
			v.format = vpiIntVal;
			v.value.integer = writev;
			vpi_put_value(h, &v, nullptr, vpiNoDelay);
			LOG(INFO) << "Set signal " << hier << " to " << writev;
		}
		for (const string &bidx: ev_bound_buses) {
			auto it = bent.find(bidx);
			LOG_IF(FATAL, it == bent.end()) << "Signal " << bidx << " for " << name << " not found";
			target_entry.second.push_back(it->second.first);
		}
	}
}

static PLI_INT32 Init(PLI_BYTE8 *args)
{
	InitGoogleLogging("nicotb");
	EventEntry e;
	BusEntry b;
	ReadConfig(e, b);
	Python::Init(e, b);
	_import_array(); // this is required for each compile unit
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
		Python::TriggerEvent(argval.value.integer);
	}
	return 0;
}

} // namespace Vpi
} // namespace Nicotb

extern "C" void VpiBoot()
{
	using namespace Nicotb::Vpi;
	static s_vpi_systf_data tasks[] = {
		{vpiSysTask, vpiSysTask, "$NicotbTriggerEvent", TriggerEvent, nullptr, nullptr, nullptr},
		{vpiSysTask, vpiSysTask, "$NicotbInit", Init, nullptr, nullptr, nullptr}
	};
	for (auto&& task: tasks) {
		vpi_register_systf(&task);
	}
}

// TODO: this is not recognized by ncverilog?
void (*vlog_startup_routines[])() = {
	VpiBoot,
	nullptr
};
