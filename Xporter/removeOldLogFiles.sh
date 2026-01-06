#!/bin/bash

# remove any logfile older than 90 days
find /daq/log -type f -mtime +90 -exec rm -f {} \;

# remove broken symlinks
find /daq/log -type l ! -exec test -e {} \; -exec rm {} \;

# remove empty directories
find /daq/log -depth -type d -empty -exec rmdir {} \;

# remove specific logfiles older than 14 days (metrics, triggerdb)
# fts logs follow same policy, but different script run by root user
find /daq/log/metrics/* -type f -mtime +14 -exec rm -f {} \;
find /daq/scratch/log/* -type f -mtime +14 -exec rm -f {} \;
find /daq/log/triggerdb/* -type f -mtime +14 -exec rm -f {} \;
