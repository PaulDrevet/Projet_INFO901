from threading import Lock, Thread

from time import sleep

from Com import Com

class Process(Thread):
    
    def __init__(self, name, nbProcess):
        Thread.__init__(self)

        self.com = Com(nbProcess, name)
        
        self.nbProcess = self.com.getNbProcess()

        self.myId = self.com.getMyId()

        self.alive = True
        self.start()
    

    def run(self):
        loop = 0
            
        while self.alive:
            sleep(2)
            
            self.com.broadcastSynchrone("Hello", 0)
            print(self.com.getFirstMessage())
            
            sleep(1)
            
            loop+=1

    def stop(self):
        self.alive = False

    def waitStopped(self):
        self.join()
    