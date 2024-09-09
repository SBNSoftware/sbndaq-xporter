#----------------------------------------
# Start FTS from a podman container image
#----------------------------------------
#
# Disclaimer:
# FTS is old, and can not be run on EL9 without significant complications.
# A prebuilt FTS container image is provided to work with Podman.
# To install on an evb machine, run as user `icarusraw`:
#   podman pull imageregistry.fnal.gov/sam-zerg/fermifts:latest
#
# Note:
# A -v mount line is needed for each local or pnfs directory that FTS needs. 
# These can be deduced from the configuration files:
#  icarus-evb_fts_config.ini
#  sam_cp.cfg
#

host=$(hostname | awk -F'.' '{print $1}')
echo "Starting FTS podman container image on ${host}"

# setting the volume paths inside the container to be the same
# matching between actual location and relative path inside
# syntax: -v /HOST-DIR:/CONTAINER-DIR

fts_x509_proxy_dir=/opt/icarusraw
fts_log_dir=/daq/log/fts_logs/$host
fts_db_dir=/var/tmp
fts_samcp_log_dir=/var/tmp
fts_config_dir=$PWD
fts_dropbox_dir=/data/fts_dropbox
fts_pnfs_dir=/pnfs/icarus

podman run \
       -v ${fts_log_dir}:/opt/fts/fts_logs \
       -v ${fts_db_dir}:/opt/fts/fts_db \
       -v ${fts_config_dir}:/opt/fts/fts_config \
       -v ${fts_dropbox_dir}:/storage \
       -v ${fts_samcp_log_dir}:/var/tmp \
       -p 8787:8787 \
       -d \
       --env-host \
       --network slirp4netns:port_handler=slirp4netns \
       --name fts_${host} \
       fermifts

# DO NOT USE WHILE TESTING... just to be sure we don't transfer anytyhing..
#       -v .${fts_pnfs_dir}:/pnfs/icarus \
# NEEDS /opt/icarusraw/... (which is not setup yet)
#       -v ${fts_x509_proxy_dir}:/opt/fts/fts_proxy \
