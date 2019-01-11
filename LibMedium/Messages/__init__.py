class Message:

    def serialise(self):
        raise NotImplementedError

    @staticmethod
    def deserialise(data: bytes):
        raise NotImplementedError