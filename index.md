---
layout: page
title: "Nicotb Document"
---
## Index
* [Project page](https://github.com/johnjohnlin/nicotb)
* Document
	* [Build Nicotb](build.html)
	* [Basic types of Nicotb](signal.html)
	* [Examples](examples.html)
	* Standalone mode
	* [Compare with cocotb](compare.html)
* Development Guide
	* [Tutorial](concurrent.html)
	* [VPI](vpi.html)

## Introduction

Nicotb aims to provide a tiny but extensible framework
for Python-Verilog co-simulation through VPI which:

* Maximize the use of existing popular libraries,
* Unify and simplify the interface between Python & Verilog.

## Caveat

I use Nicotb in my own project(s),
and it\'s enough for simulating a DNN (CNN) accelerator and connecting with a DRAM simulator.
However, this project still has many TODOs:

* More complete runtime error checking and more verbose message,
* more abundant event schedule and sync primitives,
* support for more protocols and more examples and
* check on more platforms.

If you are looking at a developed Python co-simulation framework,
please Google Cocotb, and I also make a comparison [here](compare.html).
