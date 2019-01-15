from LibMedium.Daemon import Daemon
from LibMedium.Medium.Listener import Listener
from LibMedium.Medium.Listener.Application import InvocationEvent
from LibMedium.Messages.Event import Event

import time
import struct
import typing

daemon = Daemon("com.pcthingz.libmedium.test")

listener = Listener(daemon)

apps = set()


def handle_invocation(event: InvocationEvent):
    print(event.invocation.function)

    if(event.invocation.function == b"hello_world"):
        event.complete(b"Hello World!")

    elif(event.invocation.function == b"delay_echo"):
        # Wait five seconds and echo the first argument
        time.sleep(5)

        event.complete(event.invocation.args[0])

    elif(event.invocation.function == b"error_maker"):
        event.error("This bitch empty", 1)

    else:
        event.error("No such method to invoke", 0)

def handle_app(app):
    apps.add(app)
    print("New connection!")


listener.invoked.subscribe(handle_invocation)

listener.new_connection.subscribe(handle_app)

print("Ready")

count = 0

while True:
    time.sleep(10)
    event = Event(b"tick", struct.pack("!I", count))
    
    print("Sending tick %i" % count)
    for app in apps:
        if(app.alive):
            app.send_event(event)

    count += 1