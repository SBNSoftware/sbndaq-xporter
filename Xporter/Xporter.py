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
import time
import shutil
import glob

#import psycopg2 # Get database functions

import dbvariables # get conn and cur
import X_SAM_metadata
import X_xml_db_fill
import filelock
import safe
import subprocess

#print Xporter script usage and exit
def print_usage():
    print('Command: python Xporter.py <data directory> <dropbox directory> <"dev"/"prod"/"none"> <project version> <project name>')
    sys.exit(1)

#parse directory names, check if there
#if so, reutrn updated/parsed name
#if not, return empty string
def parse_dir(dirname):
    try:
        os.chdir(dirname)
        if (dirname[len(dirname)-1] != "/"): dirname=dirname+"/"
        return dirname
    except:
        print("Directory: ", dirname, "not found")
        return ""
    
#parse commandline inputs
def parse_cmdline_inputs(args):
    print(args)
    if (not(len(args)==3 or len(args)==4 or len(args)==5 or len(args)==6)):
        print(len(args))
        print_usage()

    datadir = parse_dir(sys.argv[1])
    if(datadir==""): sys.exit(1)

    dropboxdir = parse_dir(sys.argv[2])
    if(dropboxdir==""): sys.exit(1)

    runconfigdb = ""
    if ((len(sys.argv) >= 4 and sys.argv[3]=="none") or len(sys.argv)==3):
        runconfigdb = "none"
    elif(sys.argv[3]=="dev"):
        runconfigdb="dev"
    elif(sys.argv[3]=="prod"):
        runconfigdb="prod"
    else:
        print_usage()

    projver = ""
    if ((len(sys.argv) <= 4 )):
        projver = "artdaq-3.07.01"
    else:
        projver = sys.argv[4]

    projname = ""
    if ((len(sys.argv) <= 5 )):
        projname = "DAQDL_testdata"
    else:
        projname = sys.argv[5]

    return datadir,dropboxdir,runconfigdb,projver,projname


#connect to runconfig database
#return 0 if ok
def connect_to_runconfigdb(dbname):

    if(dbname=="none"):
        print("Not connectiong to a RunConfigDB")
        return 0

    elif(dbname=="dev"):
        print("Connecting to development RunConfigDB...")
        #dbvariables.conn = psycopg2.connect(database="lariat_dev", user="randy", host="ifdbdev", port="5441")
        #dbvariables.cur=dbvariables.conn.cursor()
        return 0

    elif(dbname=="prod"):
        print("Connecting to production RunConfigDB...")

        #ntry = 0
        #nodbconnection = True
        #while nodbconnection:
            #try:
                #dbvariables.conn = psycopg2.connect(database="lariat_prd", user="lariatdataxport", password="lariatdataxport_321", host="ifdbprod2", port="5443")
                #dbvariables.cur=dbvariables.conn.cursor()
                #nodbconnection = False
            #except:
                #ntry +=1
                #if (ntry % 5 == 1): print "Failed to make lariat_prd connection for",ntry,"times... sleep for 5 minutes"
                #time.sleep(300)
        return 0

    else:
        print("Unknown RunConfigDB name: %s" % dbname)
        return -1;

def obtain_lock(lockname,timeout=5,retries=2):
    lock = filelock.FileLock(lockname+"FileLock")
    ntry=0
    while ntry<=retries:
        try: 
            lock.acquire(timeout=timeout)
            break
        except filelock.Timeout as err:
            print("Could not obtain file lock. Exiting.")
        ntry+=1

    if ntry>retries:
        print("Never obtained lock %s after %d tries" % (lockname,ntry))
        sys.exit(1)

    return lock

def get_finished_files(dirname,file_pattern="*.root"):
    return glob.glob(dirname+"/"+file_pattern)

#move files, and return the number moved
def move_files(files,destdir,moveFile):
    
    moved_files=0
    for f in files:
        fname = f.split("/")[-1]
        print("Will move/copy %s to %s" % (f,destdir+fname))

        if(len(glob.glob(dropboxdir+fname))>0):
            print("File %s already in %s" % (fname,destdir))
            continue

        if(not moveFile):
            shutil.copy2(f,destdir+fname) #copy2 to try to preserve timestamps
            os.chmod(destdir+fname,
                     stat.S_IRUSR | stat.S_IWUSR | stat.S_IRGRP | stat.S_IROTH) #only user write. Rely on manual file cleanup.
#                     stat.S_IRUSR | stat.S_IWUSR | stat.S_IRGRP | stat.S_IWGRP | stat.S_IROTH) #give write permissions to group
        else:
            shutil.move(f,destdir+fname)
            os.chmod(destdir+fname,
                     stat.S_IRUSR | stat.S_IWUSR | stat.S_IRGRP | stat.S_IROTH) #only user write. Rely on manual file cleanup.
#                     stat.S_IRUSR | stat.S_IWUSR | stat.S_IRGRP | stat.S_IWGRP | stat.S_IROTH) #give write permissions to group
        moved_files+=1

    return moved_files

def write_metadata_files(files,pv,pn):

    n_json_written = 0
    for f in files:
        metadata_fname = f+".json"
        if(len(glob.glob(metadata_fname))>0):
            print("JSON file for %s already exists." % f)
            continue

        try:
            metadata_json = X_SAM_metadata.SAM_metadata(f,pv,pn)
            print(metadata_json)
        except:
            print("ERROR Creating Metadata for file %s" % f)
            continue

        print(metadata_fname)
        with open(metadata_fname,"w") as outfile:
            outfile.write(metadata_json)
            os.chmod(metadata_fname,
                     stat.S_IRUSR | stat.S_IWUSR | stat.S_IRGRP | stat.S_IROTH) #only user write. Rely on manual file cleanup.
#                     stat.S_IRUSR | stat.S_IWUSR | stat.S_IRGRP | stat.S_IWGRP | stat.S_IROTH) #give write permissions to group

        n_json_written+=1
    return n_json_written

#
# Get directory of Xporter.py
#
Xporterdir = os.path.dirname(os.path.abspath(__file__))

#parse commandline inputs
#datadir,dropboxdir,runconfigdb = parse_cmdline_inputs(sys.argv) # new
datadir,dropboxdir,runconfigdb,projver,projname = parse_cmdline_inputs(sys.argv)

#print("Data dir=%s, Dropbox dir=%s, RunConfigDB=%s" % (datadir,dropboxdir,runconfigdb))
print("Data dir=%s, Dropbox dir=%s, RunConfigDB=%s, Project version=%s, Project name=%s" % (datadir,dropboxdir,runconfigdb,projver,projname))

#connect to runconfigdb
if(connect_to_runconfigdb(runconfigdb)!=0): 
    print("Connecting to RunConfigDB %s failed." % runconfigdb)
    sys.exit(1)

#  check for file lock
lock = obtain_lock(datadir+"XporterInProgress")

# CHANGE ME AT PRODUCTION!
# for now, just do one tenth of files
# also for now, just copy to output directory...
file_match_str = "data*_run*_*.root"
moveFile = True

#get list of finished files
files = get_finished_files(datadir,file_match_str)

print("Found %d files in data dir" % len(files))
for f in files:
    print("\t%s" % f.split("/")[-1])
    
#for each file, move/copy it to the dropbox
n_moved_files = move_files(files,dropboxdir,moveFile=moveFile)
print("Moved %d / %d files" % (n_moved_files,len(files)))

dropbox_files = get_finished_files(dropboxdir,file_match_str)
print("Found %d files in dropbox" % len(dropbox_files))
for f in files:
    print("\t%s" % f.split("/")[-1])

n_json_files_written = write_metadata_files(dropbox_files,projver,projname)
print("Wrote %d / %d metadata files" % (n_json_files_written,len(dropbox_files)))

#exit
lock.release()
sys.exit(0)

