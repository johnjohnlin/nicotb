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

class Master(Receiver):
	__slots__ = ["valid", "data", "clk", "A", "B"]
	def __init__(self, valid, data, clk, A = 1, B = 5, callbacks = list()):
		super(Master, self).__init__(callbacks)
		self.valid = valid
		self.data = data
		self.clk = clk
		self.A = A
		self.B = B
		self.valid.SetToNumber()
		self.data.SetToNumber()

	def SendIter(self):
		raise NotImplementedError()

	def Send(self, data):
		self.valid[0].value[0] = 1
		self.data.SetToNumber()
		self.data.values = data
		self.valid.Write()
		self.data.Write()
		yield self.clk
		super(Master, self).Get(data)
		self.valid[0].value[0] = 0
		self.data.SetToX()
		self.valid.Write()
		self.data.Write()

	@property
	def values(self):
		return self.data.values

class Slave(Receiver):
	__slots__ = ["valid", "data"]
	def __init__(self, valid):
		self.valid = valid
		self.data = data

	def Monitor(self):
		while True:
			yield self.valie
			self.Get(data)
