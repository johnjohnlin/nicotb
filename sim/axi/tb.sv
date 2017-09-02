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

module tb;

logic clk, rst;
logic aw_rdy, aw_ack, w_rdy, w_ack , b_rdy, b_ack , ar_rdy, ar_ack, r_rdy, r_ack;
logic [ 5:0] aw;
logic [31:0] w ;
logic [ 1:0] b ;
logic [ 5:0] ar;
logic [31:0] r ;
`Pos(rst_out, rst)
`PosIf(ck_ev, clk, rst)
`WithFinish

always #1 clk = ~clk;
assign b = 0;
assign r = 123;
initial begin
	$fsdbDumpfile("axi.fsdb");
	$fsdbDumpvars(0, tb, "+mda");
	clk = 0;
	rst = 1;
	#1 $NicotbInit();
	#11 rst = 0;
	#10 rst = 1;
	#1000 $display("Timeout");
	$NicotbFinal();
	$finish;
end

endmodule
