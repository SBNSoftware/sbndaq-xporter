#import modules
#
import os
import sys
import time
import safe
from runperiod import runperiod
import SAMUtilities
import json
import re
from datetime import datetime

import offline_run_history
import ROOT
from ROOT import TFile,TTree
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

    #file stream [beam trigger]
    stream = "unknown"
    for part in fname.split("_"):
        if(part.find("fstrm")==0):
            stream = part[5:].lower()
            break
    print("data_stream = '%s'"%stream)
    metadata["data_stream"] = stream  

    #get run number from file name
    run_num = 0
    for part in fname.split("_"):
        if (part.find("run")==0): 
            run_num = int(part[3:])
            break
    print("RunNum = %d" % run_num)

    metadata["runs"] = [ [ run_num , "physics"] ] 

    #checksum
    checksum = SAMUtilities.adler32_crc(filename)
    checksumstr = "enstore:%s" % checksum

    print("Checksum = %s" % checksumstr)

    #time
    gmt = time.gmtime(os.stat(filename).st_mtime)
    time_tuple =time.struct_time(gmt) #strftime("%d-%b-%Y %H:%M:%S",gmt)
    
    metadata["sbn_dm.file_year"] = time_tuple[0] 
    metadata["sbn_dm.file_month"] = time_tuple[1] 
    metadata["sbn_dm.file_day"] = time_tuple[2] 

    #print "Creation time:", timestr

    metadata["checksum"] = [ checksumstr ]  
    
    #ICARUS specific fields for bookkeping 

    try:
        result=offline_run_history.RunHistoryiReader().read(run_num)
        dictionary={**result[1]}

        if len(dictionary)==0:
            print("...pending run records failed. trying run records")
            result = offline_run_history.RunHistoryiReader(ucondb_uri='https://dbdata0vm.fnal.gov:9443/icarus_on_ucon_prod/app/data/run_records/configuration/key=%d').read(run_num)
            dictionary={**result[1]}

        version = dictionary['projectversion']

        metadata["icarus_project.version"] = version.rsplit()[0] #"raw_%s" % projectvers  

        metadata["icarus_project.name"] = "icarus_daq_%s" % version.rsplit()[0] #projectname

        metadata["configuration.name"] = dictionary['configuration']

        if "Physics"!=metadata["configuration.name"][0:7] and "Overlays"!=metadata["configuration.name"][0:8] and (metadata["data_stream"]=="offbeamnumiminbias" or metadata["data_stream"]=="offbeambnbminbias"):
            metadata["data_stream"]="offbeamminbiascalib"
	#we should be able to do the latter, but we (Ivan, Donatella, Matteo, and Wes) decided 7 Mar 2024 to not distinguish here
        #since there _could_ __potentially__ be something different
        #elif metadata["configuration.name"][0:7]=="Physics" and (metadata["data_stream"]=="offbeamnumiminbias" or metadata["data_stream"]=="offbeambnbminbias"):
	#    metadata["data_stream"]="offbeamminbias"
        
        s = dictionary['configuration'].lower()

    except KeyError as e:
        print("X_SAM_Metadata.py exception: "+str(e))
        print(datetime.now().strftime("%T"), "Missing metadata value in database")
        raise

    except Exception as e:
        print('X_SAM_Metadata.py exception: '+ str(e))
        print(datetime.now().strftime("%T"), "Failed to connect to RunHistoryReader")
        raise    
        
    metadata["icarus_project.stage"] = "daq" #runperiod(int(run_num)) 

       
    # beam options
    beambnb = "bnb"
    beamnumi = "numi"
    laser = "laser"
    zerobias = "zerobias"
    bnbnumi = "common"

    #if ((beambnb in s and s.find(beamnumi) == -1) or stream=='bnb' or stream=='bnbmajority' or stream=='bnbminbias'):
    ## MV: we no longer use beam-specific configuration names, stop using it to set the beam type
    if (stream=='bnb' or stream=='bnbmajority' or stream=='bnbminbias'):
       beam = "BNB"
    #elif ((beamnumi in s and s.find(beambnb) == -1) or stream=='numi' or stream=='numimajority' or stream=='numiminbias'):
    ## MV: we no longer use beam-specific configuration names, stop using it to set the beam type
    elif (stream=='numi' or stream=='numimajority' or stream=='numiminbias'):
       beam = "NUMI"
    elif ( zerobias or laser) in s:
       beam = "none"
    elif ('offbeam' in stream):
       beam = "none"
    elif (bnbnumi) in s:
       beam = "mixed"
    else:
       beam = "unknown"

    metadata["sbn_dm.beam_type"] = beam

    #for event count:
    fFile = TFile(filename,"READ")
    fTree= fFile.Get("Events")
    nEvents = fTree.GetEntries()
    print("number of event in the root file %d" % nEvents)

    metadata["sbn_dm.event_count"] = nEvents

    # components list
    #s = dictionary.get('components').replace('[','').replace(']','')
    #metadata["icarus.components"] = s.split(', ')

    #last check before releasing metadata into the wild
    try:
        metadata["icarus_project.version"]
        metadata["icarus_project.name"]
        metadata["configuration.name"]
        metadata["data_stream"]
    except KeyError as e:
        print("X_SAM_Metadata.py exception: "+str(e))
        print("Cathing missing metadata before it's too late!")
        raise

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
