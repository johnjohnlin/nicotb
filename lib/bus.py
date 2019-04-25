# Copyright (C) 2017-2018, Yu Sheng Lin, johnjohnlys@media.ee.ntu.edu.tw

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
from nicotb.common import *
from nicotb_bridge import BindBus, ReadBus, WriteBus
from collections import deque
import numpy as np

buses = list()

class SignalTuple(tuple):
	"Subclass of tuple, for implicit use only."
	def __new__(cls, t, n2s):
		return super(SignalTuple, cls).__new__(cls, t)

	def __init__(self, t, n2s):
		self._n2s = n2s._n2s if isinstance(n2s, SignalTuple) else n2s

	def __getitem__(self, i):
		return getattr(self, i) if isinstance(i, str) else super(SignalTuple, self).__getitem__(i)

	def __getattr__(self, i):
		i = self._n2s.get(i)
		if i is None:
			raise AttributeError
		return super(SignalTuple, self).__getitem__(i)

	def Copy(self):
		return SignalTuple(tuple(x.copy() for x in self), self)

class Signal(object):
	"A wrapper that keeps a signal in a bus"
	__slots__ = ["_x", "_value"]
	def __init__(self, v, x):
		self._value = v
		self._x = x

	@property
	def value(self):
		"Get the underlying numpy array representing the value(s)"
		return self._value

	@value.setter
	def value(self, value):
		if not value is self._value:
			np.copyto(self._value, value)

	@property
	def x(self):
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

	def __str__(self):
		return str(self._value) if self.is_number else "X"

class Bus(object):
	"""
	A wrapper that keeps a bus with its reference and provide accessor.
	There are 3 ways to access the signals:
	(1) self.values[99], self.xs[99]
	(2) self.signals[99].x, self.signals[99].value
	(3) self[99].x, self[99].value (Shortcut for (2))
	(4) self['abc'].x, self['abc'].value (Similar with (3), lookup by wire name.
	    If multiple wires have the same name (under diffferent modules),
	    the the name with smaller ID will be overrided.
	(5) self.abc.x, self.abc.value (__getattr__ version for (4))
	    Be careful when __getattr__ is called only when default getter fails,
	    so avoid Python class built-in names, 'idx', 'signals' and names starts with underscore(s).
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
	_write_pend = set()
	__slots__ = ["idx", "_vs", "_xs", "signals"]

	def __init__(self, idx, vs, xs):
		self.idx = idx
		self._vs = vs
		self._xs = xs
		# copy the name lookup table
		self.signals = SignalTuple((Signal(v, x) for v, x in zip(vs, xs)), vs)

	@property
	def values(self):
		"Get the underlying tuple of numpy arrays representing the value(s)"
		return self._vs

	@values.setter
	def values(self, v):
		if not v is self._vs:
			for ss, vv in zip(self.signals, v):
				ss.value = vv

	@property
	def xs(self):
		"Get the underlying tuple of numpy arrays representing the X value(s)"
		return self._xs

	@xs.setter
	def xs(self, x):
		if not x is self._xs:
			for ss, xx in zip(self.signals, x):
				ss.x = xx

	@property
	def value(self):
		return self._vs[0]

	@value.setter
	def value(self, value):
		self.signals[0].value = value

	@property
	def x(self):
		return self._xs[0]

	@x.setter
	def x(self, x):
		self.signals[0].x = x

	@property
	def signal(self):
		return self.signals[0]

	def __getitem__(self, i):
		return getattr(self, i) if isinstance(i, str) else self.signals[i]

	def __getattr__(self, i):
		if i is None:
			raise AttributeError
		return self.signals[i]

	def Read(self):
		ReadBus(self.idx, self._vs, self._xs)

	def Write(self, imm=False):
		if imm:
			WriteBus(self.idx, self._vs, self._xs)
		else:
			Bus._write_pend.add(self)

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

	def __str__(self):
		s = ",".join(str(s) for s in self.signals)
		return "Bus <{}>".format(s)

def _ConvertSignal(signal):
	if isinstance(signal, str):
		return (None, signal, tuple(), np.int32)
	else:
		l = len(signal)
		if l == 1:
			return (None, signal[0], tuple(), np.int32)
		if l == 2:
			return signal + (tuple(), np.int32)
		if l == 3:
			return signal + (np.int32,)
		if l == 4:
			return signal

def CreateBus(signals):
	n = len(buses)
	signals = tuple(_ConvertSignal(signal) for signal in signals)
	# Create numpy arrays
	name_2_sig_id = dict((s[1], i) for i, s in enumerate(signals))
	_CreateTup = lambda: SignalTuple(
		(np.zeros(
			shape=(1,) if len(signal[2]) == 0 else signal[2],
			dtype=np.int32 if signal[3] is None else signal[3]
		) for signal in signals),
		name_2_sig_id
	)
	vtup = _CreateTup()
	xtup = _CreateTup()
	assert all(a.dtype in SUPPORT_NP_TYPES for a in vtup)
	bus = Bus(n, vtup, xtup)
	buses.append(bus)
	# Prepare for the C++ part
	grps = list()
	# TOP_PREFIX is empty in Verilator mode
	cur_hier = TOP_PREFIX
	for hier, sig, shape, nptype in signals:
		# Never set hierarchy in Verilator mode
		if not hier is None and bool(TOP_PREFIX):
			cur_hier = TOP_PREFIX + hier + '.' if hier else TOP_PREFIX
		grps.append(((cur_hier+sig).encode(), shape))
	BindBus(grps)
	return bus

def CreateBuses(descs: list):
	return [CreateBus(bus) for bus in descs]

def GetBus(bus):
	if isinstance(bus, Bus):
		return bus
	else:
		return CreateBus(bus)

def FlushBusWrite():
	for s in Bus._write_pend:
		s.Write(True)
	Bus._write_pend.clear()
