#-*- coding=utf-8 -*-
'''
Created on 2015-10-30

@author: albertcheng
'''
import config

import os
import wx

import threading
import subprocess
thread_lock = threading.Lock()
import time
import ftplib

Local_Version = 'xgame_pc'
verfile = "ver.manifest"
VERSION_MANIFEST = os.path.join(Local_Version, verfile)
if not os.path.exists(Local_Version):
    os.mkdir(Local_Version)
    
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
        self.logger.AppendText("ftp connected")

    def DownLoadFile(self, LocalFile, RemoteFile):
        
        if not self.isExist(RemoteFile):
            self.logger.AppendText("remote file not exists - %s" % RemoteFile)
            return False
        if os.path.exists(LocalFile):
            os.remove(LocalFile)
        with open( LocalFile, 'wb' ) as file_handler:
            self.ftp.retrbinary( "RETR %s" %( RemoteFile ), file_handler.write )
            self.logger.AppendText("download file : %s" % RemoteFile) 
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
                
                self.logger.AppendText("uploading file: %s" % RemoteFile)
                self.logger.AppendText("file size is : %s" % s)
                self.ftp.storbinary('STOR %s' % RemoteFile, file_handler, 4096)
                return True
        #else:
            #self.logger.AppendText("no need to upload file - %s" % RemoteFile)
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
            self.logger.AppendText("*" * 20)
            self.logger.AppendText("remote file not existed.")
            return True
        elif MANIFEST_SHA1 == {}:
            self.logger.AppendText("*" * 60)
            self.logger.AppendText("local manifest hash is empty.")
            return True
        elif k not in MANIFEST_SHA1:
            #print _lf, _rf, k
            #print MANIFEST_SHA1.keys()
            self.logger.AppendText("*" * 60)
            self.logger.AppendText("local manifest hash didn't contain value of %s" % k)
            return True
        else:
            
            _lf_sha1 = genSHA1(_lf)
            _rf_sha1 = MANIFEST_SHA1[k]

            if _lf_sha1 != _rf_sha1:
                self.ftp.delete(_rf)
                self.logger.AppendText("*" * 60)
                self.logger.AppendText("local file SHA1 : %s" % _lf_sha1)
                self.logger.AppendText("remote file SHA1 : %s" % _rf_sha1)
                return True
            else:
                #self.logger.AppendText("file's SHA1 value didn't changed.")
                return False
            
class ExamplePanel(wx.Frame):
    def __init__(self):
        global thread_lock
        self.tFlag = False
        wx.Frame.__init__(self, None, -1, config.Label_Caption, size = (305, 450), style =  wx.CAPTION | wx.CLOSE_BOX)
        self.panel = wx.Panel(self, -1)
        self.logger = wx.TextCtrl(self.panel, pos=(10,170), size=(290,250), style = wx.TE_MULTILINE)

        # Add buttons
        self.button_config =wx.Button(self.panel, label= config.Label_Config, pos=(150, 5))
        self.button_launch =wx.Button(self.panel, label= config.Label_Launch, pos=(200, 125))
        self.button_AutoUpdate =wx.Button(self.panel, label= config.Label_AutoUpdate, pos=(20, 125))
        self.button_STOPAutoUpdate =wx.Button(self.panel, label= config.Label_StopAutoUpdate, pos=(20, 125))
        self.button_OpenFolder =wx.Button(self.panel, label= config.Label_OpenFolder, pos=(110, 125))
        self.Bind(wx.EVT_BUTTON, self.OnClick_config, self.button_config)
        self.Bind(wx.EVT_BUTTON, self.OnClick_launch, self.button_launch)
        self.Bind(wx.EVT_BUTTON, self.OnClick_OpenDir, self.button_OpenFolder)
        
        
        self.Bind(wx.EVT_BUTTON, self.OnClick_AutoUpdate, self.button_AutoUpdate)
        self.Bind(wx.EVT_BUTTON, self.OnClick_StopUpdate, self.button_STOPAutoUpdate)
        self.button_AutoUpdate.Show(True)
        self.button_STOPAutoUpdate.Show(False)
        
        self.Check_version = wx.CheckBox(self.panel, label= config.Label_Check, pos=(20,15))
        self.Bind(wx.EVT_CHECKBOX, self.EvtCheckBox, self.Check_version)
        
        self.ipLabel = wx.StaticText(self.panel, label= config.Label_IPChoice, pos=(20, 45))
        self.ipEdit = wx.ComboBox(self.panel, pos=(150, 45), size=(140, -1), choices=[], style=wx.CB_DROPDOWN|wx.CB_READONLY)
        self.Bind(wx.EVT_COMBOBOX, self.EvtComboBox_IP, self.ipEdit)
        
        
        self.verLabel = wx.StaticText(self.panel, label = config.Label_VerChoice, pos = (20, 85))
        self.verEdit  = wx.ComboBox(self.panel, pos=(150, 85), size=(140, -1), choices=[], style=wx.CB_DROPDOWN|wx.CB_READONLY)
        self.Bind(wx.EVT_COMBOBOX, self.EvtComboBox_VER, self.verEdit)
        
        self.s_thread = threading.Thread(target = self.makeSamba)
        self.s_thread.start()
        
    def initArgs(self):
        self.Check_version.SetValue(True)#是否检查版本，暂时没用的控件
        
        
        """
        # 处理ip_edit控件的数据
        """
        self.ip_srvList = []
        self.ip_nameList = []
        self.localcfg()# init self.cfg
        
        for n in config.RES_SERVER:
            srv, name = n.split("|")
            self.ip_srvList.append(srv)
            self.ip_nameList.append(name)
        
        self.ipEdit.SetItems(self.ip_nameList) # 设置服务器的选项，后期不用改
        
        
        if "ipEdit_idx" in self.cfg and int(self.cfg["ipEdit_idx"]) <= len(config.Label_IPChoice):
            self.ipEdit.SetSelection(int(self.cfg["ipEdit_idx"]))
            self.res_IP = self.ip_srvList[int(self.cfg["ipEdit_idx"])]
        else:
            self.ipEdit.SetSelection(0)
            self.res_IP = self.ip_srvList[0]#默认配置，肯定存在有值
            
        self.loadVerList()
        
    
    
    def makeSamba(self):
        def conn():
            try:
                #创立samba连接对象
                self.samba = SMBConnection(config.SMB_ACCOUNT, config.SMB_PASSWD, config.SMB_CLIENT,  config.SMB_SERVER, config.SMB_DOMAIN,  use_ntlm_v2 = True, sign_options=2)
                #进行连接并检查是否成功
                assert self.samba.connect(config.SMB_HOST_IP, 139)
            except:
                self.logger.AppendText(config.outlog_1)
        
        self.sambaFlag = True
        conn()
        self.initArgs()
        while self.sambaFlag:
            if hasattr(self, "d_thread") and not self.d_thread.isAlive():
                try:
                    data = self.samba.echo("1", 10)
                except:
                    self.samba.close()
                    conn()
                    self.logger.AppendText(config.outlog_22)
                
            time.sleep(10)
        self.samba.close()
        
    def localcfg(self):
        self.cfg = {}
        try:
            with open("config.ini", "rb") as F:
                fd = F.readlines()
                for line in fd:
                    k,v = line.split("=")
                    self.cfg[k.strip()] = int(v)
        except:
            with open("config.ini", "wb") as F:
                F.write("")
                
    def loadVerList(self):
        """
        # 处理ver_edit控件的相关数据
        """
        self.verList = {}
        for x in self.samba.listPath(config.SMB_ROOT , config.SMB_VERPATH):
            if x.filename not in [".", ".."]:
                self.verList[x.filename] = x
        self.verNameList = self.verList.keys()
        self.verNameList.sort(key = lambda tfile : self.verList[tfile].last_write_time)
        try:
            #检查指定的版本库，并过滤，选择最新的版本所在地址
            self.verList = {}
            for x in self.samba.listPath(config.SMB_ROOT , config.SMB_VERPATH):
                if x.filename not in [".", ".."]:
                    self.verList[x.filename] = x
            self.verNameList = self.verList.keys()
            self.verNameList.sort(key = lambda tfile : self.verList[tfile].last_write_time)
            self.logger.AppendText(config.outlog_24)
            
        except:
            self.verNameList = []
            self.logger.AppendText(config.outlog_2)
        print self.verNameList
        if len(self.verNameList) > 0:
            self.verEdit.SetItems(self.verNameList)
            if "verEdit_idx" in self.cfg and int(self.cfg["verEdit_idx"]) <= len(self.verNameList):
                self.verEdit.SetSelection(int(self.cfg["verEdit_idx"]))
                self.ver_pathName = self.verNameList[int(self.cfg["verEdit_idx"])]
            else:
                self.verEdit.SetSelection(len(self.verNameList) - 1)
                self.ver_pathName = self.verNameList[len(self.verNameList) - 1]
            self.logger.AppendText(config.outlog_20)
            
    def EvtComboBox_IP(self, event):
        self.res_IP = self.ip_srvList[event.GetSelection()]
        self.logger.AppendText(config.outlog_3 % (event.GetString() , self.res_IP))
        self.addNewLine()
        #self.modifyResConfig(self.findf(config.SMB_SAVETO + "/" + self.ver_pathName, "Configuration.txt"))
    
    
    def OnClick_OpenDir(self, event):
        if hasattr(self, "d_thread") and self.d_thread.isAlive():
            wx.MessageBox(config.outlog_23, config.Label_MSGBOX, wx.OK|wx.ICON_INFORMATION)
        else:
            open_path = os.path.join(config.SMB_SAVETO, self.ver_pathName)
            if os.path.exists(open_path):
                os.system("start %s" % open_path)
            else:
                wx.MessageBox(config.outlog_21, config.Label_MSGBOX, wx.OK|wx.ICON_INFORMATION)
                
        
    def EvtComboBox_VER(self, event):
        self.logger.AppendText(config.outlog_4 % event.GetString())
        self.ver_pathName = event.GetString()
        self.addNewLine()
        
    def OnClick_config(self,event):
        #self.logger.AppendText(config.outlog_5)
        if hasattr(self, "d_thread") and self.d_thread.isAlive():
            wx.MessageBox(config.outlog_23, config.Label_MSGBOX, wx.OK|wx.ICON_INFORMATION)
        else:
            self.loadVerList()
            self.addNewLine()
            self.verEdit.SetSelection(len(self.verEdit.GetItems()) - 1)
            self.ver_pathName = self.verNameList[len(self.verNameList) - 1]
        
        
    def OnClick_launch(self,event):
        if hasattr(self, "d_thread") and self.d_thread.isAlive():
            wx.MessageBox(config.outlog_23, config.Label_MSGBOX, wx.OK|wx.ICON_INFORMATION)
        else:
            self.logger.AppendText(config.outlog_6)
            self.addNewLine()
            launch_client = config.SMB_SAVETO + "/" + self.ver_pathName
            self.logger.AppendText(config.outlog_7 % self.res_IP)
            self.logger.AppendText(config.outlog_8 % self.ver_pathName)
            self.logger.AppendText(launch_client + "\n")
            self.addNewLine()
            
            if not os.path.exists(launch_client):
                self.logger.AppendText(config.outlog_9)
                self.OnClick_AutoUpdate(event)
            else:
                self.modifyResConfig(self.findf(config.SMB_SAVETO + "/" + self.ver_pathName, "Configuration.txt"))
                self.doLaunch()
        
    def doLaunch(self):
        with open("config.ini", "wb") as F:
            cfg_content = "verEdit_idx = %s\nipEdit_idx = %s\n" % (self.verEdit.GetSelection(), self.ipEdit.GetSelection())
            F.write(cfg_content)
            print cfg_content
        try:
            self.modifyResConfig(self.findf(config.SMB_SAVETO + "/" + self.ver_pathName, "Configuration.txt"))
        except:
            self.logger.AppendText(config.outlog_25)
        client_path = config.SMB_SAVETO + "/" + self.ver_pathName
        client_files = [x for x in os.listdir(client_path) if ".exe" in x]
        if len(client_files) >= 1:
            launch_client = os.path.join(client_path, client_files[0])
            self.l_thread = threading.Thread(target=self.exeThread, args=([launch_client,], ))
            self.l_thread.start()
        else:
            self.logger.AppendText(config.outlog_27)
            
            
            
    def exeThread(self,args):
        p = subprocess.Popen(args, shell = False)
        p.wait()
        
        
    def modifyResConfig(self, cfg, ):
        
        with open(cfg, "rb") as f:
            fd = f.readlines()
            for line in fd:
                if "default_update_ip" in line:
                    newline = "default_update_ip=%s" % self.res_IP
                    fd.remove(line)
                    fd.append(newline)
        with open(cfg, "wb") as f:
            f.write("".join(fd))
        
    def findf(self, dist, sfile): 
        for root, dirs, files in os.walk(dist):
            for f in files:
                if f == sfile:
                    return os.path.join(root, f)
        return None
    
    def EvtCheckBox(self, event):
        self.logger.AppendText(config.outlog_10)
        self.addNewLine()
    
    def OnClick_AutoUpdate(self, event):
        """
        # 独立线程进行下载
        """
        
        
        if self.ver_pathName not in self.verList:
            self.logger.AppendText(config.outlog_12)
            return
        # 获取samba的对象
        download_Ver = self.verList[self.ver_pathName]
        # 对samba路径进行遍历
        dfl = self.getFiles(config.SMB_VERPATH + "/" + download_Ver.filename, [])
        # 生成本地的存储路径（任意一个文件）
        verSaveTo = os.path.join(config.SMB_SAVETO, download_Ver.filename)#dfl[0].replace(config.SMB_VERPATH, "")
        
        self.logger.AppendText(config.outlog_11 + download_Ver.filename + "\n")
        self.addNewLine()
        
        if len(dfl) > 0 and os.path.exists(verSaveTo):
            retCode = wx.MessageBox(config.outlog_17, config.Label_MSGBOX, wx.YES_NO|wx.ICON_INFORMATION)
        else:
            retCode = 2
            
        if retCode == wx.ID_YES or retCode == 2:
            self.logger.AppendText(config.outlog_13 % len(dfl))
            self.tFlag = True
            self.d_thread = threading.Thread(target=self.threadDownload, args=(dfl, ))
            self.d_thread.start()
            
            self.button_AutoUpdate.Show(False)
            self.button_STOPAutoUpdate.Show(True)
            
        else:
            
            self.logger.AppendText(config.outlog_18)
            self.addNewLine()
            
    def OnClick_StopUpdate(self, event):
        self.tFlag = False
        while not self.d_thread.isAlive():
            break
        self.button_AutoUpdate.Show(True)
        self.button_STOPAutoUpdate.Show(False)
        
    def threadDownload(self, dfl):
        
        st = time.time()
        for nfile in dfl:
            if not self.tFlag:
                self.logger.AppendText(config.outlog_14)
                break
            sfile = config.SMB_SAVETO + nfile.replace(config.SMB_VERPATH, "")
            saveTo = os.path.dirname(sfile)
            if not os.path.exists(saveTo):
                os.makedirs(saveTo)
            self.logger.AppendText(config.outlog_15 % os.path.basename(sfile))
            self.doDownload(nfile, sfile)
        self.logger.AppendText(config.outlog_16 % (time.time() - st))
        self.addNewLine()
        self.button_AutoUpdate.Show(True)
        self.button_STOPAutoUpdate.Show(False)   
        
        if self.tFlag:
            self.tFlag = False
            retCode = wx.MessageBox(config.outlog_19, config.Label_MSGBOX, wx.YES_NO|wx.ICON_INFORMATION)
            if retCode == wx.ID_YES or retCode == 2:
                self.doLaunch()
                
    def getFiles(self, nroot, nfile):
        try:
            dfl = [x for x in self.samba.listPath(config.SMB_ROOT, nroot) if x.filename not in [".", ".."]]
        except:
            wx.MessageBox(config.outlog_22, config.Label_MSGBOX, wx.OK|wx.ICON_INFORMATION)
            dfl = []
        for n in dfl:
            ndir = nroot + "/" + n.filename#.encode("gbk")
            if not n.isDirectory and ndir not in nfile: 
                nfile.append(ndir)
            else:
                troot = nroot + "/" + n.filename#.encode("gbk")
                nfile.extend(self.getFiles(troot, []))
        return nfile
    
    def doDownload(self, dfile, sfile):
        """
        #单独剥离的samba文件下载方法
        #调用指定的samba连接对象，将指定的samba文件下载到本地保存
        #参数说明：
        # conn -- 传入的可操作的samba链接
        # dfile-- 待下载的samba文件地址或路径
        # sfile-- 将要保存为的文件地址和文件名
        """
        s_dir = os.path.dirname(sfile) 
        if not os.path.exists(s_dir):
            os.makedirs(s_dir)
        
        tfile = open(sfile, "wb")#创建临时文件
        print dfile
        print tfile
        try:
            self.samba.retrieveFile(config.SMB_ROOT,  dfile,  tfile, timeout = 45)#执行下载
        except Exception, e:
            self.logger.AppendText(config.outlog_26 % os.path.basename(sfile))
            print e
            self.logger.AppendText(repr(e) + "\n")
        tfile.close()#完成后关闭下载对象
    
    def addNewLine(self):
        self.logger.AppendText("=" * 25 + "\n")
        
        
        
app = wx.App(False)
frame = ExamplePanel()
frame.Show()
app.MainLoop() 