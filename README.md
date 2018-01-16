# Introduction

Nicotb aims to provide a tiny but extensible framework
for Python-Verilog co-simulation through VPI which:

* Maximize the use of existing popular libraries,
* Unify and simplify the interface between Python & Verilog.

# Python-Verilog Interface of Nicotb

Nicotb provides the Python-VPI mainly through these 3 structures:

* Signal: a verilog logic/wire/reg array.
* Bus: one or more Signals under a certain hierarchy,
  which is the smallest write/read unit in Nicotb.
* Event: When event happens, the Verilog part triggers the event,
  and sends several buses to Python.

In Python, the buses and events can be accessed by name or index through accessors,
and they are global structures.
However, the signal of a bus can only be accessed by index,
which is the order they are defined in the code using CreateBus(es).

The Signal has 2 members in form of numpy arrays: value and x,
which encode the 4-value of Verilog (0/1/x/z)
and such encoding is the same as VPI.
Besides, the arrays hold the reference of the value,
so if you assign new arrays to them, you just lose the reference to the Verilog parts.
The shape of numpy arrays are the same as the shape in Verilog,
while a scalar is converted to array of shape (1,)
Only bool and 1/2/4B signed/unsigned integer signal types are supported.

A Bus has a tuple consists of signals,
and independent signals can be accessed by bus[index].
The Write() function helps you write all signals to Verilog.
*Again, note that the signals are also references,
so don't try to assign new arrays to them.*

Event is usually an integer in Verilog, if the event occurred,
the Nicotb framework (1) reads the Verilog and fill the buses with the read values.
and (2) lets the Python codes wait on this event start to run.

# Nicotb Co-simulation Workflow

To run the Nicotb, at least 2 files are required.

* XXX.sv: The testbench defining the signals to be tested and controlling timing.
* XXX.py: The Python testbench which waits for events and respond to them.

After preparing the files, the Makefile helps you run the testbench.

```bash
cd <SOME PATH>
make -f <NICOTB PATH>/sim/Makefile XXX
```

By default the files must have the same name
but the provided Makefile allows you to fine-tune each file name.
Also, you have to modify the path in Makefile
in order to locate the irun (aka ncverilog) binary.

# Dependencies

* numpy and development package (TODO: version?)
* Google glog development packages (TODO: version?)
* Python (>= 3.3 ?)
* ncverilog (TODO: how about other tools which also support VPI)
* Linux (TODO: how to port?)

# Build Nicotb

First you should build the VPI library.

```bash
make -C lib/cpp
```

The examples are under the sim/ directory.
To run the examples, we have prepared a Makefile.
There are but roughly
Currently there are 2 examples, and you will lanuch the simulation
roughly like this.

```bash
cd sim/OOO
make -f ../Makefile XXX
```

where XXX is the name of toplevel Python and Verilog files.

However, you might face many problems when building the VPI library.
The Makefile is based on the configuration of my system,
and I am not familiar with the numpy/Python build flow.
Moreover, I could not access more platforms now,
so library/include paths should be modified accordingly.

# Caveat

This project is at the very primary stage,
and there are still many TODOs,
which include but are not limited to:

* More complete runtime error checking and more verbose message,
* More abundant event schedule and sync primitives,
* Support for more protocols and more examples and
* Check on more platforms.

If you are looking at a complete Python co-simulation framework,
please Google Cocotb.

# Compared with Cocotb
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

. I use *yield from* just because it's cool.


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
