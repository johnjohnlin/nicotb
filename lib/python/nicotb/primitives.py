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

def AllEvent(events):
	temp_event = CreateEvent()
	events = set(events)
	def wrap(event):
		yield event
		events.discard(event)
		if not events:
			SignalEvent(temp_event)
	for e in events:
		Fork(wrap(e))
	yield temp_event
	DestroyEvent(temp_event)

def AnyEvent(events):
	temp_event_ref = [CreateEvent()]
	events = set(events)
	def wrap(event):
		yield event
		if temp_event_ref:
			SignalEvent(temp_event_ref[0])
	for e in set(events):
		Fork(wrap(e))
	yield temp_event_ref[0]
	DestroyEvent(temp_event_ref[0])
	temp_event_ref.pop()

class JoinableFork(object):
	__slots__ = ("fin", "coro", "_event")
	def __init__(self, coro):
		self.fin = False
		self._event = CreateEvent()
		self.coro = coro
		Fork(self._wrap())

	def Join(self):
		yield None if self.fin else self._event

	def _wrap(self):
		yield from self.coro
		self.fin = True
		SignalEvent(self._event)

	def Destroy(self):
		DestroyEvent(self._event)

class Lock(object):
	__slots__ = ("locked", "_event")
	def __init__(self, locked=False):
		self.locked = locked
		self._event = CreateEvent()

	@property
	def acquire(self):
		if self.locked:
			return self._event
		else:
			self.locked = True
			return None

	def Release(self):
		self.locked = False
		SignalEvent(self._event)

	def Destroy(self):
		DestroyEvent(self._event)

class Semaphore(object):
	__slots__ = ("n_max", "n", "_acq_event", "_rel_event")
	def __init__(self, n_max=1, n=None):
		self.n_max = n_max
		if n is None:
			self.n = 0 if n_max <= 0 else n_max
		else:
			self.n = n
		self._acq_event = CreateEvent()
		self._rel_event = CreateEvent()

	def Acquire(self, n=1):
		while self.n < n:
			yield self._rel_event
		self.n -= n
		SignalEvent(self._acq_event)

	def Release(self, n=1):
		while self.n_max > 0 and self.n+n > self.n_max:
			yield self._acq_event
		self.n += n
		SignalEvent(self._rel_event)

	def AcquireNB(self, n=1):
		assert self.can_acquire
		self.n -= n
		SignalEvent(self._acq_event)

	def ReleaseNB(self, n=1):
		assert self.can_release
		self.n += n
		SignalEvent(self._rel_event)

	@property
	def can_acquire(self, n=1):
		return self.n >= n

	@property
	def can_release(self, n=1):
		return self.n_max <= 0 or self.n+n <= self.n_max

	def Destroy(self):
		DestroyEvent(self._acq_event)
		DestroyEvent(self._rel_event)
