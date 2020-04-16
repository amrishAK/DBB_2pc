import pymongo
import socket
import json
from threading import Thread

class Participant:
    
    Status = True
    payload = None
    _currentTransationId = ""
    _currentState = ""

    def __init__(self):
        try:
            self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client.connect(('localhost', 7000))
            msg = {"type" : "connectRequest", "source" : "participant"}
            self.client.send(bytes(json.dumps(msg), "utf8"))

        except Exception as ex:
            print(ex)
        receive_thread = Thread(target=self.receive)
        receive_thread.daemon = True
        receive_thread.start()
        self.Run()

    def __del__(self):
        if self.Status:
            self.client.close()



    def Run(self):
        while self.Status:
            continue


    def receive(self):
        
        while True:
            try:
                msg = self.client.recv(1024).decode("utf8")
                if msg:
                    msgJson = json.loads(msg)
                    print(msgJson)
                    if msgJson['type'] == "ReadyToCommit":
                        #if it has become primary it will replay no and close the socket
                        _currentTransationId = msgJson['transactionId']
                        _currentState = "Prepare"
                        payload = msgJson['payload']
                        msg = {"transactionId" : _currentTransationId, "type" : "ReadyToCommit", "response": True}
                        self.client.send(bytes(json.dumps(msg), "utf8"))
                    elif msgJson['type'] == "Commit":
                        if msgJson['transactionId'] == _currentTransationId:
                            try:
                                _currentState = "Commit"
                                #save in the db
                                print("comitted" + str(payload))
                                msg = {"transactionId" : _currentTransationId,"type" : "Commit", "response": True}
                                self.client.send(bytes(json.dumps(msg), "utf8"))
                            except Exception as ex:
                                print(ex)
                    elif msgJson['type'] == "Abort":
                        _currentState = "Abort"
                        msg = {"transactionId" : _currentTransationId,"type" : "Abort", "response": True}
                        self.client.send(bytes(json.dumps(msg), "utf8"))
            except Exception as ex:
                continue


if __name__ == "__main__":
    Participant()