// Copyright (C) 2017,2019, Yu Sheng Lin, johnjohnlys@media.ee.ntu.edu.tw

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

module dut(
	input  logic clk,
	input  logic rst,
	output logic [ 3:0] a,
	input  logic [10:0] b  [3][2][4],
	input  logic [10:0] c  [2][4]
);

int i;
always@(posedge clk or negedge rst) begin
	if (!rst) begin
		i <= 0;
		a <= 0;
	end else if (i < 10) begin
		i <= i+1;
		a <= a+1;
	end else if (i < 20) begin
		i <= i+1;
	end else if (i == 20) begin
		a <= 'x;
	end
end

endmodule
