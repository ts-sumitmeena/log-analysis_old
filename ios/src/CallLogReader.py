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
    isPrintLog = False
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
            time = line.split(":Thread")[0]
            timeObject = self.try_parsing_date(time)
            datetime.strptime(time,"%Y-%m-%dT%H:%M:%S:%f%z")
            # 
            # print(line)
            if "}" in line:
                log = line.split("}",1)[1]
                while length > (next_index+1) and ":Thread" not in lines[next_index+1].decode():
                    next_index += 1
                    childLines = lines[next_index].decode().replace("\n","\n")
                    log += childLines
                
                logObj = Log(timeObject,log)
                # self.logDict[timeObject]=log
                # print(timeObject,"==>",log)
                self.logs.append(logObj)
            next_index += 1

        # self.readLogs(self.logs)

    def readLogs(self):
        length = len(self.logs)
        next_index = 0 
        print("log length", length, "::", self.logs[0].log)
        while next_index < length:
            log = self.logs[next_index]
            # print(log.logTime," ==> ",log.log)
            if "[MAVCallKitManager startCall:Video:]" in log.log:
               #Start of Out going Call 
               print("outgoingcall",log.logTime)
               index = self.getOutgoingCallObject("Outgoing",next_index) 
               next_index = index

            elif "[MAVCallKitInterface reportIncomingCall:accountInfo:] Pending call is about to be answered" in log.log:
                print(log.logTime,"=>","REPORT INCOMING ")
                networkType = ""
                if "WIFIONLY" in log.log:
                    networkType = "WIFI"
                    
                elif "CMWIFI" in log.log:
                    networkType = "WIFI and DATA"
                    
                elif "CMONLY" in log.log:
                   networkType = "DATA"
                   
                next_index = self.getIncomingCallObject(networkType,next_index) 

            elif "-MAVSDK_CALL ==> Media ==> onSessionCreated : forMediaSessionID ==>>" in log.log:
                # Create Media
                print(log.logTime,"CREATE MEDIA ")
                info = log.log.split("MAVSDK_CALL ==> Media ==> onSessionCreated : forMediaSessionID ==>>")[1]
                callId = info.split("toCallID:")[1].strip()
                sessionId = info.split("toCallID:")[0].strip()
                self.getMediaSession(callId,sessionId)
                next_index += 1

            elif "[MAVSDKHttpSessionHandler performDefaultSessionTasks:]:[Signaling]:Request:KMAV_HTTP_CALL_MAKECALL" in log.log:
                # local offer for outgoing call and try to find 
                
                networkStatus = log.log.split("\"X-Access-Network-Info\" = \"")[1].split("\";")[0]
                networkType = "DATA"
                if "i-wlan-node-id=10c7539d456" in networkStatus:
                    networkType = "WIFI"
                    if " WiFi-Only" not in networkStatus:
                        networkType += " and DATA"
                
                simType = "RAKUTEN"
                if "otherOp=2" in networkStatus:
                    simType = "OTHER"

                print(log.logTime,"=>","KMAV_HTTP_CALL_MAKECALL ",networkType, "Network Type => ",simType )
                requstBodyStr = log.log.split("vvoipSessionInformation = ")[1].split("};")[0]
                # requestJson= json.loads(requstBodyStr)
                request = self.addKV(requstBodyStr)
                next_index = self.getOutgoingCallData(request,networkType,simType,next_index) 
            elif "MAVSDK_CALL ==> WebSocket SessionStatusNotification status: ==>>forwarded" in log.log:
                print(log.logTime,"Index =>",next_index,"=>","forwarded ")
                while  ("-MAVSDK_CALL ==> Get Call Object For SessionID:") not in self.logs[next_index-1].log:
                    print(log.logTime,"Index =>",next_index,"=>","forwarded 1")
                    if "-MAVSDK_CALL ==> Get Call Object For SessionID:" in self.logs[next_index].log:
                        print(log.logTime,"Index =>",next_index,"=>","forwarded 2")
                        sessionId = self.logs[next_index].log.split("-MAVSDK_CALL ==> Get Call Object For SessionID:")[1].strip().lower()
                        self.call_dict[self.call_id_dict[sessionId]].incomplete_Call(log.logTime,"FORWARDED","Call Forward to voice mail.")
                    
                    next_index += 1
                        
            elif "MAVSDK_CALL ==> WebSocket SessionStatusNotification status: ==>>terminated" in log.log:
                print(log.logTime,"Index =>",next_index,"=>","terminated ")
                previous_index  = next_index ; 
                while  ("-MAVSDK_CALL ==> reason ") not in self.logs[previous_index].log:
                    if "-MAVSDK_CALL ==> reason " in self.logs[previous_index-1].log:
                        reason = self.logs[previous_index-1].log.split("-MAVSDK_CALL ==> reason ")[1]
                    
                    previous_index -= 1
                    
                     
                
                while  ("-MAVSDK_CALL ==> Get Call Object For SessionID:") not in self.logs[next_index-1].log:
                    print(log.logTime,"Index =>",next_index,"=>","terminated 1")
                    if "-MAVSDK_CALL ==> Get Call Object For SessionID:" in self.logs[next_index].log:
                        print(log.logTime,"Index =>",next_index,"=>","terminated 2")
                        sessionId = self.logs[next_index].log.split("-MAVSDK_CALL ==> Get Call Object For SessionID:")[1].strip().lower()
                        if sessionId in self.call_id_dict and self.call_dict[self.call_id_dict[sessionId]].call_starts_at is None:
                            self.call_dict[self.call_id_dict[sessionId]].incomplete_Call(log.logTime,"TERMINATE",reason)

                    next_index += 1        

            elif "-MAVSDK_CALL ==> WebSocket SessionStatusNotification status: ==>>connected" in log.log:
                print(log.logTime,"Index =>",next_index,"=>","connected ")
                self.isPrintLog = False
                while  ("-MAVSDK_CALL ==> Get Call Object For SessionID:") not in self.logs[next_index-1].log:
                    # print(log.logTime,"Index =>",next_index,"=>","connected 1")
                    if "-MAVSDK_CALL ==> Get Call Object For SessionID:" in self.logs[next_index].log:
                        # print(log.logTime,"Index =>",next_index,"=>","connected 2")
                        sessionId = self.logs[next_index].log.split("-MAVSDK_CALL ==> Get Call Object For SessionID:")[1].strip().lower()
                        if self.activeCall is None:
                            # self.call_dict[callId].call_ends_at
                            if sessionId in self.call_id_dict and self.call_dict[self.call_id_dict[sessionId]].call_ends_at is None:
                                self.activeCall = self.call_dict[self.call_id_dict[sessionId]]
                                break
                        print(sessionId," :  ", self.activeCall.session_id)
                        if  self.activeCall is not None and self.activeCall.session_id == sessionId:
                            print(sessionId," :  2", self.activeCall.session_id)
                            self.call_dict[self.call_id_dict[sessionId]].call_starts_at = log.logTime
                    next_index += 1
                    
            elif "MAVSDK_CALL ==> Event To Perform Next : Media SetRemoteSdp Failure" in log.log:
                print("Failure")
                while  ("MAVSDK_CALL ==> Call State After Event:CallEnding for SessionID:") not in self.logs[next_index-1].log:
                    if "MAVSDK_CALL ==> Call State After Event:CallEnding for SessionID:" in self.logs[next_index].log:
                        sessionId = self.logs[next_index].log.split("MAVSDK_CALL ==> Call State After Event:CallEnding for SessionID:")[1].strip().lower()
                        if self.call_dict[self.call_id_dict[sessionId]].call_starts_at is None:
                            self.call_dict[self.call_id_dict[sessionId]].incomplete_Call(log.logTime,"FAIL","Fail to set remote SDP")
                        
                    next_index += 1
                
            elif "MAVSDK_CALL ==> Request From App: MAVSDK_CALL_ACCEPT_REQ" in log.log:
                print(log.logTime,"=>","AcceptCall ")
                while  ("MAVSDK_CALL ==> Get Call Object For SessionID:") not in self.logs[next_index-1].log:
                    if "MAVSDK_CALL ==> Get Call Object For SessionID:" in self.logs[next_index].log:
                        sessionId = self.logs[next_index].log.split("-MAVSDK_CALL ==> Get Call Object For SessionID:")[1].strip().lower()
                        print(log.logTime,"Index =>",next_index,"=>","AcceptCall 2")
                        if self.activeCall is None:
                            # self.call_dict[callId].call_ends_at
                            # print(self.call_dict)
                            if self.call_dict[self.call_id_dict[sessionId]].call_ends_at is None:
                                self.activeCall = self.call_dict[self.call_id_dict[sessionId]]
                                break

                        if  self.activeCall is not None and self.activeCall.session_id == sessionId:
                            self.call_dict[self.call_id_dict[sessionId]].call_starts_at = log.logTime
                    next_index += 1

            elif "MAVSDK_CALL ==> Request From App: MAVSDK_CALL_HOLD_REQ" in log.log:
                print(log.logTime,"=>","Hold initiate ")
                while  ("MAVSDK_CALL ==> Get Call Object For SessionID:") not in self.logs[next_index-1].log:
                    if "MAVSDK_CALL ==> Get Call Object For SessionID:" in self.logs[next_index].log:
                        sessionId = self.logs[next_index].log.split("-MAVSDK_CALL ==> Get Call Object For SessionID:")[1].strip().lower()
                        print(log.logTime,"Index =>",next_index,"=>","Call Hold Initiate 2")
                        self.call_dict[self.call_id_dict[sessionId]].isCallHold = True
                    next_index += 1

            elif "MAVSDK_CALL ==> Request From App: MAVSDK_CALL_UNHOLD_REQ" in log.log:
                print(log.logTime,"=>","unHold initiate ")
                while  ("MAVSDK_CALL ==> Get Call Object For SessionID:") not in self.logs[next_index-1].log:
                    if "MAVSDK_CALL ==> Get Call Object For SessionID:" in self.logs[next_index].log:
                        sessionId = self.logs[next_index].log.split("-MAVSDK_CALL ==> Get Call Object For SessionID:")[1].strip().lower()
                        print(log.logTime,"Index =>",next_index,"=>","Call Hold unHold 2")
                        self.call_dict[self.call_id_dict[sessionId]].isCallHold = False
                    next_index += 1
            elif "[MAVCallKitInterface remoteCallHoldConfirmed:]: callId:" in log.log:
                print(log.logTime,"=>","remote hold ")
                sessionId = self.logs[next_index].log.split("[MAVCallKitInterface remoteCallHoldConfirmed:]: callId:")[1].strip().lower()
                self.call_dict[self.call_id_dict[sessionId]].isCallHold = True
                next_index += 1

            elif "[MAVCallKitInterface remoteCallUNHoldConfirmed:]: callId:" in log.log:
                print(log.logTime,"=>","remote unhold")
                sessionId = self.logs[next_index].log.split("[MAVCallKitInterface remoteCallUNHoldConfirmed:]: callId:")[1].strip().lower()
                self.call_dict[self.call_id_dict[sessionId]].isCallHold = False
                next_index += 1

            # MAVSDK_CALL ==> Response To App:MAVSDK_CALL_REMOTEHOLD_CNF
            elif "[MEDIA] STATS REPORT For " in log.log:
                print(log.logTime,"=>","STATS ")
                next_index = self.getStatsAndMos(log,next_index)
                
            elif "Request From App: MAVSDK_CALL_REJECT_REQ" in log.log:
                print(log.logTime,"Index =>",next_index,"=>","Call Reject ")
                while  ("-MAVSDK_CALL ==> Get Call Object For SessionID:") not in self.logs[next_index-1].log:
                    print(log.logTime,"Index =>",next_index,"=>","forwarded 1")
                    if "-MAVSDK_CALL ==> Get Call Object For SessionID:" in self.logs[next_index].log:
                        print(log.logTime,"Index =>",next_index,"=>","forwarded 2")
                        sessionId = self.logs[next_index].log.split("-MAVSDK_CALL ==> Get Call Object For SessionID:")[1].strip().lower()
                        self.call_dict[self.call_id_dict[sessionId]].incomplete_Call(log.logTime,"REJECT","Call reject by MT.")
                        self.call_dict[self.call_id_dict[sessionId]].callEnd(log.logTime)
                        
                    next_index += 1
                    
            elif "CallManager terminateCall" in log.log:
                # end call before accept 
                print(log.logTime,"CallManager terminateCall ")
                if self.activeCall is not None:
                    self.call_dict[self.activeCall.call_id].callEnd(log.logTime)

            elif "EndCallConfirmed session we are looking yet is " in log.log:
                
                callId = log.log.split("EndCallConfirmed session we are looking yet is ")[1].strip().lower()
                print(log.logTime,"Index =>",next_index,"=>",callId,"EndCallConfirmed ")
                # print("End of ", self.call_id_dict,"\n",callId)
                if callId in self.call_dict:
                    self.call_dict[callId].callEnd(log.logTime)
                    if self.call_dict[callId].call_starts_at is None:
                        self.call_dict[callId].incomplete_Call(log.logTime,"TERMINATE","Call Terminate by MO.")
                
                self.activeCall = None

            next_index += 1
        
    def getOutgoingCallObject(self,callDirection,index):
        call = Call(callDirection)
        call.call_initiate_at = self.logs[index].logTime
        index += 1
        callType = "Audio"
        while  "Get Call Object For SessionID:" not in self.logs[index-1].log:
            if "Get Call Object For SessionID:" in self.logs[index].log:
                callId = self.logs[index].log.split("Get Call Object For SessionID:")[1].strip().lower()
                call.append_call_id(callId,callType)
            index += 1
        
        print("outgoing call Checking =>",call.call_id)
        self.activeCall = call
        self.call_dict[call.call_id] = call
        return index-1
    
    def getIncomingCallObject(self,networkType,index):
        index += 1
        call = Call("Incoming")
        call.call_initiate_at = self.logs[index].logTime
        call.updateNetworkType(networkType)
        while "MAVSDK_CALL ==> Create New Call Object For Incoming Call" not in self.logs[index-1].log:
            if "Data SIM MCC:" in self.logs[index].log:
                simType = self.logs[index].log.split("name: ")[1]
                call.simType = simType
            
            if "[Callkit] url " in self.logs[index].log:
                wrgUrl = self.logs[index].log.split("[Callkit] url https://")[1].split(".rcs.mobile.rakuten.co.jp")[0]
                call.wrgUrl = wrgUrl
                
            if "[Callkit] originatorAddress " in self.logs[index].log:
                data = self.logs[index].log.split("[Callkit] originatorAddress ")[1]
                originatorAddress = data.split("receiverName")[0]
                data = data.split("receiverName")[1]
                receiverName = data.split("receiverAddress")[0]
                receiverAddress = data.split("receiverAddress")[1]
                call.receiverAddress = receiverAddress
                call.originatorAddress = originatorAddress
                call.receiverName = receiverName


            if "-[MAVCallKitInterface reportIncomingCall:accountInfo:]_block_invoke ==> in callkit sync queue " in self.logs[index].log:
                callID = self.logs[index].log.split("-[MAVCallKitInterface reportIncomingCall:accountInfo:]_block_invoke ==> in callkit sync queue ")[1]
                callId = callID.strip().lower()
                call.append_call_id(callId,"Audio")
                call.session_id = callId
            index += 1

        print(self.logs[index].logTime , "Checking =>",call.session_id)     
        self.activeCall = call
        self.call_id_dict[call.session_id] = call.call_id
        self.call_dict[call.call_id] = call
        return index-1


    def getMediaSession(self,callId,mediaSessionId):
        self.call_dict[callId.lower()].create_media(mediaSessionId)

    def getOutgoingCallData(self,requestBody,networkType,simType,index):
        index += 1
        if self.activeCall != None:
            self.call_dict[self.activeCall.call_id].updateUserData(requestBody)
            self.call_dict[self.activeCall.call_id].updateNetworkType(networkType)
            self.call_dict[self.activeCall.call_id].simType = simType
            self.call_dict[self.activeCall.call_id].add_local_sdp("Offer",requestBody["sdp"])
            wrgUrl = None
            while index < len(self.logs) and  ("MAVSDK_CALL ==> Call State After Event:PreEstablished for SessionID:") not in self.logs[index-1].log:
                if "-MAVSDK_CALL ==> HTTP reqType:" in self.logs[index].log:
                    if wrgUrl is None:
                        wrgUrl = self.logs[index].log.split("resourceUrl:https://")[1].split(".rcs.mobile.rakuten.co.jp")[0].strip().lower()
                        self.call_dict[self.activeCall.call_id].wrgUrl = wrgUrl
                    
                if "MAVSDK_CALL ==> Call State After Event:PreEstablished for SessionID:" in self.logs[index].log:
                    sessionId = self.logs[index].log.split("MAVSDK_CALL ==> Call State After Event:PreEstablished for SessionID:")[1].strip().lower()
                    self.call_dict[self.activeCall.call_id].session_id = sessionId
                    
                    self.call_id_dict[sessionId] = self.activeCall.call_id
                index += 1
        return index-1
    
    def getStatsAndMos(self,log,index):
        index += 1
        session_id, stats = self.get_media_stats(log.log)
        mos = {}
        print("==>",session_id)
        if session_id not in self.call_dict:
            return index
        
        while index < len(self.logs) and "[MAVSDKCSVFileHelper writeToFile:theFileName:dictPath:uniqueKey:] ==>" not in self.logs[index-1].log:
            if "MavMediaSession computeMOS::::theActiveCode:]: PP CALCULATED" in self.logs[index].log:
                ppCalDict = self.getStatsDict(self.logs[index].log.split("MavMediaSession computeMOS::::theActiveCode:]: PP CALCULATED ")[1])
                mos["pp_calculated"] = ppCalDict
            elif "[MavMediaSession computeMOS::::theActiveCode:]: CALCULATED" in self.logs[index].log:
                callDict = self.getStatsDict(self.logs[index].log.split("[MavMediaSession computeMOS::::theActiveCode:]: CALCULATED ")[1])
                mos["calculated"] = callDict
            
            index += 1
        
        if "calculated" in mos and "pp_calculated" in mos:
            self.call_dict[session_id].add_stats(log.logTime,stats,mos)
        else:
            self.call_dict[session_id].add_stats(log.logTime,stats,None)

        return index-1
    

    def get_media_stats(self,log:str):
        statsStr = log.split("[MEDIA] STATS REPORT For ")[1]
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
                if "googActiveConnection" in data and data["googActiveConnection"] == 'true' and "googRemoteAddress" in data:
                    stats_dict["active_remote_address"] = data["googRemoteAddress"]
                
                # print("paird Id =>",pairId, "Data =>",data["googActiveConnection"])
                pairDict[pairId] = data
                stats_dict["candidate_pair"] = pairDict
        return call_id.lower(), stats_dict
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
    
   
    def addKV(self,data:str):
        result = {}
        data  = data.replace("{","")
        data = data.replace("}","")
        kvPairs = data.split(";")
        for kvPair in kvPairs:
            if "=" in kvPair:
                key = kvPair.split("=")[0].strip()
                value = kvPair.split("=")[1]
                result[key] = value

        return result

    def getStatsDict(self,data:str):
        result = {}
        data  = data.replace("{","")
        data = data.replace("}","")
        kvPairs = data.split(",")
        # print(kvPairs)
        for kvPair in kvPairs:
            if "=" in kvPair:
                key = kvPair.split("=")[0].strip()
                value = kvPair.split("=")[1].strip()
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
    
    def try_parsing_date(self, text):
        for fmt in ('%Y-%m-%dT%H:%M:%S:%f%z', '%d.%m.%Y'):
            try:
                return datetime.strptime(text, fmt)
            except ValueError:
                pass
        raise ValueError('no valid date format found')