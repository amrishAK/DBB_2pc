from DI import DependencyContainer
import http
import socketserver
import threading
from Handler.SocketHandler import SocketServer
from Manager.TwopcManager import TwoPhaseCommitManager
from flask import Flask
from flask_restful import Api, Resource, reqparse, request 
from flask import jsonify
import json

def SetupFlask():
    app = Flask(__name__)
    api = Api(app)

    class User(Resource):
        def get(self):
            size = DependencyContainer.quequeService().GetSize()
            return jsonify({"bufferSize" : size})
    
    class RecoveryResource(Resource):
        def post(self):
            print("reached")
            requestData = request.get_json()
            twopcManager : TwoPhaseCommitManager = DependencyContainer.twoPCService()
            twopcManager._requestToPause = True

            print(twopcManager._recovering)
            print(twopcManager._requestToPause)
            print(twopcManager._transactionPaused)

            while True:
                if twopcManager._transactionPaused:
                    break

            twopcManager._requestToPause = False

            logFile = open('logs/data.json', 'r') 
            dataArray = logFile.readlines() 

            dataList = []
            for data in dataArray:
                jsonData = json.loads(data)['payload']
                if jsonData['PayLoadToken'] > requestData['PayLoadToken']:
                    dataList.append(jsonData)
            
            #fetch files from log
            twopcManager._recovering = False

            return dataList


    api.add_resource(User, "/test")
    api.add_resource(RecoveryResource,"/recovery")
    app.run(host='0.0.0.0' , port=8080)

if __name__ == "__main__":
    
    try:
        twopcServer : SocketServer = DependencyContainer.socketService()
        SetupFlask()
        twopcServer.State = True
    except KeyboardInterrupt as ex:
        pass

        