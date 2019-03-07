"""create by gmh"""
import time
import logging.handlers
import sys

import os

path = ''
pars = sys.argv[0]
if '/' in pars:
    mt = pars.split('/')
    if mt[-2] != '.':
        path += '/'.join(mt[:-1]) + '/'

logsDir = os.path.abspath("logs/")
if not os.path.exists(logsDir):
    os.mkdir(logsDir)

# LOG_FILE = 'logs/extend002.log'
LOG_FILE = path + 'logs/opcua'+time.strftime("-%Y-%m-%d-%H_%M_%S", time.localtime()) +'.log'
# 超出50M切换，最多保存15个文件
handler = logging.handlers.RotatingFileHandler(LOG_FILE, maxBytes=100*1024*1024, backupCount=10)
#handler=logging.handlers.TimedRotatingFileHandler(LOG_FILE, when='midnight') #每天零点切换
#fmt = '%(asctime)s - %(filename)s:%(lineno)s - %(name)s - %(message)s' #调试级别
# 生产级别
fmt = '%(asctime)s %(filename)s [line:%(lineno)2d]-%(funcName)s %(levelname)s %(message)s'
# 实例化formatter
formatter = logging.Formatter(fmt)
# 为handler添加formatter
handler.setFormatter(formatter)
log = logging.getLogger('opcua')
# 为mylogger添加handler
log.addHandler(handler)
# 为mylogger设置输出级别
log.setLevel(logging.ERROR)

consoleHandler = logging.StreamHandler()
# 为mylogger添加handler
log.addHandler(consoleHandler)

#日志对象
def getLog():
    return log
def setLevel(level):
    return log.setLevel(level)