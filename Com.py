from pyeventbus3.pyeventbus3 import *
from time import sleep
from Message import MessageDedie
from Message import MessageBroadCast
from Message import MessageBroadcastSynchrone
from Message import MessageDedieSynchrone
from Message import MessageDedieSynchroneReply
from MessageId import MessageSendId
from MessageId import MessageRegenerateId
from Synchronization import Synchronization
from Token import Token
from State import State
import threading
from random import randint


class Com():
    def __init__(self, nbProcess, name):
        self.myId = -1
        self.nbProcess = nbProcess
        self.name = name

        self.clock = 0
        self.tokenState = State.NULL
        self.counterSynchro = nbProcess
        self.messageReceived = False
        self.semaphore = threading.Semaphore()
        self.mailbox = []
        
        self.generatedIds = []
        self.nbProcessIdToGenerate = nbProcess - 1
        
        PyBus.Instance().register(self, self)
        
        # if (self.nbProcessCreated == self.nbProcess):
        #     self.sendToken()
    
    def getNbProcess(self):
        return self.nbProcess

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
        
    def getFirstMessage(self):
        if (len(self.mailbox) > 0):
            return self.mailbox.pop(0).getPayload()
        else:
            return None

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
        
    # Message broadcast synchrone
    @subscribe(threadMode = Mode.PARALLEL, onEvent=MessageBroadcastSynchrone)
    def onBroadcastSynchrone(self, event):
        if (event.sender != self.myId):
            self.inc_clock_receive(event.getStamp())
            self.mailbox.append(event)
            self.messageReceived = True
    
    def broadcastSynchrone(self, message, _from):
        if (self.myId == _from):
            self.inc_clock()
            m = MessageBroadcastSynchrone(message, self.clock, self.myId)
            PyBus.Instance().post(m)
            self.synchronize()
        else :
            while (self.messageReceived == False):
                sleep(1)
            self.synchronize()
            self.messageReceived = False
    
    # Message dédié synchrone
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
        
    def sendToSync(self, message, dest):
        self.inc_clock()
        m = MessageDedieSynchrone(message, self.clock, dest)
        PyBus.Instance().post(m)
        while (self.messageReceived == False):
            sleep(1)
        self.messageReceived = False
    
    # Numérotation des processus
    def generateId(self):
        if (self.name == "P0"):
            self.myId = 0
        else :
            self.myId = randint(1, self.nbProcess)
            
    def numerotation(self):
        self.generateId()
        if self.name == "P0":
            self.waitForIds()  # P0 attend que tous les processus envoient leurs IDs
        else:
            print(f"{self.name} a généré l'ID {self.myId} et l'envoie à P0.")
            self.sendId(0)  # Envoyer l'ID à P0
          
    @subscribe(threadMode = Mode.PARALLEL, onEvent=MessageSendId)
    def onReceiveId(self, event):
        if (event.dest == self.myId):
            print("P0 a reçu l'ID " + str(event.payload))
            self.generatedIds.append(event.payload)            
                    
    def sendId(self, dest):
        m = MessageSendId(self.myId, dest)
        PyBus.Instance().post(m)
        
    # Générer un nouvel ID (autres processus)
    @subscribe(threadMode=Mode.PARALLEL, onEvent=MessageRegenerateId)
    def onRegenerateId(self, event):
        if event.dest == self.myId:
            print(f"{self.name} régénère son ID à la demande de P0.")
            self.generateId()
            self.sendId(0)  # Envoyer le nouvel ID à P0
    
    # Envoyer un messsage au processus pour régénérer l'id
    def requestRegenerateId(self, idToRegenerate):
        m = MessageRegenerateId(idToRegenerate)
        PyBus.Instance().post(m)
        print("Demande envoyé à tous les processus pour régénérer l'ID " + str(idToRegenerate)) 
        
    # Attendre que tous les processus envoient leurs IDs (P0)
    def waitForIds(self):
        while len(self.generatedIds) < self.nbProcessIdToGenerate:  # On attend que tous les processus (sauf P0) envoient un ID
            sleep(1)
            print(f"{len(self.generatedIds)} IDs reçus")
        self.checkForDuplicateIds()
        
    # Vérifier les doublons et gérer la régénération
    def checkForDuplicateIds(self):
        uniqueIds = set(self.generatedIds)
        if len(uniqueIds) == len(self.generatedIds):
            print("Tous les IDs sont uniques! Aucun ID à régénérer.")
        else:
            print("Des doublons ont été détectés! Demande de régénération.")
            duplicateIds = [id for id in self.generatedIds if self.generatedIds.count(id) > 1]
            self.nbProcessIdToGenerate = len(duplicateIds)
            print(set(duplicateIds))
            self.generatedIds = []  # Réinitialiser la liste et recommencer
            for id in set(duplicateIds):
                # On demande aux processus concernés de régénérer leur ID
                self.requestRegenerateId(id)
            self.waitForIds()  # Recommencer le processus d'attente d'IDs après la régénération
            
    

    
    
    
        

    
        
        
    
            
    


        
    
        
        
        

                
                
            