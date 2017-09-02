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

module test_join;

logic clk, rst;
logic dval1, dval2;
logic [10:0] d1, d2;
`Pos(rst_out, rst)
`PosIf(ck_ev, clk, rst)

always #1 clk = ~clk;
initial begin
	$fsdbDumpfile("test_join.fsdb");
	$fsdbDumpvars(0, test_join, "+mda");
	clk = 0;
	rst = 1;
	#1 $NicotbInit();
	#10 rst = 0;
	#10 rst = 1;
	#300
	$NicotbFinal;
	$finish;
end

endmodule
