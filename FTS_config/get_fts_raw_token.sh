#!/bin/bash

host=$(hostname | awk -F'.' '{print $1}')
timestamp=`date +%Y_%m_%d`
now=`date "+%Y-%m-%d %T"`
logfile="/daq/log/fts_logs/${host}/${USER}_token_${host}_${timestamp}.log"

echo "$now : Obtaining ${USER} token on ${host}" >> ${logfile}

# specify token location (default)
export BEARER_TOKEN_FILE=/run/user/$UID/bt_u$UID

# get token
htgettoken -v -i icarus -a htvaultprod.fnal.gov --credkey=${USER}/managedtokens/fifeutilgpvm01.fnal.gov -r raw --nooidc --nokerberos --nossh --minsecs 5400 >> ${logfile} 2>&1

# check token is valid
httokendecode -H >> ${logfile} 2>&1

exit 0
