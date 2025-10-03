#!/bin/bash

for server in icarus-evb07 icarus-evb08 icarus-evb09 icarus-evb10 icarus-evb11 icarus-evb12
do
    ssh icarusraw@$server 'cd ~icarusraw/sbndaq-xporter/FTS_config; ./stop_fts_container.sh'
done

