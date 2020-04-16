import json
import time
import uuid
from queue import Queue
from Pipeline.Producer import Producer
from Handler.LogHandler import LogHandler

class TwoPhaseCommitManager:

    def __init__(self,log:LogHandler):
        self._log = log
        self._particpants  = {}
        self._currentTransationId = ""
        self._currentState = ""
        self._messageReceived = {}
        self._particpantsCount = 0
        #recovery support
        self._requestToPause = False
        self._transactionPaused = True
        self._recovering = False


    def StartTransaction(self,data):
        try:
            #check all the participant status
            self.CheckSocketStatus()

            

            #request pause the transaction to retrive the log
            if self._requestToPause:
                self._transactionPaused = True
                self._recovering = True

            #pause the transation while recovery mechanism running
            if self._transactionPaused:
                if self._recovering:
                    return False
            
            #abord if there is no participant
            if len(self._particpants) == 0 : 
                self._transactionPaused = True
                return False
            else:
                self._transactionPaused = False

            #setting up for transaction
            self._particpantsCount = 0
            self._particpantsCount = len(self._particpants)
            self._currentTransationId = str(uuid.uuid1().hex)
            #phase 1
            self._currentState =  "Prepare"
            self._log.LogtransactionInfo("Phase-1",self._currentState,self._currentTransationId,str(self._particpantsCount))
            msg = {"payload" : data, "transactionId" : self._currentTransationId, "type" : "ReadyToCommit"}
            self.BroadCastCommand(json.dumps(msg))
            
            if self.WaitingRoutine():
                #phase 2
                #Check the received message
                for status in self._messageReceived:
                    if not self._messageReceived[status]:
                        #Abord Message
                        self._currentState = "Abort"
                        self._log.LogtransactionInfo("Phase-2",self._currentState,self._currentTransationId,str(self._particpantsCount))
                        msg = {"transactionId" : self._currentTransationId, "type" : "Abort"}
                        self.BroadCastCommand(json.dumps(msg))
                        return False

                # Commit Message
                self._currentState = "Commit"        
                self._log.LogtransactionInfo("Phase-2",self._currentState,self._currentTransationId,str(self._particpantsCount))
                msg = {"transactionId" : self._currentTransationId, "type" : "Commit"}
                self.BroadCastCommand(json.dumps(msg))
                
                _ = self.WaitingRoutine()
                
                self._log.DataLogger(self._currentTransationId,data)

                return True
            else:
                #Abord Message
                self._currentState = "Abort"
                self._log.LogtransactionInfo("Phase-2",self._currentState,self._currentTransationId,str(self._particpantsCount))
                msg = {"transactionId" : self._currentTransationId, "type" : "Abort"}
                self.BroadCastCommand(json.dumps(msg))
                return False
        except Exception as ex:
            print(ex)

        
        

    def BroadCastCommand(self,data):
        #clear message dic
        self._messageReceived = {}

        for node in list(self._particpants):
            try:
                node.send(bytes(data,'utf8'))
            except Exception as ex:
                self._log.LogtransactionError("Socket Error Broadcast",ex)
                del self._particpants[node]


    def CheckSocketStatus(self):
        for node in list(self._particpants):
            try:
                msg = {"type" : "SocketStatusCheck"}
                node.send(bytes(json.dumps(msg),'utf8'))
            except Exception as ex:
                self._log.LogtransactionError("Socket Error socketcheck",ex)
                del self._particpants[node]

    def WaitingRoutine(self):
        for attempt in range(5):
            waitTime = (attempt + 1) * 5.0
            time.sleep(waitTime)
            #check -> no of message received should be equal to the no of participant => yes: abort | no: proceeed 
            #check -> if any new participant joined => yes: abort | no: proceeed
            if len(self._particpants) != self._particpantsCount:
                return False 
            elif len(self._messageReceived) == self._particpantsCount:
                return True
            else:
                continue                        
        return False

    def HandlerIncomingStates(self, msgJson,client):
        if msgJson['type'] == "ReadyToCommit" or msgJson['type'] == "Commit" or msgJson['type'] == "Abort":
            if self._currentTransationId == msgJson['transactionId']:
                self._messageReceived[client] = msgJson['response']