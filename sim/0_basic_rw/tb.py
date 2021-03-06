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
import numpy as np

checkpoint = [False]*3
def rst_out_cb1():
	print("reset wait")
	checkpoint[0] = True
	yield rst_out
	print("reset out")
	checkpoint[1] = True
	yield rst_out
	assert 0, "This should not happen"

def rst_out_cb2():
	yield rst_out
	print("reset out 2")
	checkpoint[2] = True

def clk_cb():
	cbbus.SetToX()
	cbbus[0].x[1,1] = 0
	yield rst_out
	for i in range(50):
		yield clk
		abus.Read()
		if abus.is_number:
			cbbus[0].value[1,1] = abus[0].value[0]
		else:
			cbbus.SetToX()
		cbbus.Write()
	assert(all(checkpoint))
	FinishSim()

cbbus, abus = CreateBuses([
	(
		(""  , "c", (2,4)),
		(None, "b", (3,2,4)),
	),
	("a",),
])
rst_out, clk = CreateEvents(["rst_out", "ck_ev"])

RegisterCoroutines([
	clk_cb(),
	rst_out_cb1(),
	rst_out_cb2(),
])
