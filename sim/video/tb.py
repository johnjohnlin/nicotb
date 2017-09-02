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
from nicotb.protocol import Video
import numpy as np

def cb():
	W = 4
	H = 3
	master = Video.Master(vs, hs, d, clk, (1,1,1,W), (1,1,1,H))
	yield rst_out
	yield from master.SendFrame(map(lambda x: (x,), range(W*H)))
	yield clk
	yield clk

vs, hs, d = CreateBuses([
	("vs",),
	("hs",),
	("d" ,),
])
rst_out, clk = CreateEvents(["rst_out", "ck_ev"])

RegisterCoroutines([
	cb(),
])
