# Copyright (C) 2017-2019, Yu Sheng Lin, johnjohnlys@media.ee.ntu.edu.tw

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
from nicotb.common import COSIM
if COSIM:
	from nicotb.bus import *
from nicotb.event import *

__all__ = ([
	# bus
	"Signal",
	"Bus",
	"CreateBus",
	"CreateBuses",
	"GetBus",
	"FlushBusWrite",
] if COSIM else list()) + [
	# signal
	"CreateEvent",
	"CreateEvents",
	"GetEvent",
	"SignalEvent",
	"DestroyEvent",
	"INIT_EVENT",
	# utils
	"Fork",
	"RegisterCoroutines",
	"Receiver",
	"MainLoop",
	"FinishSim",
]

class Receiver(object):
	__slots__ = ["callbacks"]
	def __init__(self, callbacks = list()):
		self.callbacks = callbacks

	def AddCallback(self, cb):
		self.callbacks.append(cb)

	def Get(self, x):
		for cb in self.callbacks:
			cb(x)

def Fork(c):
	try:
		while True:
			idx = next(c)
			if not idx is None:
				# Event.waiting_coro
				waiting_coro[idx].append(c)
				break
	except StopIteration:
		pass

def RegisterCoroutines(coro: list):
	for c in coro:
		Fork(c)

def MainLoop():
	while len(event_queue) != 0:
		event_idx, all_ev = event_queue.pop()
		if all_ev:
			proc = waiting_coro[event_idx]
			waiting_coro[event_idx] = list()
		else:
			proc = [waiting_coro.pop()]
		RegisterCoroutines(proc)

def FinishSim():
	fin_bus = CreateBus(("nicotb_fin_wire",))
	fin_bus.value[0] = 1
	fin_bus.Write()
