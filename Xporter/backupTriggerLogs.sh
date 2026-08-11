#!/bin/sh

# This script backs up and compresses logfiles of trigger boardreader,
# so that they survive periodic deletion

BACKUP_DIR=/home/nfs/icarus/TriggerLogBackup
INPUT_DIR=/daq/log/boardreader

#Loop over trigger logs
#-mtime +0 # modified more than 1d ago (to exclude ongoing)
#-mmin +60 # modified more than 60min ago (to exclude ongoing)
#-L        # use source file time, rather than the symlink
#-type f   # type of the linked file is 'file'. This will exclude broken
           # symlinks. We do have broken symlinks when we delete old
           # logs.

#for logfile in $(find -L $INPUT_DIR -name "run*-icarustrigger.log" -mtime +0 -type f)
for logfile in $(find -L $INPUT_DIR -name "run*-icarustrigger.log" -mmin +60 -type f)
do
    filename=$(basename $logfile)
    outfile="${BACKUP_DIR}/${filename}.xz"
    tmpoutfile="${BACKUP_DIR}/.${filename}.xz"

    #skip already existing files
    if test -f "${outfile}"
    then
        continue
    fi

    echo Backing up "${logfile}" to "${outfile}"

#compress the output file with xz
#testing showed option --fast actually gives the best compression ratio as well

    rm -f "${tmpoutfile}"
    nice -n 19 xz -c --fast "${logfile}" > "${tmpoutfile}"
    mv "${tmpoutfile}" "${outfile}"
        
done

