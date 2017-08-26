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

	master = TwoWire.Master(irdy_bus, i_bus, iack_ev, ck_ev)
	slave = TwoWire.Slave(ocanack_bus, o_bus, ordy_ev, callbacks=[st.Get])

	values = master.values
	def it():
		for N in Ns:
			values[0][0] = N
			yield values
	yield from master.SendIter(it())

	# for i in range(100):
	# 	yield ck_ev
	yield from repeat(ck_ev, 100)
	f_bus.value[0] = 1
	f_bus.Write()

irdy_bus, ocanack_bus, i_bus, o_bus, f_bus = CreateBuses([
	((""   , "irdy"   , tuple(), None),),
	((""   , "can_ack", tuple(), None),),
	((""   , "iint"   , tuple(), None),),
	((""   , "oint"   , tuple(), None),),
	(("u_f", "fin"    , tuple(), None),),
])
rst_out_ev, ck_ev, iack_ev, ordy_ev = CreateEvents([
	"u_cs.rst_out",
	"u_cs.clock",
	"u_d0.detected",
	"u_d1.detected",
])
RegisterCoroutines([
	main(),
])
