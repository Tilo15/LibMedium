from LibMedium.Specification.Item import Item
import LibMedium.Util
import struct

class type_boolean(Item):
    label = "boolean"

    @staticmethod
    def serialise(item):
        value = 0
        if(item):
            value = 255

        return struct.pack("!B", value)

    @staticmethod
    def deserialise(item):
        return struct.unpack("!B", item)[0] == 255


class type_int8(Item):
    label = "int8"

    @staticmethod
    def serialise(item):
        return struct.pack("!b", item)

    @staticmethod
    def deserialise(item):
        return struct.unpack("!b", item)[0]


class type_uint8(Item):
    label = "uint8"

    @staticmethod
    def serialise(item):
        return struct.pack("!B", item)

    @staticmethod
    def deserialise(item):
        return struct.unpack("!B", item)[0]


class type_int16(Item):
    label = "int16"

    @staticmethod
    def serialise(item):
        return struct.pack("!h", item)

    @staticmethod
    def deserialise(item):
        return struct.unpack("!h", item)[0]


class type_uint16(Item):
    label = "uint16"

    @staticmethod
    def serialise(item):
        return struct.pack("!H", item)

    @staticmethod
    def deserialise(item):
        return struct.unpack("!H", item)[0]


class type_int32(Item):
    label = "int32"

    @staticmethod
    def serialise(item):
        return struct.pack("!i", item)

    @staticmethod
    def deserialise(item):
        return struct.unpack("!i", item)[0]


class type_uint32(Item):
    label = "uint32"

    @staticmethod
    def serialise(item):
        return struct.pack("!I", item)

    @staticmethod
    def deserialise(item):
        return struct.unpack("!I", item)[0]


class type_int64(Item):
    label = "int64"

    @staticmethod
    def serialise(item):
        return struct.pack("!q", item)

    @staticmethod
    def deserialise(item):
        return struct.unpack("!q", item)[0]


class type_uint64(Item):
    label = "uint64"

    @staticmethod
    def serialise(item):
        return struct.pack("!Q", item)

    @staticmethod
    def deserialise(item):
        return struct.unpack("!Q", item)[0]


class type_float(Item):
    label = "float"

    @staticmethod
    def serialise(item):
        return struct.pack("!f", item)

    @staticmethod
    def deserialise(item):
        return struct.unpack("!f", item)[0]


class type_double(Item):
    label = "double"

    @staticmethod
    def serialise(item):
        return struct.pack("!d", item)

    @staticmethod
    def deserialise(item):
        return struct.unpack("!d", item)[0]


class type_string(Item):
    label = "string"

    @staticmethod
    def serialise(item):
        return item.encode("utf-8")

    @staticmethod
    def deserialise(item):
        return item.decode("utf-8")


class type_binary(Item):
    label = "binary"

    @staticmethod
    def serialise(item):
        return item

    @staticmethod
    def deserialise(item):
        return item


class type_array(Item):
    def __init__(self, name, inner_type):
        self.name = name
        self.inner_type = inner_type
        self.label = "*%s" % inner_type.label

    @staticmethod
    def serialise(items):
        return LibMedium.Util.pack_list(items)
            

    @staticmethod
    def deserialise(items):
        return LibMedium.Util.unpack_list(items)
