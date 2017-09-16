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
from nicotb import Receiver
from collections import deque
from typing import Tuple
import numpy as np

def DefaultFormator(expect, get):
	return "Expected:\n{}\nGot:\n{}".format(expect, get)

class Scoreboard(object):
	scoreboards = list()
	def __init__(self):
		self.tests = dict()
		Scoreboard.scoreboards.append(self)

	def GetTest(self, name, max_err=0, formator=DefaultFormator):
		if name in self.tests:
			return self.tests[name]
		else:
			ret = Tester(name, max_err, formator)
			self.tests[name] = ret
			return ret

	def Report(self):
		if len(self.tests) == 0:
			print("Nothing to report in this scoreboard")
			return
		fail = False
		for t in self.tests.values():
			if not t.is_clean:
				print("There are still {} values in expecting queue of [{}]".format(
					len(t.exp), t.name)
				)
				fail = True
			if t.err != 0:
				"There are {} errors in [{}]".format(t.err, t.name)
				fail = True
			print("Status of [{}]: (correct/error): {}/{}".format(
				t.name,
				t.ok,
				t.err,
			))
		print("FAIL" if fail else "PASS")

	@classmethod
	def ReportAll(cls):
		sep1 = "=" * 60
		sep2 = "-" * 60
		print(sep1)
		print("Scoreboard Reports")
		print(sep1)
		for scb in cls.scoreboards:
			scb.Report()
			print(sep2)

class Tester(object):
	__slots__ = ["exp", "max_err", "name", "err", "ok", "formator"]
	def __init__(self, name, max_err, formator):
		self.exp = deque()
		self.max_err = max_err
		self.name = name
		self.ok = 0
		self.err = 0
		self.formator = formator

	def Get(self, x):
		assert len(self.exp) != 0, "{} does not expect anything".format(self.name)
		head = self.exp.popleft()
		if any(not np.array_equal(a,b) for a, b in zip(head, x)):
			print(self.formator(head, x))
			assert self.err < self.max_err, "Tester [{}] has reached the max error count".format(self.name)
			self.err += 1
		else:
			self.ok += 1

	def Expect(self, x):
		self.exp.append(x)

	@property
	def is_clean(self):
		return len(self.exp) == 0

class Stacker(Receiver):
	"""This class stacks a Bus object to tuples of ndarray"""
	__slots__ = ["n", "curn", "buf"]
	def __init__(self, n=0, callbacks=list()):
		super(Stacker, self).__init__(callbacks)
		self.n = n
		self.curn = 0
		self.buf = None

	def Resize(self, n, force=False):
		assert self.is_clean
		if n == 0:
			self.buf = None
		elif self.buf and (self.n < n or force):
			self.buf = tuple(
				np.empty(
					(n,)+a.shape[1:],
					dtype=a.dtype
				) for a in self.buf
			)
		self.n = n

	def Get(self, x):
		assert self.n != 0, "Unsized Stacker cannot get values"
		assert all(not np.any(xval) for xval in x.xs), "Signal has unknown values"
		if self.buf is None:
			self.buf = tuple(
				np.empty(
					(self.n,)+a.shape,
					dtype=a.dtype
				) for a in x.values
			)
		for dst, src in zip(self.buf, x.values):
			dst[self.curn] = src
		self.curn += 1
		if self.curn == self.n:
			super(Stacker, self).Get(tuple(a[:self.curn] for a in self.buf))
			self.curn = 0

	@property
	def is_clean(self):
		return self.curn == 0

class StackerWithX(Receiver):
	__slots__ = ["n", "curn", "buf"]
	def __init__(self, n=0):
		raise NotImplementedError()

	def Resize(self, n, force=False):
		pass

	def Get(self, x):
		pass

	@property
	def is_clean(self):
		pass

def ExpandSignalGroup(hier: str, prefix: str, groups):
	return tuple(
		(None if i != 0 else hier, prefix+s[0], s[1], s[2])
		for i, s in enumerate(groups)
	)

def RandProb(A, B):
	return np.random.randint(B) < A
