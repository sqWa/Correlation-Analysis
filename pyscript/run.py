# -*- coding: UTF-8 -*-

import time
import sys
import os
import json
from matplotlib.pyplot import table
import numpy as np
from Trans_data import Get_fashetime, Trans_para, Trans_ins, Trans_tstamp
from cal_total_pcc import Total_PCC
from Plot_orgn import Plot_orgn
from Diag_info import Diag_info
from Trend import Trend_model
from Causality_info import Causality_info
from Diff_over import compare_coef
from config import AlgoConfig
import traceback

## 保存结果
def save_result(save_path, json_key, info):
    if 'result.json' not in os.listdir(save_path):
        with open(save_path + 'result.json','w', encoding='utf-8') as f:
            str_dict = {json_key: [info]}
            f.write(json.dumps(str_dict, ensure_ascii=False))
    else:
        with open (save_path + 'result.json' , 'rb') as f:
            results_dic = json.load(f, encoding='utf-8')
        if json_key not in results_dic:  #新json_key
            results_dic[json_key] = [info]
            with open(save_path + 'result.json', 'w', encoding='utf-8') as f:
                f.write(json.dumps(results_dic, indent=2, ensure_ascii=False))
        else:
            if info not in results_dic[json_key]:  #避免相同内容重复保存  新list内容
                results_dic[json_key].append(info)
                with open(save_path + 'result.json', 'w', encoding='utf-8') as f:
                    f.write(json.dumps(results_dic, indent=2, ensure_ascii=False))

## 保存简化的历史总览结果
def save_simple_result(save_path_simple, json_key, info):
    type_name = {'3':'切片相关性','4':'斜率相关性', '5':'时差相关性', '6':'整体相关性'}
    info_simple = dict([(key,info[key]) for key in ["型号","发次","测试类型","测试阶段","参数1","参数2"]])
    result = info["结果"]
    if info["相关性类型序号"] == '3': 
        if result != '无显著切片相关性':
            resu = result.split('~')
            res=''
            for i,re in enumerate(resu):
                if i !=0:
                    res += re.split('；')[0].split('s')[1] +'；'
        else:
            res = result
    elif info["相关性类型序号"] == '4': 
        res = result.split('；')[0]
    elif info["相关性类型序号"] == '5': 
        res = result
    elif info["相关性类型序号"] == '6': 
        res = result.split('；')[0].split('：')[1]

    all_result = {}
    all_result[type_name[info["相关性类型序号"]]] = res
    info_simple['结果汇总'] = all_result

    if 'result.json' not in os.listdir(save_path_simple):
        with open(save_path_simple + 'result.json', 'w', encoding='utf-8') as f:
            str_dict = {json_key: [info_simple]}
            f.write(json.dumps(str_dict, ensure_ascii=False))
    else:
        with open (save_path_simple + 'result.json' , 'rb') as f:
            results_dict = json.load(f, encoding='utf-8')
            if json_key not in results_dict:  #新json_key
                results_dict[json_key] = [info_simple]
                with open(save_path_simple + 'result.json', 'w', encoding='utf-8') as f:
                    f.write(json.dumps(results_dict, indent=2, ensure_ascii=False))
            else:
                for i,simple_dic in enumerate(results_dict[json_key]):
                    modifi = False
                    if dict([(key,info_simple[key]) for key in ["型号","发次","测试类型","测试阶段","参数1","参数2"]]) \
                        == dict([(key,simple_dic[key]) for key in ["型号","发次","测试类型","测试阶段","参数1","参数2"]]):
                        results_dict[json_key][i]['结果汇总'][type_name[info["相关性类型序号"]]] = res   #over
                        modifi = True
                if modifi == False:
                    results_dict[json_key].append(info_simple)
                with open(save_path_simple + 'result.json', 'w', encoding='utf-8') as f:
                    f.write(json.dumps(results_dict, indent=2, ensure_ascii=False))


def creat_dirs(filename_list):
    for filename in filename_list:
        if not os.path.exists(filename):
            os.makedirs(filename)

###两参数排序，按编号小的在前，确保得到运算参数对名称的唯一性
def sortpara(para1_, para2_):
    cur_params = [para1_] + [para2_] #当前这对参数
    # parm_list = sorted(cur_params) #简易排序
    temp_array = np.zeros((2, 2))
    for s in range(2):
        temp_array[s][0] = int(cur_params[s].split('/')[0])
        temp_array[s][1] = int(cur_params[s].split('/')[1])
    idex = np.lexsort((temp_array[:,1], temp_array[:,0]))
    parm_list = [0] * 2
    for s in range(2):
        parm_list[s] = cur_params[idex[s]]  
    para1 = parm_list[0]
    para2 = parm_list[1]
    return para1, para2


## 时间对齐
def duiqi(_TV1, _TV2):
    TV1_leftbound = _TV1[0,0]
    TV2_leftbound = _TV2[0,0]
    TV1_rightbound = _TV1[_TV1.shape[0]-1,0]
    TV2_rightbound = _TV2[_TV2.shape[0]-1,0]
    common_leftbound = max(TV1_leftbound, TV2_leftbound)
    commen_rightbound = min(TV1_rightbound, TV2_rightbound)
    TV1 = _TV1[_TV1[:,0]>=common_leftbound][_TV1[_TV1[:,0]>=common_leftbound][:,0]<=commen_rightbound]
    TV2 = _TV2[_TV2[:,0]>=common_leftbound][_TV2[_TV2[:,0]>=common_leftbound][:,0]<=commen_rightbound]
    return TV1, TV2


## 获得时间区间的相对时间
def trans_timecut(table_name, argteststage, ordertime_list, fashe_time):
    pos = np.where(ordertime_list != None) #行 列 位置
    t_lr = []
    ordertime_lr = []
    #获取时间框的相对时间
    for i in range(2):
        ordertime = ordertime_list[pos[0][i],pos[1][i]]
        #指令
        if pos[0][i] == 0: 
            order = ordertime
            ins_num = argteststage.split('/')[0] + '-' + order.split('/')[0] + '-' + order.split('/')[1] + '_0'
            ins_name = order.split('/')[2]
            try:
                tv = Trans_ins(table_name, ins_num, fashe_time).run()
            except Exception as ex:
                print(traceback.format_exc())
                tv = np.array([])
            if tv.size == 0:
                AlgoConfig.task_message("该发次所选指令 "+ ins_name+" 无数据，无法计算相关性\n")
                return None, None, None
            else:
                t = float(tv[0,0])  #指令取第一个时间
                t_lr.append(t)
                ordertime_lr.append(order)
        #时间戳
        elif pos[0][i] == 1:
            time_stamp = ordertime
            t = Trans_tstamp(time_stamp, fashe_time).run()
            t_lr.append(t)
            ordertime_lr.append(time_stamp)
    
    left_s, right_s = t_lr[0], t_lr[1] #-xxx(s)
    if left_s > right_s:
        left_s, right_s = right_s, left_s
        ordertime_lr.reverse()
    elif left_s == right_s:
        result='无法计算，所选时间区间内无数据'
        return result

    return left_s, right_s, ordertime_lr


## 加载参数数据 并截取相应时间区间
def load_and_cut_data(table_name, parm_list, fashe_time, left_s, right_s,test_stage):
    data_load = {}
    for i in range(len(parm_list)):
        para = parm_list[i]
        if para not in data_load:
            row_name = test_stage.split('/')[0] + '-' + para.split('/')[0] + '-' + para.split('/')[1] + '_0'
            ### 读取数据
            try:
                TV_ = Trans_para(table_name, row_name, fashe_time).run()
            except Exception as ex:
                print(traceback.format_exc())
                TV_ = np.array([])
            if TV_.size == 0:
                AlgoConfig.task_message("该发次所选参数 "+para+" 无数据，无法进行计算\n")
                continue

            #### 截取时间区间内数据
            if left_s!=None and right_s!=None:
                try:
                    _TV = TV_[TV_[:,0]>left_s][TV_[TV_[:,0]>left_s][:,0]<right_s]
                    if _TV is None:
                        continue
                except Exception as ex:
                    print(traceback.format_exc())
                    continue
            else:
                _TV  = TV_
            data_load[para] = _TV #空数据未存key
            AlgoConfig.task_message(para + " 数据载入完成\n")

    return data_load

## 相关性运算总方法
def run_corr(arg):
    os.chdir(os.path.dirname(os.path.realpath(__file__))) #切换到当前工作目录
    print("run corr {}".format(arg))
    table_name = 'HistoryData-'+ arg['roc'].split('/')[0] + '-' + arg['num'].split('/')[0] + '-' + arg['test-ype'].split('/')[0]
    save_path = '../history/Type_'+ str(arg["type"]) + '/' 
    save_path_simple = '../history/Type_7/' 
    creat_dirs([save_path, save_path+'img/', save_path_simple, save_path_simple+'img/'])
    
    ## 在此修改用于查找发射时间的参数/指令
    referenced_para_row = arg['test-stage'].split('/')[0] + '-1306-1_0'  #用1390表的参数6的最后时间点作为发射时间
    try:
        fashe_time = Get_fashetime(table_name, referenced_para_row).run() #2016-11-03 20:45:39.655_1
    except Exception as ex:
        print(traceback.format_exc())

    ## 时间区间设置解读
    orders_list = [[arg["order-param1"]] + [arg["order-param2"]]]    #根据时间顺序排序    #before根据编号的排序方式 orders_list = [sorted(orders_list[0])] if orders_list[0][0]!=None and orders_list[0][1]!=None else orders_list #均非空时排序
    time_list = [ [arg["start-time"]] + [arg["end-time"]] ]    # time_list = [sorted(time_list[0])] if time_list[0][0]!=None and time_list[0][1]!=None else time_list
    ordertime_list = np.append(orders_list, time_list, axis=0) #[[指令1,指令2],[时间1,时间2]]
    none_count = np.sum(ordertime_list == None)
    if none_count == 2:
        left_s, right_s, ordertime_lr = trans_timecut(table_name, arg['test-stage'], ordertime_list, fashe_time) #根据指令/时间截取时间段
        left_ordertime = ordertime_lr[0]
        right_ordertime = ordertime_lr[1]
    elif none_count == 4:
        left_s, right_s = None, None
        left_ordertime = None
        right_ordertime = None
    else:
        AlgoConfig.task_message("指令/时间设置错误，无法进行计算\n")
        raise ValueError

    ##载入所有参数数据
    parm_list = arg['params1'] + arg['params2']
    AlgoConfig.task_message("正在读取参数……\n")
    data_load_all = load_and_cut_data(table_name, parm_list, fashe_time, left_s, right_s,arg['test-stage'])
    AlgoConfig.task_message("参数读取完成，开启相关性计算……\n\n")

    parm1_list= arg['params1']
    parm2_list= arg['params2']
    ##两两组合进行计算  无数据则不进行
    for i in range(len(parm1_list)):
        for j in range(len(parm2_list)):
            para1_, para2_ = parm1_list[i], parm2_list[j]
            para1, para2 = sortpara(para1_,para2_)

            _TV1 = data_load_all.get(para1,np.array([])) 
            _TV2 = data_load_all.get(para2,np.array([]))
            
            if _TV1.size != 0 and _TV2.size != 0:
                TV1, TV2 = duiqi(_TV1, _TV2)

                json_key = para1 + ' & ' + para2

                info = {}
                info["型号"] = arg["roc"]
                info["发次"] = arg["num"]
                info["测试类型"] = arg["test-ype"]
                info["测试阶段"] = arg["test-stage"]
                info["参数1"] = para1
                info["参数2"] = para2

                order_num = np.sum(ordertime_list[0] != None)
                time_num = np.sum(ordertime_list[1] != None)
                if order_num == 2:
                    info["指令起点"] = left_ordertime
                    info["指令终点"] = right_ordertime
                    info["时间起点"] = "--"
                    info["时间终点"] = "--"
                if time_num == 2:
                    info["指令起点"] = "--"
                    info["指令终点"] = "--"
                    info["时间起点"] = left_ordertime
                    info["时间终点"] = right_ordertime
                if order_num ==1 and time_num == 1:
                    if left_ordertime in [arg["order-param1"],arg["order-param2"]]:
                        info["指令起点"] = left_ordertime
                        info['指令终点'] = "--"
                        info['时间起点'] = "--"
                        info['时间终点'] = right_ordertime
                    elif left_ordertime in [arg["start-time"],arg["end-time"]]:
                        info["指令起点"] = "--"
                        info['指令终点'] = right_ordertime
                        info['时间起点'] = left_ordertime
                        info['时间终点'] = "--"
                if order_num ==0 and time_num==0:
                    info["指令起点"] = "--"
                    info["指令终点"] = "--"
                    info["时间起点"] = "--"
                    info["时间终点"] = "--"
                    

                Plot_orgn(table_name, para1, para2, TV1, TV2, save_path, info).plot_orgn()
                t4 = float(time.time())

                if str(arg["type"]) == '6':  #整体相关性
                    try:
                        str_info1 = Total_PCC(table_name, para1, para2, TV1, TV2, left_ordertime, right_ordertime).run()
                    except Exception as ex:
                        print(traceback.format_exc())
                        str_info1 = '无法从该对指令/时间中获取参数相关性信息'
                    
                    #超差判别
                    try:
                        thre_up = arg["information"][json_key]["thre_up"]
                        if thre_up !=None:
                            thre_up = str(thre_up)
                    except Exception as ex:
                        print(traceback.format_exc())
                        thre_up = None
                    try:
                        thre_down = arg["information"][json_key]["thre_down"]
                        if thre_down !=None:
                            thre_down = str(thre_down)
                    except Exception as ex:
                        print(traceback.format_exc())
                        thre_down = None
                    try:
                        deviation = arg["information"][json_key]["deviation"]
                        if deviation !=None:
                            deviation = str(deviation)
                    except Exception as ex:
                        print(traceback.format_exc())
                        deviation = None
                    
                    if thre_up!=None and thre_down!= None and deviation!=None:
                        info["判据"] = "上限：" + thre_up \
                                    + "；下限：" + thre_down \
                                    + "；误差容比：" + deviation
                    else:
                        info["判据"] = '--'


                    #进行偏差计算和超差判别（有历史时有偏差，有判据时有超差）
                    current_info = info
                    str_info2 = compare_coef(current_info, str_info1, save_path, para1, para2, thre_up, thre_down, deviation)
                    str_info = str_info1 + ' ' + str_info2

                elif str(arg["type"]) == '3':  #切片相关
                    if arg['slide-step']!=None:
                        time_slice = int(arg['slide-step']) 
                        str_info = Diag_info(table_name, para1, para2, TV1, TV2, save_path, info, time_slice).info_run()
                        info["判据"] = '时间切片步长：' + str(time_slice) + 's'
                    else:
                        str_info = Diag_info(table_name, para1, para2, TV1, TV2, save_path, info).info_run()
                        info["判据"] = '时间切片步长：1000s'

                elif str(arg["type"]) == '4':  #斜率相关
                    str_info = Trend_model(table_name, para1, para2, TV1, TV2, save_path, info).trend_run()  #, t_step
                    info["判据"] = '--'

                elif str(arg["type"]) == '5':  #时差相关性
                    ####在此修改时差：修改下一行中diff值，单位秒
                    str_info = Causality_info(table_name, para1, para2, TV1, TV2, save_path, info, info_threshold=0.01, diff=50, n=10).causality_run()  #, frequency
                    info["判据"] = '--'


                type_name = {'3':'切片相关性','4':'斜率相关性', '5':'时差相关性', '6':'整体相关性'}
                if str_info == None:
                    str_info = '无显著'+ type_name[str(arg["type"])]
                info["结果"] = str_info
                info["相关性类型序号"] = str(arg["type"])

                AlgoConfig.task_message(json.dumps(info,ensure_ascii=False) + '\n')
                save_result(save_path, json_key, info)
                
                save_simple_result(save_path_simple, json_key, info)
        
            

if __name__=='__main__': 
    os.chdir(os.path.dirname(os.path.realpath(__file__))) #切换到当前工作目录
    
    with open('../arguments-corr.json','rb') as f:
        arg = json.load(f,encoding = 'utf-8')
    run_corr(arg)
