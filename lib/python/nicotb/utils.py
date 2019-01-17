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
from nicotb import Receiver
from nicotb.bus import SignalTuple
from collections import deque
import sqlite3 as sql
from datetime import datetime
import numpy as np

def DefaultFormator(expect, get):
	ret = str()
	for i, (e, g) in enumerate(zip(expect, get)):
		if np.array_equal(e, g):
			ret += "Pair {} equal.\n".format(i)
		else:
			ret += "Pair {} not equal.\nExpected:\n{}\nGot:\n{}\n".format(i, e, g)
	return ret

class Scoreboard(object):
	scoreboards = list()
	use_sql = True

	def __init__(self, name=""):
		self.name = name
		self.tests = dict()
		Scoreboard.scoreboards.append(self)
		if Scoreboard.use_sql:
			conn = sql.connect("scoreboard.db")
			cur = conn.cursor()
			cur.executescript("""
				CREATE TABLE IF NOT EXISTS Scoreboard (
					id INTEGER PRIMARY KEY,
					name TEXT,
					last_update TIMESTAMP,
					finished INTEGER,
					passed INTEGER
				);
				CREATE TABLE IF NOT EXISTS Tests (
					id INTEGER PRIMARY KEY,
					scoreboard_id INTEGER,
					name TEXT,
					correct INTEGER,
					wrong INTEGER,
					pending INTEGER,
					FOREIGN KEY(scoreboard_id) REFERENCES Scoreboard(id)
				);
			""")
			cur.execute("SELECT * FROM Scoreboard WHERE name=?", (self.name,))
			rec = cur.fetchone()
			if rec:
				cur.execute("""
					UPDATE Scoreboard SET
					last_update=?, finished=?, passed=? WHERE id=?
				""", (datetime.now(), 0, 0, rec[0]))
			else:
				cur.execute("INSERT INTO Scoreboard VALUES (?,?,?,?,?)", (None, name, datetime.now(), 0, 0))
			conn.commit()
			conn.close()

	def GetTest(self, name, max_err=0, formator=DefaultFormator, ne=None, squeeze=False):
		if name in self.tests:
			return self.tests[name]
		else:
			ret = Tester(name, max_err, formator, ne, squeeze)
			self.tests[name] = ret
			return ret

	def Report(self, cur):
		if len(self.tests) == 0:
			print("Nothing to report in this scoreboard")
			return
		fail = False
		if Scoreboard.use_sql:
			cur.execute("SELECT * FROM Scoreboard WHERE name=?", (self.name,))
			rec_scb = cur.fetchone()
		for t in self.tests.values():
			if not t.is_clean:
				print("There are still {} values in expecting queue of [{}]".format(
					len(t.exp), t.name)
				)
				fail = True
			if t.err != 0:
				"There are {} errors in [{}]".format(t.err, t.name)
				fail = True
			elif t.ok == 0:
				"There is nothing to test in [{}]".format(t.name)
				fail = True
			print("Status of [{}]: (correct/error): {}/{}".format(
				t.name,
				t.ok,
				t.err,
			))
			if Scoreboard.use_sql:
				cur.execute("SELECT * FROM Tests WHERE name=? AND scoreboard_id=?", (t.name, rec_scb[0]))
				rec = cur.fetchone()
				if rec:
					cur.execute("""
						UPDATE Tests SET
						correct=?, wrong=?, pending=? WHERE id=? AND scoreboard_id=?
					""", (t.ok, t.err, len(t.exp), rec[0], rec_scb[0]))
				else:
					cur.execute("INSERT INTO Tests VALUES (?,?,?,?,?,?)", (None, rec_scb[0], t.name, t.ok, t.err, len(t.exp)))
		print("FAIL" if fail else "PASS")
		if Scoreboard.use_sql:
			cur.execute("""
				UPDATE Scoreboard SET
				last_update=?, finished=?, passed=? WHERE id=?
			""", (datetime.now(), 1, not fail, rec_scb[0]))

	@classmethod
	def ReportAll(cls):
		sep1 = "=" * 60
		sep2 = "-" * 60
		print(sep1)
		print("Scoreboard Reports")
		print(sep1)
		if Scoreboard.use_sql:
			conn = sql.connect("scoreboard.db")
			cur = conn.cursor()
		else:
			cur = None
		for scb in cls.scoreboards:
			scb.Report(cur)
			print(sep2)
		if Scoreboard.use_sql:
			conn.commit()
			conn.close()

class Tester(object):
	__slots__ = ["exp", "max_err", "name", "err", "ok", "formator", "ne", "squeeze"]
	def __init__(self, name, max_err, formator, ne, squeeze):
		self.exp = deque()
		self.max_err = max_err
		self.name = name
		self.ok = 0
		self.err = 0
		self.formator = formator
		self.ne = ne
		self.squeeze = squeeze

	def Get(self, x):
		assert len(self.exp) != 0, "{} does not expect anything".format(self.name)
		head = self.exp.popleft()
		if self.ne is None:
			if self.squeeze:
				nev = not all([np.array_equal(np.squeeze(a),np.squeeze(b)) for a, b in zip(head, x)])
			else:
				nev = not all([np.array_equal(a,b) for a, b in zip(head, x)])
		else:
			nev = self.ne(head, x)
		if nev:
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

class BusGetter(Receiver):
	"""This class converts a Bus transaction to a (subclass of) tuple of ndarray"""
	__slots__ = ["copy"]
	def __init__(self, copy=False, callbacks=list()):
		super(BusGetter, self).__init__(callbacks)
		self.copy = copy

	def Get(self, bus):
		unknowns = list()
		for i, xval in enumerate(bus.xs):
			if np.any(xval):
				unknowns.append(str(i))
		assert len(unknowns) == 0, "Bus has unknown values at position {}".format(",".join(unknowns))
		super(BusGetter, self).Get(bus.values.Copy() if self.copy else bus.values)

class Stacker(Receiver):
	"""This class stacks tuples."""
	__slots__ = ["n", "copy", "curn", "buf"]
	def __init__(self, n=0, copy=False, callbacks=list()):
		super(Stacker, self).__init__(callbacks)
		self.n = n
		self.copy = copy
		self.curn = 0
		self.buf = None

	def Resize(self, n, force=False):
		assert self.is_clean
		if n == 0 or n > self.n or force:
			self.buf = None
		self.n = n

	def _Allocate(self, ref):
		if self.buf is None and self.n != 0:
			self.buf = tuple(
				np.empty(
					(self.n,)+r.shape,
					dtype=r.dtype
				) for r in ref
			)

	def Get(self, x):
		assert self.n != 0, "Unsized Stacker cannot get values"
		self._Allocate(x)
		for dst, src in zip(self.buf, x):
			dst[self.curn] = src
		self.curn += 1
		if self.curn == self.n:
			got = SignalTuple((a[:self.curn] for a in self.buf), x)
			super(Stacker, self).Get(got.Copy() if self.copy else got)
			self.curn = 0

	@property
	def is_clean(self):
		return self.curn == 0

def ExpandSignalGroup(hier: str, prefix: str, groups):
	return tuple(
		(None if i != 0 else hier, prefix+s[0], s[1], s[2])
		for i, s in enumerate(groups)
	)

def RandProb(A, B):
	return np.random.randint(B) < A
