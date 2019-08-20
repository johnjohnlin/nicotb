[![Build Status](https://travis-ci.com/johnjohnlin/nicotb.svg?branch=master)](https://travis-ci.com/johnjohnlin/nicotb.svg?branch=master)

# Introduction

Nicotb is Python-Verilog co-simulation framework.
It is lightweight and can be installed with little efforts,
and it is also extensible to provide UVM-like simulation for verifying many well-known hardware protocols.
Currently Nicotb supports generic Verilog simulator that support VPI (Ncverilog, Vcs) as well as cycle-based simulator (verilator).

# Fast Setup

If your system are shipped with new toolchains, then this will work for you.
```
git clone https://github.com/johnjohnlin/nicotb
cd nicotb
python3 setup.py install --user
python3 -c "import nicotb"
```

If you are using the OS with outdated (stable) softwares like CentOS,
then you can use something like this.
```
export CC=/opt/rh/devtoolset-7/root/bin/gcc
export VCS="vcs -cpp /opt/rh/devtoolset-7/root/bin/g++"
export CXX=/opt/rh/devtoolset-7/root/bin/g++
export PY=/opt/rh/rh-python36/root/usr/bin/python3.6
git clone https://github.com/johnjohnlin/nicotb
cd nicotb
$(PY) setup.py install --user
$(PY) -c "import nicotb"
```

Simply <tt>import nicotb</tt> is not that useful, for using nicotb for RTL verification,
please see the examples in <tt>sim</tt> or read the [document page](https://johnjohnlin.github.io/nicotb/).
Also, reading <tt>.travis.yml</tt> to see how we run the regression can be useful,
and for obvious reasons we only run the regression with Verilator.

# Document

The [document page](https://johnjohnlin.github.io/nicotb/) is hosted by Github pages.

# Tested, supported platforms

We have tested Nicotb on as many environments as possible,
and these are the environments on which we can successfully Nicotb.

* CentOS 7
	* Python 3, Numpy, and g++ 7, through EPEL (tested at 2019)
	* Compiled Verilator 4.016
	* Vcs
* ArchLinux & Ubuntu 18.04
	* Verilator 4.0xx, Python 3.6+, Numpy, and g++ 7+, through apt-get or pacman (tested at 2018-2019)
	* Ncverilog
* Ubuntu 14.04
	* apt-get Verilator 3.9xx
	* Used for CI, see also .travis.yml
