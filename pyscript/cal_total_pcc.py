from math import   sqrt, nan
import numpy as np
import pandas as pd
import os
import sys


class Total_PCC():
    def __init__(self, table_name, para1, para2, TV1, TV2, left_ordertime, right_ordertime):
        self.table_name = table_name
        self.para1 = para1
        self.para2 = para2
        self.TV1 = TV1
        self.TV2 = TV2

        self.X_t = self.TV1[:,0]
        self.X_v = self.TV1[:,1]
        self.Y_t = self.TV2[:,0]
        self.Y_v = self.TV2[:,1]

        self.left_ordertime = left_ordertime
        self.right_ordertime = right_ordertime


    def pcc(self, x, y):  # 皮尔逊相关系数
        n = min(len(x), len(y))
        x = np.array(x[: n])
        y = np.array(y[: n])
        aver_x = np.average(x)
        aver_y = np.average(y)

        temp_x = x - aver_x
        temp_y = y - aver_y
        PSum = np.sum(temp_x * temp_y)
        sum1Sq = sqrt(np.sum(temp_x**2))
        sum2Sq = sqrt(np.sum(temp_y**2))

        if abs(sum1Sq) < 0.0001 or abs(sum2Sq) < 0.0001:
            return 0
        else:
            return PSum / (sum1Sq * sum2Sq)

    
    def cal_new(self):
        result = self.pcc(self.X_v, self.Y_v)
        return result

    def run(self):
        result = self.cal_new()
        if self.left_ordertime == None and self.right_ordertime == None:
            str_info_chn = '整体皮尔逊相关系数为：' + format(result, '.4f')
        elif self.left_ordertime != None and self.right_ordertime != None:
            str_info_chn = '两参数在所选时间段内的皮尔逊相关系数为：' + format(result, '.4f')
        else:
            raise ValueError
        return str_info_chn