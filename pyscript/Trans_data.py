# from msilib.schema import Class
# from click import launch
import numpy as np
import happybase as hb
import time
import pandas as pd
import os
from math import sqrt, nan
from dataloader import DataLoader



def stamp2dt(stamp):        
    date = stamp.split()[0]
    hms = stamp.split()[1]
    return date, hms

def hms2s(hms):
    hourt = float(hms.split(':')[0])      #时
    mint = float(hms.split(':')[1])       #分
    sect = float(hms.split(':')[2][:6])      #秒
    return hourt, mint, sect



class Get_fashetime(): #找零点
    def __init__(self, table_name, row_name): 
        self.table_name = table_name
        self.row_name = row_name


    def only_get_fashe_time(self): #stamp
        #指令 仅1
        if len(self.df) < 3 :  
            fashe_time_getted = self.df[0,0] +' '+ self.df[0,1]
        #参数
        else:           
            date = self.df[0, 0][0:8]
            for i in range(self.df.shape[0]):
                if self.df[i,0][0:8] != date:  #非同日数据截断
                    a = i
                    break
                else:
                    a = i+1
            fashe_time_getted = self.df[a-1,0] +' ' + self.df[a-1,1]   #带日期  
        return fashe_time_getted
    

    def run(self):
        x,y = DataLoader().data_load(self.table_name, self.row_name)
        date = []; t = []
        for str in x:
            date_, hms_ = stamp2dt(str)
            date.append(date_);   t.append(hms_)
        self.df = np.concatenate((np.array(date).reshape(-1,1), np.array(t).reshape(-1,1), np.array(y).reshape(-1,1)),axis=1)
        
        fashe_time_getted = self.only_get_fashe_time()  
        return fashe_time_getted



class Trans_para(): #参数 → 相对时间
    def __init__(self, table_name, row_name, fashe_time): 
        self.table_name = table_name
        self.row_name = row_name
        self.fashe_time = fashe_time


    def para_process(self):
        date = self.df[0, 0][0:8]
        for i in range(self.df.shape[0]):
            if self.df[i,0][0:8] != date:  #非同日数据截断
                a = i
                break
            else:
                a = i+1
        ## a:参数长度
        h, m, s = hms2s(self.fashe_time.split()[1])
        T = np.zeros([a, 2])
        T[a-1, 1] = self.df[a-1, 2]
        T[a-1, 0] = 0
        for i in range(a-2, -1, -1):
            h_p1, m_p1 ,s_p1 = hms2s(self.df[i+1, 1])
            h, m, s = hms2s(self.df[i, 1])
            if m_p1 == m : #同 分
                T[i,0] = T[i+1,0] -(s_p1 - s)  #秒数相差
            else:
                T[i,0] = T[i+1,0] -(s_p1 - s + 60) 
            T[i,1] = self.df[i,2]
        TV = T
        return TV
    
    def run(self):
        x,y = DataLoader().data_load(self.table_name, self.row_name)
        date = []; t = []
        for str in x:
            date_, hms_ = stamp2dt(str)
            date.append(date_);   t.append(hms_)
        self.df = np.concatenate((np.array(date).reshape(-1,1), np.array(t).reshape(-1,1), np.array(y).reshape(-1,1)),axis=1)
        
        TV = self.para_process()  
        return TV



class Trans_ins(): #指令 → 相对时间
    def __init__(self, table_name, row_name, fashe_time):
        self.table_name = table_name
        self.row_name = row_name
        self.fashe_time = fashe_time


    def ins_process(self):
        a = len(self.df)
        try:
            fashe_h, fashe_m, fashe_s = hms2s(self.fashe_time.split()[1])
            zerot = [fashe_h, fashe_m, fashe_s]
        except:
            zerot = [23, 59, 59]

        TV = np.array([])
        for i in range(a):
            hourt, mint, sect = hms2s(self.df[i,1])
            t = hourt*3600 + mint*60 + sect - (zerot[0]*3600 + zerot[1]*60 + zerot[2])
            v = self.df[i,2]
            if TV.size == 0:
                TV = np.array([t,v]).reshape(1,-1)
            else:
                TV = np.append(TV, np.array([t,v]).reshape(1,-1), axis=0)
        return TV

    def run(self):
        x,y = DataLoader().data_load(self.table_name, self.row_name)
        date = []; t = []
        for str in x:
            date_,hms_ = stamp2dt(str)
            date.append(date_);   t.append(hms_)
        self.df = np.concatenate((np.array(date).reshape(-1,1), np.array(t).reshape(-1,1), np.array(y).reshape(-1,1)),axis=1)

        TV = self.ins_process()   #指令 一般只有1行
        return TV



class Trans_tstamp(): #时间戳 → 相对时间
    def __init__(self, time_stamp, fashe_time):
        self.time_stamp = time_stamp
        self.fashe_time = fashe_time
    
    def tstamp_process(self):
        try:
            fashe_h, fashe_m, fashe_s = hms2s(self.fashe_time.split()[1])
            zerot = [fashe_h, fashe_m, fashe_s]
        except:
            zerot = [23, 59, 59]

        date, hms = stamp2dt(self.time_stamp)
        hourt, mint, sect = hms2s(hms)
        rela_t = hourt*3600 + mint*60 + sect - (zerot[0]*3600 + zerot[1]*60 + zerot[2])
        return rela_t 

    def run(self):
        rela_t = self.tstamp_process()
        return  rela_t


def trans_time(time):  #s → h min s
    t  = abs(time)
    h = int(t / 3600)
    h_mod = t % 3600
    min = int(h_mod / 60)
    min_mod = h_mod % 60

    time_str = str(h) +'h_' + str(min) + 'min'
    if time < 0:
        time_str = '-' + time_str

    return time_str
