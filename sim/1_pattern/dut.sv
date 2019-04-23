// Copyright (C) 2019, Yu Sheng Lin, johnjohnlys@media.ee.ntu.edu.tw

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
	output logic [7:0] character
);

localparam LEN = 25;
logic [(8*LEN)-1:0] characters;
assign characters = "AABABA__JUSTMONIKA__CDEDE";

int i;
always_ff @(posedge clk or negedge rst) begin
	if (!rst) begin
		i <= 0;
		character <= 0;
	end else if (i < LEN) begin
		i <= i+1;
		character <= characters[8*(LEN-i)-1 -: 8];
	end
end

endmodule
