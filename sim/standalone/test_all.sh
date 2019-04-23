#!/usr/bin/env bash
rm -f scoreboard.db
export PYTHONPATH=../../lib/python/:$PYTHON_PATH
nerr=0
python3 test_anyall.py        || nerr=$((nerr+1))
python3 test_join.py          || nerr=$((nerr+1))
python3 test_lock.py          || nerr=$((nerr+1))
python3 test_semaphore.py     || nerr=$((nerr+1))
[ $nerr -eq 0 ]
exit $?
