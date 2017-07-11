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
from nicotb.bus import OneWire

def main():
	rs_ev = ToEventIdx("rst")
	ck_ev = ToEventIdx("clk")
	odval_ev = ToEventIdx("dst_get")
	src_val = GetBus("src_dval")
	dsc_val = GetBus("dst_dval")
	src_dat = GetBus("src")
	dst_dat = GetBus("dst")

	yield rs_ev
	master = OneWire.Master(src_val, src_dat, ck_ev)
	values = master.values
	for i in range(30):
		values[0][0] = i
		yield from master.Send(values)
		yield ck_ev

RegisterCoroutines([
	main(),
])
