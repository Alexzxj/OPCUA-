import getopt
import json
import threading
from threading import Thread
from flask import Flask, request
from gevent import wsgi

import IBUS
from createModule.create_module import createModule, getModulePars, updateAttr
from subHandler import SubHandler
from util import Logger, SysHelp
import time
from checkConfig import checkConfig
import sys, platform
import os
from opcua.client.client import Client
# from opcua.client import Client
from updateData import updateData

# 程序版本
VERSION = "V1.2.0"
path = os.getcwd()
cfg = ''
flag = True


# 读配置文件1
def readConfig():
    content = ''
    try:
        with open(path + '/config/config.json', 'r', encoding='utf8') as f:
            content += f.read()
        return json.loads(content)
    except Exception as e:
        Logger.log.error(e)


# 读配置文件2
def readModuleConfig():
    content = ''
    try:
        with open(path + '/config/module_cfg.json', 'r', encoding='utf8') as f:
            content += f.read()
        return json.loads(content)
    except Exception as e:
        Logger.log.error(e)


# 写进程的文件
def writeProcessId():
    if platform.system() == 'Linux':
        p = '/var/run/'
        name = ''
        pars = sys.argv[0]
        if '/' in pars:
            mt = pars.split('/')
            if mt[-2] == '.':
                name += os.getcwd().split('/')[-1]
            else:
                name += mt[-2]
        else:
            name += os.getcwd().split('/')[-1]
        # 获取进程id
        pid = os.getpid()
        pidFilePath = p + name + '.pid'
        with open(pidFilePath, 'w', encoding='utf8') as f:
            f.write(str(pid))
    else:
        pass


def connect_ready(config):
    # 连接服务
    # todo：目前网关支持匿名和用户名密码登陆
    # config = config['attributes'][0]['attributes'][0]
    client = Client(config['server_url'])
    if config['mode'] == 'sign' and config['private_key'] and config['client_certificate']:
        client.load_client_certificate(config['client_certificate'])
        client.load_private_key(config['private_key'])
        print("使用签名登陆")
    elif config['mode'] == 'SignAndEncrypt' and config['policy'] \
            and config['private_key'] and config['client_certificate']:
        client.set_security_string(config['policy'], config['mode'], config['client_certificate'],
                                   config['private_key'])
        print('使用用户名签名加密登陆！！！')
    elif config['mode'] == 'None':
        pass
    # 用户名密码登陆
    if config['username'] and config['password']:
        client.set_user(config['username'])
        client.set_password(config['password'])
        print("使用用户名密码登陆！！！")
    else:
        print("使用匿名登陆！！！")
    return client


def collection_data():
    config = SessionHelper.Session().getSession('config')
    cfg = SessionHelper.Session().getSession('cfg')
    # config = readConfig()
    # url = config['attributes'][0]['attributes'][0]
    client = connect_ready(cfg)
    try:
        client.connect()
        s, t = execute(config)
        if t:
            handler = SubHandler(cfg, t, client, config)
            sub = client.create_subscription(500, handler)
            sub.subscribe_data_change(nodes=[client.get_node(rt['nodeID']) for rt in t])
        time.sleep(0.2)
        # we can also subscribe to events from server
        # sub.subscribe_events()

        while flag:
            if checkConfig.SoapServiceArray.services:
                server_name = checkConfig.SoapServiceArray.services[0]
                checkConfig.delete_server(server_name)
                if t:
                    sub.delete()
                name = os.path.basename(server_name)
                if name == 'module_cfg.json':
                    moduleCfg = readModuleConfig()
                    res = updateAttr(config, moduleCfg, apikey)
                    if not res['errorCode']:
                        print("***更新模型成功！！！")
                        try:
                            con = getModulePars(config, moduleCfg, apikey)
                            if con['errorCode']:
                                Logger.log.error(con)
                                break
                        except Exception as e:
                            Logger.log.error(e)
                            break
                        else:
                            cfg = createCfg(con)
                        SessionHelper.Session().setSession('moduleCfg', moduleCfg)
                        SessionHelper.Session().setSession('cfg', cfg)
                elif name == 'config.json':
                    config = readConfig()
                    SessionHelper.Session().setSession('config', config)
                break

            if s:
                mt = []
                for temp in s:
                    var = client.get_node(temp['nodeID'])
                    data = var.get_value()
                    if temp['conversionFormula']:
                        data = eval(str(data) + temp['conversionFormula'])
                    dic = dict()
                    # dic["oid"] = temp['oid']
                    dic["oid"] = '-'.join([cfg['projectId'], 'ms', config['mclass'], config['mname'], temp['dataId']])
                    if temp['dataType'] == 'String':
                        dic["value"] = str(data)
                    elif temp['dataType'] == 'DateTime':
                        dic["value"] = str(data)
                    elif temp['dataType'] == 'Float':
                        dic["value"] = float('%.2f' %data)
                    else:
                        dic["value"] = data
                    mt.append(dic)
                    time.sleep(0.1)
                    print("采集数据:%s：%s %s" % (temp['name'], temp['dataType'], dic['value']))
                ret = updateData.update_data(cfg['update_url']+'/IBUS/update', mt, apikey)
                if ret['errorCode']:
                    Logger.log.error(ret)
    except Exception as e:
        Logger.log.error(e)
        time.sleep(5)
        client.disconnect()
        collection_data()
    else:
        client.disconnect()
        collection_data()


def execute(config):
    lt = []
    isSub = []
    for temp in config['list']:
        if not temp['isSubscribed']:
            lt.append(temp)
        else:
            isSub.append(temp)
    return lt, isSub


def start_read(daemon):
    """带参的执行"""
    # daemon = False
    # opts, args = getopt.getopt(sys.argv[1:], "dv")
    # for op, value in opts:
    #     if op == "-d":
    #         daemon = True
    #     elif op == "-v":
    #         print(VERSION)
    #         sys.exit(0)
    # 是否已守护进程运行
    if daemon:
        pid = os.fork()
        if pid != 0:
            sys.exit(0)
        else:
            os.chdir(os.curdir)
            os.setsid()
            os.umask(0o22)
            # 写进程id
            writeProcessId()
            # 获取数据
            collection_data()
    else:
        # 写进程id
        writeProcessId()
        collection_data()


def createAndReadInfo():
    config = readConfig()
    moduleCfg = readModuleConfig()
    # 若没有初始化则创建
    if not config['isInit']:
        try:
            res = createModule(config, moduleCfg, apikey)
            if res['errorCode']:
                return res['errorCode'], res['errorMsg']
            config['isInit'] = 1
            with open(path + '/config/config.json', 'w', encoding='utf8') as f:
                f.write(json.dumps(config, ensure_ascii=False))
            # 读文件
            config = readConfig()
        except Exception as e:
            Logger.log.error(e)
            return 0, e

    try:
        con = getModulePars(config, moduleCfg, apikey)
        # con = json.loads(con)
        if con['errorCode']:
            Logger.log.error(con)
    except Exception as e:
        Logger.log.error(e)
        return 0, e
    else:
        cfg = createCfg(con)

    SessionHelper.Session().setSession("config", config)
    SessionHelper.Session().setSession("cfg", cfg)
    return config, cfg


def createCfg(con):
    cfg = dict()
    for temp in con['return']['datas']:
        if temp['oid'].split('-')[-1] == '1':
            cfg['username'] = temp['defaultValue']
        elif temp['oid'].split('-')[-1] == '2':
            cfg['password'] = temp['defaultValue']
        elif temp['oid'].split('-')[-1] == '3':
            cfg['server_url'] = temp['defaultValue']
        elif temp['oid'].split('-')[-1] == '4':
            cfg['method'] = temp['defaultValue']
        elif temp['oid'].split('-')[-1] == '5':
            cfg['mode'] = temp['defaultValue']
        elif temp['oid'].split('-')[-1] == '6':
            cfg['policy'] = temp['defaultValue']
        elif temp['oid'].split('-')[-1] == '7':
            cfg['client_certificate'] = temp['defaultValue']
        elif temp['oid'].split('-')[-1] == '8':
            cfg['private_key'] = temp['defaultValue']
        elif temp['oid'].split('-')[-1] == '9':
            cfg['update_url'] = temp['defaultValue']
        elif temp['oid'].split('-')[-1] == '10':
            cfg['projectId'] = temp['defaultValue']
    return cfg

app = Flask(__name__)
app.config['SECRET_KEY'] = 'you never guess' # 使用 session 必须要配置这个，不然会报500错误的！

from util import ConfigHelp, SessionHelper, JsonExtendEncoder
# #向EBS平台注册
apikey = ""
data = ConfigHelp.getSysConfig()
dat = readConfig()
requestHttp = "http://%s:%s" % (data['esb']['host'], data['esb']['port'])
# sendInterval = SysHelp.getInterval() // 1000
sendInterval = 10

from util import CommonHelp
def systemLogin():
    """注册"""
    time.sleep(1)
    global apikey
    args = {
        "apikey": apikey,
        "request": {
            "msid": dat['mclass'],
            "msclass": dat['mclass'],
            "msdns": dat['msdns'],
            "name": dat['mname'],
            "host": "http://%s:%s" % (SysHelp.getHostIp(), data['ibus']['port']),
            "password": SysHelp.getpassword(),
            "explain": "null",
            "service": SysHelp.getServers(),
            "ip": SysHelp.getHostIp(),
            "objectid": data['ibus']['objectId'],
            "type": data['ibus']['type'],
            "cpuUsage": SysHelp.getVirtualMemoryPercent(),
            "memoryUsage": SysHelp.getCpuPercent(),
            "systemInfo": "主机名:  %s OS名称: %s 专业版OS版本: %s" % (
            SysHelp.getNode(), SysHelp.getVersion(), SysHelp.getPlatform()),
        }}
    ebsData = IBUS.RPC("RESTful", requestHttp, "/ESBREST/master/IBUS/ESBSystem/systemLogin", "", args)
    ebsData = json.loads(ebsData)
    if ebsData["errorCode"] == 0:
        apikey += ebsData["return"]["apikey"]
        args['apikey'] = ebsData["return"]["apikey"]
        print("=====向网关注册成功,当前时间:%s"%(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())))
    else:
        errorMsg = ""
        if CommonHelp.hasKey("errorMsg", ebsData):
            errorMsg = ebsData["errorMsg"]
        else:
            errorMsg = ebsData["return"]

        print("向网关注册失败:"+errorMsg)
        # 登录失败间隔3s再次登录
        time.sleep(3)
        systemLogin()


def systemHeartBeat():
    """心跳包"""
    args = {
        "apikey": apikey,
        "request": {
            "msid": dat['mclass'],
            "password": apikey,
            "cpuUsage": SysHelp.getVirtualMemoryPercent(),
            "memoryUsage": SysHelp.getCpuPercent(),
            "systemInfo": "主机名:  %s OS名称: %s 专业版OS版本: %s" % (
                SysHelp.getNode(), SysHelp.getVersion(), SysHelp.getPlatform()),
        }
    }
    ebsData = IBUS.RPC("RESTful", requestHttp, "/ESBREST/master/IBUS/ESBSystem/systemHeartbeat", "", args)
    ebsData = json.loads(ebsData)

    if ebsData["errorCode"] == 0:
        print("=====发送心跳成功,当前时间:%s"%(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())))
    else:
        errorMsg = ""
        if CommonHelp.hasKey("errorMsg", ebsData):
            errorMsg = ebsData["errorMsg"]
        else:
            errorMsg = ebsData["return"]
        print("发送心跳失败:"+errorMsg)
        time.sleep(3)
        systemLogin()
    time.sleep(5)
    systemHeartBeat()


def sendHeartBeat():
    """发心跳包"""
    t = threading.Thread(target=systemHeartBeat)
    t.start()

#flask URL 路由规则
@app.route('/')
def index():
    return "hello world"


@app.route('/IBUS/opcua/set', methods=['POST'])
def set():
    try:
        pars = json.loads(request.data)
    except Exception as e:
        Logger.log.error(e)
        return json.dumps({"errorCode": -1, "errorMsg": "pars is not json"})
    if not pars:
        return json.dumps({"errorCode": -2, "errorMsg": "parms error!!!"})
    if 'apikey'not in pars.keys() or 'request' not in pars.keys():
        return json.dumps({"errorCode": -3, "errorMsg": "apikey or request not exist!!!"}).encode()
    req = pars["request"]
    if 'id' not in req.keys():
        return json.dumps({"errorCode": -4, "errorMsg": "id not exist!!!"})
    if 'oid' not in req.keys():
        return json.dumps({"errorCode": -10, "errorMsg": "id not exist!!!"})
    if 'attrName' not in req.keys():
        return json.dumps({"errorCode": -5, "errorMsg": "attrName not exist!!!"})
    if 'attrValue' not in req.keys():
        return json.dumps({"errorCode": -9, "errorMsg": "attrValue not exist!!!"})

    req['value'] = req['attrValue']
    config = readConfig()
    id = int(req['id'])
    # 小于200为私有属性
    lt = []
    if id > 200:
        for tmp in config['list']:
            if tmp['dataId'] == str(id):
                # 0：只读 1：只写 2：读写
                if tmp['accessLevel'] not in ["RW", "OW"]:
                    return json.dumps({"errorCode": -6, "errorMsg": "node no permission!!!"})
                if '*' in tmp['conversionFormula']:
                    tmp['formula'] = tmp['conversionFormula'].replace('*', '/')
                elif '/' in tmp['conversionFormula']:
                    tmp['formula'] = tmp['conversionFormula'].replace('/', '*')
                elif '-' in tmp['conversionFormula']:
                    tmp['formula'] = tmp['conversionFormula'].replace('-', '+')
                elif '+' in tmp['conversionFormula']:
                    tmp['formula'] = tmp['conversionFormula'].replace('+', '-')
                lt.append(tmp)
        if not lt:
            return json.dumps({"errorCode": -7, "errorMsg": "node not exist!!!"})
    else:
        # 1.私有属性设置
        lt.append(req)
        ret = updateData.update_data(cfg['update_url']+'/IBUS/update', lt, apikey)
        return ret
    client = connect_ready(cfg)
    try:
        client.connect()
        res = client.get_node(lt[0]['nodeID']).set_value(req['attrValue'])
    except Exception as e:
        Logger.log.error(e)
        return json.dumps({"errorCode": -8, "errorMsg": "set fail!!!"})
    finally:
        client.disconnect()
        return json.dumps({"errorCode": 0, "errorMsg": "success!!!"})


if __name__ == "__main__":
    daemon = False
    opts, args = getopt.getopt(sys.argv[1:], "dv")
    for op, value in opts:
        if op == "-d":
            daemon = True
        elif op == "-v":
            print(VERSION)
            sys.exit(0)
    SessionHelper.Session().init()
    systemLogin()
    sendHeartBeat()
    config, cfg = createAndReadInfo()
    if config:
        try:
            t = Thread(target=checkConfig.check_every_service_file)
            m = Thread(target=start_read, args=(daemon,))
            t.start()
            m.start()
            host = '127.0.0.1'
            port = 37000
            if data:
                host = data['ibus']["host"]
                port = data['ibus']["port"]
            # app.run(host=host, port=port)
            tserver = wsgi.WSGIServer((host, port), app)
            tserver.serve_forever()
        except Exception as e:
            Logger.log.error(e)
            print(e)
            flag = False
            sys.exit()






