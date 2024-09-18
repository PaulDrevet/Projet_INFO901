from pyeventbus3.pyeventbus3 import *


class Com():
    def __init__(self):
        self.clock = 0
        
        PyBus.Instance().register(self, self)
        
    def inc_clock(self):
        self.clock += 1


    def getEstampillage(self):
        return self.estampillage
    
    def getContenu(self):
        return self.contenu