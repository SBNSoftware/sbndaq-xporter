#!/bin/bash

crontab_file=$1

for server in icarus-evb01 icarus-evb02 icarus-evb03 icarus-evb04 icarus-evb05
do
    cat $1 > tmp.ctab
    echo "crontab to add:"
    cat tmp.ctab
    echo "Executing: ssh ${server} crontab ~icarus/FileTransfer/sbndaq-xporter/Xporter/tmp.ctab"
    ssh $server "crontab ~icarus/FileTransfer/sbndaq-xporter/Xporter/tmp.ctab"
    rm tmp.ctab
done

for server in icarus-evb06
do
    cat $1 logfile_crontab.ctab bottomcrt_crontab.ctab icarus_evb06_db.ctab > tmp.ctab
    echo "crontab to add:"
    cat tmp.ctab
    echo "Executing: ssh ${server} crontab ~icarus/FileTransfer/sbndaq-xporter/Xporter/tmp.ctab"
    ssh $server "crontab ~icarus/FileTransfer/sbndaq-xporter/Xporter/tmp.ctab"
    rm tmp.ctab
done
