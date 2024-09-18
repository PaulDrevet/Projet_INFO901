from pyeventbus3.pyeventbus3 import *
from AbstractMessage import Message
import threading


class Com():
    nbProcessCreated = 0
    def __init__(self):
        self.myId = Com.nbProcessCreated
        Com.nbProcessCreated += 1

        self.clock = 0
        self.semaphore = threading.Semaphore()
        self.mailbox = []
        
        PyBus.Instance().register(self, self)
    
    def getNbProcess(self):
        return Com.nbProcessCreated

    def getMyId(self):
        return self.myId
        
    def inc_clock(self):
        self.semaphore.acquire()
        self.clock += 1
        self.semaphore.release()
        

    @subscribe(threadMode = Mode.PARALLEL, onEvent=Message)
    def onReceive(self, event):
        if (event.to == self.myId):
            self.horloge = max(self.horloge, event.getEstampillage()) + 1
            print(self.getName() + ' get message: ' + str(event.getContenu()) + "Horloge :" + str(self.horloge))

    
    def sendTo(self, to, message):
        self.horloge += 1
        m = Message(self.horloge, message, to)
        print(self.getName() + " send: " + str(m.getContenu()) +  "Horloge :" + str(self.horloge))
        PyBus.Instance().post(m)