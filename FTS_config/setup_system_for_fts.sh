# Things to do to setup for FTS
#
# Generally this follows from these webpages:
# https://cdcvs.fnal.gov/redmine/projects/filetransferservice/wiki
#
# This should be run as user `icarusraw`

# setup some configuration for rootless containers
CONFFILE="${HOME}/.config/containers/storage.conf" 
if [ ! -f "$CONFFILE" ]; then
  echo "Creating $CONFFILE for $USER"
  mkdir -p "${HOME}/.config/containers"
  echo -e "[storage]\ndriver = \"overlay\"\n\n[storage.options.overlay]\nforce_mask = \"740\"" > "$CONFFILE"
fi

# pull latest image
podman pull imageregistry.fnal.gov/sam-zerg/fermifts:latest

# check listed images
podman images 
