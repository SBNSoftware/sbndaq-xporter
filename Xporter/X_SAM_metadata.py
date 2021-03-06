#import modules
#
import os
import sys
import time
import safe
from runperiod import runperiod
import SAMUtilities
import json

#
# Begin SAM metadata function
#
def SAM_metadata(filename, projectvers, projectname):
    "Subroutine to write out SAM information"
    
    metadata = {}

    #get filesize
    metadata["file_size"] = os.stat(filename).st_size
    
    #get file name
    fname = filename.split("/")[-1]
    metadata["file_name"] = fname

    #file type
    metadata["file_type"] = "data"

    #file format is artroot
    metadata["file_format"] = "artroot"
    
    #file tier is rawdata
    metadata["data_tier"] = "raw"

    #
    metadata["sbn_dm.detector"] = "sbn_fd"

    #file stream [beam trigger] is currently set to extbnb
    metadata["data_stream"] = "ext"
    #get run number from file name
    run_num = 0
    for part in fname.split("_"):
        print part
        if (part.find("run")==0): 
            run_num = int(part[3:])
            break
    print "RunNum = %d" % run_num

    metadata["runs"] = [ [ run_num , "physics"] ]
    
    #checksum
    checksum = SAMUtilities.adler32_crc(filename)
    checksumstr = "enstore:%s" % checksum

    #time
    gmt = time.gmtime(os.stat(filename).st_mtime)
    time_tuple =time.struct_time(gmt) #strftime("%d-%b-%Y %H:%M:%S",gmt)
    
    metadata["sbn_dm.file_year"] = time_tuple[0]
    metadata["sbn_dm.file_month"] = time_tuple[1]
    metadata["sbn_dm.file_day"] = time_tuple[2]

    #print "Creation time:", timestr

    
    metadata["checksum"] = [ checksumstr ]
    
    #ICARUS specific fields for bookkeping 

    metadata["icarus_project.version"] = "raw_%s" % projectvers

    metadata["icarus_project.name"] = projectname

    metadata["icarus_project.stage"] = runperiod(int(run_num)) 

    return json.dumps(metadata)


#comment out the rest for now

 
#    run_num = filename.split("_")
#
#    period = filename.rfind(".")
#    if (period < 0):
#        print "No suffix"
#        return False
#    suffix = filename[period+1:len(filename)]
#    if (suffix == "root"):
#        fileformat = "artroot"
#    else:
#        print "Unknown suffix:", suffix
#        return False
#    #
#    # get checksum
#    #   remove checksum calculation from .json file
#    checksum = SAMUtilities.adler32_crc(filename)
#    #    print "Checksum:", checksum
#    #
#    # get modified time
#    #
#    timestr = SAMUtilities.timestring(os.stat(filename).st_mtime)
#    #    print "Creation time:", timestr
#    #
#    # open SAM metadata file for writing
#    #
#    jj=filename.rfind("/")
#    if(jj<0):
#        jj=0
#    dropbox = dropboxdir+filename[jj:]+".json"
#    #    print dropbox
#    sf = open(dropbox,"w")
#    #    print "SAM file is open"
#    #
#    # Write pyton headers for SAM
#    #
#    sf.write('{\n')
#    #
#    # Write SAM metadata
#    #
#    sf.write('\t"file_name" : "'+filename[jj:]+'",\n')
#    sf.write('\t"file_size" : '+str(filesize)+',\n')
#    sf.write('\t"file_type" : "data",\n')
#    sf.write('\t"file_format" : "'+fileformat+'",\n')
#    sf.write('\t"data_tier" : "raw",\n')
#    sf.write('\t"group" : "lariat",\n')
#    sf.write('\t"checksum": [ "enstore:'+checksum+'" ],\n')
#    sf.write('\t"event_count" : 1,\n')
#    sf.write('\t"first_event" : '+safe.subrun+',\n')
#    sf.write('\t"last_event" : '+safe.subrun+',\n')
#    sf.write('\t"start_time" : "'+timestr+'",\n')
#    sf.write('\t"end_time" : "'+timestr+'",\n')
#    #
#    #Experiment specific fields
#    #
#    #
#    # fcl table not included
#    # project table not included
#    # filter table not included
#    #
#    #run number strut
#    #
#    sf.write('\t'+'"runs" : [ ['+safe.run+', '+safe.subrun+', "'+'physics'+'" ] ],\n' )
#    #
#    # run period
#    #
#    sf.write('\t"run.period" : "'+runperiod(int(safe.run))+'"\n')
#    #
#    # Write SAM footer data
#    #
#
#    sf.write("}\n")
#    sf.close()
#
#    #    print("SAM footer data written and file closed")
#    return True
