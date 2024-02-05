from pathlib import Path
from datetime import datetime
from Log import Log
from Call import Call
import json


def validateDate(date,formate):
    try:
        datetime.strptime(date,formate)
        return True
    except ValueError:
        return False
    
class CallLogReader:
    logs = []
    activeCall = None
    init_session_call_id = None
    call_dict = {}
    call_id_dict ={}
    # def __init__(self):
        

    def read_file(self,path:Path):
        self.path = path
        file = open(self.path,'rb')
        lines = file.readlines()
        self.line_analyser(lines)

    def line_analyser(self,lines):
        length = len(lines)
        next_index = 0 
        while next_index < length: 
            line = lines[next_index].decode()
            time = line[1:24]
            timeObject = datetime.strptime(time,"%Y-%m-%d %H:%M:%S.%f")
            log = line[26:]
            while length > (next_index+1) and (len(lines[next_index+1].decode()) < 24 or validateDate(lines[next_index+1].decode()[1:24],"%Y-%m-%d %H:%M:%S.%f") == False):
                next_index += 1
                childLines = lines[next_index].decode()
                log += childLines
            
            logObj = Log(timeObject,log)
            # self.logDict[timeObject]=log
            self.logs.append(logObj)
            next_index += 1

        # self.readLogs(self.logs)

    def readLogs(self):
        length = len(self.logs)
        next_index = 0 
        while next_index < length:
            log = self.logs[next_index]
            print(next_index,log.log)
            if "CallManager makeCall ==>> START" in log.log:
               print(log.logTime)
               index = self.getOutgoingCallObject("Outgoing",next_index) 
               next_index = index
            elif " CallHandler PNS Message ==>> " in log.log:
               jsonStr = log.log.split(" CallHandler PNS Message ==>> ")[1]
               incomingData= json.loads(jsonStr)
               next_index = self.getIncomingCallObject(incomingData,next_index) 
            elif "MavMediaImpl createMediaSessionEx Begin " in log.log:
                callId = log.log.split("MavMediaImpl createMediaSessionEx Begin ")[1].strip()
                next_index = self.getMediaSession(callId,next_index)
            elif "Volley HTTP Request ==>> SESSION_STATUS_OFFERSDP :: requestCorrelator == " in log.log:
                # local offer for outgoing call and try to find 
                requstBodyStr = log.log.split("requestBody == ")[1]
                requestJson= json.loads(requstBodyStr)
                next_index = self.getOutgoingCallData(requestJson,next_index) 
            elif "CallHandler onCallAcceptConfirmed :: " in log.log:
                data = log.log.split("CallHandler onCallAcceptConfirmed :: ")[1]
                dictData = self.getDict(data)
                sessionId = dictData["callID"].replace(">>","").strip().lower()
                self.call_dict[sessionId].call_starts_at = log.logTime
            elif "CallHandler onCallConnected :: callID ==>> " in log.log:
                sessionId = log.log.split("CallHandler onCallConnected :: callID ==>> ")[1].strip().lower()
                
                self.call_dict[self.call_id_dict[sessionId]].call_starts_at = log.logTime
            elif "MavPeerConnection STATS REPORT:" in log.log:
                next_index = self.getStatsAndMos(log,next_index)
            elif "CallManager terminateCall" in log.log:
                # end call before accept 
                if self.activeCall is not None:
                    self.call_dict[self.activeCall.call_id].call_ends_at = log.logTime

            elif "CallHandler onCallEndConfirmed :: " in log.log:
                print(log.log)
                data = log.log.split("CallHandler onCallEndConfirmed ::")[1]
                dictData = self.getDict(data)
                callId = dictData["callID"].replace(">","").strip().lower()
                print("End of ", self.call_id_dict,"\n",callId)
                if callId in self.call_id_dict:
                    self.call_dict[self.call_id_dict[callId]].callQuality = dictData["callQuality"]
                    self.call_dict[self.call_id_dict[callId]].call_ends_at = log.logTime
                
                self.activeCall = None
            elif "CallHandler onReceivedCallEnded ::"in log.log:
                data = log.log.split("CallHandler onReceivedCallEnded ::")[1]
                dictData = self.getDict(data)
                callId = dictData["callID"].replace(">","").strip().lower()
                print("End of ", self.call_id_dict,"\n",callId)
                if callId in self.call_id_dict:
                    self.call_dict[self.call_id_dict[callId]].callQuality = dictData["callQuality"]
                    self.call_dict[self.call_id_dict[callId]].call_ends_at = log.logTime

            next_index += 1
        
    def getOutgoingCallObject(self,callDirection,index):
        call = Call(callDirection)
        call.call_initiate_at = self.logs[index].logTime
        index += 1
        while  "CallUtils putCallObjIntoHash :: callID ==>> " not in self.logs[index-1].log:
            if "CallUtils putCallObjIntoHash :: callID ==>>" in self.logs[index].log:
                data = self.logs[index].log.split("CallUtils putCallObjIntoHash :: callID ==>>")[1]
                callId = data.split("CallType:")[0].strip().lower()
                CallType = data.split("CallType:")[1].strip()
                call.append_call_id(callId,CallType)
            index += 1
        self.activeCall = call
        self.call_dict[call.call_id] = call
        return index-1
    
    def getIncomingCallObject(self,incomingCallData,index):
        index += 1
        if "sessionInvitationNotification" in incomingCallData:
            call = Call("Incoming")
            call.updateUserData(incomingCallData["sessionInvitationNotification"])
            call.call_initiate_at = self.logs[index].logTime
            while "CallUtils putCallObjIntoHash :: callID ==>> " not in self.logs[index-1].log:
                if "CallUtils putCallObjIntoHash :: callID ==>>" in self.logs[index].log:
                    data = self.logs[index].log.split("CallUtils putCallObjIntoHash :: callID ==>>")[1]
                    callId = data.split("CallType:")[0].strip().lower()
                    CallType = data.split("CallType:")[1].strip()
                    call.append_call_id(callId,CallType)
                    call.session_id = callId
                index += 1
                    
            self.activeCall = call
            self.call_id_dict[call.session_id] = call.call_id
            self.call_dict[call.call_id] = call
        return index-1


    def getMediaSession(self,callId,index):
        index += 1
        while  ("MavMediaImpl createMediaSessionEx End " + callId) not in self.logs[index-1].log:
            if "MediaManager onSessionCreated :: mediaSessionID ==>> " in self.logs[index].log:
                mediaSessionId = self.logs[index].log.split("MediaManager onSessionCreated :: mediaSessionID ==>> ")[1].strip()
                self.call_dict[callId.lower()].create_media(mediaSessionId)
            index += 1

        return index-1

    def getOutgoingCallData(self,requestBody,index):
        index += 1
        self.call_dict[self.activeCall.call_id].updateUserData(requestBody["vvoipSessionInformation"])
        self.call_dict[self.activeCall.call_id].add_local_sdp("Offer",requestBody["vvoipSessionInformation"]["sdp"])
        while  (" sessionID :: ==>> ") not in self.logs[index-1].log:
            if " sessionID :: ==>> " in self.logs[index].log:
                sessionId = self.logs[index].log.split(" sessionID :: ==>> ")[1].strip().lower()
                self.call_dict[self.activeCall.call_id].session_id = sessionId
                self.call_id_dict[sessionId] = self.activeCall.call_id
            index += 1
        return index-1
    
    def getStatsAndMos(self,log,index):
        index += 1
        stats = self.get_media_stats(log.log)
        mos = {}
        while index < len(self.logs) and ("MavPeerConnection CALCULATED ") not in self.logs[index-1].log:
            if "MavPeerConnection PP CALCULATED " in self.logs[index].log:
                ppCalDict = self.getStatsDict(self.logs[index].log.split("MavPeerConnection PP CALCULATED ")[1])
                mos["pp_calculated"] = ppCalDict
            elif "MavPeerConnection CALCULATED " in self.logs[index].log:
                callDict = self.getStatsDict(self.logs[index].log.split("MavPeerConnection CALCULATED ")[1])
                mos["calculated"] = callDict
            
            index += 1
        
        if self.activeCall is not None:
            self.call_dict[self.activeCall.call_id].add_stats(log.logTime,stats,mos)

        return index-1
    

    def get_media_stats(self,log:str):
        statsStr = log.split("MavPeerConnection STATS REPORT:")[1]
        logs = statsStr.split("\n")
        call_id = logs[0].split(":")[0]
        logs.pop(0)
        #  CallLog.call_dict[call_id]
        stats_dict = {}
        pairDict =  {}
        for logStr in logs:
            if "bweforvideo:" in logStr:
                data = logStr.split("bweforvideo:")[1]
                stats_dict["bwe"] = self.getBweData(data)
            elif "AUDIO SEND STATS:" in logStr:
                data = logStr.split("AUDIO SEND STATS:")[1]
                stats_dict["audio_sent"] = self.get_send_stats(data)
            elif "AUDIO RECEIVE STATS:" in logStr:
                data = logStr.split("AUDIO RECEIVE STATS:")[1]
                # print("sumit",data)
                stats_dict["audio_receive"] = self.get_recieve_stats(data)
                # print("\n\n test -> ",stats_dict["audio_receive"],"\n\n")
            elif "googCandidatePair " in logStr:
                data = logStr.split("googCandidatePair ")[1]
                pairId, data = self.get_candidatepair(data)
                pairDict[pairId] = data
                stats_dict["candidate_pair"] = pairDict
        return stats_dict
        # self.call_dict[self.activeCall.call_id].add_stats(log.logTime,stats_dict)
        # CallLog.call_dict[call_id].add_stats(self.logTime,stats_dict)
    
    def getBweData(self,data:str):
        return self.getStatsDict(data)
        

    def get_recieve_stats(self,data:str):
        dict = self.getStatsDict(data)
        return dict
    
    def get_send_stats(self,data:str):
        dict = self.getStatsDict(data)
        return dict
    def get_candidatepair(self,data):
        
        idKv = data.split(":{")[0]
        dataKv = data.split(":{")[1]
        pair_id = idKv.split(":")[1]
        dict = self.getStatsDict(dataKv)
        return pair_id,dict
    
    def getStatsDict(self,data:str):
        result = {}
        data  = data.replace("{","")
        data = data.replace("}","")
        kvPairs = data.split(",")
        # print(kvPairs)
        for kvPair in kvPairs:
            if "=" in kvPair:
                key = kvPair.split("=")[0].strip()
                value = kvPair.split("=")[1]
                result[key] = value

        return result

    def getDict(self,data:str):
        result = {}
        kvPairs = data.split("::")
        for kvPair in kvPairs:
            key = kvPair.split("==")[0].strip()
            value = kvPair.split("==")[1].strip()
            result[key] = value

        return result
        