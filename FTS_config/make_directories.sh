#
# Directories to make 
#

hosts='icarus-evb08 icarus-evb09 icarus-evb10 icarus-evb12'
for host in $hosts
do
    echo "Making directories on $host"
    ssh icarus@$host 'mkdir -p /data/daq; chmod a+rwX /data/daq'
    ssh icarus@$host 'mkdir -p /data/test_daq; chmod a+rwX /data/test_daq'
    ssh icarus@$host 'mkdir -p /data/onmon_files; chmod g+w,o+rX /data/onmon_files'
    ssh icarusraw@$host 'mkdir -p /data/fts_dropbox; chmod a+rwX /data/fts_dropbox'
done
