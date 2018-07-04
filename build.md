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
First, you need these files, and any newer version should be fine:

* [mpfr 3.14](ftp://gcc.gnu.org/pub/gcc/infrastructure/mpfr-3.1.4.tar.bz2)
* [mpc 1.0.3](ftp://gcc.gnu.org/pub/gcc/infrastructure/mpc-1.0.3.tar.gz)
* [gmp 6.1.0](ftp://gcc.gnu.org/pub/gcc/infrastructure/gmp-6.1.0.tar.bz2)
* [gcc 8.1.0](https://ftp.gnu.org/gnu/gcc/gcc-8.1.0/gcc-8.1.0.tar.xz)
* [binutils 2.30](https://ftp.gnu.org/gnu/binutils/binutils-2.30.tar.xz)
* [Python 3.6.5](https://www.python.org/ftp/python/3.6.5/Python-3.6.5.tar.xz)
* [Numpy 1.14.5](https://files.pythonhosted.org/packages/d5/6e/f00492653d0fdf6497a181a1c1d46bbea5a2383e7faf4c8ca6d6f3d2581d/numpy-1.14.5.zip)
* [Google logger (master branch)](https://github.com/google/glog/archive/master.zip)

If the links are invalidated, then try to find in these pages:
* [binutils](https://ftp.gnu.org/gnu/binutils/)
* [gcc, g++](https://ftp.gnu.org/gnu/gcc/)
* [mpfr, mpc, gmp](ftp://gcc.gnu.org/pub/gcc/infrastructure/)
* [Python](https://www.python.org/downloads/source/)
* [Numpy](https://pypi.org/project/numpy/#files)
* [Google logger](https://github.com/google/glog)

. Note that Github does not allow older protocol of OpenSSL/wget/git,
so sometimes you might have to download them from other PCs.
Also, you should notice that some very old PCs cannot unzip these files.

```bash
mkdir ${HOME}/install
mkdir /tmp/gcc
# binutils (Note: must configure under a clean directory)
mkdir build_binutils
cd build_binutils
/absolute_path/configure --prefix=${HOME}/install
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
mkdir build_gcc
cd build_gcc
/absolute_path/configure \
	--prefix=$HOME/install/ --enable-languages=c,c++ \
	--enable-shared --enable-threads=posix -enable-__cxa_atexit \
	--with-gmp=/tmp/gcc --with-mpc=/tmp/gcc --with-mpfr=/tmp/gcc \
	--program-suffix=-8
# set path (setenv for csh)
# It's better to add this to your bashrc.
# FIXME: The 32 and 64 path might mix-up?
export PATH=$PATH:$HOME/install/bin
export CC=gcc-8
export LD_LIBRARY_PATH=$HOME/install/lib:$HOME/install/lib64
```

## Python and Numpy

```bash
# Python
./configure --prefix=${HOME}/install --enable-optimizations --enable-shared
make
make install
# Numpy（If the following build fails.)
# export BLAS=None
# export LAPACK=None
# export ATLAS=None
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
make install
```

## Modify the Makefile

The numpy include files are put under a complex path, such as:

```text
${HOME}/install/lib/python3.6/site-packages/numpy-1.14.2-py3.6-linux-x86_64.egg/numpy/core/include
```

. And you must use `-I path/to/include` flag for `g++`.
Also, you must change `g++` to `g++-8` (or whatever).

## Preload libraries

Very commonly, `LD_PRELOAD` must be used to prioritize new libraries.

```bash
export LD_PRELOAD=${HOME}/install/lib64/libstdc++.so:${HOME}/install/lib/libpython3.6m.so:${HOME}/install/lib/libglog.so
```
