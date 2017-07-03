module ClockedSignal(input i_clk, input i_rst);
integer rst_in = -1;
integer rst_out = -1;
integer clk = -1;
// always @(negedge i_rst) if (rst_in >= 0) $ev_trigger(rst_in);
// always @(posedge i_rst) if (rst_out >= 0) $ev_trigger(rst_out);
// always @(posedge i_clk) if (!i_rst && clk >= 0) $ev_trigger(clk);
endmodule
