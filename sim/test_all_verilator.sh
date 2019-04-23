#!/usr/bin/env bash
nerr=0
make -f ../Makefile.verilator -C 0_basic_rw           || nerr=$((nerr+1))
make -f ../Makefile.verilator -C 1_basic_verify       || nerr=$((nerr+1))
make -f ../Makefile.verilator -C 2_protocol_verify1   || nerr=$((nerr+1))
make -f ../Makefile.verilator -C 3_protocol_verify2   || nerr=$((nerr+1))
[ $nerr -eq 0 ]
exit $?
