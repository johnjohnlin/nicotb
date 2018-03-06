---
layout: home
title: Nicotb Document
---
# Index
* Document
	* [Build Nicotb](build.html)
	* [Basic types of Nicotb](signal.html)
	* [Examples](examples.html)
	* Standalone mode
	* [Compare with cocotb](compare.html)
* Development Guide
	* [Tutorial](concurrent.html)
	* [VPI](vpi.html)

# Introduction

Nicotb aims to provide a tiny but extensible framework
for Python-Verilog co-simulation through VPI which:

* Maximize the use of existing popular libraries,
* Unify and simplify the interface between Python & Verilog.

# Caveat

I use Nicotb in my own project(s),
and it's enough for simulating a DNN (CNN) accelerator and connecting with a DRAM simulator.
However, This project is still at the very primary stage,
and there are still many TODOs:

* More complete runtime error checking and more verbose message,
* More abundant event schedule and sync primitives,
* Support for more protocols and more examples and
* Check on more platforms.

If you are looking at a complete Python co-simulation framework,
please Google Cocotb, and I also make a comparison [here](compare.html).
