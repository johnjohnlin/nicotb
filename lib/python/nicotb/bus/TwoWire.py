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
	__slots__ = ["rdy", "data", "ack", "clk", "A", "B"]
	def __init__(self, rdy: Bus, data: Bus, ack: int, clk: int, A = 1, B = 5, callbacks=list()):
		super(Master, self).__init__(callbacks)
		self.rdy = rdy
		self.data = data
		self.ack = ack
		self.clk = clk
		self.A = A
		self.B = B
		self.rdy.value[0] = 0
		self.rdy.Write()

	def SendIter(self):
		raise NotImplementedError()

	def Send(self, data):
		yield self.clk
		self.rdy.value[0] = 1
		self.data.values = data
		self.rdy.Write()
		self.data.Write()
		yield self.ack
		super(Master, self).Get(data)
		self.rdy.value[0] = 0
		self.data.SetToX()
		self.rdy.Write()
		self.data.Write()

	@property
	def values(self):
		return self.data.values

class Slave(Receiver):
	__slots__ = ["can_ack", "data", "rdy", "clk", "A", "B"]
	def __init__(self, can_ack: Bus, data: Bus, rdy: int, A = 1, B = 5, callbacks=list()):
		super(Slave, self).__init__(callbacks)
		self.can_ack = can_ack
		self.data = data
		self.rdy = rdy
		self.A = A
		self.B = B
		self.can_ack.value[0] = RandProb(self.A, self.B)
		self.can_ack.Write()
		Fork(self.Monitor())

	def Monitor(self):
		while True:
			yield self.rdy
			if self.can_ack.value[0]:
				super(Slave, self).Get(self.data)
			self.can_ack.value[0] = RandProb(self.A, self.B)
			self.can_ack.Write()
