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
    metadata["file_size"] = os.stat(filename).st_size 
    
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
    
    #beam type
    beam = "none"
    if (stream=='bnbmajority' or stream=='bnbminbias'):
       beam = "BNB"
    elif (stream=='numimajority' or stream=='numiminbias'):
       beam = "NUMI"
    metadata["sbn_dm.beam_type"] = beam

    #get run number from file name
    run_num = 0
    for part in fname.split("_"):
        if (part.find("run")==0): 
            run_num = int(part[3:])
            break
    print("run_number = %d" % run_num)

    #checksum
    checksum = SAMUtilities.adler32_crc(filename)
    checksumstr = "enstore:%s" % checksum
    print("Checksum = %s" % checksumstr)
    metadata["checksum"] = [ checksumstr ]  

    #creation time
    gmt = time.gmtime(os.stat(filename).st_mtime)
    time_tuple =time.struct_time(gmt) #strftime("%d-%b-%Y %H:%M:%S",gmt)
    
    metadata["sbn_dm.file_year"] = time_tuple[0] 
    metadata["sbn_dm.file_month"] = time_tuple[1] 
    metadata["sbn_dm.file_day"] = time_tuple[2] 
   
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

            # if failed on both cases, raise an exception!
            if errcode < 0:
                raise Exception(dictionary['error'])

        if errcode > 0:
            print("%s required field(s) not found by RunHistoryReader!" % errcode)

	# get project name and version
        version = dictionary['projectversion']
        if "Error" in version:
            raise KeyError(version)
        metadata["icarus_project.version"] = version.rsplit()[0] # "v_10_02" % projectvers  
        metadata["icarus_project.name"] = "icarus_daq_%s" % version.rsplit()[0] #projectname

	# get configuration name 
        configuration = dictionary['configuration']
        if "Error" in configuration:
            raise KeyError(configuration)
        metadata["configuration.name"] = dictionary['configuration']

	# get components in the configuration
        components = dictionary['components']
        if "Error" in components:
            raise KeyError(components)

	# get number of components per subsystem
        tpcww = SAMUtilities.count_components(components,pattern="icarustpcww")
        tpcwe = SAMUtilities.count_components(components,pattern="icarustpcwe")
        tpcew = SAMUtilities.count_components(components,pattern="icarustpcew")
        tpcee = SAMUtilities.count_components(components,pattern="icarustpcee")
        pmtww = SAMUtilities.count_components(components,pattern="icaruspmtww")
        pmtwe = SAMUtilities.count_components(components,pattern="icaruspmtwe")
        pmtew = SAMUtilities.count_components(components,pattern="icaruspmtew")
        pmtee = SAMUtilities.count_components(components,pattern="icaruspmtee")
        crttop = SAMUtilities.count_components(components,pattern="icaruscrttop") 
        crtside = SAMUtilities.count_components(components,pattern="icaruscrt0") 
        crtbttm = SAMUtilities.count_components(components,pattern="icaruscrtbottom") 
        
        metadata["icarus_components.tpc"] = tpcww+tpcwe+tpcew+tpcee
        metadata["icarus_components.tpcww"] = tpcww
        metadata["icarus_components.tpcwe"] = tpcwe
        metadata["icarus_components.tpcew"] = tpcew
        metadata["icarus_components.tpcee"] = tpcee

        metadata["icarus_components.pmt"] = pmtww+pmtwe+pmtwe+pmtee
        metadata["icarus_components.pmtww"] = pmtww
        metadata["icarus_components.pmtwe"] = pmtwe
        metadata["icarus_components.pmtew"] = pmtew
        metadata["icarus_components.pmtee"] = pmtee
        
        metadata["icarus_components.crt"] = crttop+crtside+crtbttm
        metadata["icarus_components.crttop"] = crttop
        metadata["icarus_components.crtside"] = crtside
        metadata["icarus_components.crtbttm"] = crtbttm

    except KeyError as e:
        print("X_SAM_Metadata.py exception: "+ str(e))
        print(datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "Missing metadata value in database")
        raise

    except Exception as e:
        print("X_SAM_Metadata.py exception: "+ str(e))
        print(datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "Failed to read from RunHistoryReader")
        raise    
     
    # get run type based on configuration name
    # options: physics, calibration, laser, test 
    # config names tipycally contain only one of these (except test)
    # however, if test is present, must be test  
    config = metadata['configuration.name'].lower()
    run_type = "physics"
    if("calibration" in config):
        run_type = "calibration"
    if("laser" in config):
        run_type = "laser"
    if("test" in config): #do last, priority over other choices
        run_type = "test"
    metadata["runs"] = [ [ run_num , run_type] ] 
       
    # get event count:
    fFile = TFile(filename,"READ")
    fTree = fFile.Get("Events")
    nEvents = fTree.GetEntries()
    print("Number of event in the root file %d" % nEvents)
    metadata["sbn_dm.event_count"] = nEvents

    # final consistency checks: match between configuration names and output data streams (filenames)
    # this is to alert of possible problems that may contaminate good data streams

    # If "BNB" or NUMI" are in the config name, streams must match
    # e.g: "Calibraton_MAJORITY_NUMI_*" produces only (offbeam)numimajority streams
    if ("numi" in config and "majority" in config and stream != "offbeamnumimajority" and stream != "unknown"):
        print("X_SAM_Metadata.py exception: Config '%s' contains '%s' but produced '%s'." % (config,"numi",stream))
        print("Please check filenames in EventBuilder_standard.fcl or change the configuration name!")
        print(datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "Data stream does not match configuration name.")
        raise

    if ("bnb" in config and "majority" in config and stream != "offbeambnbmajority" and stream != "unknown"):
        print("X_SAM_Metadata.py exception: Config '%s' contains '%s' but produced '%s'." % (config,"bnb",stream))
        print("Please check filenames in EventBuilder_standard.fcl or change the configuration name!")
        print(datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "Data stream does not match configuration name.")
        raise
   
    # if data_stream is "offbeamnumiminbias" or "offbeambnbminbias", file must come from Physics or Overlays configs
    # all other offbeammininumbias (coming from standard calibrations) must go to offbeamminbiascalib
    if ((stream=="offbeamnumiminbias" or stream=="offbeambnbminbias") and ("physics" not in config) and ("overlays" not in config)):
        print("X_SAM_Metadata.py exception: Config '%s' shouldn't use offbeamminbias in '%s', but 'offbeamminbiascalib'." % (config,stream))
        print("Please check filenames in EventBuilder_standard.fcl or change the configuration name!")
        print(datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "Data stream does not match configuration name.")
        raise

    # if "unknown" stream has non-zero events, event filtering and output modules are mismatched.
    if (stream=="unknown" and nEvents>0):
        print("X_SAM_Metadata.py exception: Config %s is dropping events in '%s'." % (config,stream))
        print("Please check the event filtering  and filenames in EventBuilder_standard.fcl!")
        print(datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "Non-empty 'unknown' stream file.")
        raise

    # last check before releasing metadata into the wild
    # make sure all the important fields are there
    try:
        metadata["icarus_components.tpc"]
        metadata["icarus_components.pmt"]
        metadata["icarus_components.crt"]
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
