#!/usr/bin/env python
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
from nicotb.utils import Scoreboard
from nicotb.primitives import JoinableFork
from nicotb.event import waiting_coro
import numpy as np

def WaitCycles(n):
	for i in range(n):
		yield ck_ev

def main():
	scb = Scoreboard("Join")
	tst = scb.GetTest("test")
	tst.Expect([])
	for t1, t2 in [[5,10], [10,5], [5,5]]:
		th_fin1 = JoinableFork(WaitCycles(t1))
		th_fin2 = JoinableFork(WaitCycles(t2))
		yield from th_fin1.Join()
		yield from th_fin2.Join()
		# will cause small leak if you do not destroy them
		th_fin1.Destroy()
		th_fin2.Destroy()
	tst.Get([])
	scb.ReportAll()

ck_ev = CreateEvent()
RegisterCoroutines([
	main(),
])
for i in range(1000):
	SignalEvent(ck_ev)
	MainLoop()
	if not waiting_coro[ck_ev]:
		break
print("Simulation stop at {}".format(i))
