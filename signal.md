---
layout: default
title: Nicotb Document
---

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

