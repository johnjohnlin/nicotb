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

module ClockedSignal(input i_clk, input i_rst);
integer rst_in = -1;
integer rst_out = -1;
integer clk = -1;
always @(negedge i_rst) $NicotbTriggerEvent(rst_in);
always @(posedge i_rst) $NicotbTriggerEvent(rst_out);
always @(posedge i_clk) if (i_rst) $NicotbTriggerEvent(clk);
endmodule
