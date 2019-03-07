import os
import json
import operator

def getSysConfig():
    data = None
    DB_SECRET_FILE = 'config/sysConfig.json'
    if True == os.path.exists(DB_SECRET_FILE):
        with open(DB_SECRET_FILE) as json_file:
            data = json.load(json_file)
    return data

def getRpcHost(type):
    try:
        data = getSysConfig()
        info = {}
        if(operator.eq(type,"001")):
            info = data["link"]["extend001"]
        elif (operator.eq(type,"003")):
            info = data["link"]["extend003"]
        else:
            return ""

        return "http://%s:%s/IBUS/" %(info["host"],info["port"])
    except Exception as e:
        return ""

