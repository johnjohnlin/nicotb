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
from nicotb.protocol import TwoWire
from nicotb.primitives import Semaphore
import numpy as np

class MasterLite(object):
	__slots__ = ["aw", "w", "b", "ar", "r", "sem", "writing", "clk"]
	def __init__(
		self,
		aw_rdy: Bus, aw_ack: Bus, aw: Bus,
		w_rdy: Bus, w_ack: Bus, w: Bus,
		b_rdy: Bus, b_ack: Bus, b: Bus,
		ar_rdy: Bus, ar_ack: Bus, ar: Bus,
		r_rdy: Bus, r_ack: Bus, r: Bus,
		clk: int, A=1, B=5,
		read_callbacks=list()
	):
		clk = GetEvent(clk)
		self.clk = clk
		self.sem = Semaphore(-1)
		self.aw = TwoWire.Master(aw_rdy, aw_ack, aw, clk, callbacks=[self.sem.ReleaseNB])
		self.w  = TwoWire.Master(w_rdy , w_ack , w , clk, callbacks=[self.sem.ReleaseNB])
		self.b  = TwoWire.Slave (b_rdy , b_ack , b , clk, callbacks=[self._NoErr])
		self.ar = TwoWire.Master(ar_rdy, ar_ack, ar, clk)
		self.r  = TwoWire.Slave (r_rdy , r_ack , r , clk, callbacks=read_callbacks)
		self.writing = False

	def _NoErr(self, values):
		assert self.writing, "Premature write reponse"
		assert values[0][0] == 0, "Must get OKAY response 0b00"
		self.writing = False
		self.sem.ReleaseNB()

	def Write(self, a, d):
		self.writing = True
		self.aw.data.value[0] = a
		self.w.data.value[0] = d
		Fork(self.aw.Send(self.aw.values, imm=False))
		Fork(self.w.Send(self.w.values, imm=False))
		yield from self.sem.Acquire(3)

	def Read(self, a):
		self.r.value[0] = a
		yield from self.r.Send(self.r.values)
