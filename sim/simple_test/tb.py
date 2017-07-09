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
	yield "rst_out"
	while True:
		yield "clk"
		if abus.is_number:
			cbbus[0].value[1,1] = abus[0].value[0]
		else:
			cbbus.set_to_x()
		cbbus.write()

RegisterCoroutines([
	clk(),
	rst_out(),
	rst_out2(),
])
