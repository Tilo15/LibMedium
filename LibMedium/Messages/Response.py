from LibMedium.Messages import Message
import LibMedium.Util
import uuid

class Response(Message):
    def __init__(self, call_id: uuid.UUID, response: bytes):
        self.call_id = call_id.bytes
        self.response = response

    def serialise(self):
        return self.call_id + self.response

    @staticmethod
    def deserialise(data: bytes):
        return Response(uuid.UUID(bytes=data[:16]), data[16:])