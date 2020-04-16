import logging
import json_log_formatter
import json


'''LogsHandler handles all the log related works, it logs infos i.e. (all the requests and response) and errors
Seprate log file is maintained for transactionInfos, transactionErrors, ServerSwitchingInfo, ServerSwitchingErros
all the files will be in the log folder under handlers'''

class LogHandler:
    
    def __init__(self):
        print('LogHandler')
        try:
            #log formatter
            jsonFormat = json_log_formatter.JSONFormatter()
            #transactionLog
            transactionLogHandler = logging.FileHandler(filename="logs/transaction.json")
            transactionLogHandler.setFormatter(jsonFormat)
            self.transactionLogger = logging.getLogger('transaction')
            self.transactionLogger.addHandler(transactionLogHandler)
            self.transactionLogger.setLevel(logging.INFO)                                                                                                                                                                                          
            #error logger
            errorLogHandler = logging.FileHandler(filename="logs/error.json")
            errorLogHandler.setFormatter(jsonFormat)
            self.errorLogger = logging.getLogger('error')
            self.errorLogger.addHandler(errorLogHandler)
            self.errorLogger.setLevel(logging.ERROR)
            #data logger
            dataLogHandler = logging.FileHandler(filename="logs/data.json")
            dataLogHandler.setFormatter(jsonFormat)
            self.dataLogger = logging.getLogger('data')
            self.dataLogger.addHandler(dataLogHandler)
            self.dataLogger.setLevel(logging.INFO)
        except Exception as ex:
            print(str(ex))

    def LogtransactionInfo(self,message,state,transactionId,participantCount):
        self.transactionLogger.info(message,extra={'transactionId' : transactionId, 'state' : state, 'participantCount' : participantCount})

    def LogtransactionError(self,message,ex):
        self.errorLogger.error(message,extra={'Error' : str(ex)})

    def DataLogger(self,transactionId,payload):
        try:
            self.dataLogger.info("Commited Transaction",extra={'payload' : payload, 'transactionId' : transactionId})
        except Exception as ex:
            print(str(ex))
