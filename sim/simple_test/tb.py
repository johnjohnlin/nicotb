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
import numpy as np

def rst_out():
	print("reset wait")
	yield "rst_out"
	print("reset out")
	yield "rst_out"
	print("this should not happen")

def rst_out2():
	yield "rst_out"
	print("reset out 2")

def clk():
	abus = GetBus("a")
	cbbus = GetBus("cb")
	cbbus.SetToX()
	cbbus[0].x[1,1] = 0
	yield "rst_out"
	while True:
		yield "clk"
		if abus.is_number:
			cbbus[0].value[1,1] = abus[0].value[0]
		else:
			cbbus.SetToX()
		cbbus.Write()

CreateBuses({
	"cb": (
		("", "c", (2,4), None),
		(None, "b", (3,2,4), None),
	),
	"a": (
		("", "a", tuple(), np.int16),
	),
})
CreateEvents({
	"rst_out": ("u_cs.rst_out", []),
	"clk":     ("u_cs.clock",   [GetBusIdx('a')]),
})
RegisterCoroutines([
	clk(),
	rst_out(),
	rst_out2(),
])