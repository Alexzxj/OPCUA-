from updateData import updateData
from util import Logger
class SubHandler(object):
    """
    Subscription Handler. To receive events from server for a subscription
    data_change and event methods are called directly from receiving thread.
    Do not do expensive, slow or network operation there. Create another
    thread if you need to do such a thing
    """
    def __init__(self, cfg, lt, client, config):
        self.cfg = cfg['update_url']
        self.lt = lt
        self.client = client
        self.config = config

    def datachange_notification(self, node, val, data):
        mt = []
        for temp in self.lt:
            if node == self.client.get_node(temp['nodeID']):
                if temp['conversionFormula']:
                    data = eval(str(val) + temp['conversionFormula'])
                # print("update data:%s：%s" % (temp['name'], val))
                Logger.log.info("update data:%s：%s" % (temp['name'], val))
                dic = dict()
                dic["oid"] = '-'.join([self.cfg['projectId'], 'ms',
                                       self.config['mid'], self.config['mname'], temp['dataId']])
                if temp['dataType'] == 'String':
                    dic["value"] = str(val)
                elif temp['dataType'] == 'DateTime':
                    dic["value"] = str(val)
                elif temp['dataType'] == 'Float':
                    dic["value"] = float('%.2f' % val)
                else:
                    dic["value"] = val

                mt.append(dic)
        updateData.update_data(self.url + '/IBUS/update', mt)

    def event_notification(self, event):
        print("Python: New event", event)

