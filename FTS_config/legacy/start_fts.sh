#!/bin/bash

for server in icarus-evb01 icarus-evb02 icarus-evb03 icarus-evb04 icarus-evb05
do
    ssh icarusraw@$server 'cd ~icarusraw/sbndaq-xporter/FTS_config; source setup_fts.sh; start_fts'
done
