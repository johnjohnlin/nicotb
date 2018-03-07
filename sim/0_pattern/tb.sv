// Copyright (C) 2018, Yu Sheng Lin, johnjohnlys@media.ee.ntu.edu.tw

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

localparam LEN = 25;
logic clk, rst;
logic [7:0] character;
logic [(8*LEN)-1:0] characters;
assign characters = "AABABA__JUSTMONIKA__CDEDE";
`Pos(rst_out, rst)
`PosIf(ck_ev, clk, rst)

always #1 clk = ~clk;
initial begin
	$fsdbDumpfile("tb.fsdb");
	$fsdbDumpvars(0, tb, "+mda");
	clk = 0;
	rst = 1;
	character = 0;
	#1 $NicotbInit();
	#10 rst = 0;
	#10 rst = 1;
	#5
	for (int i = 0; i < LEN; i++) begin
		@(posedge clk)
		character <= characters[8*(LEN-i)-1 -: 8];
	end
	#100
	$NicotbFinal();
	$finish;
end

endmodule
