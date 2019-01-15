from LibMedium.Medium.Listener.Application import InvocationEvent

import threading
import rx

class Defer:
    def __init__(self):
        # Create an attached lock and acquire it
        self._attached = threading.Lock()
        self._attached.acquire()

        self._event: InvocationEvent = None
        self._serialise = None
        self._except = None
        self.has_completed = False

    def _attach(self, event: InvocationEvent, serialiser, exception_handler):
        self._event = event
        self._serialise = serialiser
        self._except = exception_handler
        self._attached.release()


    def complete(self, result):
        self.has_completed = True

        with self._attached:
            self._event.complete(self._serialise(result))

    def error(self, e: Exception):
        self.has_completed = True

        with self._attached:
            self._event.error(*self._except(e))