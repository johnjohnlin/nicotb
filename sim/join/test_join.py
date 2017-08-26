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
from nicotb.protocol import OneWire
import numpy as np

N = 10

def main():
	def it(v, n):
		for i in range(n):
			v[0][0] = i
			yield v
	yield rs_ev
	master1 = OneWire.Master(dval1_bus, d1_bus, ck_ev, callbacks=[print], A=4)
	master2 = OneWire.Master(dval2_bus, d2_bus, ck_ev, callbacks=[print], A=4)

	values1 = master1.values
	values2 = master2.values
	for t1, t2 in [[5,10], [10,5]]:
		th_fin1 = JoinableFork(master1.SendIter(it(values1, t1)))
		th_fin2 = JoinableFork(master2.SendIter(it(values2, t2)))
		yield from th_fin1.Join()
		yield from th_fin2.Join()
		print("Finish")
		# will cause small leak if you do not destroy them
		th_fin1.Destroy()
		th_fin2.Destroy()
		for i in range(30):
			yield ck_ev
	print("All done")

dval1_bus, dval2_bus, d1_bus, d2_bus = CreateBuses([
	(("", "dval1", tuple(), None),),
	(("", "dval2", tuple(), None),),
	(("", "d1"   , tuple(), None),),
	(("", "d2"   , tuple(), None),),
])
ck_ev, rs_ev = CreateEvents(["u_cr.clock", "u_cr.rst_out"])
RegisterCoroutines([
	main(),
])
