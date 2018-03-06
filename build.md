---
layout: page
title: "Build Nicotb"
---
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

The examples are under the `sim/` directory.
To run the examples, we have prepared a Makefile,
and you will lanuch the simulation like this.

```bash
cd sim/OOO
make -f ../Makefile XXX
```

where XXX is the name of toplevel Python and Verilog files.
You can find more details in [examples](examples.html).

However, you might face many problems when building the VPI library.
The Makefile is based on the configuration of my system,
and I am not familiar with the numpy/Python build flow.
Moreover, I could not access more platforms now,
so library/include paths should be modified accordingly.

# Build Nicotb on a very old Linux, without root

I use Arch as my primary OS, but many EDA tools are installed on a old Linux PC,
and it\'s very hard to install the dependencies from official repos.
In a very old system (e.g. gcc 4.1),
it is necessary to compile everything from source code.
The most difficult and time-consuming part is to compile gcc.
Fortunately, there is a
[good article](https://stackoverflow.com/questions/9450394/how-to-install-gcc-piece-by-piece-with-gmp-mpfr-mpc-elf-without-shared-libra)
about installing gcc.
In following parts I will give a brief introduction about installing the gcc dependencies, gcc, Python, glog, and numpy in order.
First, you need these files (any newer version should be fine):

```text
gcc-6.1.0.tar.bz2
glog-master.zip
gmp-6.1.0.tar.bz2
mpc-1.0.3.tar.gz
mpfr-3.1.4.tar.bz2
numpy-1.14.2.zip
binutils-2.30.tar.gz
Python-3.6.5.tgz
```

. Note that Github does not allow older protocol of OpenSSL/wget/git,
so sometimes you might have to download them from other PCs.
Also, you should notice that some very old PCs cannot unzip these files.

```bash
mkdir ${HOME}/install
# binutils
./configure --prefix=${HOME}/install
make install
# GMP
./configure \
	--disable-shared --enable-static \
	--prefix=/tmp/gcc
make install
# MPFR
./configure \
	--disable-shared --enable-static \
	--prefix=/tmp/gcc --with-gmp=/tmp/gcc
make install
# MPC
./configure \
	--disable-shared --enable-static \
	--prefix=/tmp/gcc --with-gmp=/tmp/gcc --with-mpfr=/tmp/gcc
make install
# GCC (Note: must configure under a clean directory)
mkdir build
cd build
../configure \
	--prefix=$HOME/install/ --enable-languages=c,c++ \
	--enable-shared --enable-threads=posix -enable-__cxa_atexit \
	--with-gmp=/tmp/gcc --with-mpc=/tmp/gcc --with-mpfr=/tmp/gcc \
	--program-suffix=-6.1
# set path (setenv for csh)
# It's better to add this to your bashrc.
# FIXME: The 32 and 64 path might mix-up?
export PATH=$PATH:$HOME/install/bin
export CC=gcc-6.1
export LD_LIBRARY_PATH=$HOME/install/lib:$HOME/install/lib64
```

## Python and Numpy

```bash
# Python
./configure --prefix=${HOME}/install --enable-optimizations --enable-shared
make
make install
# Numpy
~/install/bin/python3 setup.py build
~/install/bin/python3 setup.py build_ext
~/install/bin/python3 setup.py build_py
~/install/bin/python3 setup.py build_clib
~/install/bin/python3 setup.py build install
```

## Glog

This is simpler to compile.

```bash
./autogen.sh --force
./configure --prefix=${HOME}/install
```

## Modify the Makefile

The numpy include files are put under a complex path, such as:

```text
${HOME}/install/lib/python3.6/site-packages/numpy-1.14.2-py3.6-linux-x86_64.egg/numpy/core/include
```

. And you must use `-I path/to/include` flag for `g++`.
Also, you must change `g++` to `g++-6.1` (or whatever).

## Preload libraries

Very commonly, `LD_PRELOAD` must be used to prioritize new libraries.

```bash
export LD_PRELOAD=${HOME}/install/lib64/libstdc++.so:${HOME}/install/lib/libpython3.6m.so
```
