#!/bin/bash

for server in icarus-evb12
do
    ssh icarusraw@$server 'cd ~icarusraw/sbndaq-xporter/FTS_config; ./stop_fts_container.sh'
done

