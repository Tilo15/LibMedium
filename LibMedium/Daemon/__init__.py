from LibMedium.Medium import Medium


class Daemon:
    def __init__(self, namespace: str, base_folder = "/var/run"):
        self.namespace = namespace
        self.base_folder = base_folder
        
    def summon(self):
        return Medium(self)
    