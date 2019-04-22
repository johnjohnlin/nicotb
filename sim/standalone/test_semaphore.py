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
from nicotb.primitives import Semaphore
from nicotb.event import waiting_coro
import numpy as np

ACQ = [1,2,3,4]
SUM = sum(ACQ)

def producer():
	global resource
	for i in range(SUM):
		for j in range(1+np.random.randint(20)):
			yield ck_ev
		resource += 1
		yield from sem.Release()

def consumer():
	global resource
	scb = Scoreboard("Semaphore")
	tst = scb.GetTest("test")
	tst.Expect([])
	for i in ACQ:
		for j in range(1+np.random.randint(10)):
			yield ck_ev
		yield from sem.Acquire(i)
		resource -= i
		assert resource >= 0
	tst.Get([])
	scb.ReportAll()

ck_ev = CreateEvent()
resource = 0
sem = Semaphore(-1)
RegisterCoroutines([
	producer(),
	consumer(),
])
for i in range(1000):
	SignalEvent(ck_ev)
	MainLoop()
	if not waiting_coro[ck_ev]:
		break
print("Simulation stop at {}".format(i))
