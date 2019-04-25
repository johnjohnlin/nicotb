# Copyright (C) 2018, Yu Sheng Lin, johnjohnlys@media.ee.ntu.edu.tw

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

# Only 32b mode
# Do not support error and burst

class Master(object):
	__slots__ = [
		"hsel", "haddr", "hwrite", "htrans", "hsize", "hburst",
		"hready", "hresp", "hrdata", "hwdata", "clk",
	]
	def __init__(
		self,
		hsel, haddr, hwrite, htrans, hsize, hburst, hready, hresp,
		hrdata, hwdata, clk
	):
		clk = GetEvent(clk)
		self.clk = clk
		self.hsel = hsel
		self.haddr = haddr
		self.hwrite = hwrite
		self.htrans = htrans
		self.hsize = hsize
		self.hburst = hburst
		self.hready = hready
		self.hresp = hresp
		self.hrdata = hrdata
		self.hwdata = hwdata
		self.hsel.value[0] = 0
		self.hwrite.value[0] = 0
		self.haddr.value[0] = 0
		self.htrans.value[0] = 0
		self.hsize.value[0] = 2
		self.hburst.value[0] = 0
		self.hsel.Write()
		self.hwrite.Write()
		self.haddr.Write()
		self.htrans.Write()
		self.hsize.Write()
		self.hburst.Write()

	def Write(self, a, d):
		yield from self.IssueCommands([(True, a, d)])

	def Read(self, a):
		ret = yield from self.IssueCommands([(False, a)])
		return ret[0]

	def IssueCommands(self, it):
		# format: iterable tuples (True, write_a, write_d) or (False, read_a)
		# return a list of read_d
		ret = list()
		prev = None
		self.hsel.value[0] = 1
		self.htrans.value[0] = 2
		self.hsel.Write()
		self.htrans.Write()
		for cmd in it:
			self._HandleCommand(cmd)
			self._HandleWdata(prev)
			if prev is None:
				# Fisrt cycle should be responsed immediately
				yield self.clk
			else:
				yield from self._WaitReady(prev[0], ret)
			prev = cmd
		# prev is None when iter is empty
		if not prev is None:
			self._HandleWdata(prev)
			self.htrans.value[0] = 0
			self.htrans.Write()
			yield from self._WaitReady(prev[0], ret)
			self.hsel.value[0] = 0
			self.hsel.Write()
		return ret

	def _HandleCommand(self, cmd):
		self.haddr.value[0] = cmd[1]
		self.hwrite.value[0] = int(cmd[0])
		self.haddr.Write()
		self.hwrite.Write()

	def _HandleWdata(self, cmd_prev):
		if (not cmd_prev is None) and cmd_prev[0]:
			self.hwdata.value[0] = cmd_prev[2]
			self.hwdata.Write()

	def _WaitReady(self, is_write, ret):
		while True:
			yield self.clk
			self.hready.Read()
			if self.hready.value[0]:
				if not is_write:
					self.hrdata.Read()
					ret.append(int(self.hrdata.value[0]))
				break
