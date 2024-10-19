#!/bin/bash

# Things to do to setup for FTS
#
# Generally this follows from these webpages
# https://cdcvs.fnal.gov/redmine/projects/filetransferservice/wiki
# https://github.com/containers/podman/blob/main/docs/tutorials/rootless_tutorial.md

# this should be run as user `icarusraw`
if [ "$(whoami)" != "icarusraw" ]; then
    echo "This script must be run as icarusraw, you silly goose!"
    exit 1
fi

# enable linger mode for icarusraw: avoids container exiting after user logs out
# https://github.com/containers/podman/blob/main/troubleshooting.md#21-a-rootless-container-running-in-detached-mode-is-closed-at-logout
loginctl enable-linger $(whoami) 

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
echo "List of available podman images:"
podman images 
