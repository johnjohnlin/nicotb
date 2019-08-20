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
module sm_dut(input clk, input rst, input i_dval, input logic [3:0] i [2], output logic o_dval, output logic [6:0] o);

logic [1:0] cnt_r, cnt_w;
logic o_dval_w;
logic [6:0] o_w;
logic [4:0] ii;

always_comb begin
	ii = i[0] + i[1];
	if (i_dval) begin
		if (cnt_r == 2) begin
			cnt_w = 0;
			o_dval_w = 1;
		end else begin
			cnt_w = cnt_r+1;
			o_dval_w = 0;
		end
		if (cnt_r == 0) begin
			o_w = 7'(ii);
		end else begin
			o_w = 7'(ii)+o;
		end
	end else begin
		cnt_w = cnt_r;
		o_dval_w = 0;
		o_w = o;
	end
end

always_ff @(posedge clk or negedge rst) begin
	if (!rst) begin
		cnt_r <= '0;
		o_dval <= 1'b0;
		o <= '0;
	end else begin
		cnt_r <= cnt_w;
		o_dval <= o_dval_w;
		o <= o_w;
	end
end

endmodule

