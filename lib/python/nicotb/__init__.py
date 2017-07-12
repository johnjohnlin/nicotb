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
from typing import Union, Tuple
from collections import deque
import numpy as np

__all__ = [
	"WriteBus",
	"ToBusIdx",
	"GetBus",
	"ToEventIdx",
	"SetEvent",
	"Fork",
	"RegisterCoroutines",
	"MainLoop",
	"Receiver",
	"Signal",
	"Report",
	"scoreboards",
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
	def value(self) -> np.ndarray:
		"Get the underlying numpy array representing the value(s)"
		return self._value

	@value.setter
	def value(self):
		if not value is self._value:
			np.copyto(self._value, value)

	@property
	def x(self) -> np.ndarray:
		"Get the underlying numpy array representing the X value(s)"
		return self._x

	@x.setter
	def x(self):
		if not x is self._x:
			np.copyto(self._x, x)

	def SetToZ(self):
		self._value.fill(0)
		self._x.fill(-1)

	def SetToX(self):
		self._value.fill(-1)
		self._x.fill(-1)

	def SetToNumber(self):
		self._x.fill(0)

	@property
	def is_number(self):
		return not np.any(self._x)

class BusWrap(object):
	"""
	A wrapper that keeps a bus with its reference and provide accessor.
	There are 2 ways to access the signals:
	(1) self.values[99], self.xs[99]
	(2) self.signals[99].x, self.signals[99].value
	There are many ways to modify the reference:
	(1-1) self.values[99] = 0 (wrong, "values" is a tuple)
	(1-2) self.values[99][0] = 123 (modify the element of numpy array directly)
	(1-3) self.values = ... (update all entries by @setter, the RHS must be compatiable with self.values)
	(2-1) self.signals[99].value[0] = 123 (the same as 1-2)
	(2-2) self.signals[99].value = 123 (update all entries by @setter, the RHS must be compatiable with self.value)
	after that, a self.Write() call actually updates the value to Verilog

	Shortcuts such as self.signal, self.value and self.x, are provided to access
	signals[0], values[0] and xs[0],
	which is useful when the bus has only 1 signal.
	Using these shortcuts, only (1-2), (2-1) and (2-2) is available.
	"""
	__slots__ = ["idx", "_vs", "_xs", "signals"]
	def __init__(self, idx, ev_entry):
		self.idx = idx
		self._vs, self._xs = ev_entry
		self.signals = tuple(Signal(v, x) for v, x in zip(*ev_entry))

	@property
	def values(self) -> Tuple[np.ndarray, ...]:
		"Get the underlying tuple of numpy arrays representing the value(s)"
		return self._vs

	@values.setter
	def values(self, v):
		if not v is self._vs:
			for ss, vv in zip(self._signals, v):
				ss.value = vv

	@property
	def xs(self) -> Tuple[np.ndarray, ...]:
		"Get the underlying tuple of numpy arrays representing the X value(s)"
		return self._xs

	@xs.setter
	def xs(self, x):
		if not x is self._xs:
			for ss, xx in zip(self._signals, x):
				ss.x = xx

	@property
	def value(self) -> np.ndarray:
		return self._vs[0]

	@property
	def x(self) -> np.ndarray:
		return self._xs

	@property
	def signal(self) -> Signal:
		return self.signals[0]

	def __getitem__(self, i):
		return self.signals[i]

	def Write(self):
		WriteBus(self.idx, self._vs, self._xs)

	def SetToZ(self):
		for s in self.signals:
			s.SetToZ()

	def SetToX(self):
		for s in self.signals:
			s.SetToX()

	def SetToNumber(self):
		for s in self.signals:
			s.SetToNumber()

	@property
	def is_number(self):
		return all(s.is_number for s in self.signals)

class Receiver(object):
	__slots__ = ["callbacks"]
	def __init__(self, callbacks = list()):
		self.callbacks = callbacks

	def AddCallback(self, cb):
		self.callbacks.append(cb)

	def Get(self, x):
		for cb in self.callbacks:
			cb(x)

buses_wrapped = list(BusWrap(i, b) for i, b in enumerate(buses))

def ToBusIdx(idx: Union[str,int]):
	return bus_dict[idx] if isinstance(idx, str) else idx

def GetBus(idx):
	return buses_wrapped[ToBusIdx(idx)]

def ToEventIdx(idx: Union[str,int]):
	return event_dict[idx] if isinstance(idx, str) else idx

def SetEvent(ev):
	event_queue.append(ToEventIdx(ev))

def Fork(c):
	try:
		waiting_coro[ToEventIdx(next(c))].append(c)
	except StopIteration:
		pass

def RegisterCoroutines(coro: list):
	for c in coro:
		Fork(c)

def MainLoop():
	while len(event_queue) != 0:
		event_idx = event_queue.pop()
		proc = waiting_coro[event_idx]
		waiting_coro[event_idx] = list()
		event = events[event_idx]
		for read_idx in event:
			ReadBus(read_idx, buses[read_idx][0], buses[read_idx][1])
		RegisterCoroutines(proc)

scoreboards = list()
def Report():
	for i, s in enumerate(scoreboards):
		print("Reporting scoreboard {}...".format(i))
		s.Report()
