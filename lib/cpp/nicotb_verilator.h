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
#include <nicotb_python.h>
#include <cstdint>
#include <string>
#include <vector>

namespace Nicotb {

extern bool nicotb_fin_wire;

namespace Verilator {

using namespace std;
void AddEvent(string ev_name);
size_t GetEventIdx(const string &ev_name);
void AddSignal(string signal_name, uint8_t *ptr, size_t dsize, vector<size_t> shape);
// Wrappers
void Init();
static inline void Final() { Nicotb::Python::Final(); }
static inline bool UpdateWrite() { return Nicotb::Python::UpdateWrite(); }
static inline bool TriggerEvent(size_t i) { return Nicotb::Python::TriggerEvent(i); }

template<class T> vector<size_t> ArraySize(T)
{
    return vector<size_t>();
}

template<class T, size_t N> vector<size_t> ArraySize(T (&x)[N])
{
    auto ret = ArraySize(x[0]);
    ret.push_back(N);
    return ret;
}

template<class T> constexpr size_t ArrayDataSize(T)
{
    return sizeof(T);
}

template<class T, size_t N> constexpr size_t ArrayDataSize(T (&x)[N])
{
    return ArrayDataSize(x[0]);
}

} // namespace Verilator
} // namespace Nicotb

// define TOP as the pointer before this line
#define MAP_SIGNAL(name) Nicotb::Verilator::AddSignal(#name, (uint8_t*)&TOP->name, Nicotb::Verilator::ArrayDataSize(TOP->name), Nicotb::Verilator::ArraySize(TOP->name))
// Alias version
#define MAP_SIGNAL_ALIAS(name, alias_name) Nicotb::Verilator::AddSignal(#alias_name, (uint8_t*)&TOP->name, Nicotb::Verilator::ArrayDataSize(TOP->name), Nicotb::Verilator::ArraySize(TOP->name))
// OK, if you don't want your module is named TOP
#define MAP_SIGNAL_ALIAS_TOP(name, alias_name, top) Nicotb::Verilator::AddSignal(#alias_name, (uint8_t*)&top->name, Nicotb::Verilator::ArrayDataSize(top->name), Nicotb::Verilator::ArraySize(top->name))
