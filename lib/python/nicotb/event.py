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
from nicotb.common import *
from nicotb_bridge import BindEvent
from collections import deque

event_released = set()
waiting_coro = list()
event_queue = deque()

def CreateEvent(hier: str = ""):
	n = len(waiting_coro)
	if len(hier):
		BindEvent(n, (TOP_PREFIX+hier).encode())
	waiting_coro.append(list())
	return n

def CreateEvents(descs: list):
	return [CreateEvent(event) for event in descs]

def GetEvent(ev):
	return ev if isinstance(ev, int) else CreateEvent(ev)

def SignalEvent(ev, all_ev=True):
	event_queue.append((ev, all_ev))

def DestroyEvent(ev: int):
	waiting_coro[ev] = list()
	event_released.add(ev)

# Initialize a default event, so coroutines can implement SystemC-like dont_initialize
INIT_EVENT = CreateEvent()
SignalEvent(INIT_EVENT)
