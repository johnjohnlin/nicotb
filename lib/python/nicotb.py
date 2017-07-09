# Copyright (C) 2017, Yu Sheng Lin, johnjohnlys@media.ee.ntu.edu.tw

# This file is part of Nicotb.

# Nicotb is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# Nicotb is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with Nicotb.  If not, see <http://www.gnu.org/licenses/>.
from nicotb_bridge import events, event_dict, buses, bus_dict, ReadBus, WriteBus
from typing import Union
from collections import deque
import numpy as np

__all__ = [
	'WriteBus',
	'ToBusIdx',
	'GetBus',
	'ToEventIdx',
	'SetEvent',
	'RegisterCoroutines',
	'MainLoop',
]

waiting_coro = [list() for _ in range(len(event_dict))]
event_queue = deque()

class Signal(object):
	"A wrapper that keeps a signal in a bus"
	__slots__ = ["_x", "_value"]
	def __init__(self, v, x):
		self._value = v
		self._x = x

	@property
	def x(self):
		return self._x

	@x.setter
	def x(self):
		np.copyto(self._x, x)

	@property
	def value(self):
		return self._value

	@value.setter
	def value(self):
		np.copyto(self._value, value)

	def set_to_z(self):
		self._value.fill(0)
		self._x.fill(-1)

	def set_to_x(self):
		self._value.fill(-1)
		self._x.fill(-1)

	def set_to_number(self):
		self._x.fill(0)

	@property
	def is_number(self):
		return not np.any(self._x)

class BusWrap(object):
	"A wrapper that keeps a bus with its reference and provide accessor"
	__slots__ = ["idx", "vs", "xs", "signals"]
	def __init__(self, idx, ev_entry):
		self.idx = idx
		self.vs, self.xs = ev_entry
		self.signals = tuple(Signal(v, x) for v, x in zip(*ev_entry))

	def __getitem__(self, i):
		return self.signals[i]

	def write(self):
		WriteBus(self.idx, self.vs, self.xs)

	def set_to_z(self):
		for s in self.signals:
			s.set_to_z()

	def set_to_x(self):
		for s in self.signals:
			s.set_to_x()

	def set_to_number(self):
		for s in self.signals:
			s.set_to_number()

	@property
	def is_number(self):
		return all(s.is_number for s in self.signals)

buses_wrapped = list(BusWrap(i, b) for i, b in enumerate(buses))

def ToBusIdx(idx: Union[str,int]):
	return bus_dict[idx] if isinstance(idx, str) else idx

def GetBus(idx):
	return buses_wrapped[ToBusIdx(idx)]

def ToEventIdx(idx: Union[str,int]):
	return event_dict[idx] if isinstance(idx, str) else idx

def SetEvent(ev):
	event_queue.append(ToEventIdx(ev))

def RegisterCoroutines(coro: list):
	for c in coro:
		try:
			waiting_coro[ToEventIdx(next(c))].append(c)
		except StopIteration:
			pass

def MainLoop():
	while len(event_queue) != 0:
		event_idx = event_queue.pop()
		proc = waiting_coro[event_idx]
		waiting_coro[event_idx] = list()
		event = events[event_idx]
		for read_idx in event:
			ReadBus(read_idx, buses[read_idx][0], buses[read_idx][1])
		RegisterCoroutines(proc)
