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
from nicotb.primitives import Semaphore
import numpy as np

def f0():
	print("f0")
	global cnt
	while True:
		cnt += 1
		yield clk_ev

def f1():
	print("f1")
	for i in range(10):
		for j in range(1+np.random.randint(20)):
			yield clk_ev
		print("Rel?")
		yield from sem.Release()
		print(f"Rel {sem.n}")

def f2():
	print("f2")
	for i in [1,2,3,4]:
		for j in range(1+np.random.randint(10)):
			yield clk_ev
		print("Acq?")
		yield from sem.Acquire(i)
		print(f"Acq {sem.n}")

clk_ev = CreateEvent("ck_ev")
cnt = 0
sem = Semaphore(-1)
RegisterCoroutines([
	f0(),
	f1(),
	f2(),
])
