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
ROOT_BUILD_HASH=$(spack find --format '{architecture} /{hash:7}' root 2>/dev/null | grep -m 1 ${SPACK_ARCH} | awk '{print $2}')

echo "$now : Found ROOT build hash '$ROOT_BUILD_HASH' for ${SPACK_ARCH}" >> ${logfile_attempt} 2>&1

# very often Spack doesn't load the package correctly
# try up until then times before giving up...
# report in logfile each attempt
for i in {1..10}; do
  echo "$now : Sourcing Spack ROOT build '$ROOT_BUILD_HASH' for ${SPACK_ARCH} (try $i)" >> ${logfile_attempt} 2>&1
  if [ -n "$ROOT_BUILD_HASH" ] && spack load ${ROOT_BUILD_HASH} >> ${logfile_attempt} 2>&1;
  then
    echo "$now : Loaded ROOT build '$ROOT_BUILD_HASH' for ${SPACK_ARCH}" >> ${logfile_attempt} 2>&1;
    break
  else
    echo "$now : [Error] \"spack load ${ROOT_BUILD_HASH}\" failed. Retrying..." >> ${logfile_attempt} 2>&1;
    sleep $((4 + RANDOM % 3))
    ROOT_BUILD_HASH=$(spack find --format '{architecture} /{hash:7}' root 2>/dev/null | grep -m 1 ${SPACK_ARCH} | awk '{print $2}')
    sleep $((4 + RANDOM % 3))
  fi
done

PYTHON_ENV="/home/nfs/icarus/FileTransfer/venv"
if [[ ! -d $PYTHON_ENV ]]; then
    echo "$now : Creating python environment with $(python3 --version)" >> ${logfile_attempt}
    python3 -m venv $PYTHON_ENV 
    source $PYTHON_ENV/bin/activate
    python3 -m pip install --upgrade pip -q 2>&1
    python3 -m pip install requests -q 2>&1
else
    echo "$now : Activating python environment" >> ${logfile_attempt}
    source $PYTHON_ENV/bin/activate
fi

# Run Xporter.py
echo "$now : Running Xporter..." >> ${logfile_attempt}
python3 -u /home/nfs/icarus/FileTransfer/sbndaq-xporter/Xporter/Xporter.py /data/daq /data/fts_dropbox sbndaq_v1_10_02 DataXport_2024-10-18 >> ${logfile} 2>&1

echo "$now : Xport Finished! Releasing lock file $file_lock now!" >> ${logfile_attempt} 2>&1
rm $file_lock

exit 0
