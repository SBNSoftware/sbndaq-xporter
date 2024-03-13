#!/bin/bash

ssh icarus-crt11 "find /scratch_local/crt_tests/backend_data/ -path \"/scratch_local/crt_tests/backend_data/runs1/DATA/Run_*/binary/*\" -type f -mtime +7 -exec rm -f '{}' +"
