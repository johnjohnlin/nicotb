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
`include "ClockedSignal.sv"
`include "sm_dut.sv"
module sm;

logic clk, rst;
logic i_dval, o_dval;

always #1 clk = ~clk;
initial begin
	$fsdbDumpfile("sm.fsdb");
	$fsdbDumpvars(0, sm, "+mda");
	clk = 0;
	rst = 1;
	#1 $NicotbInit();
	#10 rst = 0;
	#10 rst = 1;
	#1000 $finish;
end

ClockedSignal u_cr(clk, rst);
LevelDetect u_ldo(clk, rst, o_dval);
sm_dut u_dut(.clk(clk), .rst(rst), .i_dval(i_dval), .i(), .o_dval(o_dval), .o());

endmodule
