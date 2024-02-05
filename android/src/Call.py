from datetime import datetime

class Call:
    session_id = None
    call_id = None
    media = None
    call_initiate_at = None
    call_starts_at = None
    call_ends_at = None
    
    lastMosDetails = None
    lastStatsDetails = None
    callQuality = None
    
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
    
    def add_stats(self,time:datetime,stats,mosDict):
    #    print("stats:->",self.call_id,stats)
       time = time.strftime("%Y-%m-%dT%H:%M:%S")
       statsObj = Stats(time,stats,mosDict)
       self.lastMosDetails = mosDict
       self.lastStatsDetails = stats
       self.stats[time] = statsObj
        
    

class Stats:
    def __init__(self,time:datetime, stats,mosDict):
        self.time = time
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