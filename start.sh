#!/bin/bash
kill -9 `ps aux | grep "python judger.py$" | awk '{print $2}'`
python judger.py >> log.txt 2>&1 &

