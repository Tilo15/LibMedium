from LibMedium.Messages import Message
import LibMedium.Util
import uuid

class Invocation(Message):
    def __init__(self, function: bytes, call_id: uuid.UUID, *args):
        self.function = function
        self.call_id = call_id.bytes
        self.args = args

    def serialise(self):
        items = [self.function, self.call_id]
        items.extend(self.args)
        return LibMedium.Util.pack_list(items)

    @staticmethod
    def deserialise(data: bytes):
        items = LibMedium.Util.unpack_list(data)
        return Invocation(items[0], uuid.UUID(bytes=items[1]), *items[2:])