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
from nicotb.protocol import TwoWire
import numpy as np
from itertools import repeat

def main():
	Ns = np.array([0,8,7], dtype=np.int32)
	scb = Scoreboard()
	test = scb.GetTest("test")
	golden = np.concatenate([
		np.arange(N+1, dtype=np.int32) for N in Ns
	])[:,np.newaxis]
	st = Stacker(golden.shape[0], [test.Get])
	test.Expect((golden,))
	yield rst_out_ev

	master = TwoWire.Master(irdy, iack, i, ck_ev)
	slave = TwoWire.Slave(ordy, oack, o, ck_ev, callbacks=[st.Get])

	values = master.values
	def it():
		for N in Ns:
			values[0][0] = N
			yield values
	yield from master.SendIter(it())

	# for i in range(100):
	# 	yield ck_ev
	yield from repeat(ck_ev, 100)
	FinishSim()

irdy, iack, i = CreateBuses([
	("irdy",),
	("iack",),
	("iint",),
])
ordy, oack, o = CreateBuses([
	("ordy",),
	("oack",),
	("oint",),
])
rst_out_ev, ck_ev = CreateEvents(["rst_out", "ck_ev",])
RegisterCoroutines([
	main(),
])
