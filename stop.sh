#!/bin/bash
kill -9 `ps aux | grep "python judger.py$" | awk '{print $2}'`
