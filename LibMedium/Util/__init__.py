import struct
import os

def get_socket_address(namespace: str, base_folder):
    return "%s/%s/socket" % (base_folder, namespace)


def create_socket_dir(namespace: str, base_folder):
    path = "%s/%s" % (base_folder, namespace)
    if(not os.path.exists(path)):
        os.mkdir(path, 711)

    # If the folder exists, maybe the socket is still there. Attempt to remove it if it is.
    elif(os.path.exists(get_socket_address(namespace, base_folder))):
        os.unlink(get_socket_address(namespace, base_folder))


def pack_list(list_data):
    message = b""
    for item in list_data:
        message += struct.pack("!I", len(item))
        message += item

    return message



def unpack_list(data: bytes):
    list_data = []
    message = data
    while len(message) != 0:
        size = struct.unpack("!I", message[0:4])[0]
        list_data.append(message[4:size+4])
        message = message[size+4:]
        
    return list_data