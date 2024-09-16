#!/bin/bash

host=$(hostname | awk -F'.' '{print $1}')
timestamp=`date +%Y_%m_%d`
now=`date "+%Y-%m-%d %T"`
logfile="/daq/log/fts_logs/${host}/xporter_${host}_${timestamp}.log"
logfile_attempt="/daq/log/fts_logs/${host}/attempt_xporter_${host}_${timestamp}.log"

file_lock="/tmp/xporter_${host}.lock"

if [ -f $file_lock ]; then
    echo "$now : Xport in progress! Do not run" >> ${logfile_attempt} 2>&1
    exit 0
fi

echo "$now : Xport Starting! Obtaining lock file $file_lock now!" >> ${logfile_attempt} 2>&1
touch $file_lock

# need to source ROOT to get pyRoot
SPACK_ENV="/daq/software/spack_packages/spack/current/NULL/share/spack/setup-env.sh"
SPACK_ARCH="linux-$(spack arch --operating-system 2>/dev/null)-x86_64_v2"   
source ${SPACK_ENV_SCRIPT}
spack load root@6.28.10 %gcc@12.2.0 arch=${SPACK_ARCH}

(( $(pip3 freeze |grep requests |wc -l) )) ||  { echo "requests is missing; installing requests..."; pip3 install --user requests; }

#python3 /home/nfs/icarus/FileTransfer/sbndaq-xporter/Xporter/Xporter.py /data/daq /data/fts_dropbox none >> ${logfile} 2>&1
python3 -u /home/nfs/icarus/FileTransfer/sbndaq-xporter/Xporter/Xporter.py /data/daq /data/fts_dropbox none sbndaq_v1_10_01 DataXport_20240913 >> ${logfile} 2>&1
#python3 /home/nfs/icarus/FileTransfer/sbndaq-xporter/Xporter/Xporter.py /data/daq /data/fts_dropbox none sbndaq_v0_04_03 DataXportTesting_03Feb2020 

echo "$now : Xport Finished! Releasing lock file $file_lock now!" >> ${logfile_attempt} 2>&1
rm $file_lock

exit 0
