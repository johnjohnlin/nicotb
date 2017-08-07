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
from nicotb.primitives import JoinableFork
from nicotb.bus import OneWire
import numpy as np

N = 10

def main():
	def it(v, n):
		for i in range(n):
			v[0][0] = i
			yield v
	rs_ev = GetEventIdx("rst")
	ck_ev = GetEventIdx("clk")
	dval1_bus = GetBus("dval1")
	dval2_bus = GetBus("dval2")
	d1_bus = GetBus("d1")
	d2_bus = GetBus("d2")

	yield rs_ev
	master1 = OneWire.Master(dval1_bus, d1_bus, ck_ev, callbacks=[print])
	master2 = OneWire.Master(dval2_bus, d2_bus, ck_ev, callbacks=[print])

	values1 = master1.values
	values2 = master2.values
	for t1, t2 in [[5,10], [10,5]]:
		th_fin1 = JoinableFork(master1.SendIter(it(values1, t1)))
		th_fin2 = JoinableFork(master2.SendIter(it(values2, t2)))
		print("Waiting: {}, {}".format(th_fin1.event, th_fin2.event))
		yield th_fin1.event
		print("Middle: {}, {}".format(th_fin1.event, th_fin2.event))
		yield th_fin2.event
		print("Finish: {}, {}".format(th_fin1.event, th_fin2.event))
		# will cause small leak if you do not destroy them
		th_fin1.Destroy()
		th_fin2.Destroy()
	print("All done")

CreateBuses({
	"dval1": (("", "dval1", tuple(), None),),
	"dval2": (("", "dval2", tuple(), None),),
	"d1":    (("", "d1"   , tuple(), None),),
	"d2":    (("", "d2"   , tuple(), None),),
})
CreateEvents({
	"clk":      ("u_cr.clock",     []),
	"rst":      ("u_cr.rst_out",   []),
})
RegisterCoroutines([
	main(),
])
