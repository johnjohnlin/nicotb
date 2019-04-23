# How to execute
## Direct version

    make -f ../Makefile sm

## Iterable version

    ITER= make -f ../Makefile sm

## Verilator version

    make TEST=sm sm_dut -f ../Makefile.verilator
