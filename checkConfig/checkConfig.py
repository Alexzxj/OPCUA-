from xml.dom import minidom as soapXml
import time

from util import common
import os
import sys
import importlib
from watchdog.observers import Observer
from watchdog.events import *
from util import Logger

webservice_dir = os.path.abspath("./config/")
path = os.getcwd()


class FileEventHandler(FileSystemEventHandler):
    def __init__(self):
        FileSystemEventHandler.__init__(self)

    def on_created(self, event):
        pass

    def on_deleted(self, event):
        pass

    def on_modified(self, event):
        # pass
        # if not event.is_directory:
        #     try:
        #         webservice_file = os.path.basename(event.src_path)
        #         module_name = "config."+os.path.splitext(webservice_file)[0]
        #         remove_service_by_module_name(module_name)
        #         del sys.modules[module_name]
        #         importlib.import_module(module_name)
        #         # load_all_service()
        #     except Exception as e:
        #         Logger.log.error(e)
        add_service(event.src_path)


class SoapServiceArray(object):
    services = []
    flag = True


def add_service(service_name):
    if os.path.splitext(service_name)[1] == '.json' and service_name not in SoapServiceArray.services:
        SoapServiceArray.services.append(service_name)
        SoapServiceArray.flag = False


def delete_server(service_name):
    SoapServiceArray.services.remove(service_name)
    SoapServiceArray.flag = True


def load_all_service():
    service_file = os.listdir(webservice_dir)
    for webservice_file in service_file:  # 获取文件目录
        if os.path.splitext(webservice_file)[1] == '.py':
            module_name = os.path.splitext(webservice_file)[0]
            module_spec = importlib.util.find_spec("webservice." + module_name)
            if module_spec:
                importlib.import_module("webservice."+module_name)


def check_every_service_file():
    observer = Observer()
    event_handler = FileEventHandler()
    observer.schedule(event_handler, webservice_dir, True)
    observer.setDaemon(True)
    observer.start()


def soap_interface_init():
    sys.path.append("config")
    # 加载所有的webservice服务到内存
    load_all_service()
    # 定时检查webservice目录是否有新的模块需要加载或者模块修改
    check_every_service_file()


if __name__ == '__main__':
    soap_interface_init()
    while True:
        time.sleep(1)




