import sys
def task_message(msg):
    if "current_task" in AlgoConfig.task_map:
        proc = AlgoConfig.task_map['current_task']
    if proc==None:
        sys.stdout.write(msg)
        sys.stdout.flush()
    else:
        proc.appendResult(msg)
class AlgoConfig():
    __shared_data = {}
    def __init__(self):        
        print("global config created")
        self.__dict__ = self.__shared_data
        self.task_map = {}
        self.TASK_STATUS = "idle"
AlgoConfig.task_message = task_message
AlgoConfig.TASK_STATUS = "idle"
AlgoConfig.task_map = {}