# Introduction

Nicotb aims to provide a tiny but extensible framework
for Python-Verilog co-simulation through VPI which:

* Maximize the use of existing popular libraries,
* Simplify the interface between Python & Verilog and
* Let users define the Python-VPI bridging through a configuration file,
  rather than through program.

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
which is the order they are defined in the protobuf text.

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
The write() function helps you write all signals to Verilog.
Again, note that the signals are also references,
so don't try to assign new arrays to them.

Event is usually an integer in Verilog, if the event occurred,
the Nicotb framework (1) reads the Verilog and fill the buses with the read values.
and (2) lets the Python codes wait on this event start to run.

# Nicotb Co-simulation Workflow

To run the Nicotb, at least 3 files are required.

* XXX.sv: The testbench defining the signals to be tested and controlling timing.
* XXX.py: The Python testbench which waits for events and respond to them.
* XXX.txt: Text format protocol buffer describing the Python-VPI bridging.

After preparing the files, the Makefile helps you run the testbench.

```bash
cd <SOME PATH>
make -f <NICOTB PATH>/sim/Makefile XXX
```

By default the three files must have the same name
but the provided Makefile allows you to fine-tune each file name.
Also, you have to modify the path in Makefile
in order to locate the irun (aka ncverilog) binary.

# Dependencies

* numpy and development package (TODO: version?)
* Google glog, protobuf and development packages (TODO: version?)
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
Currently there are only example.

```bash
cd sim/simple_test
make -f ../Makefile tb
```

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
* Support for more protocols and more examples,
* Check on more platforms and
* Scoreboard.
