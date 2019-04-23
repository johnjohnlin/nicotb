# Copyright (C) 2018, Yu Sheng Lin, johnjohnlys@media.ee.ntu.edu.tw

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

def main():
	# If we find string "JUSTMONIKA", then finish the simulation
	pattern = [ord(c) for c in "JUSTMONIKA"]
	match_idx = 0
	yield rst_out
	while True:
		yield clk
		bus.Read()
		if bus.character.value[0] == pattern[match_idx]:
			match_idx = match_idx+1
			if match_idx == len(pattern):
				break
		else:
			match_idx = 0
	yield clk
	FinishSim()

bus = CreateBus((
	(""  , "character"),
))
rst_out, clk = CreateEvents(["rst_out", "ck_ev"])

RegisterCoroutines([main()])
