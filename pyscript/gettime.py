from dataloader import DataLoader
import sys
import os

def getTime(rock_id,roc_num,test_type,test_stage,table_num,param_num):
    try:
        #命令行输入型号 发次 测试类型 测试阶段 表号 参数编号
        table_name='HistoryData-'+str(rock_id)+'-'+str(roc_num)+'-'+str(test_type)
        row_name=str(test_stage)+'-'+str(table_num)+'-'+str(param_num+'_0')
        getter=DataLoader()
        time,val=getter.data_load(table_name,row_name)
        start_time=time[0].split('_')[0]    #起始时间
        end_time=time[-1].split('_')[0]     #终止时间
        return (str(start_time)+'/'+str(end_time))
    except:
        return 'null'

if __name__=='__main__':
    #切换到当前工作目录
    os.chdir(os.path.dirname(__file__))
    try:
        #命令行输入型号 发次 测试类型 测试阶段 表号 参数编号
        table_name='HistoryData-'+str(sys.argv[1])+'-'+str(sys.argv[2])+'-'+str(sys.argv[3])
        row_name=str(sys.argv[4])+'-'+str(sys.argv[5])+'-'+str(sys.argv[6]+'_0')
        getter=DataLoader()
        time,val=getter.data_load(table_name,row_name)
        start_time=time[0].split('_')[0]    #起始时间
        end_time=time[-1].split('_')[0]     #终止时间
        f=open("../time.txt","w")
        f.write(str(start_time)+'/'+str(end_time))
        f.close()
    except:
        f=open("../time.txt","w")
        f.write("null")
        f.close()