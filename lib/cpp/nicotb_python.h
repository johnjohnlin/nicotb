#pragma once
// Copyright (C) 2017-2018, Yu Sheng Lin, johnjohnlys@media.ee.ntu.edu.tw

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
#include <glog/logging.h>
#include <numpy/ndarraytypes.h>
#include <Python.h>
#include <cstdlib>
#include <cstring>
#include <memory>
#include <string>
#include <vector>
#include <utility>

namespace Nicotb {

typedef std::vector<std::pair<
	char*,           // hier
	std::vector<int> // shape
>> BusEntry;
class ValueIterProxy {
	PyObject *p_it_v_, *p_it_x_, *_p_v_, *_p_x_, *p_v_, *p_x_;
	PyArrayObject *p_vx_[2];
	char **data_ptr_array_, *v_dat_, *x_dat_;
	NpyIter *iter_;
	NpyIter_IterNextFunc *IterNext_;
	npy_intp inner_stride0_, inner_stride1_, item_size0_, item_size1_, *inner_size_ptr_, inner_size_, inner_count_;
	npy_uint32 OP_FLAGS_[2];
	enum State: int {INIT, LOOP, DONE} state_;
	bool done_;
public:
	ValueIterProxy(PyObject *value_list, PyObject *xxx_list, const npy_uint32 ITER_FLAG):
		OP_FLAGS_{ITER_FLAG, ITER_FLAG},
		state_(INIT)
	{
		CHECK_EQ(PyTuple_Size(value_list), PyTuple_Size(xxx_list)) << "Tuple length mismatch";
		p_it_v_ = CHECK_NOTNULL(PyObject_GetIter(value_list));
		p_it_x_ = CHECK_NOTNULL(PyObject_GetIter(xxx_list));
		this->Next();
	}
	void Set(const int aval, const int bval)
	{
		memcpy(v_dat_, &aval, item_size0_);
		memcpy(x_dat_, &bval, item_size1_);
	}
	void Get(int &aval, int &bval)
	{
		memcpy(&aval, v_dat_, item_size0_);
		memcpy(&bval, x_dat_, item_size1_);
	}
	bool Next();
	bool Done() { return state_ == DONE; }
	~ValueIterProxy()
	{
		Py_DECREF(p_it_v_);
		Py_DECREF(p_it_x_);
	}
};

namespace Python {

void Init();
void InitTest();
void Final();
bool UpdateWrite();
bool TriggerEvent(size_t i);
// VPI must implement these functions
void ReadBusExt(const size_t i, ValueIterProxy &&value_list);
void WriteBusExt(const size_t i, ValueIterProxy &&value_list);
void BindEventExt(const size_t i, char *hier);
void BindBusExt(const BusEntry &bus);

} // namespace Python
} // namespace Nicotb

static inline std::unique_ptr<char[]> ToCharUqPtr(const std::string &s)
{
	std::unique_ptr<char[]> cs(new char[s.size()+1]);
	strcpy(cs.get(), s.c_str());
	return cs;
}

static inline const char *GetEnv(const char *name)
{
	using namespace google;
	const char *value = getenv(name);
	CHECK(value != nullptr) << "Environment variable " << name << " not set";
	return value;
}

static inline bool EnvSet(const char *name)
{
	return getenv(name) != nullptr;
}
