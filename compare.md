---
layout: page
title: "Compare with Cocotb"
---
## Coroutine
Cocotb wraps everything perfectly by its coroutine.

    # Cocotb
    # decorator
    @coroutine
    def Func():
        # yield an event
        # connected to Verilog by GPI
        yield clk_pos
    # yield a coroutine
    yield Func()

Nicotb, on the other hand, uses more Python features.

    # Nicotb
    def Func():
        # yield an event
        # In fact, events are just integers.
        # They can be registered from Verilog.
        # They can also be created in the testbench (maybe implicitly).
        yield clk_pos
    # yield from a coroutine
    yield from Func()

BTW, the *yield from* is introduced in Python 3.3.
The Python 2 equivalent is

    # Nicotb
    def Func():
        yield clk_pos
    for x in Func():
        yield x

. I use *yield from* just because it\'s cool.


## Connect to Verilog
Compared with Cocotb, Nicotb use a Verilog file as the top module testbench.
Therefore, Nicotb can be integerated to existing EDA tools easier and gives you better control over the Verilog code directly.

In Cocotb, the signals are accessed accordingly the hierarchy under the toplevel DUT.

    # Cocotb
    # read
    print(int(dut.sig))
    # write
    dut.sub.nested_sig = 1
    # write (immediate)
    dut.sig.setimmediate(99)

In Nicotb, the signals are grouped as *buses*, and the grouping is defined by users.
Buses are represented as Numpy arrays and the reading and writing should be called explicitly.

    # Nicotb
    bus = CreateBus((
        ("dut", "sig"),
        ("dut.sub", "nested_sig"),
    ));
    # read (Verilog to Python)
    bus.Read()
    # read
    print(bus.values[0][0]) # dut.sub
    # write
    bus.values[1][0] = 100 # dut.sub.nested_sig
    numpy.copyto(bus.values[1][0], 100) # the same
    # write (Python to Verilog)
    bus.Write()
    # write (Python to Verilog, immediate)
    bus.Write(True)

## Scoreboard
Nicotb has Scoreboard functionality, and can dump the results to a SQL DB.
We also provide the Makefile to display the results.
(TODO document)

## High level verification
Currently Nicotb supports many common protocols such as vsync/hsync and AXI.
(TODO document)