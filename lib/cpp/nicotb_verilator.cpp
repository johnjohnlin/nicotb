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
#include <unordered_map>

namespace Nicotb {

using namespace std;
// ptr, type size, (..., dim2, dim1, dim0)
typedef tuple<uint8_t*, size_t, vector<size_t>> ArrayHandle;
// ptr, type size
typedef pair<uint8_t*, size_t> SignalHandle;
static unordered_map<string, size_t> ev_name_to_id;
static unordered_map<string, ArrayHandle> sig_name_to_array;
static vector<vector<SignalHandle>> registered_handles;
bool nicotb_fin_wire = false;

namespace Verilator {

void AddEvent(string ev_name)
{
	auto it = ev_name_to_id.emplace(move(ev_name), 0);
	CHECK(it.second) << "Event name " << ev_name << " already exists.";
}

size_t GetEventIdx(const string &ev_name)
{
	auto it = ev_name_to_id.find(ev_name);
	CHECK(it != ev_name_to_id.end()) << "Cannot find event " << ev_name;
	return it->second;
}

void AddSignal(string signal_name, uint8_t *ptr, size_t dsize, vector<size_t> shape)
{
	auto it = sig_name_to_array.emplace(
		move(signal_name),
		forward_as_tuple(ptr, dsize, move(shape))
	);
	CHECK(it.second) << "Signal name " << signal_name << " already exists.";
}

static void ExtractSignal(vector<SignalHandle> &handles, const vector<int> &d, char *hier)
{
	auto it = sig_name_to_array.find(hier);
	CHECK(it != sig_name_to_array.end()) << "Cannot find signal " << hier;
	uint8_t *arr_ptr = get<0>(it->second);
	const size_t arr_dsize = get<1>(it->second);
	const auto &arr_shape = get<2>(it->second);
	vector<size_t> src, dst;
	CHECK_EQ(d.size(), arr_shape.size()) << "Dimensions of " << hier << " are mismatch";
	src.push_back(0);
	auto it_dim = arr_shape.rbegin();
	for (int l: d) {
		dst.clear();
		for (size_t h: src) {
			for (int i = 0; i < l; ++i) {
				dst.push_back((*it_dim)*h + i);
			}
		}
		swap(src, dst);
		++it_dim;
	}
	handles.resize(handles.size() + src.size());
	auto it_dst = handles.end() - src.size();
	for (auto &h: src) {
		LOG(INFO) << "Index " << h << " of " << hier << " (" << (void*)arr_ptr << ") is used.";
		it_dst->first = arr_ptr + h*arr_dsize;
		it_dst->second = arr_dsize;
		++it_dst;
	}
}

void Init()
{
	google::InitGoogleLogging("nicotb");
	Nicotb::Python::Init();
	Nicotb::Python::InitTest();
	PyErr_Print();
}

} // namespace Verilator

namespace Python {

void ReadBusExt(const size_t i, ValueIterProxy &&values_proxy)
{
	auto it = registered_handles[i].begin(), it_end = registered_handles[i].end();
	while (true) {
		const bool fin1 = it == it_end;
		const bool fin2 = values_proxy.Done();
		int aval = 0;
		if (fin1 or fin2) {
			LOG_IF(ERROR, not (fin1 and fin2)) << "Signal " << i << " has different numbers of elements with numpy.";
			break;
		}
		memcpy(&aval, it->first, it->second);
		values_proxy.Set(aval, 0);
		++it;
		values_proxy.Next();
	}
}

void WriteBusExt(const size_t i, ValueIterProxy &&values_proxy)
{
	// FIXME: Workaround for matching FinishSim() in Python
	if (nicotb_fin_wire) {
		LOG_FIRST_N(INFO, 1) << "FinishSim is called(), disabling the WriteBus().";
		return;
	}
	auto it = registered_handles[i].begin(), it_end = registered_handles[i].end();
	while (true) {
		const bool fin1 = it == it_end;
		const bool fin2 = values_proxy.Done();
		int aval, bval;
		if (fin1 or fin2) {
			LOG_IF(WARNING, not (fin1 and fin2)) << "Signal " << i << " has different numbers of elements with numpy.";
			break;
		}
		values_proxy.Get(aval, bval);
		// TODO: utilize bval
		memcpy(it->first, &aval, it->second);
		++it;
		values_proxy.Next();
	}
}

void BindBusExt(const BusEntry &bus)
{
	registered_handles.emplace_back();
	for (auto &&s: bus) {
		// FIXME: Workaround for matching FinishSim() in Python
		if (strcmp(s.first, "nicotb_fin_wire") == 0) {
			nicotb_fin_wire = true;
			break;
		}
		Verilator::ExtractSignal(registered_handles.back(), s.second, s.first);
	}
}

void BindEventExt(const size_t i, char *hier)
{
	auto it = ev_name_to_id.find(hier);
	CHECK(it != ev_name_to_id.end()) << "Cannot find event " << hier;
	it->second = i;
}

} // namespace Python

} // namespace Nicotb

