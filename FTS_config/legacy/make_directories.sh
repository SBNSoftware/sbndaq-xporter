#
# Directories to make 
#
#
hosts='icarus-evb01 icarus-evb02 icarus-evb03 icarus-evb04'
for host in $hosts
do
    echo "Making directories on $host"
    ssh icarus@$host 'mkdir -p /data/daq; chmod a+rwX /data/daq'
    ssh icarus@$host 'mkdir -p /data/test_daq; chmod a+rwX /data/test_daq'
    ssh icarusraw@$host 'mkdir -p /data/fts_dropbox; chmod a+rwX /data/fts_dropbox'
done
