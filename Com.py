from pyeventbus3.pyeventbus3 import *
from time import sleep
from Message import MessageDedie
from Message import MessageBroadCast
from Message import MessageBroadcastSynchrone
from Message import MessageDedieSynchrone
from Message import MessageDedieSynchroneReply
from Synchronization import Synchronization
from Token import Token
from State import State
import threading


class Com():
    nbProcessCreated = 0
    def __init__(self, nbProcess):
        self.myId = Com.nbProcessCreated
        self.nbProcess = nbProcess
        self.name = "P" + str(self.myId)
        Com.nbProcessCreated += 1

        self.clock = 0
        self.tokenState = State.NULL
        self.counterSynchro = nbProcess
        self.messageReceived = False
        self.semaphore = threading.Semaphore()
        self.mailbox = []
        
        PyBus.Instance().register(self, self)
        
        # if (self.nbProcessCreated == self.nbProcess):
        #     self.sendToken()
    
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
    
    def inc_clock_receive(self, stamp):
        self.semaphore.acquire()
        self.clock = max(self.clock, stamp) + 1
        self.semaphore.release()

    # Message asynchrone dédié
    @subscribe(threadMode = Mode.PARALLEL, onEvent=MessageDedie)
    def onReceive(self, event):
        if (event.dest == self.myId):
            self.inc_clock_receive(event.getStamp())
            self.mailbox.append(event)
            print(self.getName() + ' get message: ' + str(event.getPayload()) + "Horloge :" + str(self.clock))


    def sendTo(self, message, dest):
        self.inc_clock()
        m = MessageDedie(message,self.clock, dest)
        PyBus.Instance().post(m)
        print(self.getName() + " send: " + str(m.getPayload()) +  "Horloge :" + str(self.clock))
        
    
    # Message asynchrone broadcast
    @subscribe(threadMode = Mode.PARALLEL, onEvent=MessageBroadCast)
    def onBroadcast(self, event):
        if (event.sender != self.myId):
            self.inc_clock_receive(event.getStamp())
            self.mailbox.append(event)
            print(self.getName() + ' get message: ' + str(event.getPayload()) + "Horloge :" + str(self.clock))
        
    def broadcast(self, contenu):
        self.inc_clock()
        m = MessageBroadCast(contenu, self.clock, self.myId)
        print(self.getName() + " send: " + str(m.getPayload()) +  "Horloge :" + str(self.clock))
        PyBus.Instance().post(m)
        
    # Gestion de section critique
    @subscribe(threadMode = Mode.PARALLEL, onEvent=Token)
    def onToken(self, event):
        if (event.to == self.myId):
            if (self.tokenState == State.REQUEST):
                self.tokenState = State.SC
                print(self.getName() + " get token" + "at " + time.strftime("%H:%M:%S", time.localtime()))
                while (self.tokenState == State.SC):
                    sleep(1)
            
            self.tokenState = State.RELEASE
            self.sendToken()
            
    def sendToken(self):
        t = Token((self.myId + 1) % self.nbProcess)
        PyBus.Instance().post(t)
                
    def requestSC(self):
        self.tokenState = State.REQUEST
        while (self.tokenState == State.REQUEST):
            sleep(1)
            
    def releaseSC(self):
        self.tokenState = State.RELEASE
    
    # Synchronisation
    @subscribe(threadMode = Mode.PARALLEL, onEvent=Synchronization)
    def onSynchronized(self, event):
        if (event.sender != self.myId):
            self.inc_clock_receive(event.stamp)
            self.counterSynchro -= 1
    
    def synchronize(self):
        self.inc_clock()
        PyBus.Instance().post(Synchronization(self.clock, self.myId))
        print(self.getName() + " wait for synchronization")
        while (self.counterSynchro > 1): # 1 car on recoit pas notre propre message
            print(self.getName() + " is waiting for " + str(self.counterSynchro) + " processes")
            sleep(1)
        print(self.getName() + " is synchronized")
        self.counterSynchro = self.nbProcess
        
    #Message broadcast synchrone
    @subscribe(threadMode = Mode.PARALLEL, onEvent=MessageBroadcastSynchrone)
    def onBroadcastSynchrone(self, event):
        if (event.sender != self.myId):
            self.inc_clock_receive(event.getStamp())
            self.mailbox.append(event)
            self.messageReceived = True
    
    def broadcastSynchrone(self, payload, _from):
        if (self.myId == _from):
            self.inc_clock()
            m = MessageBroadcastSynchrone(payload, self.clock, self.myId)
            PyBus.Instance().post(m)
            self.synchronize()
        else :
            while (self.messageReceived == False):
                sleep(1)
            self.synchronize()
            self.messageReceived = False
    
    #Message dédié synchrone
    @subscribe(threadMode = Mode.PARALLEL, onEvent=MessageDedieSynchrone)
    def receiveMessageSynchrone(self, event):
        if (event.dest == self.myId):
            self.inc_clock_receive(event.getStamp())
            self.mailbox.append(event)
            self.messageReceived = True
    
    def receiveFromSynchrone(self):
        while (self.messageReceived == False):
            sleep(1)
        lastMessage = self.mailbox.pop()
        m = MessageDedieSynchrone("", self.clock, lastMessage.sender)
        PyBus.Instance().post(m)
        self.messageReceived = False
    
    @subscribe(threadMode = Mode.PARALLEL, onEvent=MessageDedieSynchroneReply)
    def receiveMessageSynchroneReply(self, event):
        if (event.dest == self.myId):
            self.inc_clock_receive(event.getStamp())
            self.mailbox.append(event)
            self.messageReceived = True
        
    def sendToSync(self, _to, payload):
        self.inc_clock()
        m = MessageDedieSynchrone(payload, self.clock, _to)
        PyBus.Instance().post(m)
        while (self.messageReceived == False):
            sleep(1)
        self.messageReceived = False
    
        
        
    
            
    


        
    
        
        
        

                
                
            