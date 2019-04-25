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
from nicotb.primitives import AnyEvent, AllEvent
import numpy as np

lst = [[0],[1],[2],[0,1],[0,2],[1,2],[0,1,2]]
fin_all = [False,False,False,False,False,False,False]
fin_any = [False,False,False,False,False,False,False]

def all_coro(i):
	yield from AllEvent([evs[j] for j in lst[i]])
	fin_all[i] = True

def any_coro(i):
	yield from AnyEvent([evs[j] for j in lst[i]])
	fin_any[i] = True

evs = [CreateEvent() for i in range(3)]
RegisterCoroutines([all_coro(i) for i in range(7)])
RegisterCoroutines([any_coro(i) for i in range(7)])
def Trigger(i):
	SignalEvent(evs[i])
	MainLoop()
scb = Scoreboard("AnyAll")
tst = scb.GetTest("test")
tst.Expect([])
Trigger(0)
assert fin_all == [True,False,False,False,False,False,False]
assert fin_any == [True,False,False,True,True,False,True]
Trigger(0)
assert fin_all == [True,False,False,False,False,False,False]
assert fin_any == [True,False,False,True,True,False,True]
Trigger(1)
assert fin_all == [True,True,False,True,False,False,False]
assert fin_any == [True,True,False,True,True,True,True]
Trigger(0)
assert fin_all == [True,True,False,True,False,False,False]
assert fin_any == [True,True,False,True,True,True,True]
Trigger(1)
assert fin_all == [True,True,False,True,False,False,False]
assert fin_any == [True,True,False,True,True,True,True]
Trigger(0)
assert fin_all == [True,True,False,True,False,False,False]
assert fin_any == [True,True,False,True,True,True,True]
Trigger(2)
assert fin_all == [True,True,True,True,True,True,True]
assert fin_any == [True,True,True,True,True,True,True]
tst.Get([])
scb.ReportAll()
