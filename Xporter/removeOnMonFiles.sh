#!/bin/bash

# this needs to run on each evb machine as /data is on local disk
# (technically only the one that runs the OM)
find /data/onmon_files -name '*.root' -type f -mtime 0.25 -delete
