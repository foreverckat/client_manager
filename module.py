#-*- coding=utf8 -*-
'''
Created on 2015.12.11

@author: albertcheng
'''
import os
import sys
import re
import logging
# config logging  
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

def ifFileExists(func):
    """
    # 修饰函数，用于统一检查待读取文件是否存在
    """
    def __deco(*argu):
        bfile  = argu[0] + ".bin" # 构造bin文件路径
        csfile = argu[0] + ".cs" # 构造cs文件路径
        if not os.path.exists(bfile):
            logger.error(u"文件  [%s] 不存在" % bfile)
            assert os.path.exists(bfile)
        if not os.path.exists(csfile):
            logger.error(u"文件  [%s] 不存在" % csfile)
            assert os.path.exists(csfile)
        return func(*argu)
    return __deco

def loadBin(func):
    """
    # 修饰函数，用于统一文件读取的默认操作
    """
    
    def __deco(*argu):
        bfile = argu[0] + ".bin" # 构造bin文件路径
        csfile = argu[0] + ".cs" # 构造cs文件路径
        with open(bfile, "rb") as Bin_File:
            argu = list(argu)
            argu.append([[y for y in x.split("\t") if y != "\r\n"] for x in Bin_File.readlines()])
        
        with open(csfile, "rb") as csharp_File:
            p = re.compile("[\";]")
            argu.append([p.sub("", line.strip().split(" ")[-1]) for line in csharp_File.readlines() if line.strip().startswith("public") and line.strip().endswith(";")  and "=" not in line])
        
        return func(*argu)
    return __deco

@ifFileExists   
@loadBin
def LoadSingleKey(*argu):
    key, bindata, tableData = argu[1:]
    ret = {}
    key_idx = tableData.index(key)
    for data in bindata:
        # 断言检查角色ID的配置唯一性
        assert data[key_idx] not in ret
        ret[data[key_idx]] = data
    ret["__table"] = tableData
    return ret

@ifFileExists
@loadBin
def LoadDoubleKey(*argu):
    key1, key2, bindata, tableData= argu[1:]
    key1_idx = tableData.index(key1)
    key2_idx = tableData.index(key2)
    ret = {}
    for data in bindata:
        key1ID = data[key1_idx]
        key2ID = data[key2_idx] 
        if key1ID not in ret:
            ret[key1ID] = {}
        assert key2ID not in ret[key1ID]
        ret[key1ID][key2ID] = data
    ret["__table"] = tableData
    return ret
