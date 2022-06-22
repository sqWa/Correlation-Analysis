import os
import json

def compare_coef(current_info, current_result, find_path, para1, para2, thre_up, thre_down, deviation):
    json_key = para1 + ' & ' + para2
    
    current_faci = dict([(key,current_info[key]) for key in ["发次","测试类型","测试阶段"]])
    same_info = dict([(key,current_info[key]) for key in ["型号","参数1","参数2","指令起点","指令终点"]])
    current_coef = float(current_result.split("；")[0].split("：")[1]) #当前系数

    ## 无历史发次时无法进行偏差计算
    if not os.path.exists(find_path + 'result.json'):
        piancha_info = '；暂无历史记录，无法进行偏差计算'
    else:
        with open(find_path + 'result.json' , 'rb') as f:
            results_dic = json.load(f, encoding='utf-8')
            histfaci_coef = {}
            if json_key in results_dic:
                hist_list = results_dic[json_key] #[]
                for info in hist_list:  #该对参数的不同计算历史 info:{}
                    sssame_info = set(same_info.items())
                    iiinfo = set(info.items())
                    if sssame_info.issubset(iiinfo): #指令/时间等均相同的  
                        faci = dict([(key,info[key]) for key in ["发次","测试类型","测试阶段"]])
                        facistr = info["发次"] +','+ info["测试类型"] +','+ info["测试阶段"]
                        if faci != current_faci and facistr not in histfaci_coef: #非本次、且新鲜 的历史发次  一个发次仅取1个
                            histfaci_coef[facistr] = float(info["结果"].split("；")[0].split("：")[1])

            if len(histfaci_coef) == 0:
                piancha_info = '；暂无历史记录，无法进行偏差计算'
            else:
                #####偏差计算部分
                sum = 0
                diff = []
                fuhao =[]
                for i in range(len(histfaci_coef)):
                    g = []
                    faci_i = list(histfaci_coef.keys())[i]
                    v_i = histfaci_coef[list(histfaci_coef.keys())[i]]
                    
                    sum += v_i
                    d = current_coef - v_i
                    diff.append(abs(d))
                    if d >= 0:
                        fuhao.append('p')
                    else:
                        fuhao.append('n')
                    
                his_mean = sum / len(histfaci_coef)#历史平均值
                diff_hismean = format(current_coef - his_mean, '.3f')
                fuhao_hismax = fuhao[diff.index(max(diff))]
                if fuhao_hismax == 'p':
                    diff_hismax = format(max(diff),'.3f')
                else:
                    diff_hismax = format(0- max(diff),'.3f')
                piancha_info = '；与历史发次平均值偏差：' + diff_hismean + ', 与历史发次最大偏差：'+ diff_hismax


    #未设定阈值时不进行超差判定
    if thre_up == None or thre_down == None or deviation == None:  
        thre_info = '；未设定阈值范围无法进行超差判别'
    else:
        thre_up = float(thre_up)
        thre_down = float(thre_down)
        deviation = float(deviation)

        down = thre_down - thre_down*deviation
        up = thre_up + thre_up*deviation
        if current_coef < down or current_coef > up:
            thre_info = '；本发次该参数对相关系数<超出>设定的阈值范围'
        else:
            thre_info = '；本发次该参数对相关系数<未超出>设定的阈值范围'

    result = piancha_info + thre_info
    return result





#####以下为寻找历史可信中心的方法
def over(a, b, thre):
    if abs(a-b) > thre:
        return 1
    else:
        return 0

def compare_coef_before(current_faci, find_path, para1_chn, para2_chn, thre):
    info = {}
    key = para1_chn + ' & ' + para2_chn
    for faci in os.listdir(find_path):
        with open(find_path + faci + '/' + 'result.json' , 'rb') as f:
            results_dic = json.load(f)
            if key in results_dic:
                info[faci] = float(results_dic[key].split('：')[1])
    if len(info) <= 1:
        result = '本发次下该参数对暂无历史相关系数记录，无法进行超差判别'
        return result
    elif len(info) >= 2:
        group= {}
        for i in range(len(info)):
            g = []
            faci_i = list(info.keys())[i]
            v_i = info[list(info.keys())[i]]
            for j in range(len(info)):#i+1, 
                if i != j:
                    faci_j = list(info.keys())[j]
                    v_j = info[list(info.keys())[j]]
                    if not over(v_i, v_j, thre):
                        g.append(faci_j)
            group[faci_i] = g

        max_len = 0
        for i, g in group.items():
            l = len(g)
            if l > max_len:
                max_len = l
        if False not in [(len(g) == max_len) for i,g in group.items()]: #全部等长  #[True, False, True]
            result = '本发次下该参数对相关系数较历史发次相关系数分散'
        if len(group[current_faci]) == max_len:
            result = '本发次下该参数对相关系数处在正常范围'
        elif len(group[current_faci]) < max_len:
            result = '本发次下该参数对相关系数较历史发次相关系数差距高于阈值'
        
    return result




    

