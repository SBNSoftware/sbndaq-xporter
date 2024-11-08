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

# need to source ROOT from Spack to get pyROOT
# current paradigm requires to select a build hash
# build hash depends on the current architecture
SPACK_ENV="/daq/software/spack_packages/spack/current/NULL/share/spack/setup-env.sh"
source ${SPACK_ENV} >> ${logfile_attempt} 2>&1  
SPACK_ARCH="linux-$(spack arch --operating-system 2>/dev/null)-x86_64_v2"

# hardcoded hash map for available ROOT builds 
declare -A build_hash_map=(
    [scientific7]="/zvbmgig"
    [almalinux9]="/se7z5bo"
)
ROOT_BUILD_HASH="${build_hash_map[$(spack arch --operating-system 2>/dev/null)]:-}"

# very often Spack doesn't load the package correctly
# try up until then times before giving up...
# report in logfile each attempt
for i in {1..10}; do
  echo "$now : Sourcing Spack ROOT build $ROOT_BUILD_HASH for ${SPACK_ARCH} (try $i)" >> ${logfile_attempt} 2>&1
  if spack load ${ROOT_BUILD_HASH} >> ${logfile_attempt} 2>&1;
  then
    echo "$now : Loaded ROOT build $ROOT_BUILD_HASH for ${SPACK_ARCH}" >> ${logfile_attempt} 2>&1;
    break
  else
    echo "$now : [Error] \"spack load ${ROOT_BUILD_HASH}\" failed. Retrying..." >> ${logfile_attempt} 2>&1;
    sleep $((4 + RANDOM % 3))
  fi
done

# install mising python packaged (if needed)
(( $(pip3 freeze |grep requests |wc -l) )) ||  { echo "requests is missing; installing requests..."; pip3 install --user requests; }

# Run Xporter.py
python3 -u /home/nfs/icarus/FileTransfer/sbndaq-xporter/Xporter/Xporter.py /data/daq /data/fts_dropbox none sbndaq_v1_10_02 DataXport_2024-10-18 >> ${logfile} 2>&1

echo "$now : Xport Finished! Releasing lock file $file_lock now!" >> ${logfile_attempt} 2>&1
rm $file_lock

exit 0
