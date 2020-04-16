from queue import Queue


class Producer:

    #initiate =queqe
    _quque = Queue()

    def Produce(self,data):
        print(data)
        self._quque.put(data)

    def GetSize(self):
        return self._quque.qsize()

    def GetNext(self):
        return self._quque.get()

    def TaskDone(self):
        self._quque.task_done()

