#!/bin/bash

host=$(hostname | awk -F'.' '{print $1}')
timestamp=`date +%Y_%m_%d`
now=`date "+%Y-%m-%d %T"`
logfile="/daq/log/fts_logs/${host}/icarusraw_token_${host}_${timestamp}.log"

echo "$now : Obtaining icarusraw token on ${host}" >> ${logfile}

htgettoken -i icarus -a htvaultprod.fnal.gov --credkey=icarusraw/managedtokens/fifeutilgpvm01.fnal.gov -r raw --nooidc --nokerberos --nossh --minsecs 5400 >> ${logfile} 2>&1

exit 0
