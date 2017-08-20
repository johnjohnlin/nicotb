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
from nicotb_bridge import BindEvent, BindBus, ReadBus, WriteBus
from os import environ
from typing import Union, Tuple, Iterable, Any
from collections import deque
import numpy as np

__all__ = [
	"WriteBus",
	"GetBusIdx",
	"GetBus",
	"GetEventIdx",
	"SetEvent",
	"Fork",
	"RegisterCoroutines",
	"CreateBus",
	"CreateBuses",
	"CreateEvent",
	"CreateAnonymousEvent",
	"DestroyAnonymousEvent",
	"CreateEvents",
	"MainLoop",
	"Receiver",
	"Bus",
	"Signal",
]
SUPPORT_NP_TYPES = [np.int8, np.int16, np.int32, np.uint8, np.uint16, np.uint32,]
TOP_PREFIX = environ.get("TOPMODULE") + "."
buses = list()
event_dict = dict()
event_released = set()
bus_dict = dict()
waiting_coro = list()
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
	def value(self, value):
		if not value is self._value:
			np.copyto(self._value, value)

	@property
	def x(self) -> np.ndarray:
		"Get the underlying numpy array representing the X value(s)"
		return self._x

	@x.setter
	def x(self, x):
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

class Bus(object):
	"""
	A wrapper that keeps a bus with its reference and provide accessor.
	There are 3 ways to access the signals:
	(1) self.values[99], self.xs[99]
	(2) self.signals[99].x, self.signals[99].value
	(3) self[99].x, self[99].value (Shortcut for (2))
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
	def __init__(self, idx, vs, xs):
		self.idx = idx
		self._vs = vs
		self._xs = xs
		self.signals = tuple(Signal(v, x) for v, x in zip(vs, xs))

	@property
	def values(self) -> Tuple[np.ndarray, ...]:
		"Get the underlying tuple of numpy arrays representing the value(s)"
		return self._vs

	@values.setter
	def values(self, v):
		if not v is self._vs:
			for ss, vv in zip(self.signals, v):
				ss.value = vv

	@property
	def xs(self) -> Tuple[np.ndarray, ...]:
		"Get the underlying tuple of numpy arrays representing the X value(s)"
		return self._xs

	@xs.setter
	def xs(self, x):
		if not x is self._xs:
			for ss, xx in zip(self.signals, x):
				ss.x = xx

	@property
	def value(self) -> np.ndarray:
		return self._vs[0]

	@value.setter
	def value(self, value):
		self.signals.value = value

	@property
	def x(self) -> np.ndarray:
		return self._xs

	@x.setter
	def x(self, x):
		self.signals.x = x

	@property
	def signal(self) -> Signal:
		return self.signals[0]

	def __getitem__(self, i):
		return self.signals[i]

	def Read(self):
		ReadBus(self.idx, self._vs, self._xs)

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

def CreateBus(name: str, signals: Tuple[Tuple[Union[None, str], str, Tuple[int,...], Any]]):
	n = len(bus_dict)
	if n != bus_dict.setdefault(name, n):
		print("Bus [{}] already exists".format(name))
	else:
		# Create numpy arrays
		_CreateTup = lambda: tuple(
			np.zeros(
				shape=(1,) if len(signal[2]) == 0 else signal[2],
				dtype=np.int32 if signal[3] is None else signal[3]
			) for signal in signals
		)
		vtup = _CreateTup()
		xtup = _CreateTup()
		assert all(a.dtype in SUPPORT_NP_TYPES for a in vtup)
		buses.append(Bus(n, vtup, xtup))
		# Prepare for the C++ part
		grps = list()
		cur_hier = TOP_PREFIX
		for hier, sig, shape, nptype in signals:
			if not hier is None:
				cur_hier = TOP_PREFIX + hier + '.' if hier else TOP_PREFIX
			grps.append(((cur_hier+sig).encode(), shape))
		BindBus(grps)

def CreateEvent(name: str, hier: str):
	n = len(waiting_coro)
	if n != event_dict.setdefault(name, n):
		print("Event [{}] already exists".format(name))
	else:
		BindEvent(n, (TOP_PREFIX+hier).encode())
		waiting_coro.append(list())

def CreateAnonymousEvent():
	if len(event_released):
		return event_released.pop()
	else:
		n = len(waiting_coro)
		waiting_coro.append(list())
		return n

def DestroyAnonymousEvent(ev: int):
	waiting_coro[ev] = list()
	event_released.add(ev)

def CreateBuses(descs: dict):
	for k, v in descs.items():
		CreateBus(k, v)

def CreateEvents(descs: dict):
	for k, v in descs.items():
		CreateEvent(k, v)

def GetBusIdx(idx: Union[str,int]):
	return bus_dict[idx] if isinstance(idx, str) else idx

def GetBus(idx):
	return buses[GetBusIdx(idx)]

def GetEventIdx(idx: Union[str,int]):
	return event_dict[idx] if isinstance(idx, str) else idx

def SetEvent(ev):
	event_queue.append((GetEventIdx(ev),True))

def SetEvent1(ev):
	event_queue.append((GetEventIdx(ev),False))

def Fork(c):
	try:
		while True:
			idx = GetEventIdx(next(c))
			if not idx is None:
				waiting_coro[idx].append(c)
				break
	except StopIteration:
		pass

def RegisterCoroutines(coro: list):
	for c in coro:
		Fork(c)

def MainLoop():
	while len(event_queue) != 0:
		event_idx, all_ev = event_queue.pop()
		if all_ev:
			proc = waiting_coro[event_idx]
			waiting_coro[event_idx] = list()
		else:
			proc = [waiting_coro.pop()]
		RegisterCoroutines(proc)
