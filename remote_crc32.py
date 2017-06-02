#-*- coding=utf8 -*-
"""
Created on 2015.12.18
@author: albertcheng
# remote control script through telnet connect
# step 1: connect remote server through telnet tunnel.
# step 2: change directory to this script's path.
# step 3: run this script with arguments which is the very path of all updated files are.
"""
import binascii
import os
import sys
import time
def getFiles(path):
    """
    # get all files
    """
    _files = [] 
    for root, dirs, files in os.walk(path):
        for f in files:
            fpath = os.path.join(root, f)
            _files.append(fpath)
    return _files

def genCRC32(_file):
    """
    get crc32 code of specific file 
    """
    if os.path.exists(_file):
        with open(_file, "rb") as _:
            data = _.read()
            return binascii.crc32(data) & 0xFFFFFFFF
    else:
        return None
    
def getArgus():
    if len(sys.argv) != 2:
        print "error"
        return None
    else:
        _path = sys.argv[1]
        verfile = os.path.join(_path, "ver.manifest")
        if os.path.exists(verfile):os.remove(verfile)
        crc_list = [(_file.replace(_path, ""), genCRC32(_file))for _file in getFiles(_path)]
        crc_stream = "# x-game resource list\r\n# updateTime: %s\r\n\r\n" % int(time.time())
        for _info in crc_list:
            crc_stream += "%s\t%s\r\n" % _info
        with open(verfile, "wb") as _verfile:
            _verfile.write(crc_stream)
        return crc_list
    
if __name__ == "__main__":
    getArgus()
            