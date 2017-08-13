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
	__slots__ = ["valid", "data", "clk", "A", "B"]
	def __init__(self, valid: Bus, data: Bus, clk: int, A = 1, B = 5, callbacks = list()):
		super(Master, self).__init__(callbacks)
		self.valid = valid
		self.data = data
		self.clk = clk
		self.A = A
		self.B = B
		self.valid.SetToNumber()
		self.data.SetToNumber()

	def _D(self, data):
		self.valid.value[0] = 1
		self.data.SetToNumber()
		self.data.values = data
		self.valid.Write()
		self.data.Write()

	def _X(self):
		self.valid.value[0] = 0
		self.data.SetToX()
		self.valid.Write()
		self.data.Write()

	def SendIter(self, it):
		for data in it:
			self._D(data)
			yield self.clk
			super(Master, self).Get(data)
			if not RandProb(self.A, self.B):
				self._X()
				yield self.clk
				while not RandProb(self.A, self.B):
					yield self.clk
		self._X()
		yield self.clk

	def Send(self, data):
		self._D(data)
		yield self.clk
		super(Master, self).Get(data)
		self._X()
		yield self.clk

	@property
	def values(self) -> tuple:
		return self.data.values

class Slave(Receiver):
	__slots__ = ["valid", "data"]
	def __init__(self, data: Bus, valid: int, callbacks = list()):
		super(Slave, self).__init__(callbacks)
		self.valid = valid
		self.data = data
		Fork(self.Monitor())

	def Monitor(self):
		while True:
			yield self.valid
			self.data.Read()
			super(Slave, self).Get(self.data)
