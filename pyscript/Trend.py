import numpy as np
import os
import matplotlib.pyplot as plt
import copy
# from matplotlib import font_manager as fm, rcParams #为解决中文显示问题而加的3行
# plt.rcParams['font.sans-serif']=['SimHei'] 
# plt.rcParams['axes.unicode_minus']=False 


class Trend_model():
    def __init__(self, table_name, para1, para2, TV1, TV2, save_path, save_info, mean_t_step=1000): #t_step 求平均的时间步长
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

        self.mean_t_step = mean_t_step
        self.format = '.0f'


    def mean_nocare_fre(self, X_t_int, X_v_int, t_step): #根据时间范围
        X_mean = []
        t_int = []
        idx_int = []
        count = 0
        for i, t in enumerate(X_t_int):
            if float(format(t, self.format)) % t_step == 0 :
                t_tmp = float(format(t, self.format))
                t_int.append(t_tmp)
                idx_int.append(i)
                if count>0 and t_tmp == t_int[count-1]:
                    del t_int[-1]
                    del idx_int[-1]
                else:
                    count += 1
        X_t_mean =[]
        X_v_mean = []
        for i in range(len(idx_int)-1):
            sum = 0
            cnt = 0
            for v in  X_v_int[idx_int[i]: idx_int[i+1]]:
                sum += v
                cnt += 1
            X_v_mean.append(sum / cnt)
            X_t_mean.append((t_int[i] + t_int[i+1]) / 2)
        return X_t_mean, X_v_mean


    def new_mean_nocare_fre(self, X_t_int, X_v_int, t_step):  #可应对采样不均匀及漏采、不同频率
        X_t_mean = []
        X_v_mean = []
        start = X_t_int[0]
        end = X_t_int[-1]
        for t_int in range(int(start), int(end), t_step):
            sum = 0
            cnt = 0
            for idx, t in enumerate(X_t_int):
                if t_int < t < t_int + t_step : 
                    sum += X_v_int[idx]
                    cnt += 1
            X_v_mean.append(sum / cnt)
            X_t_mean.append((t_int + t_int+t_step) / 2)
        return X_t_mean, X_v_mean



    def slope(self, t, v, _range):
        norm_k = []
        for i in range(len(t)-1):
            norm_k.append((v[i+1]-v[i]) / _range )
        return norm_k


    def remove_both_ends(self, T, V, t_step):
        for t in T:
            if float(format(t,self.format)) % t_step == 0:
                start = t
                break
        for t in reversed(T):
            if float(format(t,self.format)) % t_step == 0:
                end = t
                break
        T_int = []
        V_int = []
        for i, t in enumerate(T):
            if start<= t <= end:
                T_int.append(t)
                V_int.append(V[i])
        return start, end, T_int, V_int
        

    def compare_k(self, X_t_mean, X_norm_k, Y_t_mean, Y_norm_k):
        '''计算斜率相似程度'''
        t_list = []
        score_list = []
        del X_t_mean[-1]
        del Y_t_mean[-1]
        for i, t_i in enumerate(X_t_mean):
            for j, t_j in enumerate(Y_t_mean):
                if format(t_i,'.0f') == format(t_j,'.0f') or float(format(t_i,'.0f')) == float(format(t_j,'.0f'))+1 or float(format(t_i,'.0f')) == float(format(t_j,'.0f'))-1:
                    t_list.append(format(t_i,'.0f'))
                    k1 = X_norm_k[i]
                    k2 = Y_norm_k[j]
                    s = (2*k1*k2) / (k1**2 + k2**2 + 0.001) 
                    score_list.append(s)
        return t_list, score_list


    def threshold(self, score_list):
        ##阈值以上追溯到0.15保留
        idx_no = -1
        idx_r = []
        idx_l = []
        for i, s in enumerate(score_list):
            if abs(s) > 0.7:
                idx_no = i
                pn = 'p' if s > 0 else 'n'
                break
        if idx_no != -1:
            for j_r in range(idx_no+1,len(score_list)):
                if pn == 'p':
                    if score_list[j_r] > 0.15:
                        idx_r.append(j_r)
                    else:
                        break
                elif pn == 'n':
                    if score_list[j_r] < -0.15:
                        idx_r.append(j_r)
                    else:
                        break
            for j_l in range(idx_no-1,-1,-1):
                if pn == 'p':
                    if score_list[j_l] > 0.15:
                        idx_l.append(j_l)
                    else:
                        break
                elif pn == 'n':
                    if score_list[j_l] < -0.15:
                        idx_l.append(j_l)
                    else: 
                        break
            idx_l.reverse()
            idx = idx_l + [idx_no] + idx_r
            return idx, pn
        else:
            return None, None


    def strinfo(self, idx_dict, pn_dict, t_list, score_list):
        yingshe = {'p':'斜率正相关','n':'斜率负相关'}
        str_chn_info = ''
        for count, idx in idx_dict.items():
            pn = pn_dict[count]
            if len(idx) > 1: #除去仅一个点的情况
                mean, width = self.getmeanandwidth(t_list, score_list, idx)
                start = int(t_list[idx[0]]) - 0.5*self.mean_t_step 
                end = int(t_list[idx[-1]]) + 0.5*self.mean_t_step
                #转换成h min s
                trans_start = self.trans_time(start)
                trans_end = self.trans_time(end)
                str_chn_info = str_chn_info +  ' 在' +str(trans_start) + ' ~ ' + str(trans_end) +' ' + yingshe[pn] \
                                + '，斜率相关强度：' + str(mean) \
                                + '，斜率强相关时长：' + str(width) +'s；'
        return str_chn_info

    def judge(self, t_list, score_list):
        idx_dict = {}
        pn_dict = {}
        score_list_rest = copy.deepcopy(score_list)
        count = 0
        while len(score_list_rest) > 0:
            idx, pn = self.threshold(score_list_rest)  #每次找一个峰
            if idx!=None:
                if count == 0:
                    idx_dict[count] = idx
                else:
                    idx_dict[count] = [idx[i] + idx_dict[count-1][-1]+1 for i in range(len(idx))]
                pn_dict[count] = pn
                del score_list_rest[:idx[-1]+1]
                count +=1
            else:
                break

        if len(idx_dict)!=0:
            str_chn_info = self.strinfo(idx_dict, pn_dict, t_list, score_list)
            if str_chn_info == '':
                str_chn_info = None
        else:
            str_chn_info = None
            
        return str_chn_info


    def trans_time(self, time):  #s → h min s
        t  = abs(time)
        h = int(t / 3600)
        h_mod = t % 3600
        min = int(h_mod / 60)
        min_mod = h_mod % 60
        s = min_mod
        if h == 0:
            if min == 0:
                if s == 0:
                    time_str = str(0)
                else:
                    time_str = str(s) + 's'
            else:
                time_str = str(min) + 'min_' + str(s) + 's'
        else:
            time_str = str(h) +'h_' + str(min) + 'min_' + str(s) + 's'
        if time < 0:
            time_str = '-' + time_str
        return time_str


    def getmeanandwidth(self, t_list, score_list, idx_conti):  # 求平均值和半高宽
        '''平均值'''
        global st, ed
        sum = 0
        for i in idx_conti:  # 将区间内所有值相加
            sum += score_list[i]
        mean = format(sum / len(idx_conti), '.4f')  # 得到平均值
        '''半高宽'''
        maxv = abs(score_list[idx_conti[0]])
        for j in idx_conti:
            if abs(score_list[j]) >= maxv:
                maxv = abs(score_list[j])
        halfmax = maxv / 2  # 半高值
        global i1
        i1 = 0
        while abs(score_list[idx_conti[i1]]) <= halfmax:
            i1 += 1
        if i1 != 0:  # 避免i1等于0
            i1 = i1 - 1
        global i2
        i2 = len(idx_conti) - 1
        while abs(score_list[idx_conti[i2]]) <= halfmax:
            i2 -= 1
        if i2 != len(idx_conti) - 1:
            i2 = i2 + 1
        width = int(t_list[idx_conti[i2]]) - int(t_list[idx_conti[i1]])
        return mean, width


    def plotting(self,t_list, score_list):
        plt.figure(figsize=(12,6))
        plt.plot(t_list, score_list)
        plt.ylim(-1.1,1.1)
        plt.title(self.para1 + ' & ' +self.para2 + ' 斜率相关度曲线')
        plt.ylabel('斜率相关因子')
        plt.xlabel('时间/s')
        plt.xticks(rotation=90)

        fig_name = ''
        for key,value in self.save_info.items():
            if key in ['时间起点','时间终点']: #只到秒 毫秒以后保存出问题
                value = value.split('.')[0]
            fig_name +=  value + ';'
        ##名字中带有/会在路径中分级 半角转全角会避免此问题
        fig_name = fig_name.replace('/','／')
        fig_name = fig_name.replace(':','：')
        plt.savefig(self.save_path + 'img/' + fig_name)  #####
        plt.close()


    def trend_run(self):
        '''斜率相关性总方法'''
        X_start, X_end, X_t_int, X_v_int = self.remove_both_ends(self.X_t, self.X_v, self.mean_t_step) #掐头去尾 留下1000整数倍  X_t_int的首末即X_start X_end


        X_t_mean, X_v_mean = self.mean_nocare_fre(X_t_int, X_v_int, self.mean_t_step)

        X_range = max(X_v_mean)-min(X_v_mean)
        X_norm_k = self.slope(X_t_mean, X_v_mean, X_range)


        Y_start, Y_end, Y_t_int, Y_v_int = self.remove_both_ends(self.Y_t, self.Y_v, self.mean_t_step)

        Y_t_mean, Y_v_mean = self.mean_nocare_fre(Y_t_int, Y_v_int, self.mean_t_step)

        Y_range = max(Y_v_mean)-min(Y_v_mean)
        Y_norm_k = self.slope(Y_t_mean, Y_v_mean, Y_range)

        t_list, score_list = self.compare_k(X_t_mean, X_norm_k, Y_t_mean, Y_norm_k)


        self.plotting(t_list, score_list)
        str_chn_info = self.judge(t_list, score_list)
        return str_chn_info
