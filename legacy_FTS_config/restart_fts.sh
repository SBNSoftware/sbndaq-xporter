#!/bin/bash

for server in icarus-evb01 icarus-evb02 icarus-evb03 icarus-evb04 icarus-evb05 icarus-evb06
do
    ssh icarusraw@$server 'cd ~icarusraw/sbndaq-xporter/FTS_config; source setup_fts.sh; stop_fts; start_fts'
done

