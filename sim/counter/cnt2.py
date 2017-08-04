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
from nicotb.bus import TwoWire
import numpy as np
from itertools import repeat

def main():
	Ns = np.array([0,8,7], dtype=np.int32)
	ck_ev = GetEventIdx("clk")
	iack_ev = GetEventIdx("iack")
	ordy_ev = GetEventIdx("ordy")
	irdy_bus    = GetBus("irdy"   )
	ocanack_bus = GetBus("ocanack")
	i_bus       = GetBus("i"      )
	o_bus       = GetBus("o"      )
	f_bus       = GetBus("f"      )
	scb = Scoreboard()
	test = scb.GetTest("test")
	golden = np.concatenate([
		np.arange(N+1, dtype=np.int32) for N in Ns
	])[:,np.newaxis]
	st = Stacker(golden.shape[0], [test.Get])
	test.Expect((golden,))
	yield "rst_out"

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

CreateBuses({
	"irdy":    ((""   , "irdy"   , tuple(), None),),
	"ocanack": ((""   , "can_ack", tuple(), None),),
	"i":       ((""   , "iint"   , tuple(), None),),
	"o":       ((""   , "oint"   , tuple(), None),),
	"f":       (("u_f", "fin"    , tuple(), None),),
})
CreateEvents({
	"rst_out": ("u_cs.rst_out",  []),
	"clk":     ("u_cs.clock",    []),
	"iack":    ("u_d0.detected", []),
	"ordy":    ("u_d1.detected", [GetBusIdx('o')]),
})
RegisterCoroutines([
	main(),
])
