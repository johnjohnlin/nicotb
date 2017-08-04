// Copyright (C) 2017, Yu Sheng Lin, johnjohnlys@media.ee.ntu.edu.tw

// This file is part of Nicotb.

// Nicotb is free software: you can redistribute it and/or modify
// it under the terms of the GNU General Public License as published by
// the Free Software Foundation, either version 3 of the License, or
// (at your option) any later version.

// Nicotb is distributed in the hope that it will be useful,
// but WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
// GNU General Public License for more details.

// You should have received a copy of the GNU General Public License
// along with Nicotb.  If not, see <http://www.gnu.org/licenses/>.
`timescale 1ns/1ns
`include "Utils.sv"
`include "cnt_dut.sv"

module cnt;

logic clk, rst;
logic [10:0] iint, oint;
logic irdy, iack;
logic ordy, oack, can_ack;

always #1 clk = ~clk;
initial begin
	$fsdbDumpfile("cnt.fsdb");
	$fsdbDumpvars(0, cnt, "+mda");
	clk = 0;
	rst = 1;
	#1 $NicotbInit();
	#11 rst = 0;
	#10 rst = 1;
	#1000 $display("Timeout");
	$NicotbFinal();
	$finish;
end

ClockedSignal u_cs(clk, rst);
LevelDetect u_d0(clk,rst,iack);
LevelDetect u_d1(clk,rst,ordy);
Finish u_f();
assign oack = ordy && can_ack;
Dut dut(clk,rst,irdy,iack,iint,ordy,oack,oint);

endmodule
