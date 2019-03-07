import operator
import time

def hasKey(key, data):
    if(isinstance(data, dict)):
        if key in data.keys():
            return True
    return False

def hasKeyNotEmpty(key, data):
    """判断字典是否存在，并且非空"""
    if(hasKey(key, data) and data[key] != ""):
        return  True
    return  False
#判断布尔字符串
def objToBool(objValue):
    return operator.eq(str(objValue).upper(),"TRUE")
#获取字典里指定的值，没有则返回空字符串
def getHasKeyValue(key, data):
    value = ""
    if hasKeyNotEmpty(key,data) == True:
        value =  data[key]

    return value
#判断是否为日期格式
def isVaildDate(date):
    try:
        if ":" in date:
            time.strptime(date, "%Y-%m-%d %H:%M:%S")
        else:
            time.strptime(date, "%Y-%m-%d")
        return True
    except:
        return False
#判断是否为数字
def isNumber(date):
    t=0
    for i in range(0,len(date)):
        if ord(date[i])>57 or ord(date[i])<48: #转化为ascii码 判断每一位是否都为数字
            if date[i] != '.' or t==1 : #如果不是数字或第二次出现小数点，那么得到结果不是数字
                return False
            elif date[i] == '.': #如果不是数字但是是小数点.那么做个标记，表示已出现过一次小数点
                t=1
    return True #如果完成全部循化，则是数字

#获取格式化数据
def getFormatData(datas):
    if(datas == "" or len(datas) <= 0):
        return {}

    colName = []
    rows = []
    isIDX = False
    try:
        for itemColumn in datas[0]:
            if(operator.eq(itemColumn,'IDX')):
                isIDX = True
                continue
            colName.append(itemColumn)

        index = 0
        for itemRow in datas:
            rowdata = []
            row = {}
            index += 1
            if(isIDX):
                row["rowName"] = itemRow["IDX"]
            else:
                row["rowName"] = index

            for itemColumn in colName:
                if isinstance(itemRow[itemColumn], bytes):
                    data = int.from_bytes(itemRow[itemColumn], byteorder='big', signed=True)
                    rowdata.append(data)
                else:
                    rowdata.append(itemRow[itemColumn])

            row["rowData"] = rowdata
            rows.append(row)
    except Exception as e:
        pass

    return { "colName" : colName, "rows" : rows }

def getFormatRowToColumn(datas):
    if (datas == "" or len(datas) <= 0):
        return {}

    colName = {}
    rows = []
    try:
        for itemColumn in datas[0]:
            if (operator.eq(itemColumn, 'IDX')):
                continue
            colName[itemColumn] = []

        for itemRow in datas:
            for itemColumn in colName:
                colName[itemColumn].append(itemRow[itemColumn])

        for item in colName:
            rows.append({"rowName" : item, "rowData" : colName[item]})


    except Exception as e:
        pass

    return { "rows" : rows }
