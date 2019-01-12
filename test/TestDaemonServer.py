from TestDaemon.Server import TestDaemonServerBase
import TestDaemon.Exceptions
import TestDaemon.Models

import time

class TestDaemonServer(TestDaemonServerBase):
    
    def run(self):
        # This is called when the daemon is ready to communicate. Do your background tasks in here.
        # Communication is managed in a different thread, so feel free to place your infinate loop here.
        # A set of application connections can be found at 'self.applications'.
        # All your events are available to fire off at any time using 'self.event_name(*params)'.
        # To fire an event to a single application instance, pass in the application as the last
        # paramater in the event call, eg. 'self.event_name(param1, param2, application)'
        pass
        count = 0
        while True:
            time.sleep(1)
            self.tick(count)
            count += 1
    
    
    # Below are all the method calls you will need to handle.
    def hello_world(self) -> bytes:
        return b"Hello World!"
    
    
    def error_maker(self):
        raise TestDaemon.Exceptions.YeetException("This bitch empty")
    
    
    def delay_echo(self, message: bytes) -> bytes:
        time.sleep(5)
        return message
    
    
    def wrapper(self, data: TestDaemon.Models.TestModel, name: str) -> TestDaemon.Models.TestModelWrapper:
        return TestDaemon.Models.TestModelWrapper(name, data)
    
    
# If you run this module, it will run your daemon class above
if __name__ == '__main__':
    daemon = TestDaemonServer()

