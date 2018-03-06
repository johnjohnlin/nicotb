---
layout: page
title: "Running Examples"
---

## Index

You can find these examples under the `sim/` folder.

1. [Basic signal](examples/0_simple.html)
1. [Basic protocol](examples/1_protocol.html)
1. AXI or AHB
1. Simulate with Ramulator DRAM simulator

## Nicotb Co-simulation Workflow

To simulate with Nicotb, at least 2 files are required.

* **XXX.sv**: The testbench defining the signals to be tested and controlling the timing.
  For simplicity, the top-level testbench module might be **module XXX;**.
* **XXX.py**: The Python testbench which waits for events and respond to them.

After preparing the files, the Makefile in the example folder helps you run the testbench.

```bash
cd <SOME PATH>
make -f <NICOTB PATH>/sim/Makefile XXX
```

By default the files must have the same name
but the provided Makefile allows you to fine-tune each file name as well as the top-level module name.
You can also modify the logging level since we are using Glog library.
Also, you have to modify the path in Makefile
in order to locate the irun (aka ncverilog) binary (also refer to [build](build.html)).

## Templates

The following template is enough for most module verification with one clock and reset (with little modification):

### Verilog

```verilog
module tb;
logic clk, rst;
`Pos(rst_out, rst)
`PosIf(ck_ev, clk, rst)
`WithFinish
always #1 clk = ~clk;
initial begin
    clk = 0;
    rst = 1;
    #1 $NicotbInit();
    #10 rst = 0;
    #10 rst = 1;
    #5
    #1000
    $NicotbFinal();
    $finish;
end
initial begin
    #10000
    $display("Something wrong");
    $NicotbFinal();
    $finish;
end
MyModule dut(clk, rst);
endmodule
```

### Python

```python
def main():
    yield rst_out
    for i in range(300):
        yield clk
        print(f"{i}-th clock after reset")
    # You can use this line if you use the macro `WithFinish
    FinishSim()

rst_out, clk = CreateEvents(["rst_out", "ck_ev"])
RegisterCoroutines([main()])
```
