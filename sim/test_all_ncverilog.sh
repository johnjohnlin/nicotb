#!/usr/bin/env bash
nerr=0
make -f ../Makefile -C 0_basic_rw           || nerr=$((nerr+1))
make -f ../Makefile -C 0_basic_rw           clean
make -f ../Makefile -C 1_basic_verify       || nerr=$((nerr+1))
make -f ../Makefile -C 1_basic_verify       clean
make -f ../Makefile -C 2_protocol_verify1   || nerr=$((nerr+1))
make -f ../Makefile -C 2_protocol_verify1   clean
make -f ../Makefile -C 3_protocol_verify2   || nerr=$((nerr+1))
make -f ../Makefile -C 3_protocol_verify2   clean
[ $nerr -eq 0 ]
exit $?
