#!/bin/bash

for server in icarus-evb12
do
    ssh icarusraw@$server 'cd ~icarusraw/sbndaq-xporter/FTS_config; ./run_fts_container.sh'
done

