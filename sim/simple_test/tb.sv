`timescale 1ns/1ns
`include "ClockedSignal.sv"

module tb;

logic clk, rst;
logic [3:0] a;
logic [10:0] b [3][2][4];
logic [10:0] c [2][4];
ClockedSignal u_cs(clk, rst);

always #1 clk = ~clk;
initial begin
	$fsdbDumpfile("tb.fsdb");
	$fsdbDumpvars(0, tb, "+mda");
	clk = 0;
	rst = 1;
	a = 0;
	#1 $NicotbInit();
	#10 rst = 0;
	#10 rst = 1;
	#100 $finish;
end

initial begin
	#5
	@(posedge rst)
	for (int i = 0; i < 10; i++) begin
		@(posedge clk) a <= a+1;
	end
	for (int i = 0; i < 10; i++) begin
		@(posedge clk);
	end
	a <= 'x;
end

endmodule
