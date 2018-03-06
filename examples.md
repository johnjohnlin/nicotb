---
layout: page
title: Running Examples
---

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

