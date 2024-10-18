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
#  fts.conf
#  sam_cp.cfg
#

host=$(hostname | awk -F'.' '{print $1}')
echo "Starting FTS podman container image on ${host}"

# setting the volume paths inside the container to be the same
# matching between actual location and relative paths inside
# syntax: -v /HOST-DIR:/CONTAINER-DIR

# these are real locations on the current host
# using the same as the legacy FTS setup
fts_x509_proxy_dir=/opt/icarusraw
fts_log_dir=/daq/log/fts_logs/$host
fts_db_dir=/var/tmp
fts_samcp_log_dir=/var/tmp
fts_config_dir=~icarusraw/FTS/$host
fts_dropbox_dir=/data/fts_dropbox

# copy config files into host-specific config directory
# this is not stricly necessary, but keeps things tidy?
mkdir -p $fts_config_dir
cp $PWD/fts.conf $PWD/sam_cp.cfg $fts_config_dir/

# additional things the run command does:
# - set hostname inside the container as ${host}
# - set $USER inside the container as current user
# - set container name to fts_${host}
# - expose port 8787 for localhost:8787 status page

podman run \
       -v ${fts_log_dir}:/opt/fts/fts_logs \
       -v ${fts_db_dir}:/opt/fts/fts_db \
       -v ${fts_config_dir}:/opt/fts/fts_config \
       -v ${fts_dropbox_dir}:/storage \
       -v ${fts_samcp_log_dir}:/var/tmp \
       -v ${fts_x509_proxy_dir}:/opt/fts/fts_proxy \
       -p 8787:8787 \
       -d \
       --network slirp4netns:port_handler=slirp4netns \
       --hostname ${host} \
       --env USERNAME=${USER} \
       --name fts_${host} \
       --replace \
       fermifts
