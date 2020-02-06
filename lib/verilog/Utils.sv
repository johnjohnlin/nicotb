`ifndef __NICOTB_UTIL_SV__
`define __NICOTB_UTIL_SV__
// Copyright (C) 2017,2019,2020, Yu Sheng Lin, johnjohnlys@media.ee.ntu.edu.tw

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

package Nicotb;
	task Abort(input logic [256:0] istr);
		$display({60{"^"}});
		$display(">>> Errors occur in Nicotb::%0s", istr);
		$display({60{"="}});
		$finish(2);
	endtask
endpackage

`define Pos(name, sig) \
	integer name = -1; \
	always @(posedge sig) \
		if($NicotbTriggerEvent(name)) Nicotb::Abort("TriggerEvent"); \
		else #0 if ($NicotbUpdateWrite()) Nicotb::Abort("UpdateWrite");
`define Neg(name, sig) \
	integer name = -1; \
	always @(negedge sig) \
		if($NicotbTriggerEvent(name)) Nicotb::Abort("TriggerEvent"); \
		else #0 if ($NicotbUpdateWrite()) Nicotb::Abort("UpdateWrite");
`define PosIf(name, sig, cond) \
	integer name = -1; \
	always @(posedge sig) \
		if ((cond) && $NicotbTriggerEvent(name)) Nicotb::Abort("TriggerEvent"); \
		else #0 if ($NicotbUpdateWrite()) Nicotb::Abort("UpdateWrite");
`define NegIf(name, sig, cond) \
	integer name = -1; \
	always @(negedge sig) \
		if ((cond) && $NicotbTriggerEvent(name)) Nicotb::Abort("TriggerEvent"); \
		else #0 if ($NicotbUpdateWrite()) Nicotb::Abort("UpdateWrite");
// useful for gate level
`define PosIfDelayed(name, sig, cond, t) \
	integer name = -1; \
	always @(posedge sig) \
		if ((cond) && $NicotbTriggerEvent(name)) Nicotb::Abort("TriggerEvent"); \
		else #(t) if ($NicotbUpdateWrite()) Nicotb::Abort("UpdateWrite");
`define NegIfDelayed(name, sig, cond, t) \
	integer name = -1; \
	always @(negedge sig) \
		if ((cond) && $NicotbTriggerEvent(name)) Nicotb::Abort("TriggerEvent"); \
		else #(t) if ($NicotbUpdateWrite()) Nicotb::Abort("UpdateWrite");
`define WithFinish \
	logic nicotb_fin_wire; \
	initial begin \
		nicotb_fin_wire = 0; \
		@(posedge nicotb_fin_wire) \
		if ($NicotbFinal()) Nicotb::Abort("Final"); \
		$finish; \
	end
`define NicotbInit if ($NicotbInit()) Nicotb::Abort("Init");
`define NicotbFinal if ($NicotbFinal()) Nicotb::Abort("Final");
`endif
