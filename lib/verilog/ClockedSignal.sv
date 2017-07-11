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

module ClockedSignal(input clk, input rst);
integer rst_in = -1;
integer rst_out = -1;
integer clock = -1;
always @(negedge rst) $NicotbTriggerEvent(rst_in);
always @(posedge rst) $NicotbTriggerEvent(rst_out);
always @(posedge clk) if (rst) $NicotbTriggerEvent(clock);
endmodule

module LevelDetect(input clk, input rst, input level);
parameter bit LEVEL = 1;
integer detected = -1;
always @(posedge clk or negedge rst) begin
	if (rst && level == LEVEL) begin
		$NicotbTriggerEvent(detected);
	end
end
endmodule

module ConditionLevelDetect(input clk, input rst, input level, input cond, output both);
parameter bit LEVEL = 1;
integer detected = -1;
assign both = level == LEVEL && cond;
always @(posedge clk or negedge rst) begin
	if (rst && both) begin
		$NicotbTriggerEvent(detected);
	end
end
endmodule
