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

`define Pos(name, sig) \
	integer name = -1; \
	always @(posedge sig) \
		if($NicotbTriggerEvent(name)) $error("NicotbTriggerEvent"); \
		else #0 if ($NicotbUpdateWrite()) $error("NicotbUpdateWrite");
`define Neg(name, sig) \
	integer name = -1; \
	always @(negedge sig) \
		if($NicotbTriggerEvent(name)) $error("NicotbTriggerEvent"); \
		else #0 if ($NicotbUpdateWrite()) $error("NicotbUpdateWrite");
`define PosIf(name, sig, cond) \
	integer name = -1; \
	always @(posedge sig) \
		if ((cond) && $NicotbTriggerEvent(name)) $error("NicotbTriggerEvent"); \
		else #0 if ($NicotbUpdateWrite()) $error("NicotbUpdateWrite");
`define NegIf(name, sig, cond) \
	integer name = -1; \
	always @(negedge sig) \
		if ((cond) && $NicotbTriggerEvent(name)) $error("NicotbTriggerEvent"); \
		else #0 if ($NicotbUpdateWrite()) $error("NicotbUpdateWrite");
// useful for gate level
`define PosIfDelayed(name, sig, cond, t) \
	integer name = -1; \
	always @(posedge sig) \
		if ((cond) && $NicotbTriggerEvent(name)) $error("NicotbTriggerEvent"); \
		else #(t) if ($NicotbUpdateWrite()) $error("NicotbUpdateWrite");
`define NegIfDelayed(name, sig, cond, t) \
	integer name = -1; \
	always @(negedge sig) \
		if ((cond) && $NicotbTriggerEvent(name)) $error("NicotbTriggerEvent"); \
		else #(t) if ($NicotbUpdateWrite()) $error("NicotbUpdateWrite");
`define WithFinish \
	logic nicotb_fin_wire; \
	initial begin \
		nicotb_fin_wire = 0; \
		@(posedge nicotb_fin_wire) \
		if ($NicotbFinal()) $error("NicotbFinal"); \
		$finish; \
	end
`define NicotbInit if ($NicotbInit()) $error("NicotbInit");
`define NicotbFinal if ($NicotbFinal()) $error("NicotbFinal");
