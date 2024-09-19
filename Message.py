from abc import ABC

# Classe abstraite pour les messages génériques
class Message(ABC):
    def __init__(self, payload, stamp):
        self.payload = payload
        self.stamp = stamp
        
    def getPayload(self):
        return self.payload
    
    def getStamp(self):
        return self.stamp   
    
class MessageDedie(Message):
    def __init__(self, payload, stamp, dest):
        super().__init__(payload, stamp)
        self.dest = dest
        
class MessageBroadCast(Message):
    def __init__(self, payload, stamp, sender):
        super().__init__(payload, stamp)
        self.sender = sender
        
class MessageSynchronized(Message):
    def __init__(self, payload, stamp, sender):
        super().__init__(payload, stamp, sender)
