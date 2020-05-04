import socket
import threading
import json
import time
from queue import Queue
from Helper.JsonHandler import JsonHandler
from Pipeline.Producer import Producer
from Manager.TwopcManager import TwoPhaseCommitManager
from Handler.LogHandler import LogHandler

'''
The receive manager handles two types of messages
1 - connect request
2 - the data from the primary node => pushes it to the queque
3 - Messages from the participants => to coordinate 2pc
'''

class SocketServer:

    def __init__(self, dataPipeline : Producer, twoPhaseManager : TwoPhaseCommitManager,log : LogHandler):
        self.State = False
        self._log = log
        self._dataPipeline = dataPipeline
        self._twoPhaseManager = twoPhaseManager
        jsonHandler = JsonHandler()
        socketConfig = jsonHandler.LoadJson('Config.json')
        self._socketAddress = (socketConfig['host'],socketConfig['port'])
        self._bufferSize = socketConfig['bufferSize']

        if(self.CreateSocket()):
            self._socket.listen(10)
            self._hcrThread = threading.Thread(target=self.HandleConnectionRequest)
            self._hcrThread.daemon = True
            self._hcrThread.start()

            #Waiting for all the client to join
            #time.sleep(30)
            self._thread = threading.Thread(target=self.PiplineConsumer)
            self._thread.daemon = True
            self._thread.start()
            self.run()

    def __del__(self):
        self.State = False
        self._socket.close()

    def run(self):
        while self.State:
            continue

    def CreateSocket(self):
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        try:
            self._socket.bind(self._socketAddress)
            return True
        except Exception as ex:
            print(str(ex))
            return False

    
    def HandleConnectionRequest(self):        
        while True:
            client, _ = self._socket.accept()
            threading.Thread(target=self.ClientMessageHandler,args=(client,)).start()

    
    def ClientMessageHandler(self,client : socket.socket):
        while True:
            try:
                messages = client.recv(self._bufferSize).decode('utf8')
                if messages:
                    print(messages)
                    msgJson = json.loads(messages)
                    if msgJson['type'] == "data":
                        self._dataPipeline.Produce(msgJson['payload'])
                    elif msgJson['type'] == "connectRequest":
                        self._twoPhaseManager._particpants[client] = client
					elif msgJson['type'] == "connectClose":
                        del self._twoPhaseManager._particpants[client]
                    else: 
                        self._twoPhaseManager.HandlerIncomingStates(msgJson,client)
            except Exception as ex:
                print(ex)
                self._log.LogtransactionError("Socket error",ex)
                break

    def PiplineConsumer(self):
        while True:
            try:
                item = self._dataPipeline.GetNext()
                while True:
                    if self._twoPhaseManager.StartTransaction(item):
                        self._dataPipeline.TaskDone()
                        self._twoPhaseManager._transactionPaused = True
                        break
            except:
                continue
