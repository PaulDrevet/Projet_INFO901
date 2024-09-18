from abc import ABC

# Classe abstraite pour les messages génériques
class Message(ABC):
    def __init__(self, payload, stamp):
        self.payload = payload
        self.stamp = stamp        
    
class MessageDedie(Message):
    def __init__(self, payload, stamp, to):
        super().__init__(payload, stamp)
        self.to = to
        
class MessageBroadCast(Message):
    def __init__(self, payload, stamp, sender):
        super().__init__(payload, stamp)
        self.sender = sender
