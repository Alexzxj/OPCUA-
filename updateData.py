import json

import requests

from util import Logger


class updateData(object):
    # 上传数据到数仓
    def update_data(url, temp, apikey):
        json_data = {
            "apikey": apikey,
            "method": "system#update",
            "request": {
                "datas": {
                    "oids": temp
                }
            }
        }
        headers = {"Content-Type": "application/json", "charset": "utf-8"}
        try:
            ret = requests.post(url=url, json=json_data, headers=headers)
            return json.loads(ret.text)
        except Exception as e:
            Logger.log.error(e)



