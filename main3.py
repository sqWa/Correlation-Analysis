from base64 import encode
from bottle import route, run, template, request, response, Bottle, static_file
import json
import os
import sys
from threading import Thread
import time
import logging
import logging.handlers as handlers
sys.path.append(os.path.dirname(os.path.realpath(__file__)) + "/pyscript")
from gettime import getTime
from config import AlgoConfig
import run as corr_run
import jump_detection
import peak_detection
import lstm_pred
logHandler = handlers.RotatingFileHandler(os.environ.get("LOGFILE", "./web.log"), maxBytes=40960000, backupCount=6)
logHandler.setLevel(logging.INFO)
formatter = logging.Formatter(logging.BASIC_FORMAT)
logHandler.setFormatter(formatter)

logging.disable(logging.CRITICAL)
root = logging.getLogger()
root.setLevel(os.environ.get("LOGLEVEL", "WARN"))
root.addHandler(logHandler)

log = root



urlmapping = {
    "/C7HealthMonitor/param/tables?rocketType=1":"/method1",
    "/C7HealthMonitor/param/tables?rocketType=2":"/method2",
    "/C7HealthMonitor/param/tables?rocketType=1&types=1,2":"/method3",
    "/C7HealthMonitor/param/tables?rocketType=2&types=0":"/method4",
    "/C7HealthMonitor/param/tables?rocketType=1&types=0":"/method5",
    "/C7HealthMonitor/param/tables?rocketType=2&types=1,2":"/method6",
    "/C7HealthMonitor/param/parameters?rocketType=1&tblSeq=1210":"/method7",
    "/C7HealthMonitor/param/parameters?rocketType=1&tblSeq=1210&types=1,2":"/method7",
    "/C7HealthMonitor/param/parameters?rocketType=1&tblSeq=1220":"/method8",
    "/C7HealthMonitor/param/parameters?rocketType=1&tblSeq=1220&types=1,2":"/method8",
    "/C7HealthMonitor/param/parameters?rocketType=1&tblSeq=1230":"/method9",
    "/C7HealthMonitor/param/parameters?rocketType=1&tblSeq=1230&types=1,2":"/method9",
    "/C7HealthMonitor/param/parameters?rocketType=1&tblSeq=1306":"/method10",
    "/C7HealthMonitor/param/parameters?rocketType=1&tblSeq=1306&types=0":"/method10",
    "/C7HealthMonitor/param/parameters?rocketType=1&tblSeq=1390":"/method11",
    "/C7HealthMonitor/param/parameters?rocketType=1&tblSeq=1390&types=0":"/method11",
    "/C7HealthMonitor/param/parameters?rocketType=2&tblSeq=1210":"/method12",
    "/C7HealthMonitor/param/parameters?rocketType=2&tblSeq=1210&types=1,2":"/method12",
    "/C7HealthMonitor/param/parameters?rocketType=2&tblSeq=1220":"/method13",
    "/C7HealthMonitor/param/parameters?rocketType=2&tblSeq=1220&types=1,2":"/method13",
    "/C7HealthMonitor/param/parameters?rocketType=2&tblSeq=1230":"/method14",
    "/C7HealthMonitor/param/parameters?rocketType=2&tblSeq=1230&types=1,2":"/method14",
    "/C7HealthMonitor/param/parameters?rocketType=2&tblSeq=1306":"/method15",
    "/C7HealthMonitor/param/parameters?rocketType=2&tblSeq=1306&types=0":"/method15",
    "/C7HealthMonitor/param/parameters?rocketType=2&tblSeq=1390":"/method16",
    "/C7HealthMonitor/param/parameters?rocketType=2&tblSeq=1390&types=0":"/method16",

    "/C7HealthMonitor/fourStructure/GetRocList":"/method17",
    "/C7HealthMonitor/fourStructure/GetNum?*":"/method018",
    "/C7HealthMonitor/fourStructure/GetTesType?*":"/method019",
    "/C7HealthMonitor/fourStructure/GetTesStage?*":"/method020",

    "/C7HealthMonitor/param/systems?rocketType=1":"/method21",
    "/C7HealthMonitor/param/tables?rocketType=1&systemId=513":"/method3",
    "/C7HealthMonitor/param/tables?rocketType=1&systemId=514":"/method4",
    "/C7HealthMonitor/param/tables?rocketType=1&systemId=514&types=0":"/method-1",
    "/C7HealthMonitor/param/tables?rocketType=1&systemId=515":"/method3",
    "/C7HealthMonitor/param/tables?rocketType=1&systemId=515&types=0":"/method0",
    "/C7HealthMonitor/param/tables?rocketType=1&systemId=1":"/method4",
    "/C7HealthMonitor/param/tables?rocketType=1&systemId=1&types=0":"/method4",
    "/C7HealthMonitor/param/tables?rocketType=1&systemId=1&types=1,2":"/method3",
    "/C7HealthMonitor/fourStructure/GetNum":"/method018",
    "/C7HealthMonitor/fourStructure/GetTesType":"/method019",
    "/C7HealthMonitor/fourStructure/GetTesStage":"/method020",
}
app = Bottle()

@app.hook('after_request')
def enable_cors():
    """
    You need to add some headers to each request.
    Don't use the wildcard '*' for Access-Control-Allow-Origin in production.
    """
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'PUT, GET, POST, DELETE, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Origin, Accept, Content-Type, X-Requested-With, X-CSRF-Token'
    response.headers['Content-Type'] = 'text/plain;charset=utf-8'

BASE_DIR   = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, 'static')
f = open(BASE_DIR+"/jsonserver/tableparam.json",encoding="utf-8")
PARAMS_DATA = json.load(f)

WEB_DIR = os.path.join(BASE_DIR, 'web')

CSS_DIR = os.path.join(WEB_DIR, 'css')
IMAGE_DIR = os.path.join(WEB_DIR, 'images')
JS_DIR = os.path.join(WEB_DIR, 'js')
DOC_DIR = os.path.join(WEB_DIR, 'doc')

SETTING_DIR = os.path.join(WEB_DIR, 'setting')
HISTORY_PATH=os.path.join(BASE_DIR, 'history') 
HISVIEW_DIR = os.path.join(WEB_DIR, 'dist')

# 相关性历史数据查看页面
@app.route('/history')
def view_his():
    return static_file("index.html", root=HISVIEW_DIR)

@app.route('/static/css/<filepath:path>')
def server_view_history_static_css(filepath):
    return static_file(filepath, root=HISVIEW_DIR+"/static/css")

@app.route('/static/js/<filepath:path>')
def server_view_history_static_css(filepath):
    return static_file(filepath, root=HISVIEW_DIR+"/static/js")

@app.route('/static/img/<filepath:path>')
def server_view_history_static_css(filepath):
    return static_file(filepath, root=HISVIEW_DIR+"/static/img")

@app.route('/static/fonts/<filepath:path>')
def server_view_history_static_css(filepath):
    return static_file(filepath, root=HISVIEW_DIR+"/static/fonts")

# 普通静态资源
@app.route('/css/<filepath:path>')
def server_css(filepath):
    return static_file(filepath, root=CSS_DIR)

@app.route('/js/<filepath:path>')
def server_js(filepath):
    return static_file(filepath, root=JS_DIR)

@app.route('/images/<filepath:path>')
def server_img(filepath):
    return static_file(filepath, root=IMAGE_DIR)

@app.route('/doc/<filepath:path>')
def server_img(filepath):
    return static_file(filepath, root=DOC_DIR)

@app.route('/setting/<filepath:path>')
def server_setting(filepath):
    return static_file(filepath, root=SETTING_DIR)

@app.route("/<htmlpage:re:.*html$>")
def server_html(htmlpage):
    return static_file(htmlpage, root=WEB_DIR)


@app.route ('/index')
def index_html():
    #payload = merge_dicts(dict(request.forms), dict(request.query.decode()))
    payload = dict(request.query)
    print('payload: {}'.format(payload))
    pagenum = int(payload.get("page",1))
    if pagenum==1:
        return static_file("frame.html", root=WEB_DIR)
    elif pagenum==12:
        return static_file("frame12.html", root=WEB_DIR)
    elif pagenum==2:
        return static_file("frame2.html", root=WEB_DIR)
    elif pagenum==22:
        return static_file("frame22.html", root=WEB_DIR)
    elif pagenum==3:
        return static_file("frame3.html", root=WEB_DIR)
    elif pagenum==32:
        return static_file("frame32.html", root=WEB_DIR)
    elif pagenum==4:
        return static_file("frame4.html", root=WEB_DIR)
    elif pagenum==42:
        return static_file("frame42.html", root=WEB_DIR)
    else:
        return static_file("frame.html", root=WEB_DIR)

chinese_key_map = {
    "型号":"model",
    "发次":"faci",
    "测试类型":"testType",
    "测试阶段":"testPhase",
    "参数1":"key1",
    "参数2":"key2",
    "指令起点":"inst_start",
    "指令终点":"inst_end",
    "时间起点":"time_start",
    "时间终点":"time_end",
    "判据":"judge",
    "结果":"result",
    "相关性类型序号":"corr_index",
    "结果汇总":"result_sum",
    "整体相关性":"whole_corr",
    "斜率相关性":"slope_corr",
    "因果相关性":"ce_corr",
    "对角线相关性":"diag_corr"
}
def cn_key_to_en_keymap(data,type_id):
    if data==None:
        return {}
    retdata = {}
    allresult = data.get("结果汇总",{})
    if isinstance(allresult, dict):
        data.update(allresult)
    keys = list(data.keys())
    for key in keys:
        retdata[chinese_key_map.get(key,key)]=data.get(key)
    import hashlib
    hashdata = "{}_{}".format(type_id,json.dumps(retdata,ensure_ascii=False,separators=(',',':'),indent=1).encode('utf8'))
    m = hashlib.md5()
    m.update(hashdata.encode('utf8'))
    id = m.hexdigest()
    retdata["id"] = id
    return retdata
@app.route ('/get_chart_data',method='POST')
def get_corr_data():
    params = None
    type_id = request.query.type_id or None
    reqdata = request.json or {}
    print("jsondata:{}/{}".format(type_id,reqdata))

    model = reqdata.get("model","--")
    num = reqdata.get("num","--")
    testType = reqdata.get("testType","--")
    testPhase = reqdata.get("testPhase","--")
    key1 = reqdata.get("key1","--")
    key2 = reqdata.get("key2","--")
    inst_start = reqdata.get("inst_start","--")
    inst_end = reqdata.get("inst_end","--")
    time_start = reqdata.get("time_start","--")
    time_end = reqdata.get("time_end","--")
    criterion = reqdata.get("criterion","--")

    fig_name = "{};{};{};{};{};{};{};{};{};{};.json".format(model,num,testType,testPhase,key1,key2,inst_start,inst_end,time_start,time_end)
    fig_name = fig_name.replace('/','／')
    fig_name = fig_name.replace(':','：')
    # fig_name = fig_name.replace(';','；')


    fspath="{}/{}/img/{}".format(HISTORY_PATH,type_id,fig_name)
    print(fspath)
    if os.path.exists(fspath):
        f = open(fspath)
        insdata = []
        try:
            data = json.load(f)
            return json.dumps({"status":200,"message":"ok","data":data})
        except Exception as ex:
            print(ex)
            log.error("load json error,{}".format(ex))
            return json.dumps({"status":501,"message":"result file is broken", "data":{}})
        pass
    else:
        return json.dumps({"status":404,"message":"data not found", "data":{}})

@app.route ('/get_charts',method='POST')
def get_corr_charts():
    params = None
    type_id = request.query.type_id or None
    reqjson = request.json or {}
    print("jsondata:{}/{}".format(type_id,reqjson))

    params = reqjson.get("params",[])
    retdata = []
    for reqdata in params:
        model = reqdata.get("model","--")
        num = reqdata.get("faci","--")
        testType = reqdata.get("testType","--")
        testPhase = reqdata.get("testPhase","--")
        key1 = reqdata.get("key1","--")
        key2 = reqdata.get("key2","--")
        inst_start = reqdata.get("inst_start","--")
        inst_end = reqdata.get("inst_end","--")
        time_start = reqdata.get("time_start","--").split('.')[0]
        time_end = reqdata.get("time_end","--").split('.')[0]
        criterion = reqdata.get("judge","--")

        fig_name = "{};{};{};{};{};{};{};{};{};{};.json".format(model,num,testType,testPhase,key1,key2,inst_start,inst_end,time_start,time_end)
        fig_name = fig_name.replace('/','／')
        fig_name = fig_name.replace(':','：')
        # fig_name = fig_name.replace(';','；')


        fspath="{}/{}/img/{}".format(HISTORY_PATH,type_id,fig_name)
        if os.path.exists(fspath):
            print(fspath," is found")
            f = open(fspath)
            insdata = []
            try:
                data = json.load(f)
                d = {
                    "params1": data["params1"],
                    "params2": data["params2"],
                    "plot_X": data["plot_X"],
                    "plot_Y": data["plot_Y"]
                }
                retdata.append(d)
            except Exception as ex:
                print("load file error",ex)
                log.error("load json error,{}".format(ex))
                continue
                #return json.dumps({"status":501,"message":"result file is broken", "data":{}})
        else:
            print("file is not found {}".format(fspath))
    print("total lines:",len(retdata))
    return json.dumps({"status":200,"message":"ok","data":retdata})

@app.route ('/getinst_pair',method='GET')
def get_instructs():
    params = None
    type_id = request.query.type_id or None
    print("{}".format(type_id))
    fspath="{}/{}/result.json".format(HISTORY_PATH,type_id)
    if os.path.exists(fspath):
        f = open(fspath,encoding="utf-8")
        insdata = []
        try:
            data = json.load(f)
            insdata = list(data.keys())
            returndata = []
            for inskey in insdata:
                keypair = inskey.split("&")
                kdata = {
                    "pair":inskey,
                    "key1":keypair[0].strip(),
                    "key2":keypair[1].strip()
                }
                returndata.append(kdata)
            print(returndata)
            return json.dumps({"status":200,"message":"ok","data":returndata})
        except Exception as ex:
            print(ex)
            log.error("load json error,{}".format(ex))
            return json.dumps({"status":501,"message":"result file is broken", "data":{}})
        pass
    else:
        return json.dumps({"status":404,"message":"data not found", "data":{}})

@app.route ('/getinst',method='POST')
def get_instructs():
    params = None
    type_id = request.query.type_id or None
    reqdata = request.json or {}
    print("json:{}/{}".format(type_id,reqdata))
    fspath="{}/{}/result.json".format(HISTORY_PATH,type_id)
    params =  reqdata.get("params",[])
    if len(params)==0:
        log.info("invalid params request data")
        return {"status":404,"message":"params is not provided", "data":{}}
    if os.path.exists(fspath):
        f = open(fspath,encoding="utf-8")
        insdata = []
        try:
            data = json.load(f)
            #print(json.dumps(data))
            for pam in params:
                key = "{} & {}".format(pam.get("key1",""),pam.get("key2",""))
                #print(data.get(key))
                if key in data:
                    inslist = data.get(key,[])
                    for ins1 in inslist:
                        ins1["key1"] = pam.get("key1","")
                        ins1["key2"] = pam.get("key2","")
                        insdata.append(cn_key_to_en_keymap(ins1,type_id))
            return json.dumps({"status":200,"message":"ok","data":insdata})
        except Exception as ex:
            print(ex)
            log.error("load json error,{}".format(ex))
            return json.dumps({"status":501,"message":"result file is broken", data:{}})
        pass
    else:
        return {"status":404,"message":"data not found", "data":{}}


AlgoConfig.task_map = {}
AlgoConfig.TASK_STATUS = "idle"

class TaskProcessor(Thread):
   def __init__(self, threadID, algotype, params):
      Thread.__init__(self)
      self.threadID = threadID
      self.algotype = algotype
      self.params = params
      self.daemon = True
      self.resultList = []
   def appendResult(self,data):
       self.resultList.append(data)

   def getResult(self):
       return self.resultList

   def getMessage(self):
       if len(self.resultList)>0:
           return self.resultList.pop(0)
       else:
           return len(self.resultList)

   def run(self):
        print("run {}".format(self.algotype))
        import traceback
        try:
            if self.algotype=="corr":
                corr_run.run_corr(self.params)
            elif self.algotype=="jumpdetection":
                jump_detection.run_jump_detection(self.params)
            elif self.algotype=="peakdetection":
                peak_detection.peak_detection(self.params)
            elif self.algotype=="lstm":
                lstm_pred.lstm_detection(self.params)
        except Exception as ex:
            self.resultList.append("ERROR")
            print("============error:",ex)
            print(traceback.format_exc())
            log.error("========error")
        time.sleep(6)
        AlgoConfig.TASK_STATUS = "idle"
        AlgoConfig.task_map["current_task"] = None

        # if self.threadID in task_map:
        #     del task_map[self.threadID]
@app.route ('/post',method='POST')
def post_submit_analysis():
    queryparam = request.query_string
    data = request.json or {}
    print("json:",data)
    print('/post?{}'.format(queryparam))
    if "time" in queryparam:
        time_ = 'null'
        for param in data['params']:
            _time = getTime(data['roc'], data['num'], data['testype'],
            data['teststage'], param.split('/')[0], param.split('/')[1])
            print(_time)
            time_ = _time if _time is not 'null' else time_
        return time_

    taskid = "task_{}".format(time.time())
    algotype = None

    if "corr" in queryparam:
        algotype = "corr"
    elif "jumpdetection" in queryparam:
        algotype = "jumpdetection"
    elif "peakdetection" in queryparam:
        algotype = "peakdetection"
    elif "lstm" in queryparam:
        algotype = "lstm"
    if algotype!=None:
        AlgoConfig.TASK_STATUS = "busy"
        tp = TaskProcessor(taskid,algotype,data)
        AlgoConfig.task_map[taskid] = tp
        AlgoConfig.task_map["current_task"] = tp
        tp.start()
    return data
    #return {"taskid":taskid}

@app.route ('/task_status/<taskid>',method='get')
def get_task_status(taskid):
    print("get taskid:"+taskid)
    task = AlgoConfig.task_map.get(taskid,None)
    if task!=None:
        return {"status":200,"data":task.getResult()}
    return {"status":100,"data":[]}

@app.route ('/get')
def get_request():
    response.content_type = 'text/plain;charset=utf-8'
    queryparam = request.query_string
    paramdict = dict(request.query.decode("utf-8"))
    if not "fetch" in paramdict:
        print('/get?{}'.format(paramdict))

    if "status" == queryparam:
        return AlgoConfig.TASK_STATUS

    elif "fetch" == queryparam:
        # print(task_map)
        task = AlgoConfig.task_map.get("current_task",None)
        if task!=None:
            msg = task.getMessage()
        else:
            msg = "terminate"
        return msg
    elif "close" == queryparam:
        AlgoConfig.task_map["current_task"] = None
        return ""
    elif "jumpdetection" == queryparam:
        return static_file("jump_detection.json", root=BASE_DIR)
    elif "peakdetection" == queryparam:
        return static_file("peak_detection.json", root=BASE_DIR)
    elif "lstmdetection" == queryparam:
        return static_file("lstm_detection.json", root=BASE_DIR)
    # elif "time&" in queryparam:
    #     hbase_addr = queryparam.split('&')
    #     return getTime(hbase_addr[1], hbase_addr[2], hbase_addr[3], hbase_addr[4], hbase_addr[5], hbase_addr[6])
    elif "resultimg=corr" in queryparam:
        rocket_type = paramdict.get("rocket_type","--")
        rock_id = paramdict.get("rock_id","--")
        test_type = paramdict.get("test_type","--")
        test_stage = paramdict.get("test_stage","--")
        param1 = paramdict.get("param1","--")
        param2 = paramdict.get("param2","--")
        order1 = paramdict.get("order1","--")
        order2 = paramdict.get("order2","--")
        start_time = paramdict.get("start_time","--").split('.')[0].replace('+',' ')
        end_time = paramdict.get("end_time","--").split('.')[0].replace('+',' ')
        relation_type_id = paramdict.get("relation_type_id","--")

        fig_name = "{};{};{};{};{};{};{};{};{};{};.json".format(rocket_type,rock_id,test_type,test_stage,param1,param2,order1,order2,start_time,end_time)
        fig_name = fig_name.replace('/','／')
        fig_name = fig_name.replace(':','：')
        # fig_name = fig_name.replace(';','；')
        fspath="{}/Type_{}/img/{}".format(HISTORY_PATH,relation_type_id,fig_name)
        print(fspath)
        if os.path.exists(fspath):
            f = open(fspath)
            insdata = []
            try:
                data = json.load(f)
                return data
            except Exception as ex:
                print(ex)
                log.error("load json error,{}".format(ex))
                return {}
        else:
            return {}
    elif "resultimg=midcorr" in queryparam:
        rocket_type = paramdict.get("rocket_type","--")
        rock_id = paramdict.get("rock_id","--")
        test_type = paramdict.get("test_type","--")
        test_stage = paramdict.get("test_stage","--")
        param1 = paramdict.get("param1","--")
        param2 = paramdict.get("param2","--")
        order1 = paramdict.get("order1","--")
        order2 = paramdict.get("order2","--")
        start_time = paramdict.get("start_time","--").split('.')[0].replace('+',' ')
        end_time = paramdict.get("end_time","--").split('.')[0].replace('+',' ')
        relation_type_id = paramdict.get("relation_type_id","--")

        fig_name = "{};{};{};{};{};{};{};{};{};{};.png".format(rocket_type,rock_id,test_type,test_stage,param1,param2,order1,order2,start_time,end_time)
        fig_name = fig_name.replace('/','／')
        fig_name = fig_name.replace(':','：')
        # fig_name = fig_name.replace(';','；')
        fspath="{}/Type_{}/img/{}".format(HISTORY_PATH,relation_type_id,fig_name)
        print(fspath)
        if os.path.exists(fspath):
            # f = open(fspath)
            # insdata = []
            try:
                return static_file(fig_name, root="{}/Type_{}/img/".format(HISTORY_PATH,relation_type_id))
                # fspath
                # data = json.load(f)
                return data
            except Exception as ex:
                print(ex)
                log.error("load json error,{}".format(ex))
                return {}
        else:
            return {}
    elif "resultimg" in paramdict:
        rocket_type = paramdict.get("rocket_type","--")
        rock_id = paramdict.get("rock_id","--")
        test_type = paramdict.get("test_type","--")
        test_stage = paramdict.get("test_stage","--")
        param = paramdict.get("param","--")
        table = paramdict.get("table","--")
        relation_type_id = paramdict.get("relation_type_id","--")
        rtimg = paramdict.get("resultimg",None)
        train_params = paramdict.get("train_params","--")

        base_datapath = ""
        fname = ""
        if rtimg=="jumpdetection":
            base_datapath = "JumpDetection"
            fname = param
        elif rtimg=="peakdetection":
            base_datapath = "PeakDetection"
            fname = param
        else:
            base_datapath = "LSTM"
            fname = "{} & {}".format(param,train_params)

        fig_name = "{}/{}/{} & {} & {}/img/{}.json".format(rocket_type,table,rock_id,test_type,test_stage,fname)
        fspath="{}/{}/{}".format(HISTORY_PATH,base_datapath,fig_name)
        print("=================",base_datapath,fig_name)
        if os.path.exists(fspath):
            f = open(fspath)
            insdata = []
            try:
                data = json.load(f)
                return data
            except Exception as ex:
                print(ex)
                log.error("load json error,{}".format(ex))
                return {}
    elif "resulttxt" in paramdict:
        rocket_type = paramdict.get("rocket_type","--")
        rock_id = paramdict.get("rock_id","--")
        test_type = paramdict.get("test_type","--")
        test_stage = paramdict.get("test_stage","--")
        param = paramdict.get("param","--")
        table = paramdict.get("table","--")
        rtimg = paramdict.get("resulttxt",None)
        base_datapath = ""
        if rtimg=="jumpdetection":
            base_datapath = "JumpDetection"
        elif rtimg=="peakdetection":
            base_datapath = "PeakDetection"
        else:
            base_datapath = "LSTM"

        file_name = "{}/{}/{} & {} & {}/result.json".format(rocket_type,table,rock_id,test_type,test_stage)
        fspath="{}/{}/{}".format(HISTORY_PATH,base_datapath,file_name)
        print(fspath)
        if os.path.exists(fspath):
            f = open(fspath,encoding='utf-8')
            insdata = []
            try:
                data = json.load(f)
                return data[param]
            except Exception as ex:
                print(ex)
                log.error("load json error,{}".format(ex))
                return {}
    elif "historyinfo=corr" in queryparam:
        param1 = paramdict.get("param1","--")
        param2 = paramdict.get("param2","--")
        relation_type_id = paramdict.get("relation_type_id","7")
        pam = paramdict
        fspath="{}/Type_{}/result.json".format(HISTORY_PATH,relation_type_id)
        print("fspath:{}".format(fspath))

        insdata = []
        if os.path.exists(fspath):
            f = open(fspath,"r",encoding="utf-8")
            try:
                data = json.load(f)
                key = "{} & {}".format(pam.get("param1",""),pam.get("param2",""))
                print(key,data.get(key,[]))
                insdata.extend(data.get(key,[]))
                return json.dumps({"historyinfo":insdata})
            except Exception as ex:
                print(ex)
                log.error("load json error,{}".format(ex))
                return json.dumps({"historyinfo":insdata})
        else:
            print("fspath not found:{}".format(fspath))

            return json.dumps({"historyinfo":insdata})
    elif "historyinfo" in paramdict:
        rocket_type = paramdict.get("rocket_type","--")
        params = paramdict.get("param","7")
        table = paramdict.get("table","--")

        rtimg = paramdict.get("historyinfo",None)
        train_params = paramdict.get("params","--")
        base_datapath = ""
        fname = ""
        if rtimg=="jumpdetection":
            base_datapath = "JumpDetection"
            fname = "JumpDetection/{}/{}".format(rocket_type,table)
        elif rtimg=="peakdetection":
            base_datapath = "PeakDetection"
            fname = "PeakDetection/{}/{}".format(rocket_type,table)
        else:
            base_datapath = "LSTM"
            fname = "LSTM/{}/{}".format(rocket_type,table)


        fspath="{}/{}".format(HISTORY_PATH,fname)
        resultlist = []
        for file in os.listdir(fspath):
            resultfile = "{}/{}/{}".format(fspath,file,"result.json")
            print("searching:",file,resultfile)
            if os.path.exists(resultfile):
                print("searching:",file,resultfile)
                f = open(resultfile,encoding="utf-8")
                insdata = []
                try:
                    data = json.load(f)
                    if params in data:
                        resultlist.append([file,data[params]])
                except Exception as ex:
                    print(ex)
                    log.error("load json error,{}".format(ex))                
            else:
                print("not found:",file,resultfile)


        print("=================",base_datapath,fspath,resultlist)
        return json.dumps({"historyinfo":resultlist})

@app.route("/<url:re:.*>")
def match_all_other(url):
  log.info("url:"+url)
  file = WEB_DIR+"/"+url
  if os.path.exists(file):
      return static_file(url, root=WEB_DIR)
  response.content_type = 'application/json; charset=utf-8'
  #response.status_code = 200
  urlkey = "/"+url
  fullurl = request.url
  index = fullurl.find("/C7HealthMonitor")
  key="/"+url
  if index!=-1:
      key = fullurl[index:]
  if key in urlmapping:
      key = urlmapping.get(key,{})
  elif urlkey in urlmapping:
      key = urlmapping.get(urlkey,{})

  return PARAMS_DATA.get(key[1:],{})

if __name__ == '__main__':
    try:
        run(app,server='paste',host=str(sys.argv[1]), port=str(sys.argv[2]))
    except:
        run(app,server='paste',host='localhost', port=8000)
