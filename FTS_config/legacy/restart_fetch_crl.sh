#!/bin/bash

for server in icarus-evb01 icarus-evb02 icarus-evb03 icarus-evb04 icarus-evb06
do
    ssh root@$server 'systemctl restart fetch-crl-cron; fetch-crl'
done

