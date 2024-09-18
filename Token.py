class Token():
    def __init__(self, estampillage, to):
        self.free = True
        self.estampillage = estampillage
        self.to = to

    def isFree(self):
        return self.free
    
    def setFree(self, free):
        self.free = free
    