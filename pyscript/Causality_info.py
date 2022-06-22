
from math import   sqrt, nan
import numpy as np
import pandas as pd
import os
import matplotlib.pyplot as plt
from matplotlib.pyplot import MultipleLocator
from matplotlib import font_manager as fm, rcParams #为解决中文显示问题而加的3行
plt.rcParams['font.sans-serif']=['SimHei'] 
plt.rcParams['axes.unicode_minus']=False 



class Cuowei_Coef(): 
    def __init__(self, table_name, para1, para2, TV1, TV2, save_path, save_info, frequency=2, info_threshold=0.01, diff=50, n=10):
        '''diff：一次错位秒数  n：向前&后错位个数(+1) '''
        self.table_name = table_name
        self.para1 = para1
        self.para2 = para2
        self.TV1 = TV1
        self.TV2 = TV2

        self.X_t = self.TV1[:,0]
        self.X_v = self.TV1[:,1]
        self.Y_t = self.TV2[:,0]
        self.Y_v = self.TV2[:,1]

        self.save_path = save_path
        self.save_info = save_info

        self.fre = frequency
        self.diff = diff
        self.n = n
        self.info_threshold = info_threshold


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
    

    def cal_cuowei(self, v1, v2):
        n = self.n
        diff = self.diff
        diff_list = sorted([-i*diff for i in range(n)]) + [i*diff for i in range(1,n)]
        df = pd.DataFrame([],columns = diff_list, dtype = object)

        coefs = []
        for diff_i in diff_list:
            if diff_i > 0 :
                value1_diff = v1[diff_i*self.fre:]
                value2_diff = v2[:-diff_i*self.fre]
            elif diff_i < 0:
                value1_diff = v1[:diff_i*self.fre]
                value2_diff = v2[-diff_i*self.fre:]
            elif diff_i == 0:
                value1_diff = v1
                value2_diff = v2
            if len(value1_diff) > 10*self.fre and len(value2_diff) > 10*self.fre:
                pearson_diff_coef = self.pcc(value1_diff, value2_diff)
                df.loc[0,diff_i] = pearson_diff_coef
                coefs.append(pearson_diff_coef)

        return diff_list, df


    def info(self, diff_list,  df):
        coefs = [abs(i) for i in list(df.loc[0,:])]
        maxcoef_diff = diff_list[coefs.index(max(coefs))]
        if maxcoef_diff != 0:
            if abs(df.loc[0, maxcoef_diff]) >= 0.15 and abs(df.loc[0, maxcoef_diff]) - abs(coefs[0]) > self.info_threshold:
                str_info_chn = '当时差为' + str(int(maxcoef_diff)) + 's时体现出更强的相关性'
                return str_info_chn


    def segments_coefs(self):

        diff_list, df = self.cal_cuowei(self.X_v, self.Y_v) #错位

        plt.figure(figsize=(10,5))
        plt.plot(df.loc[0,:])
        x_major_locator = MultipleLocator(self.diff)
        ax=plt.gca()
        ax.xaxis.set_major_locator(x_major_locator)

        for a, b in df.loc[0,:].items():
            plt.text(a-2, b+0.01,'%.4f'%b)
        plt.ylim(-1.1,1.1)
        plt.title(self.para1 + ' & ' + self.para2 + ' 时差相关性计算')
        plt.xlabel('时间差 /s')
        plt.ylabel('Pearson相关系数')

        fig_name = ''
        for key,value in self.save_info.items():
            if key in ['时间起点','时间终点']: #只到秒 毫秒以后保存出问题
                value = value.split('.')[0]
            fig_name +=  value + ';'
        ##名字中带有/会在路径中分级 半角转全角会避免此问题
        fig_name = fig_name.replace('/','／')
        fig_name = fig_name.replace(':','：')
        plt.savefig(self.save_path + 'img/' + fig_name) 
        plt.close()

        str_info_chn = self.info(diff_list, df)
        return str_info_chn


class Causality_info(): 
    def __init__(self, table_name, para1, para2, TV1, TV2, save_path, save_info, frequency=2, info_threshold=0.01, diff=5, n=5):
        self.table_name = table_name
        self.para1 = para1
        self.para2 = para2
        self.TV1 = TV1
        self.TV2 = TV2

        self.X_t = self.TV1[:,0]
        self.X_v = self.TV1[:,1]
        self.Y_t = self.TV2[:,0]
        self.Y_v = self.TV2[:,1]

        self.save_path = save_path
        self.save_info = save_info

        self.fre = frequency
        self.diff = diff
        self.n = n
        self.info_threshold = info_threshold
    

    def causality_run(self):
        str_info = Cuowei_Coef(self.table_name,self.para1, self.para2, self.TV1, self.TV2, self.save_path, self.save_info, self.fre, self.info_threshold, self.diff, self.n).segments_coefs()
        return str_info
