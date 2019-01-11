from LibMedium.Messages import Message
import uuid
import struct

class ErrorResponse(Message):
    def __init__(self, call_id: uuid.UUID, message: str, error_no: int = 0):
        self.call_id = call_id.bytes
        self.message = message
        self.error_no = error_no

    def serialise(self):
        return self.call_id + struct.pack("!I", self.error_no) + self.message.encode("utf-8")

    @staticmethod
    def deserialise(data: bytes):
        return ErrorResponse(uuid.UUID(bytes=data[:16]), data[20:].decode("utf-8"), struct.unpack("!I", data[16:20])[0])