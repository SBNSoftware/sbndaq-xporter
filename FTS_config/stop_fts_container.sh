#----------------------------------------
# Stop FTS from a podman container image
#----------------------------------------
#
# Disclaimer:
# FTS is old, and can not be run on EL9 without significant complications.
# A prebuilt FTS container image is provided to work with Podman.
#

host=$(hostname | awk -F'.' '{print $1}')
echo "Stop FTS podman container image on ${host}"

podman run fermifts
