import json
import os
import requests

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
filename = BASE_DIR + '/config/module_cfg.json'


def createModule(config, moduleCfg, apikey):
    # a = open(filename, "r", encoding='UTF-8')
    # out = a.read()
    out = json.dumps(moduleCfg)
    json_data = {
        "apikey": apikey,
        "request": {
            "msid": config['mclass'],
            "mid": config['mid'],
            "datas": "%s"%out
        }
    }
    print(json_data)
    url = ''
    for temp in moduleCfg['datas']:
        # 获取上传url
        # if temp['name'] == 'update_url':
        if temp['id'] == 9:
            url += temp['defaultValue']
            break
    url += '/ESBREST/master/IBUS/ESBSystem/createMSModuleAttr'
    headers = {"Content-Type": "application/json", "charset": "utf-8"}
    t = requests.post(url=url, json=json_data, headers=headers)
    return json.loads(t.text)


def getModulePars(config, moduleCfg, apikey):
    json_data = {
        "apikey": apikey,
        "request": {
            "msid": config['mclass'],
            "mid": config['mid'],
        }
    }
    url = ''
    for temp in moduleCfg['datas']:
        # 获取上传url
        # if temp['name'] == 'update_url':
        if temp['id'] == 9:
            url += temp['defaultValue']
            break
    url += "/ESBREST/master/IBUS/ESBSystem/getMSModuleAttr"
    headers = {"Content-Type": "application/json", "charset": "utf-8"}
    t = requests.post(url=url, json=json_data, headers=headers)
    return json.loads(t.text)


def updateAttr(config, moduleCfg, apikey):
    """更新属性"""
    out = json.dumps(moduleCfg)
    json_data = {
        "apikey": apikey,
        "request": {
            "msid": config['mclass'],
            "mid": config['mid'],
            "datas": "%s" % out
        }
    }
    url = ''
    for temp in moduleCfg['datas']:
        # 获取上传url
        # if temp['name'] == 'update_url':
        if temp['id'] == 9:
            url += temp['defaultValue']
            break
    url += '/ESBREST/master/IBUS/ESBSystem/updateMSModuleData'
    headers = {"Content-Type": "application/json", "charset": "utf-8"}
    t = requests.post(url=url, json=json_data, headers=headers)
    return json.loads(t.text)


if __name__ == '__main__':
    # createModule()
    json_data = {
        "apikey": "",
        "request": {
            "msid": "opcuaManage",
            "mid": "opcua"
        }
    }
    url = "http://10.10.11.232:3000/ESBREST/master/IBUS/ESBSystem/getMSModuleAttr"
    headers = {"Content-Type": "application/json", "charset": "utf-8"}
    t = requests.post(url=url, json=json_data, headers=headers)
    print(t.text)

