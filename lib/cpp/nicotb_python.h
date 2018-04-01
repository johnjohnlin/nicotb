#pragma once
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
#include <glog/logging.h>
#include <Python.h>
#include <cstdlib>
#include <memory>
#include <string>
#include <vector>
#include <utility>

namespace Nicotb {

typedef std::vector<std::pair<
	char*,           // hier
	std::vector<int> // shape
>> BusEntry;

namespace Python {

void Init();
void InitTest();
void Final();
bool UpdateWrite();
bool TriggerEvent(size_t i);
// VPI must implement these functions
void ReadBusExt(const size_t i, PyObject *value_list, PyObject *xxx_list);
void WriteBusExt(const size_t i, PyObject *value_list, PyObject *xxx_list);
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
	LOG_IF(FATAL, value == nullptr) << "Environment variable" << name << " not set";
	return value;
}
