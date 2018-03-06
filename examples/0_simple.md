---
layout: page
title: "Connect to SystemVerilog"
---

## The SystemVerilog code to test

Here we show an example that drives characters of a string into an 8-bit `logic`,
which a SystemVerilog programmer can easily understand this code except the Nicotb VPI function calls.
Besides, we shall illustrate later using Nicotb to detect the 6 characters right after the marker string `"JUST"`,
which is `"MONIKA"`.

```verilog
always #1 clk = ~clk;
initial begin
    clk = 0;
    rst = 1;
    character = 0;
    #1 $NicotbInit();
    #10 rst = 0;
    #10 rst = 1;
    #5
    for (int i = 0; i < LEN; i++) begin
        @(posedge clk)
        // assign characters = "AABABA__JUSTMONIKA__CDEDE";
        character <= characters[8*(LEN-i)-1 -: 8];
    end
    #100
    $NicotbFinal();
    $finish;
end
```

I don\'t intend to introduce the SystemVerilog part further,
so I just explain `$NicotbInit()`, `$NicotbFinal()`.
As their names suggest, you must `$NicotbFinal()` call it right before `$finish`,
and call `$NicotbInit()` call it right after the initialization (preferably with little latency),

To co-simulate with Python, Python has to know about the timing of clock and reset,
and this can be done by macros that defines two integer IDs `rst_out`, `ck_ev`.
Whenever these events happen, these IDs are used to notify Python for such occurence.

```verilog
`Pos(rst_out, rst)
// Roughly equivalent to:
//   integer rst_out;
//   always@(posedge rst) $NicotbTriggerEvent(rst_out);
`PosIf(ck_ev, clk, rst)
```

## The Nicotb testbench in Python
### Connect SystemVerilog signals

For connecting signals and events in Python, we need `CreateEvents` and `CreateBus`.
The `CreateEvents` is easy and doesn\'t need much explanation;
A bus is a set of signals, so `CreateBus` function call accepts a tuple type.
For now our bus has only one signal,
and `("", "character")` means the `character` signal under the top-level module.

```python
rst_out, clk = CreateEvents(["rst_out", "ck_ev"])
bus = CreateBus((
    ("", "character"),
))
```

After connecting the hardware parts, this following is the testbench logic,
which is mostly standard Python codes.
A main difference is `yield`, and you can view it as equivalence of `@(posedge clk)` in SystemVerilog.

To access the SystemVerilog signal value, an explicit `bus.Read()` is required to read the value from SystemVerilog through VPI.
In this case, we call at every cycle, namely after `yield clk`.
(Also, some simulators require special flags to let you access signals through VPI, such as `+access+rw` for ncverilog.)
The signals of a bus can be accessed by the name like `bus.character`,
and we provide several ways to access the signals, but this is the simplest one.
A signal has two fields -- `value` and `x`,
which is exactly the 4-value encoding of VPI.
If you are sure the signal is not `x` or `z`, then you can use only `value`.
The `value` and `x` are all Numpy arrays, and if it is a scalar, its shape is `(1,)`,
which means you can access the value of `character` through `bus.character.value[0]` after calling `bus.Read()`.

```python
def main():
    pattern = [ord(c) for c in "JUST"]
    n_trail = 6
    match_idx = 0
    yield rst_out
    while True:
        yield clk
        bus.Read()
        if bus.character.value[0] == pattern[match_idx]:
            match_idx = match_idx+1
            if match_idx == len(pattern):
                break
        else:
            match_idx = 0
    s = str()
    for i in range(n_trail):
        yield clk
        bus.Read()
        s += chr(bus.character.value[0])
    print(s)

RegisterCoroutines([main()])  # this means main is an initial block
```

You can find this example in `0_pattern/` directory.
Running this code by `make -f ../Makefile tb`, you can see the `MONIKA` is output during the simulation as desired.
Similar example(s) are `simple_test/`, which can be run by the same command.
