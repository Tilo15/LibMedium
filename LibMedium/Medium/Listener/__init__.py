from LibMedium.Daemon import Daemon
from LibMedium.Medium.Listener.Application import Application
import LibMedium.Util

import socket
import threading
import rx

class Listener:
    def __init__(self, daemon: Daemon):
        self.daemon = daemon
        self._socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        LibMedium.Util.create_socket_dir(self.daemon.namespace)
        self._socket.bind(LibMedium.Util.get_socket_address(self.daemon.namespace))
        self.new_connection = rx.subjects.Subject()
        self.invoked = rx.subjects.Subject()
        self._running = True

        # Start listening for connections
        threading.Thread(target=self._listen).start()


    def _listen(self):
        self._socket.listen()
        while self._running:
            connection, address = self._socket.accept()
            self._handle_connection(connection)


    def _handle_connection(self, connection):
        app = Application(connection)
        app.invoked.subscribe(lambda i: self.invoked.on_next(i))

        # Start handling requests
        threading.Thread(target=app._listen).start()

        # Notify of new app
        self.new_connection.on_next(app)


    def stop(self):
        self._running = False
        self._socket.close()


    def __del__(self):
        self.stop()

    

