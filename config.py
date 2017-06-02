#-*- coding=utf8 -*-

import os

'''
Created on 

@author: albertcheng
'''
##---------------------
## 工具自己的参数区域
##---------------------
linesep = os.linesep
FTP_Host = "192.168.1.24" # ftp ip
FTP_Port =  21# ftp port
FTP_User =  "joker"# ftp user
FTP_Passwd =  "zhaoqing@2015"# ftp password
FTP_Root = "res_tool_for_xgame/"#工具的更新路径

TL_Host = "192.168.1.24" # telnet ip
TL_User = "administrator" # telnet user
TL_Pawd = "zhaoguichun@2015" # telnet password
TL_finish_unix = ":~$"
TL_finish_win32 = ">"

VERSION_MANIFEST = "ver.manifest"


SMB_VERPATH   = u"/6.版本仓库/xgame_pc"
SMB_SAVETO    = "./xgame_pc"
RES_SERVER = [u"http://192.168.1.120/resource|策划1 - 120",
              u"http://192.168.1.121/resource|策划2 - 121", 
              u"http://192.168.1.122/resource|策划3 - 122", 
              u"http://192.168.1.66:8080|内网测试服 - 66"]
Label_Caption = "xgame tool"
Label_Config  = u"刷新列表"
Label_Launch  = u"启动客户端"
Label_MSGBOX  = u"注意"
Label_OpenFolder = u"打开文件夹"
Label_AutoUpdate  = u"自动更新"
Label_StopAutoUpdate = u"停止更新"
Label_Check   = u"检查版本更新"
Label_IPChoice   = u"选择资源更新服务器"
Label_VerChoice  = u"选择自动更新的版本"
SMB_ACCOUNT   = "joker"#"albertcheng"#"joker" 
SMB_PASSWD    = "zhaoqing@2015"#"0506"#"zhaoqing@2015"
SMB_CLIENT    = "xgame-tool"
SMB_SERVER    = "FileServer"
SMB_DOMAIN    = "WORKGROUP"
SMB_HOST_IP   = "192.168.1.24"
SMB_ROOT      = "ShareFiles"
outlog_1 = "samba connected failed."
outlog_2 = u"获取版本资源的路径清单失败。"
outlog_3 = u'目前资源服务器选择为： %s \n服务器对应地址为 %s\n'
outlog_4 = u'目前版本选择为： %s\n'
outlog_5 = u"参数配置功能未开放，有本事你提需求\n"
outlog_6 = u"准备启动游戏客户端...\n"
outlog_7 = u'目前资源服务器选择为： %s \n'
outlog_8 = u'游戏版本选择为： %s \n'
outlog_9 = u"客户端不存在，即将开始下载，下载后会自动启动游戏...\n"
outlog_10 = u'切换工具的更新开关，然并卵，因未做\n'
outlog_11 = u"选择更新版本为："
outlog_12 = u"查找版本失败，版本已经被删除或版本名异常"
outlog_13 = u"有 [%s] 个文件等待下载 \n"
outlog_14 = u"用户暂停客户端的下载线程\n"
outlog_15 = u"正在下载文件 - %s\n"
outlog_16 = u"更新版本共计耗时： [%.2f] 秒\n" 
outlog_17 = u"要下载的版本已经存在，是否继续下载？"
outlog_18 = u"用户放弃了版本资源下载\n"
outlog_19 = u"版本下载完毕，是否启动客户端？" 
outlog_20 = u"列表加载完毕.\n"
outlog_21 = u"要打开的版本不存在，请先更新。"
outlog_22 = u"samba连接已经中断，请重新启动工具或等待重连。\n"
outlog_23 = u"正在下载资源，请稍安勿躁。"
outlog_24 = u"拉取资源清单成功。\n"
outlog_25 = u"修改资源服务器配置失败。"
outlog_26 = u"下载文件 - %s 失败。\n"
outlog_27 = u"启动游戏失败，未发现可执行程序，请检查版本目录。\n" 
log_msg_31 = u"准备上传 [%s - %s] 到Ftp"  
log_msg_32 = u"上传文件 [%s] 到Ftp成功"
log_msg_33 = u"上传完成，耗时%.2f秒"
log_msg_34 = u"所有文件上传完成，耗时%.2f秒"