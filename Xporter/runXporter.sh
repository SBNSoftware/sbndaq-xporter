#!/bin/bash

timestamp=`date +%Y_%m_%d`
logfile="/daq/log/fts_logs/`hostname`/xporter_`hostname`_${timestamp}.log"

file_lock="/tmp/xporter_`hostname`.lock"

if [ -f $file_lock ]; then
    echo "Xport in progress! Do not run"
    exit 0
fi

touch $file_lock

#echo $logfile
#echo $timestamp

python /home/nfs/icarus/FileTransfer/sbndaq-xporter/Xporter/Xporter.py /data/daq /data/fts_dropbox none sbndaq_v0_04_03 DataXportTesting_03Feb2020 >> ${logfile} 2>&1

#echo "done?"

rm $file_lock

exit 0