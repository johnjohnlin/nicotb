[![Build Status](https://travis-ci.com/johnjohnlin/nicotb.svg?branch=master)](https://travis-ci.com/johnjohnlin/nicotb.svg?branch=master)

# Introduction

Nicotb is Python-Verilog co-simulation framework.
It is lightweight and can be installed with little efforts,
and it is also extensible to provide UVM-like simulation for verifying many well-known hardware protocols.
Currently Nicotb supports generic Verilog simulator that support VPI (ncverilog) as well as cycle-based simulator (verilator).

# Fast Setup

```
git clone https://github.com/johnjohnlin/nicotb
cd nicotb
python setup.py install --user
python -c "import nicotb"
```

Simply <tt>import nicotb</tt> is not that useful, for using nicotb for RTL verification,
please see the examples in <tt>sim</tt> or read the [document page](https://johnjohnlin.github.io/nicotb/).
Also, reading <tt>.travis.yml</tt> to see how we run the regression can be useful,
and for obvious reasons we only run the regression with Verilator.

# Document

The [document page](https://johnjohnlin.github.io/nicotb/) is hosted by Github pages.

