#
# Various support functions to make SAM files
#

import sys
from zlib import adler32
import time

# Calculate Adler-32 checksum
def adler32_crc(filename):
    "Calculate checksum for file filename)"

    BLOCKSIZE = 1024*1024
    crc = 0
    with open(filename,"rb") as f:
        while True:
            data = f.read(BLOCKSIZE)
            if not data:
                break
            crc = adler32(data,crc)
    #crc=int(crc)
    if crc < 0:
        crc = ( crc & 0x7FFFFFFF) | 0x80000000
    return str(crc)

# Make properly formatted date
def timestring(tt):
    " Output a time string that is to SAM's liking"
    gmt = time.gmtime(tt)
    timestr = time.strftime("%d-%b-%Y %H:%M:%S",gmt)
    return timestr

# Count configuration components matching pattern
def count_components(components, pattern):
    " Count the number of DAQ components matching name pattern"
    sanitized_list = components.lstrip("[").rstrip("]").split(",")
    counter=0
    for c in sanitized_list:
        if pattern in c:
            counter+=1
    return counter
