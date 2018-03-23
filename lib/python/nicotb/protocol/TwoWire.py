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
from nicotb.utils import RandProb

class Master(Receiver):
	__slots__ = ["rdy", "ack", "data", "clk", "A", "B", "strict"]
	def __init__(
		self, rdy: Bus, ack: Bus, data: Bus,
		clk: int, A = 1, B = 5, callbacks = list(), strict = True
	):
		super(Master, self).__init__(callbacks)
		self.rdy = GetBus(rdy)
		self.ack = GetBus(ack)
		self.data = GetBus(data)
		self.clk = GetEvent(clk)
		self.A = A
		self.B = B
		self.strict = strict
		self.rdy.value[0] = 0
		self.rdy.Write()

	def _D(self, data):
		self.rdy.value[0] = 1
		self.data.SetToNumber()
		self.data.values = data
		self.rdy.Write()
		self.data.Write()

	def _X(self):
		self.rdy.value[0] = 0
		if self.strict:
			self.data.SetToX()
		self.rdy.Write()
		self.data.Write()

	def SendIter(self, it):
		for data in it:
			self._D(data)
			while True:
				yield self.clk
				self.ack.Read()
				if self.ack.x[0] == 0 and self.ack.value[0] != 0:
					break
			super(Master, self).Get(data)
			if not RandProb(self.A, self.B):
				self._X()
				yield self.clk
				while not RandProb(self.A, self.B):
					yield self.clk
		self._X()
		yield self.clk

	def Send(self, data, imm=True):
		while not (imm or RandProb(self.A, self.B)):
			yield self.clk
		self._D(data)
		while True:
			yield self.clk
			self.ack.Read()
			if self.ack.x[0] == 0 and self.ack.value[0] != 0:
				break
		super(Master, self).Get(data)
		self._X()
		yield self.clk

	@property
	def values(self):
		return self.data.values

class Slave(Receiver):
	__slots__ = ["rdy", "ack", "data", "clk", "A", "B"]
	def __init__(
		self, rdy: Bus, ack: Bus, data: Bus,
		clk: int, A=1, B=5, callbacks=list()
	):
		super(Slave, self).__init__(callbacks)
		self.rdy = GetBus(rdy)
		self.ack = GetBus(ack)
		self.data = GetBus(data)
		self.clk = GetEvent(clk)
		self.A = A
		self.B = B
		self.ack.value[0] = RandProb(self.A, self.B)
		self.ack.Write()
		Fork(self.Monitor())

	def Monitor(self):
		while True:
			yield self.clk
			self.rdy.Read()
			if self.rdy.x[0] != 0 or self.rdy.value[0] == 0:
				continue
			if self.ack.value[0] != 0:
				self.data.Read()
				super(Slave, self).Get(self.data)
			self.ack.value[0] = RandProb(self.A, self.B)
			self.ack.Write()
