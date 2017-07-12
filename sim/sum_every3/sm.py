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
	rs_ev = ToEventIdx("rst")
	ck_ev = ToEventIdx("clk")
	odval_ev = ToEventIdx("dst_dval")
	src_val = GetBus("src_dval")
	src_dat = GetBus("src")
	dst_dat = GetBus("dst")
	scb = Scoreboard()
	test1 = scb.GetTest("test1")
	st = Stacker(N, [test1.Get])

	yield rs_ev
	master = OneWire.Master(src_val, src_dat, ck_ev, callbacks=[print])
	slave = OneWire.Slave(odval_ev, dst_dat, callbacks=[print, st.Get])
	values = master.values
	arr = np.random.randint(16, size=N*3)
	golden = np.sum(np.reshape(arr, (-1,3)), axis=1, keepdims=1)
	test1.Expect((golden,)) # must pass
	# test1.Expect((golden+1,)) # must fail
	for i in arr:
		values[0][0] = i
		yield from master.Send(values)
		yield ck_ev

RegisterCoroutines([
	main(),
])
