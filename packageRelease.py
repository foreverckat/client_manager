#-*- coding=utf8 -*-
"""
Created on 2015.12.18
@author: albertcheng
# remote control script through telnet connect
# step 1: connect remote server through telnet tunnel.
# step 2: change directory to this script's path.
# step 3: run this script with arguments which is the very path of all updated files are.

# caculate crc
# upload file
# remote crc
# download data
# compare crc
"""
import hashlib
import os
import sys
import time
import telnetlib
from config import *
import ftplib 
import logging
fmt = '%(asctime)s - %(lineno)s - %(levelname)s - %(message)s'
logging.basicConfig(stream = sys.stdout ,level=logging.DEBUG,  
                    format= fmt,  
                    filename='res_tool.log',  
                    filemode='w')  
# define a handler
console = logging.StreamHandler()  
console.setLevel(logging.INFO)  
# 设置日志打印格式  
formatter = logging.Formatter(fmt)  
console.setFormatter(formatter)  
# 将定义好的console日志handler添加到root logger  
logger = logging.getLogger('')
logger.addHandler(console)



def refreshFtpSHA1(_ftpRoot, _ftp):
    
    # remote running script to make a new version file on the ftp server
    logger.info("ready to connected to telnet server.")
    _TL = telnetlib.Telnet(TL_Host)
    #_TL.set_debuglevel(2)
    _TL.read_until('login: ')
    _TL.write(TL_User + linesep)
    _TL.read_until('password: ')
    _TL.write(TL_Pawd + linesep)
    _TL.read_until(TL_finish_win32) 
    rf_path = "D:" + os.sep + "JokerFtpRoot" + _ftpRoot
    #print rf_path
    _TL.write("python remote_crc32.py  %s %s" % (rf_path, linesep))
    _TL.read_until(TL_finish_win32) 
    logger.info("telnet executing successful.")
    _TL.close()
    logger.info("telnet exited.")
    
    _ftp.DownLoadFile(VERSION_MANIFEST, verfile)
    
    
def genSHA1(_file):
    if os.path.exists(_file):
        with open(_file, "rb") as _:
            _sha1 = hashlib.sha1()
            while True:
                data = _.read(10240)
                if not data:
                    break
                _sha1.update(data)
            return _sha1.hexdigest()
    else:
        return None
    
class myFtp:
    ftp = ftplib.FTP()
    
    bIsDir = False
    path = ""
    def __init__(self, host, port='21'):
        #self.ftp.set_debuglevel(2) #打开调试级别2，显示详细信息 
        #self.ftp.set_pasv(0)      #0主动模式 1 #被动模式
        self.ftp.connect( host, port )
        
    def Login(self, user, passwd):
        self.ftp.login( user, passwd )
        logger.info("ftp connected")

    def DownLoadFile(self, LocalFile, RemoteFile):
        
        if not self.isExist(RemoteFile):
            logger.info("remote file not exists - %s" % RemoteFile)
            return False
        if os.path.exists(LocalFile):
            os.remove(LocalFile)
        with open( LocalFile, 'wb' ) as file_handler:
            self.ftp.retrbinary( "RETR %s" %( RemoteFile ), file_handler.write )
            logger.info("download file : %s" % RemoteFile) 
            return True
    
    def UpLoadFile(self, LocalFile, RemoteFile):
        def getsize(_f):
            _s = int(os.stat(_f).st_size) * 1.0
            if _s > (1024 * 1024 * 1024):
                return "%.1fGB" % _s / (1024 * 1024 * 1024)
            elif _s > (1024 * 1024):
                return "%.1fMB" % (_s / (1024 * 1024))
            elif _s > 1024:
                return "%.1fKB" % (_s / 1024)
            else:
                return "%.1fBytes" % _s
            
        if os.path.isfile( LocalFile ) == False:
            return False
        if self.uploadCheck(LocalFile, RemoteFile):
            s = getsize(LocalFile)
            with open(LocalFile, "rb") as file_handler:
                
                logger.info("uploading file: %s" % RemoteFile)
                logger.info("file size is : %s" % s)
                self.ftp.storbinary('STOR %s' % RemoteFile, file_handler, 4096)
                return True
        #else:
            #logger.info("no need to upload file - %s" % RemoteFile)
    
    def UpLoadFileTree(self, LocalDir, RemoteDir, SHAs = {}):
        if os.path.isdir(LocalDir) == False:
            return False
        LocalNames = os.listdir(LocalDir)
        _cwd = self.ftp.nlst()
        if RemoteDir not in _cwd:
            self.ftp.mkd(RemoteDir)
        self.ftp.cwd( RemoteDir )
        for Local in LocalNames:
            src = os.path.join( LocalDir, Local)
            if os.path.isdir( src ): self.UpLoadFileTree( src, Local )
            else:
                self.UpLoadFile( src, Local )
        self.ftp.cwd( ".." )
        return
    
    def DownLoadFileTree(self, LocalDir, RemoteDir):
        if os.path.isdir( LocalDir ) == False:
            os.makedirs( LocalDir )
        self.ftp.cwd( RemoteDir )
        RemoteNames = self.ftp.nlst()  
        for _f in RemoteNames:
            Local = os.path.join( LocalDir, _f )
            
            if self.isDir( _f ):
                self.DownLoadFileTree( Local, _f )                
            else:
                self.DownLoadFile( Local, _f )
        self.ftp.cwd( ".." )
        return
    
    def show(self, l):
        result = l.lower().split( " " )
        if self.path.lower() in result and "<dir>" in result:
            self.bIsDir = True
            
    def isExist(self, path):
        result = self.ftp.nlst()
        return os.path.basename(path) in result
        
        
    def check(self, l):
        self.result = l.lower().split( " " )
        
        
    
    def isDir(self, path):
        self.bIsDir = False
        self.path = path
        #this ues callback function ,that will change bIsDir value
        self.ftp.retrlines( 'LIST', self.show )
        return self.bIsDir
    
    def close(self):
        self.ftp.quit()
    
    def uploadCheck(self, _lf, _rf):
        k = _lf.replace(Local_Version + "\\", "")
        if _rf not in self.ftp.nlst():
            logger.info("*" * 20)
            logger.info("remote file not existed.")
            return True
        elif MANIFEST_SHA1 == {}:
            logger.info("*" * 20)
            logger.info("local manifest hash is empty.")
            return True
        elif k not in MANIFEST_SHA1:
            #print _lf, _rf, k
            #print MANIFEST_SHA1.keys()
            logger.info("*" * 20)
            logger.info("local manifest hash didn't contain value of %s" % k)
            return True
        else:
            
            _lf_sha1 = genSHA1(_lf)
            _rf_sha1 = MANIFEST_SHA1[k]

            if _lf_sha1 != _rf_sha1:
                self.ftp.delete(_rf)
                logger.info("*" * 60)
                logger.info("local file SHA1 : %s" % _lf_sha1)
                logger.info("remote file SHA1 : %s" % _rf_sha1)
                return True
            else:
                #logger.info("file's SHA1 value didn't changed.")
                return False
                        
def getManifestSHA1():
    with open(VERSION_MANIFEST, "rb") as _f_local:
        _fd = _f_local.readlines()
        _ftp_files = {}
        for line in _fd:
            if not line.startswith("#") and line.strip() != "":
                _line = [x.strip() for x in line.split("\t")]
                _ftp_files[_line[0].decode("gbk")] = _line[1]
    return _ftp_files    


        
if __name__ == "__main__":
    
    
    
    
    
    Local_Version = 'xgame_pc'
    verfile = "ver.manifest"
    VERSION_MANIFEST = os.path.join(Local_Version, verfile)
    if not os.path.exists(Local_Version):
        os.mkdir(Local_Version)
        
    ftp = myFtp(FTP_Host)
    ftp.Login(FTP_User, FTP_Passwd)
    ftp.ftp.cwd("/xgame_pc/latest_ver")
    ftp.DownLoadFile(VERSION_MANIFEST, verfile)
    ftp.ftp.cwd("..")
    MANIFEST_SHA1 = getManifestSHA1()
    ftp.UpLoadFileTree(Local_Version, "latest_ver")
    ftp.ftp.cwd("latest_ver")
    refreshFtpSHA1(os.sep + "xgame_pc"+ os.sep + "latest_ver" + os.sep, ftp)
    ftp.ftp.cwd("..")
    ftp.close()
    logger.info("release finished.")
    os.system("pause")



"""    
def uploadToFtp(**argus):
    def getsize(_f):
        _s = int(os.stat(_f).st_size) * 1.0
        if _s > (1024 * 1024 * 1024):
            return "%.1fGB" % _s / (1024 * 1024 * 1024)
        elif _s > (1024 * 1024):
            return "%.1fMB" % (_s / (1024 * 1024))
        elif _s > 1024:
            return "%.1fKB" % (_s / 1024)
        else:
            return "%.1fBytes" % _s
    
    def _doUpload(_f):
        if not os.path.exists(_f):
            logger.error("file - %s not exists." % _f)
            return
        with open(_f, "rb") as f:
            _f = _f.replace(FTP_LOCAL + "\\","").split("\\")
            print _f
            _ftp.storbinary("STOR " + _f, f)
        return
    logger.info("ready to uploading file.")
    _ftp = argus["ftp"]
    _upload = [(_f.decode("gbk"), genSHA1(_f)) for _f in getFiles(argus["LocalPath"])]
    
    st = time.time()
    for _file, _crc in _upload:
        logger.info("-" * 30)
        _st = time.time()
        logger.info(log_msg_31 %  (_file, getsize(_file)))
        _doUpload(_file)
        logger.info(log_msg_32 %  os.path.basename(_file))
        logger.info(log_msg_33 % (time.time() - _st))
    _ftp.close()
    logger.info(log_msg_34 % (time.time() - st))
    return _upload

#@makeFtpConn(FTP_DOWNLOAD)
#@refreshFtpSHA1(FTP_DOWNLOAD)
def compareCrc(Uploads = []):
    logger.info("ready to compare.")
    with open(VERSION_MANIFEST, "rb") as _f_local:
        _fd = _f_local.readlines()
        _ftp_files = {}
        for line in _fd:
            if not line.startswith("#") and line.strip() != "":
                _line = [x.strip() for x in line.split("\t")]
                _ftp_files[_line[0].decode("gbk")] = _line[1]
                
    sha_error = 0
    for _file, _sha1 in Uploads:
        _file = os.path.basename(_file)
        if _file not in  _ftp_files:
            sha_error += 1
            logger.error( "no file name: %s" % _file)
        elif str(_sha1).strip() != _ftp_files[_file].strip():
            sha_error += 1
            logger.error( "not correct sha1:", _sha1, "\t", _ftp_files[_file])
    logger.info("sha1 compare finished.")
    if sha_error != 0:
        logger.info("package release failed")
    else:
        logger.info("package release successful.")
        
def getFiles(path):
    
    # get all files
    
    _files = [] 
    for root, dirs, files in os.walk(path):
        for f in files:
            fpath = os.path.join(root, f)
            _files.append(fpath)
    return _files


def genSHA1(_file):
    if os.path.exists(_file):
        with open(_file, "rb") as _:
            _sha1 = hashlib.sha1()
            while True:
                data = _.read(10240)
                if not data:
                    break
                _sha1.update(data)
            return _sha1.hexdigest()
    else:
        return None
    
def getTime():
    return str(time.strftime("%y-%m-%d %H:%M:%S", time.gmtime()))

def addVersion(_json = None, content = ""):
    def _get_new_ver():
        if _json["latestVer"] == {}:
            return {
                      "ver":"0.1.1",
                      "build":1,
                      "date":getTime(),
                      "time":time.time(),
                      "content": content
                      }
        else:
            ver0, ver1, ver2 = _json["latestVer"]["ver"].split(".")
            ver_date = time.gmtime(_json["latestVer"]["time"])
            now_date = time.gmtime(time.time())
            if ver_date.tm_mon != now_date.tm_mon:ver1 = str(int(ver1) + 1)
            if ver_date.tm_wday > now_date.tm_wday:ver2 = str(int(ver2) + 1)
            return {
                      "ver":".".join([ver0, ver1, ver2]),
                      "build":_json["latestVer"]["build"] + 1,
                      "date":getTime(),
                      "time":time.time(),
                      "content": content
                      }
    if _json == None or _json == {}:
        _json = {
                 "describe":"version list",
                 "maintain_time":getTime(),
                 "latestVer":{},
                 "oldVer":{}
                 }
    new_ver = _get_new_ver()
    if new_ver != None:
        _json["latestVer"] = new_ver
        if _json["latestVer"]["ver"] not in _json["oldVer"]:
            _json["oldVer"][_json["latestVer"]["ver"]] = []
        _json["oldVer"][_json["latestVer"]["ver"]].append(new_ver)
        with open("version.list","wb") as _json_file:  
            json.dump(_json, _json_file, indent = 4)
            
def maintainVersion():
    version_list = "version.list"
    if not os.path.exists(version_list):
        with open("version.list","wb") as _json_file:  
            json.dump({}, _json_file)
    with open("version.list","rb") as _json_file:  
        _json = json.load(_json_file)
    addVersion(_json)
    
    
def release():
    Uploads = uploadToFtp(LocalPath = FTP_LOCAL)
    compareCrc(Uploads = uploadToFtp(LocalPath = FTP_LOCAL))
    
    
if __name__ == "__main__":
    release()
"""