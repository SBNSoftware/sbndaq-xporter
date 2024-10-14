#
# Generic setup script for FTS
#
#    You may need to set the explicit version of FTS
#    $SAM_CP_CONFIG_DIR should point to the directory
#    where the sam_cp.cfg file resides.
#

source /daq/software/products/setup
source /home/nfs/icarusraw/ups/setups
setup sam_cp v9_0_8
setup encp -q stken:x86_64
setup ifdhc v2_6_1 -q e20:p392:prof
setup ifdhc_config v2_6_1b

ups active

export SAM_CP_CONFIG_DIR=$PWD
export X509_USER_PROXY=/opt/icarusraw/icarusraw.Raw.proxy

source ~icarusraw/FTS/bin/activate

export FTS_RUN_DIR=~icarusraw/FTS/`hostname`
export FTS_CONFIG_FILE=$PWD/icarus-evb_fts_config.ini
cp $FTS_CONFIG_FILE $FTS_RUN_DIR/


#export X509_CERT_DIR=
