#import modules
import os
import sys
import time
from datetime import datetime
import SAMUtilities
import json
import re
import offline_run_history
from ROOT import TFile,TTree

#
# Begin SAM metadata function:
# builds file metadata starting from file name
# and DAQ configuration stored in run history db
#

def SAM_metadata(filename, projectvers, projectname):
    "Subroutine to write out SAM information"
    
    metadata = {}
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    fname = filename.split("/")[-1]
    
    print("%s Preparing metadata for %s" % (now,fname))   

    #get file name
    metadata["file_name"] = fname 

    #get filesize
    #metadata["file_size"] = os.stat(filename).st_size 
    
    #file type
    metadata["file_type"] = "data" 

    #file format is artroot
    metadata["file_format"] = "artroot" 
    
    #file tier is rawdata
    metadata["data_tier"] = "raw"

    #detector location
    metadata["sbn_dm.detector"] = "sbn_fd"  

    #file data stream
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
    print("run_number = %d" % run_num)

    #checksum
    #checksum = SAMUtilities.adler32_crc(filename)
    #checksumstr = "enstore:%s" % checksum
    #print("Checksum = %s" % checksumstr)
    #metadata["checksum"] = [ checksumstr ]  

    #creation time
    #gmt = time.gmtime(os.stat(filename).st_mtime)
    #time_tuple =time.struct_time(gmt) #strftime("%d-%b-%Y %H:%M:%S",gmt)
    
    #metadata["sbn_dm.file_year"] = time_tuple[0] 
    #metadata["sbn_dm.file_month"] = time_tuple[1] 
    #metadata["sbn_dm.file_day"] = time_tuple[2] 
   
    # ICARUS project stage
    metadata["icarus_project.stage"] = "daq"

    try:

	# try to extract the DAQ configuration from the run history db
        # lots of info can be extracted just from config name	       
        result = offline_run_history.RunHistoryiReader().read(run_num)

        # errcode = 0 (all good), < 0 (db connection issues)
        # errcode > 0 (error count for missing fields)
        errcode, dictionary = result

        if errcode < 0:
            print("... search in pending run records db failed: %s" % errcode)
            print(dictionary['error'])
	
	    # try the run_records db instead of the pending one
            print("... trying search in run records db")
            run_records_uri = 'https://dbdata0vm.fnal.gov:9443/icarus_on_ucon_prod/app/data/run_records/configuration/key=%d'
            result = offline_run_history.RunHistoryiReader(ucondb_uri=run_records_uri).read(run_num)
            errcode, dictionary = result

            if errcode < 0:
                print('X_SAM_Metadata.py exception: %s' % dictionary['error'] )
                print(datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "Failed to connect to RunHistoryReader")
                raise



        version = dictionary['projectversion']

        metadata["icarus_project.version"] = version.rsplit()[0] #"raw_%s" % projectvers  

        metadata["icarus_project.name"] = "icarus_daq_%s" % version.rsplit()[0] #projectname

        metadata["configuration.name"] = dictionary['configuration']
        
        if "Error" in metadata["icarus_project.version"]:
            raise Exception(version)

        if "Physics"!=metadata["configuration.name"][0:7] and "Overlays"!=metadata["configuration.name"][0:8] and (metadata["data_stream"]=="offbeamnumiminbias" or metadata["data_stream"]=="offbeambnbminbias"):
            metadata["data_stream"]="offbeamminbiascalib"
	#we should be able to do the latter, but we (Ivan, Donatella, Matteo, and Wes) decided 7 Mar 2024 to not distinguish here
        #since there _could_ __potentially__ be something different
        #elif metadata["configuration.name"][0:7]=="Physics" and (metadata["data_stream"]=="offbeamnumiminbias" or metadata["data_stream"]=="offbeambnbminbias"):
	#    metadata["data_stream"]="offbeamminbias"
        
        s = dictionary['configuration'].lower()

    except KeyError as e:
        print("X_SAM_Metadata.py exception: "+str(e))
        print(datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "Missing metadata value in database")
        raise

    except Exception as e:
        print('X_SAM_Metadata.py exception: '+ str(e))
        raise    
        

    metadata["runs"] = [ [ run_num , "physics"] ] 
       
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
        metadata["icarus_project.stage"]
        metadata["configuration.name"]
        metadata["data_stream"]
        metadata["data_tier"]
    except KeyError as e:
        print("X_SAM_Metadata.py exception: "+str(e))
        print("Missing essential metadata for data selection")
        raise

    return json.dumps(metadata)
