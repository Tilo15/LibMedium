from LibMedium.Daemon import Daemon
from LibMedium.Medium import RemoteCallException

daemon = Daemon("com.pcthingz.libmedium.test")

print("Summoning 'com.pcthingz.libmedium.test'")
medium = daemon.summon()
print("Ready")

def handle_event(event):
    print("\nGot event!")
    print(event.name)
    print(event.args)
    print("---\n")

medium.event_received.subscribe(handle_event)

print("\nInvoking 'hello_world'")
res = medium.invoke(b"hello_world")
print(res.response)

print("\nInvoking 'delay_echo' with 'echo!'")
res = medium.invoke(b"delay_echo", b"echo!")
print(res.response)

print("\nInvoking 'yeet' with 'echo!'")
try:
    res = medium.invoke(b"yeet", b"echo!")
    print(res.response)

except RemoteCallException as e:
    print("Error: %s\nError Number: %i" % (str(e), e.error_no))

print("\nGoing into infinate loop...")
while True:
    pass