#!/bin/bash

for server in icarus-evb07 icarus-evb08 icarus-evb09 icarus-evb10 icarus-evb11 icarus-evb12
do
    echo "Executing: rm /tmp/xporter*.lock"
    ssh $server "rm /tmp/xporter*.lock"
    echo "Executing: rm /data/daq/XporterInProgress*"
    ssh $server "rm /data/daq/XporterInProgress*"
done

