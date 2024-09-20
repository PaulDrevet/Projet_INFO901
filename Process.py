from threading import Lock, Thread

from time import sleep

from Com import Com

class Process(Thread):
    
    def __init__(self,name, nbProcess):
        Thread.__init__(self)

        self.com = Com(nbProcess)
        
        self.nbProcess = self.com.getNbProcess()

        self.myId = self.com.getMyId()
        self.setName(name)

        self.alive = True
        self.start()
    

    def run(self):
        loop = 0
            
        while self.alive:
            sleep(1)
            self.com.synchronize()
            sleep(1)
            
            loop+=1

    def stop(self):
        self.alive = False

    def waitStopped(self):
        self.join()
    