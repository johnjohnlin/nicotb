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
from nicotb.protocol import Axi
import numpy as np

def main():
	master = Axi.MasterLite(
		("aw_rdy",),
		("aw_ack",),
		("aw",),
		("w_rdy",),
		("w_ack",),
		("w",),
		("b_rdy",),
		("b_ack",),
		("b",),
		("ar_rdy",),
		("ar_ack",),
		("ar",),
		("r_rdy",),
		("r_ack",),
		("r",),
		ck_ev,
		read_callbacks=[print]
	)
	yield rst_out
	yield ck_ev

	yield from master.Write(0, 2)
	yield from master.Write(1, 5)
	yield from master.Write(4, 3)
	yield from master.Read(4)
	yield from master.Read(0)
	yield from master.Read(1)

	for i in range(100):
		yield ck_ev
	FinishSim()

rst_out, ck_ev = CreateEvents(["rst_out", "ck_ev",])
RegisterCoroutines([
	main(),
])
