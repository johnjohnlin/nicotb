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
from nicotb.utils import Scoreboard, Stacker
from nicotb.bus import OneWire
import numpy as np

N = 10

def main():
	rs_ev = GetEventIdx("rst")
	ck_ev = GetEventIdx("clk")
	odval_ev = GetEventIdx("dst_dval")
	src_val = GetBus("src_dval")
	src_dat = GetBus("src")
	dst_dat = GetBus("dst")
	scb = Scoreboard()
	test1 = scb.GetTest("test1")
	st = Stacker(N, [test1.Get])

	yield rs_ev
	master = OneWire.Master(src_val, src_dat, ck_ev, callbacks=[print])
	slave = OneWire.Slave(dst_dat, odval_ev, callbacks=[print, st.Get])
	values = master.values
	arr = np.random.randint(16, size=N*3, dtype=np.int32)
	golden = np.sum(np.reshape(arr, (-1,3)), axis=1, keepdims=1, dtype=np.int32)
	test1.Expect((golden,)) # must pass
	# test1.Expect((golden+1,)) # must fail
	def it():
		for i in arr:
			values[0][0] = i
			yield values
	yield from master.SendIter(it())

	for i in range(10):
		yield ck_ev
	assert st.is_clean

CreateBuses({
	"src_dval": (
		("", "i_dval", tuple(), None),
	),
	"src": (
		("u_dut", "i", tuple(), None),
	),
	"dst": (
		("u_dut", "o", tuple(), None),
	),
})
CreateEvents({
	"clk":      "u_cr.clock",
	"rst":      "u_cr.rst_out",
	"dst_dval": "u_ldo.detected",
})
RegisterCoroutines([
	main(),
])
