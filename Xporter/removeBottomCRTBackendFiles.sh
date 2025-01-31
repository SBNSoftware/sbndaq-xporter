#!/bin/bash

timestamp=`date +%Y_%m_%d_%H_%M`
host=`hostname -s`
echo "Running removeBottomCRTBackendFiles.sh on ${host} at ${timestamp}"

# 2024-03-21 MV: commenting out the ssh command, cronjobs don't pick up kerberos tickets easily 
# so moving to running this directly on icarus_crt11
# ssh icarus-crt11 "find /scratch_local/crt_tests/backend_data/ -path \"/scratch_local/crt_tests/backend_data/runs1/DATA/Run_*/binary/*\" -type f -mtime +7 -exec rm -f '{}' +"

find /scratch_local/crt_tests/backend_data/ -path "/scratch_local/crt_tests/backend_data/runs1/DATA/Run_*/binary/*" -type f -mtime +7 -exec rm -f '{}' +
