import base64
import numpy as np
import matplotlib.pyplot as plt
import json
plt.rcParams['font.sans-serif']=['SimHei'] 
plt.rcParams['axes.unicode_minus']=False 
plt.switch_backend('agg')

class Plot_orgn():
    def __init__(self, table_name, para1, para2, TV1, TV2,
             save_path, save_info, start_time=None, end_time=None): 
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

        self.left = start_time
        self.right = end_time
    
    def plot_orgn(self):
        if self.left == None and self.right== None:
            plot_X_t = self.X_t
            plot_X_v = self.X_v
        elif self.left == None and self.right != None:
            X_tv =  np.append(self.X_t.reshape(-1,1),self.X_v.reshape(-1,1),axis=1)   
            plot_X_t = X_tv[X_tv[:,0]<self.right][:,0]
            plot_X_v = X_tv[X_tv[:,0]<self.right][:,1]
        elif self.left != None and self.right == None:
            X_tv =  np.append(self.X_t.reshape(-1,1),self.X_v.reshape(-1,1),axis=1)  
            plot_X_t = X_tv[X_tv[:,0]>self.left][:,0]
            plot_X_v = X_tv[X_tv[:,0]>self.left][:,1]
        else:
            X_tv =  np.append(self.X_t.reshape(-1,1),self.X_v.reshape(-1,1),axis=1)    
            plot_X_t = X_tv[X_tv[:,0]>self.left][X_tv[X_tv[:,0]>self.left][:,0]<self.right][:,0]
            plot_X_v = X_tv[X_tv[:,0]>self.left][X_tv[X_tv[:,0]>self.left][:,0]<self.right][:,1]


        plt.subplot(311)
        plt.xlabel('时间')
        plt.ylabel('数值')
        plt.plot(plot_X_t, plot_X_v, label = self.para1) 
        if self.left == None and self.right== None:
            plt.title(self.para1 +' & ' +self.para2 + ' 原始数据图\n' ,size =12)
        else:
            plt.title(self.para1 +' & ' +self.para2 + ' 原始数据图(局部)\n (' + str(format(self.left,'.0f')) + \
                's~' + str(format(self.right,'.0f')) + 's)',size =12)
        plt.legend()


        plt.subplot(312)
        plt.xlabel('时间')
        plt.ylabel('数值')
        if self.left == None and self.right== None:
            plot_Y_t = self.Y_t
            plot_Y_v = self.Y_v
        elif self.left == None and self.right != None:
            Y_tv =  np.append(self.Y_t.reshape(-1,1),self.Y_v.reshape(-1,1),axis=1)
            plot_Y_t = Y_tv[Y_tv[:,0]<self.right][:,0]
            plot_Y_v = Y_tv[Y_tv[:,0]<self.right][:,1]
        elif self.left != None and self.right == None:
            Y_tv =  np.append(self.Y_t.reshape(-1,1),self.Y_v.reshape(-1,1),axis=1)
            plot_Y_t = Y_tv[Y_tv[:,0]>self.left][:,0]
            plot_Y_v = Y_tv[Y_tv[:,0]>self.left][:,1]
        else:
            Y_tv =  np.append(self.Y_t.reshape(-1,1),self.Y_v.reshape(-1,1),axis=1)  
            plot_Y_t = Y_tv[Y_tv[:,0]>self.left][Y_tv[Y_tv[:,0]>self.left][:,0]<self.right][:,0]
            plot_Y_v = Y_tv[Y_tv[:,0]>self.left][Y_tv[Y_tv[:,0]>self.left][:,0]<self.right][:,1]

        plt.plot(plot_Y_t, plot_Y_v, label = self.para2,color = 'darkorange') 
        plt.legend()


        plt.subplot(313)
        plt.xlabel('时间')
        plt.ylabel('数值')
        plt.plot(plot_X_t, plot_X_v, label = self.para1) 
        plt.plot(plot_Y_t, plot_Y_v, label = self.para2,color = 'darkorange') 
        plt.legend()

        fig_name = ''
        for key,value in self.save_info.items():
            if key in ['时间起点','时间终点']: #只到秒 毫秒以后保存出问题
                value = value.split('.')[0]
            fig_name +=  value + ';'
        ##名字中带有/会在路径中分级 半角转全角会避免此问题
        fig_name = fig_name.replace('/','／')
        fig_name = fig_name.replace(':','：')

        fig_name2 = ''
        for key,value in self.save_info.items():
            if key in ["型号","发","型","段","参数1","参数2"]: 
                fig_name2 +=  value + ';'  #名字太长 中文；改成英文;
        fig_name2 += '--;--;--;--;'
        ##名字中带有/会在路径中分级 半角转全角会避免此问题
        fig_name2 = fig_name2.replace('/','／')
        fig_name2 = fig_name2.replace(':','：')

    
        ####### 图数保存
        plot_X = np.append(plot_X_t.reshape(-1,1), plot_X_v.reshape(-1,1), axis=1)
        plot_Y = np.append(plot_Y_t.reshape(-1,1), plot_Y_v.reshape(-1,1), axis=1)
        fig_name2 = self.save_path + '../Type_7/img/' + fig_name2 + '.json'
        fig_name = self.save_path + 'img/' + fig_name + '.json'
        with open(fig_name2, 'w+', encoding='utf-8') as f:
            plot_points = {'params1':str(self.para1),
                            'params2':str(self.para2),
                            'plot_X': plot_X.tolist(),
                            'plot_Y': plot_Y.tolist(),
                        }
            json.dump(plot_points, f)

        with open(fig_name, 'w+', encoding='utf-8') as f:
            plot_points = {'params1':str(self.para1),
                            'params2':str(self.para2),
                            'plot_X': plot_X.tolist(),
                            'plot_Y': plot_Y.tolist(),
                        }
            json.dump(plot_points, f)

