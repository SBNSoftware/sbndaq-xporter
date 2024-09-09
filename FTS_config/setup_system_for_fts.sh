#
# Things to do to setup for FTS
#
# Generally this follows from these webpages:
# https://cdcvs.fnal.gov/redmine/projects/filetransferservice/wiki
#
# This should be run as user `icarusraw`

# pull latest image
podman pull imageregistry.fnal.gov/sam-zerg/fermifts:latest

# check listed images
podman images 
