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
import numpy as np

class AllEvent(object):
	def __init__(self, events):
		raise NotImplementedError()
		self._event = CreateAnonymousEvent()
		self.events = events

	@property
	def event(self):
		events = set(event, self.events)
		for ev in self.events:
			Fork(self._wrap(events, event, self._event))
		return self._event

	@staticmethod
	def _wrap(events, event, trigger_on_fin):
		yield event
		events.discard(event)
		if not events:
			SetEvent(trigger_on_fin)

	def Destroy(self):
		DestroyAnonymousEvent(self._event)

class AnyEvent(object):
	def __init__(self, events):
		raise NotImplementedError()
		self._event = CreateAnonymousEvent()
		self.events = events

	@property
	def event(self):
		flag = [None]
		for ev in self.events:
			Fork(self._wrap(flag, ev, self._event))
		return self._event

	@staticmethod
	def _wrap(flag, event, trigger_on_fin):
		yield event
		if flag:
			flag.clear()
			SetEvent(trigger_on_fin)

	def Destroy(self):
		DestroyAnonymousEvent(self._event)

class JoinableFork(object):
	def __init__(self, coro):
		self.fin = False
		self._event = CreateAnonymousEvent()
		self.coro = coro
		Fork(self._wrap())

	@property
	def event(self):
		return None if self.fin else self._event

	def _wrap(self):
		yield from self.coro
		self.fin = True
		SetEvent(self._event)

	def Destroy(self):
		DestroyAnonymousEvent(self._event)
