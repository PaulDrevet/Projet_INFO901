class Message():
    def __init__(self, estampillage, contenu, to):
        self.contenu = contenu
        self.estampillage = estampillage
        self.to = to

    def getEstampillage(self):
        return self.estampillage
    
    def getContenu(self):
        return self.contenu
    
    def getTo(self):
        return self.to