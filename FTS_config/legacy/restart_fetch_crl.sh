#!/bin/bash

for server in icarus-evb02 icarus-evb03 icarus-evb04 icarus-evb05 icarus-evb06
do
    ssh root@$server 'systemctl restart fetch-crl-cron; fetch-crl'
done

