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
from nicotb.protocol import OneWire, Response
from nicotb.primitives import Semaphore
from nicotb.utils import RandProb
import numpy as np

class SlaveLite(object):
	__slots__ = ["clk", "read_fn", "write_fn", "A", "B", "wen", "ren", "wait_req", "addr", "wd", "rd", "resp"]
	def __init__(
		self, wen: Bus, ren: Bus, wait_req: Bus, rval: Bus,
		addr: Bus, wd: Bus, rd: Bus,
		write_fn, read_fn,
		clk: int, A=1, B=5, Aresp=0, Bresp=1,
		read_callbacks=list()
	):
		clk = GetEvent(clk)
		self.clk = clk
		self.write_fn = write_fn
		self.read_fn = read_fn
		self.A = B-A
		self.B = B
		(
			self.wen, self.ren, self.wait_req,
			self.addr, self.wd
		) = CreateBuses([wen, ren, wait_req, addr, wd])
		self.rd = OneWire.Master(rval, rd, clk, callbacks=read_callbacks)
		self.resp = Response.Response(self.rd.SendIter, clk, Aresp, Bresp)
		self.wait_req.value[0] = RandProb(self.A, self.B)
		self.wait_req.Write()
		Fork(self._Response())

	def _Response(self):
		while True:
			yield self.clk
			self.wen.Read()
			self.ren.Read()
			if (
				self.wen.x[0] != 0 or self.ren.x[0] != 0 or
				self.ren.value[0] == 0 and self.wen.value[0] == 0
			):
				continue
			if self.wait_req.value[0] == 0:
				self.addr.Read()
				if self.ren.value[0] == 1:
					rd_int = self.read_fn(self.addr.value[0])
					rd = np.empty_like(self.rd.values[0])
					rd[0] = rd_int
					self.resp.Append((rd,))
				else:
					self.wd.Read()
					self.write_fn(self.addr.value[0], self.wd.value[0])
			self.wait_req.value[0] = RandProb(self.A, self.B)
			self.wait_req.Write()
