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

// FIXME: #0 is a very bad workaround
`define Pos(name, sig) \
	integer name = -1; \
	always @(posedge sig) #0 if($NicotbTriggerEvent(name)) $finish;
`define Neg(name, sig) \
	integer name = -1; \
	always @(negedge sig) #0 if($NicotbTriggerEvent(name)) $finish;
`define PosIf(name, sig, cond) \
	integer name = -1; \
	always @(posedge sig) #0 if (cond) if ($NicotbTriggerEvent(name)) $finish;
`define NegIf(name, sig, cond) \
	integer name = -1; \
	always @(negedge sig) #0 if (cond) if ($NicotbTriggerEvent(name)) $finish;
`define WithFinish \
	logic nicotb_fin_wire; \
	initial begin \
		nicotb_fin_wire = 0; \
		@(posedge nicotb_fin_wire) \
		$NicotbFinal; \
		$finish; \
	end
