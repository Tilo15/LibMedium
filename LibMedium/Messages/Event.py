from LibMedium.Messages import Message
import LibMedium.Util

class Event(Message):
    def __init__(self, name: bytes, *args):
        self.name = name
        self.args = args

    def serialise(self):
        items = [self.name,]
        items.extend(self.args)
        return LibMedium.Util.pack_list(items)

    @staticmethod
    def deserialise(data: bytes):
        items = LibMedium.Util.unpack_list(data)
        return Event(items[0], *items[1:])