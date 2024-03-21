#!/bin/bash

# 2024-03-21 MV: commenting out the ssh command, cronjobs don't pick up kerberos tickes easily so moving to running this directly on icarus_crt11
#ssh icarus-crt11 "find /scratch_local/crt_tests/backend_data/ -path \"/scratch_local/crt_tests/backend_data/runs1/DATA/Run_*/binary/*\" -type f -mtime +7 -exec rm -f '{}' +"

find /scratch_local/crt_tests/backend_data/ -path \"/scratch_local/crt_tests/backend_data/runs1/DATA/Run_*/binary/*\" -type f -mtime +7 -exec rm -f '{}' +
