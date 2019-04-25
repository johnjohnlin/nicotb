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
from nicotb import *
import numpy as np

class Master(Receiver):
	__slots__ = [
		"vsync", "hsync", "data", "clk",
		"VRANGE", "VSYNC", "VVALID",
		"HRANGE", "HSYNC", "HVALID",
		"strict",
	]
	def _Translate(self, timing):
		idx = np.arange(sum(timing), dtype=np.int32)
		return (
			idx,
			np.bitwise_or(idx < timing[0], idx >= timing[0]+timing[1]),
			idx >= sum(timing[:-1])
		)

	def __init__(
		self, vsync: Bus, hsync: Bus, data: Bus, clk: int,
		VTIMING, HTIMING, callbacks = list(), strict = True
	):
		super(Master, self).__init__(callbacks)
		self.vsync = GetBus(vsync)
		self.hsync = GetBus(hsync)
		self.data = GetBus(data)
		self.clk = GetEvent(clk)
		self.VRANGE, self.VSYNC, self.VVALID = self._Translate(VTIMING)
		self.HRANGE, self.HSYNC, self.HVALID = self._Translate(HTIMING)
		self.vsync.value[0] = 1
		self.hsync.value[0] = 1
		self.data.SetToNumber()
		self.strict = strict

	def _FrameBody(self, frame):
		it = iter(frame)
		for y in self.VRANGE:
			for x in self.HRANGE:
				self.hsync.value[0] = self.VSYNC[y]
				self.vsync.value[0] = self.HSYNC[x]
				if self.VVALID[y] and self.HVALID[x]:
					self.data.SetToNumber()
					self.data.values = next(it)
				elif self.strict:
					self.data.SetToX()
				self.hsync.Write()
				self.vsync.Write()
				self.data.Write()
				yield self.clk
		super(Master, self).Get(frame)

	def _FrameEnd(self):
		self.hsync.value[0] = 1
		self.vsync.value[0] = 1
		self.data.SetToX()
		self.hsync.Write()
		self.vsync.Write()
		self.data.Write()
		yield self.clk

	def SendFrame(self, frame):
		yield from self._FrameBody(frame)
		yield from self._FrameEnd()

	def SendFrames(self, frames):
		for frame in frames:
			yield from self._FrameBody(frame)
		yield from self._FrameEnd()

	@property
	def values(self) -> tuple:
		return self.data.values

"""
class Slave(Receiver):
	__slots__ = ["valid", "data"]
	def __init__(self, data, valid, callbacks = list()):
		super(Slave, self).__init__(callbacks)
		self.valid = GetEvent(valid)
		self.data = GetBus(data)
		Fork(self.Monitor())

	def Monitor(self):
		while True:
			yield self.valid
			self.data.Read()
			super(Slave, self).Get(self.data)
"""
