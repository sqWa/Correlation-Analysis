# from msilib.schema import Class
import numpy as np
import happybase as hb
import time
import os
import json

'''
输入：表名 table_name 行名 row_name 需要读取的个数 n
当n大于表的最大个数时读取停止,如果没有表名 table_name会报错，表名存在没有行名 row_name不报错但不会读出数据
输出：时间，键值
使用：data_load("表名","行名")
'''

class DataLoader():
    def __init__(self):
        os.chdir(os.path.dirname(__file__)) #切换到当前工作目录
        with open('../web/setting/setting.txt','r',encoding = 'utf-8') as f:
            arg = json.load(f)
        self.host = arg['HBaseAddr']
        self.port = int(arg['HBasePort'])

    def data_load(self,table_name,row_name):
        try:
            connection = hb.Connection(self.host,self.port) #根据hbase部署地址的情况即时修改
        except:
            print('数据库连接出错')
        table = hb.Table(table_name,connection)
        rowfilter="RowFilter(=,'regexstring:"+row_name+"*')"
        data = None
        for k,v in table.scan(filter=rowfilter): 
            data = v
            break
        if data==None:
            return None,None
        #keys键时间 raw_data原始hbase内byte类型
        keys = list(data.keys())
        raw_data = list(data.values())
        #利用lambda表达式批量处理原始数据
        parsed_x = list(map(lambda key:str(key)[7:][:-1],keys))
        parsed_y = list(map(lambda x:float(x.decode()),raw_data))

        return np.array(parsed_x), np.array(parsed_y)

    def data_load2(self,table_name,row_name, n):
        connection = hb.Connection(self.host,self.port) #根据hbase部署地址的情况即时修改
        table = hb.Table(table_name,connection)
        data = table.row(row_name)
        keys = data.keys()
        count = 0
        x = []
        y = []
        rowfilter="RowFilter(=,'regexstring:"+row_name+"*')"
        for k,v in table.scan(filter=rowfilter): 
            print(k)  
            break
        for key in keys:
            t = str(key)[7:][:-1] 
            value = float(table.cells(row_name, key)[0])
            count += 1
            print(key, value)
            x.append(t) 
            y.append(value)
            if count >= n:
                break
        return np.array(x), np.array(y)


