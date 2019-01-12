from TestDaemon import TestDaemonConnection
import TestDaemon.Exceptions
import TestDaemon.Models

daemon = TestDaemonConnection()

daemon.tick.subscribe(lambda args: print("Ticked %i times" % args[0]))

print(daemon.hello_world())
print(daemon.delay_echo(b'Delay mate'))

data = TestDaemon.Models.TestModel("Billy Barrow", 19)
wrapped = daemon.wrapper(data, "Student")
print(wrapped.name, wrapped.value.message, wrapped.value.count)


