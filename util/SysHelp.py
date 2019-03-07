import json
import platform
import socket

import os
import psutil
import sys
from util import DBHelper
from IBUS import IFS_IBUS


def getPlatform():
    '''获取操作系统名称及版本号'''
    return platform.platform()

def getVersion():
    '''获取操作系统版本号'''
    return platform.version()

def getArchitecture():
    '''获取操作系统的位数'''
    return platform.architecture()

def getMachine():
    '''计算机类型'''
    return platform.machine()

def getNode():
    '''计算机的网络名称'''
    return platform.node()

def getProcessor():
    '''计算机处理器信息'''
    return platform.processor()

def getSystem():
    '''获取操作系统类型'''
    return platform.system()

def getUname():
    '''汇总信息'''
    return platform.uname()

def getVirtualMemoryPercent():
    '''内存的使用率'''
    return (psutil.virtual_memory().percent)

def getCpuPercent():
    """cpu使用率"""
    return psutil.cpu_percent(0)

def getHostIp():
    """获取本机ip"""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()
    except Exception as e:
        raise e
    finally:
        s.close()
        return ip[0]

def getDir():
    """获取文件目录"""
    path = ''
    dir = ''
    pars = sys.argv[0]
    tars = os.getcwd()
    if '/' in pars:
        mt = pars.split('/')
        if mt[-2] == '.':
            dir += tars.split('/')[-1]
        else:
            path += '/'.join(mt[:-1]) + '/'
            dir += mt[-2]
    else:
        dir += tars.split('/')[-1]
    return path, dir

def getServers():
    """获取服务模块"""
    lt = []
    for servers in IFS_IBUS.SERVERS:
        for s in servers:
            # if s.type == 'public':
            dic = {}
            dic['mid'] = s.name.split('/')[0]
            dic['name'] = s.name.split('/')[1]
            dic['isStartup'] = s.isStartup
            dic['type'] = s.type
            dic['help'] = s.help
            lt.append(dic)
    else:
        lt.append({"mid": "opcua", "name": "opcua", "isStartup": "false", "type":"public","help":""})
    return json.dumps(lt, ensure_ascii=False)

def getpassword():
    db = DBHelper.DB()
    result = db.fetchone('select `value` from _sys_t_system_module_param where id="initPassword"')
    return result['value']


def getInterval():
    db = DBHelper.DB()
    result = db.fetchone('select `value` from _sys_t_system_module_param where id="timeout"')
    return int(result['value'])

"""获取DNS列表"""
HOST = []

