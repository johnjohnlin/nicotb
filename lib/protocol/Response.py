# Copyright 2016 Yu Sheng Lin

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
from nicotb import Fork
from collections import deque
from numpy.random import randint

class Response(object):
	__slots__ = ["send_coro", "ck_ev", "cur", "q", "A", "B"]
	def __init__(self, send_coro, ck_ev, A=0, B=1, iter_mode=True):
		assert B > 0
		self.send_coro = send_coro
		self.ck_ev = ck_ev
		self.cur = 0
		self.q = deque()
		self.A = A
		self.B = B
		Fork(self._CkCount())
		Fork(self._Response() if iter_mode else self._ResponseOne())

	def Append(self, data):
		self.q.append((self.cur+self.A+randint(self.B), data))

	def _CkCount(self):
		while True:
			yield self.ck_ev
			self.cur += 1

	def _has_data(self):
		return len(self.q) != 0 and self.cur >= self.q[0][0]

	def _IterAllValid(self):
		while self._has_data():
			yield self.q.popleft()[1]

	def _Response(self):
		while True:
			yield self.ck_ev
			if self._has_data():
				yield from self.send_coro(self._IterAllValid())

	def _ResponseOne(self):
		raise NotImplementedError("Not tested")
		while True:
			yield self.ck_ev
			if self._has_data():
				yield from self.send_coro(self.q.popleft()[1])
