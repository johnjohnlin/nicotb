#!/usr/bin/env python
# Copyright (C) 2019, Yu Sheng Lin, johnjohnlys@media.ee.ntu.edu.tw

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
from nicotb.primitives import Lock
from nicotb.event import waiting_coro
import numpy as np

def competitor(idx):
	global resource
	for i in range(10):
		yield from lck.Acquire()
		resource = idx
		for j in range(1+np.random.randint(3)):
			yield ck_ev
			assert resource == idx
		lck.Release()

ck_ev = CreateEvent()
resource = 0
lck = Lock()
RegisterCoroutines([competitor(i) for i in range(5)])
scb = Scoreboard("Lock")
tst = scb.GetTest("test")
tst.Expect([])
for i in range(1000):
	SignalEvent(ck_ev)
	MainLoop()
	if not waiting_coro[ck_ev]:
		break
tst.Get([])
scb.ReportAll()
print("Simulation stop at {}".format(i))
