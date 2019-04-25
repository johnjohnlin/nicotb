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
from nicotb.common import *
try:
	from nicotb_bridge import BindEvent
	COSIM = True
except ImportError:
	COSIM = False
from collections import deque

event_released = set()
waiting_coro = list()
event_queue = deque()

def CreateEvent(hier: str = ""):
	if event_released:
		n = event_released.pop()
	else:
		n = len(waiting_coro)
		waiting_coro.append(list())
	if COSIM and hier:
		BindEvent(n, (TOP_PREFIX+hier).encode())
	return n

def CreateEvents(descs: list):
	return [CreateEvent(event) for event in descs]

def GetEvent(ev):
	return ev if isinstance(ev, int) else CreateEvent(ev)

def SignalEvent(ev, all_ev=True):
	event_queue.append((ev, all_ev))

def DestroyEvent(ev: int):
	# Do not destroy events created with hier name
	waiting_coro[ev] = list()
	event_released.add(ev)

# Initialize a default event, so coroutines can implement SystemC-like dont_initialize
INIT_EVENT = CreateEvent()
SignalEvent(INIT_EVENT)
