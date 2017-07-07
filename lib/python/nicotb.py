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
from nicotb_bridge import events, event_dict, buses, bus_dict, ReadBus, WriteBus
from typing import Union
from collections import deque

__all__ = [
	'WriteBus',
	'ToBusIdx',
	'GetBus',
	'ToEventIdx',
	'SetEvent',
	'RegisterCoroutines',
	'MainLoop',
]

waiting_coro = [list() for _ in range(len(event_dict))]
event_queue = deque()

def ToBusIdx(idx: Union[str,int]):
	return bus_dict[idx] if isinstance(idx, str) else idx

def GetBus(idx):
	return buses[ToBusIdx(idx)]

def ToEventIdx(idx: Union[str,int]):
	return event_dict[idx] if isinstance(idx, str) else idx

def SetEvent(ev):
	event_queue.append(ToEventIdx(ev))

def RegisterCoroutines(coro: list):
	for c in coro:
		try:
			waiting_coro[ToEventIdx(next(c))].append(c)
		except StopIteration:
			pass

def MainLoop():
	while len(event_queue) != 0:
		event_idx = event_queue.pop()
		proc = waiting_coro[event_idx]
		waiting_coro[event_idx] = list()
		event = events[event_idx]
		for read_idx in event:
			ReadBus(read_idx, buses[read_idx][0], buses[read_idx][1])
		RegisterCoroutines(proc)
