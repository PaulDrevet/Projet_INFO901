from threading import Lock, Thread

from time import sleep

#from geeteventbus.subscriber import subscriber
#from geeteventbus.eventbus import eventbus
#from geeteventbus.event import event

#from EventBus import EventBus

from Message import Message
from Token import Token


class Process(Thread):
    nbProcessCreated = 0
    def __init__(self, name, nbProcess):
        Thread.__init__(self)

        self.nbProcess = nbProcess
        self.myId = Process.nbProcessCreated
        Process.nbProcessCreated +=1
        self.setName(name)

        self.alive = True
        self.start()
        
        
    @subscribe(threadMode = Mode.PARALLEL, onEvent=BroadcastMessage)
    def onBroadcast(self, event):
        if (event.emetteur != self.myId):
            self.horloge = max(self.horloge, event.getEstampillage()) + 1
            print(self.getName() + ' get message: ' + str(event.getContenu()) + "Horloge :" + str(self.horloge))
        
    def broadcast(self, contenu):
        self.horloge += 1
        m = BroadcastMessage(self.horloge, contenu, self.myId)
        print(self.getName() + " send: " + str(m.getContenu()) + "Horloge :" + str(self.horloge))
        PyBus.Instance().post(m)
        
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
        
    @subscribe(threadMode=Mode.PARALLEL, onEvent=Token)
    def onToken(self, event):
        if event.to == self.myId:
            if (self.tokenState == 'request'):
                self.horloge = max(self.horloge, event.estampillage) + 1
                self.tokenState == 'sc'
                print(self.getName() + " has entered SC." + time.ctime())
                sleep(3) # Simuler une interaction dans la section critique
                self.releaseSC()
            self.horloge += 1
            next_process_id = (self.myId + 1) % self.npProcess
            t = Token(self.horloge, next_process_id)
            PyBus.Instance().post(t)
                
            
                
    def requestSC(self):
        self.tokenState = 'request'
        while not self.tokenState == 'sc':
            print(self.getName() + " is waiting for the token...")
            sleep(2)
    
    def releaseSC(self): 
        self.tokenState = 'release'
        print(self.getName() + " has released the token.")
            

    def run(self):
        loop = 0
        while self.alive:
            sleep(3)
            
            self.requestSC()
            
            # if self.getName() == "P1":
            #     self.broadcast('Hello all !')
            # if self.getName() == "P2":
            #    self.sendTo(0, 'Hello !')

            loop+=1
        print(self.getName() + " stopped")
    
    def stop(self):
        self.alive = False

    def waitStopped(self):
        self.join()
    
    
        
        
