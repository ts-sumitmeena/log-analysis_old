from datetime import datetime
class Log:
    call_dict = {}
    media_dict = {}
    def __init__(self, time:datetime,log: str):
        self.log = log
        self.logTime = time