#  Usage: python Xporter.py <data directory> <dropbox directory>
#
# program to:
#       1) Check to see if there are new files and if there are:
#       2) update run configuration database
#       3) create the SAM metadata file
#       4) move the data file to the dropbox
#

# import modules
import sys
import os, stat
import shutil
import glob
import logging
import X_SAM_metadata
import filelock

# temporary logger (until log filepath is parsed)
# goes to stdout, which must be captured
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

# print Xporter script usage and exit
def print_usage():
    logging.info('Command: python Xporter.py <data directory> <dropbox directory> <log filepath>')
    sys.exit(1)

# parse directory names, check if there
# if so, return updated/parsed name
# if not, return empty string
def parse_dir(dirname):
    try:
        os.chdir(dirname)
        if (dirname[len(dirname)-1] != "/"): dirname=dirname+"/"
        return dirname
    except:
        logging.error("Directory: ", dirname, "not found")
        return ""
    
# parse file path, check if there
# if not, return empty string
def parse_path(filepath):
    dirpath = os.path.dirname(os.path.abspath(filepath))
    if os.path.isdir(dirpath):
        return os.path.abspath(filepath)
    else:
        logging.error("Directory: ", dirpath, "not found")
        return ""

# parse commandline inputs
def parse_cmdline_inputs(args):
    
    if (not(len(args)==2 or len(args)==3 or len(args)==4)):
        print(len(args))
        print_usage()

    datadir = parse_dir(sys.argv[1])
    if(datadir==""): sys.exit(1)

    dropboxdir = parse_dir(sys.argv[2])
    if(dropboxdir==""): sys.exit(1)

    logpath = parse_path(sys.argv[3])
    if(logpath==""): sys.exit(1)

    return datadir,dropboxdir,logpath

# Get a lock to avoid multiple processes running at the same time
# if lock already in place, exit
def obtain_lock(lockname,timeout=5,retries=2):

    lock = filelock.FileLock(lockname+"FileLock")
    ntry=0
    while ntry<=retries:
        try: 
            lock.acquire(timeout=timeout)
            break
        except filelock.Timeout as err:
            logging.warning("Could not obtain file lock. Exiting.")
        ntry+=1

    if ntry>retries:
        logging.error("Never obtained lock %s after %d tries" % (lockname,ntry))
        sys.exit(1)

    return lock

# Get list of files produced by the DAQ
def get_finished_files(dirname,file_pattern="*.root"):
    return glob.glob(dirname+"/"+file_pattern)

# Move files from the data directory to the dropbox directory,
# and return the number moved
def move_files(files,destdir,moveFile):
    
    moved_files=0
    for f in files:
        fname = f.split("/")[-1]
        logging.info("Will move/copy %s to %s" % (f,destdir+fname))

        if(len(glob.glob(destdir+fname))>0):
            logging.info("File %s already in %s" % (fname,destdir))
            continue

        if(not moveFile):
            shutil.copy2(f,destdir+fname) #copy2 to try to preserve timestamps
            os.chmod(destdir+fname,
                     stat.S_IRUSR | stat.S_IWUSR | stat.S_IRGRP | stat.S_IROTH) #only user write. Rely on manual file cleanup.
                     #stat.S_IRUSR | stat.S_IWUSR | stat.S_IRGRP | stat.S_IWGRP | stat.S_IROTH) #give write permissions to group
        else:
            shutil.move(f,destdir+fname)
            os.chmod(destdir+fname,
                     stat.S_IRUSR | stat.S_IWUSR | stat.S_IRGRP | stat.S_IROTH) #only user write. Rely on manual file cleanup.
                     #stat.S_IRUSR | stat.S_IWUSR | stat.S_IRGRP | stat.S_IWGRP | stat.S_IROTH) #give write permissions to group
        moved_files+=1

    return moved_files

# Build metadata json file
def write_metadata_files(files):

    n_json_written = 0
    for f in files:
        metadata_fname = f+".json"
        if(len(glob.glob(metadata_fname))>0):
            logging.info("JSON file for %s already exists." % f)
            continue

        try:
            metadata_json = X_SAM_metadata.SAM_metadata(f)
            logging.info(metadata_json)
        except:
            logging.error("Creating Metadata for file %s" % f)
            continue

        print(metadata_fname)
        with open(metadata_fname,"w") as outfile:
            outfile.write(metadata_json)
            os.chmod(metadata_fname,
                     stat.S_IRUSR | stat.S_IWUSR | stat.S_IRGRP | stat.S_IROTH) #only user write. Rely on manual file cleanup.
                     #stat.S_IRUSR | stat.S_IWUSR | stat.S_IRGRP | stat.S_IWGRP | stat.S_IROTH) #give write permissions to group

        n_json_written+=1
    return n_json_written


def main():

    logging.info("Running Xporter.py")

    # parse commandline inputs
    datadir,dropboxdir,logpath = parse_cmdline_inputs(sys.argv)

    logging.shutdown()  # close any existing logging
    logging.basicConfig(
        filename=logpath,
        level=logging.INFO,
        format="%(asctime)s - [%(levelname)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S")
    logging.info("Data dir=%s, Dropbox dir=%s, Logfile path=%s" % (datadir,dropboxdir,logpath))

    # check for file lock
    lock = obtain_lock(datadir+"XporterInProgress")

    # get list of finished files from data directory
    # moving the files, instead of copying them
    file_match_str = "data*_run*_*.root"
    moveFile = True
    files = get_finished_files(datadir,file_match_str)

    logging.info("Found %d files in data dir" % len(files))
    for f in files:
        logging.info("\t%s" % f.split("/")[-1])
    
    #for each file, move/copy it to the dropbox
    n_moved_files = move_files(files,dropboxdir,moveFile=moveFile)
    logging.info("Moved %d / %d files" % (n_moved_files,len(files)))

    dropbox_files = get_finished_files(dropboxdir,file_match_str)
    logging.info("Found %d files in dropbox" % len(dropbox_files))
    for f in files:
        logging.info("\t%s" % f.split("/")[-1])

    n_json_files_written = write_metadata_files(dropbox_files)
    logging.info("Wrote %d / %d metadata files" % (n_json_files_written,len(dropbox_files)))

    #exit
    lock.release()
    sys.exit(0)


if __name__=="__main__":
     main()
