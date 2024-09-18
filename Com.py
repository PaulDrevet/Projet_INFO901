from pyeventbus3.pyeventbus3 import *
from Message import MessageDedie
from Message import MessageBroadCast
import threading


class Com():
    nbProcessCreated = 0
    def __init__(self, nbProcess):
        self.myId = Com.nbProcessCreated
        self.nbProcess = nbProcess
        self.name = "P" + str(self.myId)
        Com.nbProcessCreated += 1

        self.clock = 0
        self.semaphore = threading.Semaphore()
        self.mailbox = []
        
        PyBus.Instance().register(self, self)
    
    def getNbProcess(self):
        return Com.nbProcessCreated

    def getMyId(self):
        return self.myId
    
    def getName(self):
        return self.name
        
    def inc_clock(self):
        self.semaphore.acquire()
        self.clock += 1
        self.semaphore.release()
        

    @subscribe(threadMode = Mode.PARALLEL, onEvent=MessageDedie)
    def onReceive(self, event):
        if (event.dest == self.myId):
            self.clock = max(self.clock, event.getStamp())
            self.inc_clock()
            self.mailbox.append(event)
            print(self.getName() + ' get message: ' + str(event.getPayload()) + "Horloge :" + str(self.clock))


    def sendTo(self, message, dest):
        self.inc_clock()
        m = MessageDedie(message,self.clock, dest)
        PyBus.Instance().post(m)
        print(self.getName() + " send: " + str(m.getPayload()) +  "Horloge :" + str(self.clock))
        
        
    @subscribe(threadMode = Mode.PARALLEL, onEvent=MessageBroadCast)
    def onBroadcast(self, event):
        if (event.sender != self.myId):
            self.clock = max(self.clock, event.getStamp()) + 1
            print(self.getName() + ' get message: ' + str(event.getPayload()) + "Horloge :" + str(self.clock))
        
    def broadcast(self, contenu):
        self.clock += 1
        m = MessageBroadCast(contenu, self.clock, self.myId)
        print(self.getName() + " send: " + str(m.getPayload()) +  "Horloge :" + str(self.clock))
        PyBus.Instance().post(m)
