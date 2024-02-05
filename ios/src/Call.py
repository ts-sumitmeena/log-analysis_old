from datetime import datetime

class Call:
    session_id = None
    call_id = None
    media = None
    call_initiate_at = None
    isCallHold = False
    call_starts_at = None
    call_ends_at = None
    call_duration = None
    
    lastMosDetails = None
    lastStatsDetails = None
    callQuality = None
    incompleteCall = None
    wrgUrl = None
    networkTypes = []
    simType = None
    jitter_sum = 0
    latency_sum = 0
    mos_index=0
    receiverAddress = ""
    originatorAddress = ""
    originatorName = ""
    receiverName  = ""
    def __init__(self, callDirection):
        self.callDirection = callDirection
        self.stats = {}
    
    def updateUserData(self,data):
        self.receiverAddress = data["receiverAddress"]
        self.originatorAddress = data["originatorAddress"]
        self.originatorName = data["originatorName"]
        self.receiverName = data["receiverName"]
    
    def updateNetworkType(self,networkType):
        self.networkTypes.append(networkType)

    def append_call_id(self,call_id,callType):
        self.call_id = call_id
        self.call_type = callType

    def create_media(self,media_id):
       self.media =  Media(media_id)
    
    def add_local_sdp(self,sdpStr:str,stpType:str) -> None:
        sdp = SDP(stpType,sdpStr)
        self.media.local_sdp = sdp
    
    def add_remote_sdp(self,sdpStr:str,stpType:str):
        sdp = SDP(stpType,sdpStr)
        self.media.remote = sdp
    
    def incomplete_Call(self,time:datetime,status,reason):
        if self.incompleteCall is None:
            self.incompleteCall = IncompleteCall(time,status,reason)
    
    def add_stats(self,time:datetime,stats,mosDict):
       print("stats:->",self.call_id,stats)
           
       time = time.strftime("%Y-%m-%dT%H:%M:%S")
       statsObj = Stats(time,stats,mosDict,self.isCallHold)
       if mosDict is not None:
            jitter = int(mosDict["pp_calculated"]["jitter"])
            delay = int(mosDict["pp_calculated"]["delay"])
            self.jitter_sum += jitter
            self.latency_sum += delay
            self.mos_index += 1
            
            if self.lastMosDetails is None:
                self.lastMosDetails = mosDict
                avg_calculation = mosDict["calculated"]
                avg_calculation["jitter-min"] = jitter
                avg_calculation["jitter-max"] = jitter
                avg_calculation["latency-min"] = delay
                avg_calculation["latency-max"] = delay
                
                self.lastMosDetails["calculated"] = avg_calculation
                
            avg_calculation = self.lastMosDetails["calculated"]
            avg_calculation["jitter-min"] = min(int(avg_calculation["jitter-min"]),jitter)
            avg_calculation["jitter-max"] = max(int(avg_calculation["jitter-max"]),jitter)
            avg_calculation["latency-min"] = min(delay,int(avg_calculation["latency-min"]))
            avg_calculation["latency-max"] = max(delay,int(avg_calculation["latency-max"]))
            avg_calculation["jitter-avg"] = int(self.jitter_sum/self.mos_index)
            avg_calculation["latency-avg"] = int(self.latency_sum/self.mos_index)
            mosDict["calculated"] = avg_calculation
            print(avg_calculation)
       self.lastMosDetails = mosDict
       self.lastStatsDetails = stats
       self.stats[time] = statsObj
       
    def callEnd(self,time:datetime):
        self.call_ends_at = time
        if self.call_starts_at is not None:
            diff = self.call_ends_at - self.call_starts_at
            days, seconds = diff.days, diff.seconds
            hours = days * 24 + seconds // 3600
            minutes = (seconds % 3600) // 60
            seconds = seconds % 60
            self.call_duration = str(hours) + ":" +str(minutes) + ":" + str(seconds)
            
        
    
class IncompleteCall:
    def __init__(self,time:datetime,status,reason):
        self.time = time
        self.status = status
        self.reason = reason
        
class Stats:
    def __init__(self,time:datetime, stats,mosDict,isCallHold:bool):
        # print("isCallHold",isCallHold)
        self.time = time
        self.isCallHold = isCallHold
        self.stats = stats
        self.mos = mosDict

class Media:
    local_track_dict = {}
    remote_track_dict = {}
    local_sdp = None
    remote_sdp = None
    def __init__(self, media_session_id):
        self.media_session_id = media_session_id

    def add_local_track(self,track_id,track_type,stream_ids):
        track = Track(track_id, track_type,stream_ids,False)
        self.local_track_dict[track_id] = track

    def add_remote_track(self,track_id,track_type,stream_ids):
        track = Track(track_id, track_type,stream_ids,True)
        self.remote_track_dict[track_id] = track

class Track:
    def __init__(self,track_id,track_type,stream_ids,is_remote):
        self.track_id = track_id
        self.track_type = track_type
        self.stream_ids = stream_ids
        self.is_remote = is_remote

class SDP:
    def __init__(self,sdp_type,sdp):
        self.sdp_type = sdp_type
        self.sdp  = sdp