from TestDaemon import TestDaemonConnection

daemon = TestDaemonConnection()

daemon.tick.subscribe(lambda args: print("Ticked %i times" % args[0]))

print(daemon.hello_world())
print(daemon.delay_echo(b'Delay mate'))
daemon.error_maker()