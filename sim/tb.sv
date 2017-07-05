`timescale 1ns/1ns
`include "ClockedSignal.sv"

module tb;

logic clk, rst;
logic [3:0] a;
logic [10:0] b [3][2][4];
logic [10:0] c [2][4];
ClockedSignal u_cs(clk, rst);

initial begin
	clk = 0;
	rst = 1;
	$NicotbInit();
	#10 $finish;
end

endmodule
