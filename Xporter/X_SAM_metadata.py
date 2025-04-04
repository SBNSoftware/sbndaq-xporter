#import modules
import os
import time
import SAMUtilities
import json
import logging
import offline_run_history
from ROOT import TFile

#
# Begin SAM metadata function:
# builds file metadata starting from file name
# and DAQ configuration stored in run history db
#

def SAM_metadata(filename):
    "Subroutine to write out SAM information"
    
    metadata = {}
    fname = filename.split("/")[-1]
    
    logging.info("Preparing metadata for %s" % (fname))   

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
    logging.info("data_stream = '%s'"%stream)
    metadata["data_stream"] = stream  
    
    #beam type
    beam = "none"
    if (stream=='bnbmajority' or stream=='bnbminbias'):
       beam = "BNB"
    elif (stream=='numimajority' or stream=='numiminbias'):
       beam = "NUMI"
    elif (stream=='unknown'):
       beam = "unknown"
    metadata["sbn_dm.beam_type"] = beam

    #get run number from file name
    run_num = 0
    for part in fname.split("_"):
        if (part.find("run")==0): 
            run_num = int(part[3:])
            break
    logging.info("run_number = %d" % run_num)

    #checksum
    checksum = SAMUtilities.adler32_crc(filename)
    checksumstr = "enstore:%s" % checksum
    logging.info("Checksum = %s" % checksumstr)
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
            logging.warning("... search in pending run records db failed: %s" % errcode)
            logging.warning(dictionary['error'])
	
	        # try the run_records db instead of the pending one
            logging.warning("... trying search in run records db")
            run_records_uri = 'https://dbdata0vm.fnal.gov:9443/icarus_on_ucon_prod/app/data/run_records/configuration/key=%d'
            result = offline_run_history.RunHistoryiReader(ucondb_uri=run_records_uri).read(run_num)
            errcode, dictionary = result

            # if failed on both cases, raise an exception!
            if errcode < 0:
                raise Exception(dictionary['error'])

        if errcode > 0:
            logging.error("%s required field(s) not found by RunHistoryReader!" % errcode)

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
        #tpc = SAMUtilities.count_components(components,pattern="icarustpc")
        #pmt = SAMUtilities.count_components(components,pattern="icaruspmt")
        #crt = SAMUtilities.count_components(components,pattern="icaruscrt")     
        #metadata["icarus_components.tpc"] = tpc
        #metadata["icarus_components.pmt"] = pmt
        #metadata["icarus_components.crt"] = crt

    except KeyError as e:
        logging.error("X_SAM_Metadata.py exception: "+ str(e))
        logging.error("Missing metadata value in database")
        raise

    except Exception as e:
        logging.error("X_SAM_Metadata.py exception: "+ str(e))
        logging.error("Failed to read from RunHistoryReader")
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
    logging.info("Number of event in the root file %d" % nEvents)
    metadata["sbn_dm.event_count"] = nEvents

    # final consistency checks: match between configuration names and output data streams (filenames)
    # this is to alert of possible problems that may contaminate good data streams

    # If "BNB" or NUMI" are in the config name, streams must match
    # e.g: "Calibraton_MAJORITY_NUMI_*" produces only (offbeam)numimajority streams
    if ("numi" in config and "majority" in config and stream != "offbeamnumimajority" and stream != "unknown"):
        logging.error("X_SAM_Metadata.py exception: Config '%s' contains '%s' but produced '%s'." % (config,"numi",stream))
        logging.error("Please check filenames in EventBuilder_standard.fcl or change the configuration name!")
        logging.error("Data stream does not match configuration name.")
        raise

    if ("bnb" in config and "majority" in config and stream != "offbeambnbmajority" and stream != "unknown"):
        logging.error("X_SAM_Metadata.py exception: Config '%s' contains '%s' but produced '%s'." % (config,"bnb",stream))
        logging.error("Please check filenames in EventBuilder_standard.fcl or change the configuration name!")
        logging.error("Data stream does not match configuration name.")
        raise
   
    # if data_stream is "offbeamnumiminbias" or "offbeambnbminbias", file must come from Physics or Overlays configs
    # all other offbeammininumbias (coming from standard calibrations) must go to offbeamminbiascalib
    if ((stream=="offbeamnumiminbias" or stream=="offbeambnbminbias") and ("physics" not in config) and ("overlays" not in config)):
        logging.error("X_SAM_Metadata.py exception: Config '%s' shouldn't use offbeamminbias in '%s', but 'offbeamminbiascalib'." % (config,stream))
        logging.error("Please check filenames in EventBuilder_standard.fcl or change the configuration name!")
        logging.error("Data stream does not match configuration name.")
        raise

    # if "unknown" stream has non-zero events, event filtering and output modules are mismatched.
    if (stream=="unknown" and nEvents>0):
        logging.error("X_SAM_Metadata.py exception: Config %s is dropping events in '%s'." % (config,stream))
        logging.error("Please check the event filtering  and filenames in EventBuilder_standard.fcl!")
        logging.error("Non-empty 'unknown' stream file.")
        raise

    # last check before releasing metadata into the wild
    # make sure all the important fields are there
    try:
        #metadata["icarus_components.tpc"]
        #metadata["icarus_components.pmt"]
        #metadata["icarus_components.crt"]
        metadata["icarus_project.version"]
        metadata["icarus_project.name"]
        metadata["icarus_project.stage"]
        metadata["configuration.name"]
        metadata["data_stream"]
        metadata["data_tier"]
    except KeyError as e:
        logging.error("X_SAM_Metadata.py exception: "+str(e))
        logging.error("Missing essential metadata for data selection")
        raise

    return json.dumps(metadata)
