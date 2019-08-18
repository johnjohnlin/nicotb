# Copyright (C) 2017,2019, Yu Sheng Lin, johnjohnlys@media.ee.ntu.edu.tw

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
from nicotb.utils import Scoreboard, BusGetter, Stacker
from nicotb.protocol import OneWire
import numpy as np
from os import getenv

N = 10

def main():
	scb = Scoreboard()
	test1 = scb.GetTest("test1", squeeze=True)
	st = Stacker(N, callbacks=[test1.Get, lambda x: print("Print with name: {}".format(x.o))])
	bg = BusGetter(callbacks=[st.Get])
	yield rs_ev
	yield ck_ev
	master = OneWire.Master(src_val, src_dat, ck_ev, callbacks=[print])
	slave = OneWire.Slave(dst_val, dst_dat, ck_ev, callbacks=[print, bg.Get])
	values = master.values
	arr = np.random.randint(16, size=(N*3,2)).astype(np.int32)
	golden = np.sum(np.reshape(arr, (-1,6)), axis=1, dtype=np.int32)
	test1.Expect((golden,)) # must pass
	# test1.Expect((golden+1,)) # must fail
	ITER = not getenv("ITER") is None
	print("Iteration mode is set to {}".format(ITER))
	if ITER:
		def it():
			for i in arr:
				print(arr, i)
				np.copyto(values.i, i)
				yield values
		yield from master.SendIter(it())
	else:
		for i in arr:
			np.copyto(values.i, i)
			yield from master.Send(values)
	for i in range(10):
		yield ck_ev
	assert st.is_clean
	FinishSim()

src_val, dst_val, src_dat, dst_dat = CreateBuses([
	("i_dval",),
	("o_dval",),
	(("u_dut", "i", (2,)),),
	(("u_dut", "o"),),
])
ck_ev, rs_ev = CreateEvents(["ck_ev", "rst_out",])
RegisterCoroutines([
	main(),
])
