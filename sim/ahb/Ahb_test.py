# Copyright (C) 2018, Yu Sheng Lin, johnjohnlys@media.ee.ntu.edu.tw

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
from nicotb.utils import Scoreboard, BusGetter
from nicotb.protocol import Ahb
import operator as op
import numpy as np
from os import getenv

def main():
	N = 10
	scb = Scoreboard()
	test = scb.GetTest("ahb", ne=op.ne, max_err=10)
	bg = BusGetter(callbacks=[test.Get])
	ms = Ahb.Master(hsel, haddr, hwrite, htrans, hsize, hburst, hready, hresp, rd, wd, ck_ev)
	yield rs_ev
	for i in range(10):
		yield ck_ev

	def rng(magic):
		while True:
			magic = (magic*199 + 12345) & 65535
			yield magic
	r = rng(25251)

	MAGIC = next(r)
	ADR = 0
	print(
		"Test Single R/W\n"
		f"MAGIC/ADR is {MAGIC}/{ADR}"
	)
	test.Expect(MAGIC)
	yield from ms.Write(ADR, MAGIC)
	read_v = yield from ms.Read(ADR)
	test.Get(read_v)

	yield ck_ev
	MAGIC = next(r)
	ADR = 100
	print(
		"Test Pipelined R/W\n"
		f"MAGIC/ADR is {MAGIC}/{ADR}"
	)
	wcmd = [(True, ADR+i*4, MAGIC+i) for i in range(N)]
	rcmd = [(False, ADR+i*4) for i in range(N)]
	test.Expect([MAGIC+i for i in range(N)])
	read_v = yield from ms.IssueCommands(wcmd + rcmd)
	test.Get(read_v)

	yield ck_ev
	MAGIC = next(r)
	ADR = 200
	print(
		"Test Pipelined Interleaved R/W\n"
		f"MAGIC/ADR is {MAGIC}/{ADR}"
	)
	wcmd = [(True, ADR+i*4, MAGIC+i) for i in range(N)]
	rcmd = [(False, ADR+i*4) for i in range(N)]
	cmd = [v for p in zip(wcmd, rcmd) for v in p]
	test.Expect([MAGIC+i for i in range(N)])
	read_v = yield from ms.IssueCommands(cmd)
	test.Get(read_v)

	for i in range(10):
		yield ck_ev

wd, rd = CreateBuses([("wd",), ("rd",),])
hsel, haddr, hwrite, htrans, hsize, hburst, hready, hresp = CreateBuses([
	(("u_dut", "HSEL"),),
	(("u_dut", "HADDR"),),
	(("u_dut", "HWRITE"),),
	(("u_dut", "HTRANS"),),
	(("u_dut", "HSIZE"),),
	(("u_dut", "HBURST"),),
	(("u_dut", "HREADY"),),
	(("u_dut", "HRESP"),),
])
ck_ev, rs_ev = CreateEvents(["ck_ev", "rst_out",])
RegisterCoroutines([
	main(),
])
