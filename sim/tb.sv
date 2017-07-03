`timescale 1ns/1ns

module tb;

logic clk, rst;
logic [3:0] a;
logic [10:0] b [1];
ClockedSignal u_cs(clk, rst);

initial begin
	clk = 0;
	rst = 1;
	$NicotbInit();
	#10 $finish;
end

endmodule
