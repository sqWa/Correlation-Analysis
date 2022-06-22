from math import sqrt
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib import font_manager as fm, rcParams #为解决中文显示问题而加的3行
plt.rcParams['font.sans-serif']=['SimHei'] 
plt.rcParams['axes.unicode_minus']=False 



class Cal_and_Plot():
    def __init__(self, table_name, para1, para2, TV1, TV2, save_path, save_info, time_slice):
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

        self.time_slice = time_slice

    def pcc(self,x, y):  #皮尔逊相关系数
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

    ## 处理数据
    def DataProcess(self, t, val):
        nt = len(t)
        nv = len(val)

        data = []
        low = 0
        n = 0
        interval = []
        if nt == nv:
            for i in range(nt):
                if low != t[i] // self.time_slice * self.time_slice:
                    low = t[i] // self.time_slice * self.time_slice
                    data.append([])
                    interval.append(low)
                    n += 1
                data[n - 1].append(val[i])
        else:
            print(nt, nv)
            raise ValueError

        return data, interval

    #判断两参数公共部分
    def find_start(self, interval_a, interval_b):
        n1 = len(interval_a)
        n2 = len(interval_b)
        for i in range(n1):
            for j in range(n2):
                if interval_a[i] == interval_b[j]:
                    return i, j
        print("No overlap")
        raise ValueError

    # 计算相关系数矩阵
    def correlate(self):
        data1, interval1 = self.DataProcess(self.X_t, self.X_v)
        data2, interval2 = self.DataProcess(self.Y_t, self.Y_v)

        n1 = len(interval1)
        n2 = len(interval2)

        start1, start2 = self.find_start(interval1, interval2)
        interval1.reverse()
        interval2.reverse()
        end1, end2 = self.find_start(interval1, interval2)

        n = abs(start1 - start2) + abs(end1 - end2) + (n1 - 1 - start1 - end1)
        end1 = n - 1 - end1
        end2 = n - 1 - end2
        range1 = [start2, end2]
        range2 = [start1, end1]

        time = np.zeros(n)
        for i in range(n):
            time[i] = min(interval1[-1], interval2[-1]) + float(self.time_slice) * i
        ticks = [str(i) for i in time]
        
        coeffs = np.zeros((n, n))

        for i in range(n):
            for j in range(n):
                if range1[0] <= i <= range1[1] and range2[0] <= j <= range2[1]:
                    coeffs[i][j] = self.pcc(data1[i - range1[0]], data2[j - range2[0]])
                else:
                    coeffs[i][j] = -99
        df = pd.DataFrame(coeffs, columns=ticks, index=ticks)
        df = df.replace(-99, np.nan)
        return df

    #绘图
    def ploting(self, df):
        ax = sns.heatmap(df, vmin=-1, vmax=1, square=True, center=0)
        plt.title(self.para1 + ' & ' +self.para2 + ' 时间切片相关系数矩阵')
        plt.ylabel('时间/s\n('+self.para1+')')
        plt.xlabel('时间/s\n('+self.para2+')')
        fig_name = ''
        for key,value in self.save_info.items():
            if key in ['时间起点','时间终点']: #只到秒 毫秒以后保存出问题
                value = value.split('.')[0]
            fig_name +=  value + ';'
        ##名字中带有/会在路径中分级 半角转全角会避免此问题
        fig_name = fig_name.replace('/','／')
        fig_name = fig_name.replace(':','：')
        plt.savefig(self.save_path +'img/'+ fig_name, bbox_inches='tight')
        plt.close()

    # 总方法
    def correlate_run(self):
        coeffs = self.correlate()
        try:
            self.ploting(coeffs)
        except:
            pass

        return coeffs


## 提取切片相关信息
class Diag_info():  
    def __init__(self, table_name, para1, para2, TV1, TV2, save_path,save_info, time_slice=1000):#period=None不分段 period='new'新数据
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

        self.time_slice = time_slice
        self.info = pd.DataFrame([],columns=['start','end','length(s)','parameter','value','average','property','degree','type','top 20 related instructions and degree'],dtype=object)


    def load_coeffs(self):
        coeffs = Cal_and_Plot(self.table_name, self.para1, self.para2, self.TV1, self.TV2, self.save_path, self.save_info, self.time_slice).correlate_run()
        return coeffs


    def get_diag(self):
        df = self.load_coeffs()
        diag = {}
        for index, row in df.iterrows():
            diag[float(index)] = row[str(index)]
        return diag


    def diag_bigger_or_smaller_than(self, threshold):
        diag = self.get_diag()
        key_ = []
        value_ = []
        for key, value in diag.items():
            if threshold > 0:
                if value > threshold:
                    key_.append(key)
                    value_.append(value)
            else:
                if value < threshold:
                    key_.append(key)
                    value_.append(value)
        return key_


    def remove_those_keys_in_square(self, key_):

        def getmax(df, i, j):
            M = 3
            N = 3
            while len(np.argwhere(df[i:i+M, j:j+N] > 0.3)) == M*N or len(np.argwhere(df[i:i+M, j:j+N] < -0.3)) == M*N:
                N += 1
            N = N-1
            while len(np.argwhere(df[i:i+M, j:j+N] > 0.3)) == M*N or len(np.argwhere(df[i:i+M, j:j+N] < -0.3)) == M*N:
                M += 1
            M = M-1
            return M, N
        
        def saveinfo(point_col, point_row, row, col, t, info):
            info.loc[t, 'col_range'] = [point_col, point_col+ col*10] 
            info.loc[t, 'row_range'] = [point_row, point_row+ row*10]

        def find_square(df):
            start = df.index[0]
            df = np.array(df)
            L = len(df)
            info = pd.DataFrame([], columns=['col_range','row_range'], dtype=object)
            t = 0
            for i in range(L - 2):
                for j in range(L - 2):
                    if len(np.argwhere(df[i:i + 3, j:j + 3] > 0.3)) == 9 or len(np.argwhere(df[i:i + 3, j:j + 3] < -0.3)) == 9:
                        point_col = start + j * 10
                        point_row = start + i * 10
                        row, col = getmax(df, i, j)
                        newnum = df[i:i + row, j:j + col]
                        allnum = df[i:i + row, j:j + col].flatten()
                        sum = 0
                        for num in allnum:
                            sum += num
                        average = sum / (row * col)
                        saveinfo(point_col,point_row, row, col, t, info)
                        df[i:i + row, j:j + col] = np.zeros([row, col])
                        t += 1
            if t != 0:
                print(info)
            return info

        df = self.load_csv()
        squares = find_square(df)
        key__ = key_
        remove_key = []
        if not squares.empty:
            for key in key_:
                for i in range(squares.shape[0]):
                    if (squares.loc[i, 'col_range'][0] < key <= squares.loc[i,'col_range'][1])  and  (squares.loc[i, 'row_range'][0] < key <= squares.loc[i,'row_range'][1]):
                        remove_key.append(key)
            for r in remove_key:
                key__.remove(r)
        return key__


    def degree(self, average):
        if average > 0:
            corr = '正相关'
        else:
            corr = '负相关' 

        if 0.15 <= abs(average) < 0.3:
            deg = '弱'  
        elif 0.3 <= abs(average) < 0.7:
            deg = '中' 
        elif  abs(average) >= 0.7:
            deg = '强' 
        return corr , deg


    def diag_conti_pieces(self, key_):
        diag = self.get_diag()
        
        all_start = []   #连续片段
        all_end = []
        point = key_[0]
        if len(key_) > 1 :
            all_start.append(point)
            for n in range(len(key_)-1):
                if key_[n+1] - key_[n] == self.time_slice:
                    point += self.time_slice
                    if n == len(key_)-2:
                        all_end.append(key_[n+1])
                else:
                    all_end.append(key_[n]) #包含
                    if n != len(key_)-2 : 
                        all_start.append(key_[n+1])
                        point = key_[n+1]
        
        continous_num = 5  #连续5个及以上
        start = []  
        end = []
        for i in range(len(all_start)):
            if all_end[i] +self.time_slice - all_start[i] >= self.time_slice* continous_num:
                start.append(all_start[i])
                end.append(all_end[i])

        maxidx = self.info.shape[0]  
        for j in range(len(start)): 
            #转换成h min s
            self.info.loc[maxidx + j, 'start'] = self.trans_time(int(start[j]))
            self.info.loc[maxidx + j, 'end'] = self.trans_time(int(end[j] + self.time_slice))

            self.info.loc[maxidx + j, 'length(s)'] = end[j] + self.time_slice -start[j]
            self.info.loc[maxidx + j, 'value'] = [diag[x] for x in range(int(start[j]), int(end[j]+self.time_slice), self.time_slice)]
            self.info.loc[maxidx + j, 'average'] = np.mean([diag[x] for x in range(int(start[j]), int(end[j]+self.time_slice), self.time_slice)])
            self.info.loc[maxidx + j, 'property'], self.info.loc[maxidx + j, 'degree'] = self.degree(self.info.loc[maxidx + j, 'average'])
            self.info.loc[maxidx + j, 'type'] = 'diag'
        
        if start != []:
            return 'have'
        else:
            return 'not have'


    def property_jump(self):
        maxidx = self.info.shape[0] #已有行数 = 当前最大index + 1

        self.info.sort_values(by=['start(s)'], ascending=True, inplace=True) #时间顺序排序
        self.info.reset_index(drop=True, inplace=True)

        count = 0
        jump_idx = {}
        jump_start = {}
        jump_end = {}
        for idx in range(maxidx-1):
            if self.info.loc[idx,'property'] != self.info.loc[idx+1,'property']:
                count += 1
                jump_idx[count] = idx
                jump_start[count] = self.info.loc[idx, 'end(s)']
                jump_end[count] = self.info.loc[idx+1, 'start(s)']

        for i in range(count):
            self.info.loc[maxidx + i, 'start(s)'] = jump_start[i+1]
            self.info.loc[maxidx + i, 'end(s)'] = jump_end[i+1]

            self.info.loc[maxidx + i, 'length(s)'] = jump_end[i+1] - jump_start[i+1]
            self.info.loc[maxidx + i, 'property'] = self.info.loc[jump_idx[i+1],'property'] + ' to ' + self.info.loc[jump_idx[i+1] + 1,'property'] 
            self.info.loc[maxidx + i, 'type'] = 'diag jump'


    def trans_time(self, time):
        t  = abs(time)
        h = int(t / 3600)
        h_mod = t % 3600
        min = int(h_mod / 60)
        min_mod = h_mod % 60
        s = min_mod

        if h == 0:
            if min == 0:
                if s == 0:
                    time_str = str(0) + 's'
                else:
                    time_str = str(s) + 's'
            else:
                time_str = str(min) + 'min ' + str(s) + 's'
        else:
            time_str = str(h) +'h ' + str(min) + 'min ' + str(s) + 's'
            
        if time < 0:
            time_str = '-' + time_str
        return time_str


    def info_run(self, save=True):
        key_p = self.diag_bigger_or_smaller_than(0.15)
        if key_p != []:
            p_have = self.diag_conti_pieces(key_p)

        key_n = self.diag_bigger_or_smaller_than(-0.15)
        if key_n != []:
            n_have = self.diag_conti_pieces(key_n)

        str_info_s = ''
        for index in range(len(self.info)):
            str_info_s = str_info_s + (str(self.info.loc[index,'start'] + ' ~ ' + self.info.loc[index,'end'] + self.info.loc[index,'property'] + '(' + self.info.loc[index,'degree'] + ')')) + '；'

        if not self.info.empty:
            return str_info_s
        else:
            return None

        
