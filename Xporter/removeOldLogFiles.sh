#!/bin/bash

find /daq/log/* -type f -mtime +90 -exec rm -f {} \;
find /daq/log/* -type l ! -exec test -e {} \; -exec rm {} \;
find /daq/log -type d -empty -exec rmdir {} \;
find /daq/log/metrics/* -type f -mtime +14 -exec rm -f {} \;
rm /daq/log/grafana/graphite/exception.log
rm /daq/log/grafana/carbon/listener.log
