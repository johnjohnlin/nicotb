# Introduction

(TODO)

# Dependencies

* numpy and development package (TODO: version?)
* Google glog, protobuf and development packages (TODO: version?)
* Python (>= 3.3 ?)
* ncverilog (TODO: how about other tools which also support VPI)
* Linux (TODO: how to port?)

# Building

First you should build the VPI library.

```bash
make -C lib/cpp
```

To run the example, we have prepared a Makefile.
Currently there are only example.

```bash
cd sim/simple_test
make -f ../Makefile
```

This example (TODO).

However, you might face many problems when building the VPI library.
The Makefile is based on the configuration of my system,
and I am not familiar with the numpy/Python build flow.
Moreover, I could not access more platforms now,
so library/include paths should be modified accordingly.

# Caveat

This project is at the very primary stage,
and there are still many TODOs,
which include but are not limited to:

* More complete runtime error checking and more verbose message.
* Support for more protocols.
* Check on more platforms.
