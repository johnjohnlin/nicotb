from nicotb import *

def rst_out():
	print("reset wait")
	yield "rst_out"
	print("reset out")
	yield "rst_out"
	print("this should not happen")

def rst_out2():
	yield "rst_out"
	print("reset out 2")

def clk():
	yield "rst_out"
	while True:
		yield "clk"
		print("clk")

RegisterCoroutines([
	clk(),
	rst_out(),
	rst_out2(),
])
