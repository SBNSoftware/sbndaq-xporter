#!/bin/bash

for server in icarus-evb01 icarus-evb02 icarus-evb03 icarus-evb04 icarus-evb06
do
    ssh icarusraw@$server 'cd ~icarusraw/sbndaq-xporter/FTS_config/legacy; source setup_fts.sh; start_fts'
done

