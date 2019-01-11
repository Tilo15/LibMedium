from LibMedium.Medium import Medium


class Daemon:
    def __init__(self, namespace: str):
        self.namespace = namespace
        
    def summon(self):
        return Medium(self)
    