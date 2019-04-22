#!/usr/bin/env bash
rm -f scoreboard.db
export PYTHONPATH=../../lib/python/:$PYTHON_PATH
set +e
python3 test_anyall.py
python3 test_join.py
python3 test_lock.py
python3 test_semaphore.py
