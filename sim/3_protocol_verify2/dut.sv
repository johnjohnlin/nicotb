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
module Dut(
	input         clk,
	input         rst,
	input               irdy,
	output logic        iack,
	input        [10:0] iint,
	output logic        ordy,
	input               oack,
	output logic [10:0] oint
);

logic ordy_w;
logic [10:0] oint_w;
logic [10:0] iint_r;
logic [10:0] iint_w;
assign iack = irdy && !ordy;

always_comb begin
	casez ({iack,oack,oint == iint_r})
		3'b1??: begin
			ordy_w = 1'b1;
			oint_w = '0;
			iint_w = iint;
		end
		3'b00?: begin
			ordy_w = ordy;
			oint_w = oint;
			iint_w = iint_r;
		end
		3'b010: begin
			ordy_w = 1'b1;
			oint_w = oint + 'b1;
			iint_w = iint_r;
		end
		3'b011: begin
			ordy_w = 1'b0;
			oint_w = oint;
			iint_w = iint_r;
		end
	endcase
end

always_ff @(posedge clk or negedge rst) begin
	if (!rst) begin
		ordy <= 1'b0;
		oint <= 1'b0;
		iint_r <= '0;
	end else begin
		ordy <= ordy_w;
		oint <= oint_w;
		iint_r <= iint_w;
	end
end

endmodule
