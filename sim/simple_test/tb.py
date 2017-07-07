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
		if GetBus("a")[1][0][0]:
			GetBus("cb")[0][0][1,1] = -1
			GetBus("cb")[1][0][1,1] = -1
		else:
			GetBus("cb")[0][0][1,1] = GetBus("a")[0][0][0]
			GetBus("cb")[1][0][1,1] = 0
		WriteBus(ToBusIdx("cb"), GetBus("cb")[0], GetBus("cb")[1])

RegisterCoroutines([
	clk(),
	rst_out(),
	rst_out2(),
])
