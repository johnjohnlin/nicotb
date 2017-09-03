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

module Stage(input clk, input rst, input irdy, output iack, output iboth, output logic ordy, input oack);
assign iack = oack || !ordy;
assign iboth = irdy && iack;
always_ff @(posedge clk or negedge rst) if (!rst) begin
	ordy <= 0;
end else begin
	ordy <= irdy || ordy && !oack;
end
endmodule

module tb;

logic clk, rst;
logic aw_rdy, aw_ack, w_rdy, w_ack , b_rdy, b_ack , ar_rdy, ar_ack, r_rdy, r_ack;
logic [ 5:0] aw;
logic [31:0] w ;
logic [ 1:0] b ;
logic [ 5:0] ar;
logic [31:0] r ;
`Pos(rst_out, rst)
`PosIf(ck_ev, clk, rst)
`WithFinish

always #1 clk = ~clk;
assign b = 0;
initial begin
	$fsdbDumpfile("axi.fsdb");
	$fsdbDumpvars(0, tb, "+mda");
	clk = 0;
	rst = 1;
	#1 $NicotbInit();
	#11 rst = 0;
	#10 rst = 1;
	#1000 $display("Timeout");
	$NicotbFinal();
	$finish;
end

logic awboth;
logic wboth ;
logic bboth ;
logic arboth;
logic rboth ;
logic aw_got;
logic w_got;
logic bsrc_rdy;
logic bsrc_ack;
logic rsrc_rdy;
logic rsrc_ack;
logic [ 5:0] aw_r;
logic [31:0] w_r ;
logic [ 5:0] ar_r;
logic [31:0] internal_buf [8];
assign bsrc_rdy = aw_got && w_got;
Stage u_st_aw(clk, rst, aw_rdy, aw_ack, awboth, aw_got, bboth);
Stage u_st_w (clk, rst, w_rdy , w_ack , wboth , w_got , bboth);
Stage u_st_b (clk, rst, bsrc_rdy, bsrc_ack, bboth, b_rdy, b_ack);
Stage u_st_ar(clk, rst, ar_rdy, ar_ack, arboth, rsrc_rdy, rsrc_ack);
Stage u_st_r (clk, rst, rsrc_rdy, rsrc_ack, rboth, r_rdy, r_ack);

always @(posedge clk or negedge rst) if (!rst) begin
	aw_r <= 0;
end else if (awboth) begin
	aw_r <= aw;
end

always @(posedge clk or negedge rst) if (!rst) begin
	w_r <= 0;
end else if (wboth) begin
	w_r <= w;
end

always @(posedge clk or negedge rst) if (!rst) begin
	for (int i = 0; i < 8; i++) begin
		internal_buf[i] <= 0;
	end
end else if (bboth) begin
	internal_buf[aw_r] <= w_r;
end

always @(posedge clk or negedge rst) if (!rst) begin
	ar_r <= 0;
end else if (arboth) begin
	ar_r <= ar;
end

always @(posedge clk or negedge rst) if (!rst) begin
	r <= 0;
end else if (rboth) begin
	r <= internal_buf[ar_r];
end

endmodule
