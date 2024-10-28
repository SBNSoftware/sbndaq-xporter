#!/bin/bash

# needs to run as root because fts logs 
# are owned by both icarus and icarusraw
find /daq/log/fts_logs/* -type f -mtime +14 -exec rm -f {} \;
