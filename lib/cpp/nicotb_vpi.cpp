// Copyright (C) 2017-2020, Yu Sheng Lin, johnjohnlys@media.ee.ntu.edu.tw

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
#include "vpi/vpi_user.h"
#include "nicotb_python.h"
#include <fstream>

namespace Nicotb {

using namespace std;
static vector<vector<vpiHandle>> registered_handles;
static bool VCS_FIX;

namespace Vpi {

static inline vpiHandle HandleByName(char *hier, vpiHandle h);
static void ExtractSignal(vector<vpiHandle> &handles, const vector<int> &d, char *hier);

} // namespace Vpi

namespace Python {

void ReadBusExt(const size_t i, ValueIterProxy &&values_proxy)
{
	auto it = registered_handles[i].begin(), it_end = registered_handles[i].end();
	while (true) {
		const bool fin1 = it == it_end;
		const bool fin2 = values_proxy.Done();
		if (fin1 or fin2) {
			LOG_IF(ERROR, not (fin1 and fin2)) << "Signal " << i << " has different numbers of elements with numpy.";
			break;
		}
		s_vpi_value v;
		v.format = vpiVectorVal;
		vpi_get_value(*it, &v);
		values_proxy.Set(v.value.vector->aval, v.value.vector->bval);
		++it;
		values_proxy.Next();
	}
}

void WriteBusExt(const size_t i, ValueIterProxy &&values_proxy)
{
	static s_vpi_time tm {vpiSimTime, 0, 0, 0};
	auto it = registered_handles[i].begin(), it_end = registered_handles[i].end();
	while (true) {
		const bool fin1 = it == it_end;
		const bool fin2 = values_proxy.Done();
		if (fin1 or fin2) {
			LOG_IF(WARNING, not (fin1 and fin2)) << "Signal " << i << " has different numbers of elements with numpy.";
			break;
		}
		s_vpi_value v;
		s_vpi_vecval vecval;
		v.format = vpiVectorVal;
		v.value.vector = &vecval;
		values_proxy.Get(vecval.aval, vecval.bval);
		vpi_put_value(*it, &v, &tm, vpiInertialDelay);
		++it;
		values_proxy.Next();
	}
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
	CHECK(bool(ret)) << "Cannot find " << hier;
	LOG(INFO) << "Found vpiHandle " << ret << " from " << hier << " of vpiHandle " << h;
	return ret;
}

static void ExtractSignal(vector<vpiHandle> &handles, const vector<int> &d, char *hier)
{
	auto hier_cs = ToCharUqPtr(hier);
	vector<vpiHandle> append_handles, append_handles_tmp;
	append_handles.push_back(vpi_handle_by_name(hier, nullptr));
	if (append_handles.back()) {
		LOG(INFO) << hier << " founded: " << append_handles.back();
	} else {
		LOG(FATAL) << hier << " not founded.";
	}
	auto AppendHandle = [](vector<vpiHandle> &v, const int idx, vpiHandle h) {
		v.push_back(h);
		if (v.back()) {
			LOG(INFO) << "Index " << idx << " of " << h << " found: " << v.back();
		} else {
			LOG(FATAL) << "Index " << idx << " of " << h << " not found.";
		}
	};

	auto AppendHandlesND = [&]() {
		if (d.empty()) {
			return;
		}
		vector<int> indices(d.size(), 0);
		DCHECK_EQ(append_handles.size(), 1);
		vpiHandle root_handle = append_handles.front();
		for (int i = 0;; ++i) {
			AppendHandle(append_handles_tmp, i, vpi_handle_by_multi_index(root_handle, int(d.size()), indices.data()));
			auto it_idx = indices.rbegin();
			auto it_dim = d.rbegin();
			while (true) {
				*it_idx += 1;
				if (*it_idx == *it_dim) {
					*it_idx = 0;
				} else {
					break;
				}
				++it_idx;
				++it_dim;
				if (it_dim == d.rend()) {
					DCHECK(it_idx == indices.rend()) << "iterator must end at the same time";
					swap(append_handles, append_handles_tmp);
					return;
				}
			}
		}
		DCHECK(false);
	};

	if (VCS_FIX) {
		// TODO: check whether this works for ncverilog VPI
		AppendHandlesND();
	} else {
		// This works fine for IUS
		vector<vpiHandle> appdne_handles_tmp;
		for (int l: d) {
			append_handles_tmp.clear();
			for (auto &&h: append_handles) {
				for (int i = 0; i < l; ++i) {
					AppendHandle(append_handles_tmp, i, vpi_handle_by_index(h, i));
				}
			}
			swap(append_handles, append_handles_tmp);
		}
	}
	handles.insert(handles.end(), append_handles.begin(), append_handles.end());
}

static PLI_INT32 Init(PLI_BYTE8 *args)
{
	VCS_FIX = EnvSet("NICOTB_VCS");
	LOG_IF(INFO, VCS_FIX) << "Simulate in VCS VPI";

	vpiHandle systfref;
	s_vpi_value argval;
	systfref = vpi_handle(vpiSysTfCall, nullptr);
	argval.format = vpiIntVal;
	argval.value.integer = Python::InitTest();
	vpi_put_value(systfref, &argval, nullptr, vpiNoDelay);
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
	s_vpi_value argval;
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
		{vpiSysFunc, vpiSysFunc, "$NicotbUpdateWrite", UpdateWrite, nullptr, nullptr, nullptr},
		{vpiSysFunc, vpiSysFunc, "$NicotbInit", Init, nullptr, nullptr, nullptr},
		{vpiSysFunc, vpiSysFunc, "$NicotbFinal", Final, nullptr, nullptr, nullptr}
	};
	for (auto&& task: tasks) {
		vpi_register_systf(&task);
	}
	google::InitGoogleLogging("nicotb");
	Nicotb::Python::Init();
}
