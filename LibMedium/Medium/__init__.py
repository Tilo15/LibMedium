from LibMedium.Messages import Event, Invocation, Response, ErrorResponse
import LibMedium.Util

import socket
import struct
import threading
import uuid
import rx

class Medium:
    def __init__(self, daemon):
        self.daemon = daemon
        self.alive: bool = False
        self.event_received = rx.subjects.Subject()
        self._socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self._response_locks = {}
        self._responses = {}

        # Connect to the socket
        self._socket.connect(LibMedium.Util.get_socket_address(self.daemon.namespace))

        # Make sure the daemon is responsive
        self._send_message(b"\x01")

        # Wait for response
        message = self._receive_message()

        # Handle response
        self._handle_message(message)

        # Check that the connection is now alive
        if(not self.alive):
            raise IOError("Daemon sent unexpected response to summon request")

        # Start listening for messages in a different thread
        threading.Thread(target=self._listen).start()


    def invoke(self, method_name: bytes, *args) -> Response:
        if(not self.alive):
            raise IOError("The connection to the daemon is not active")

        call = uuid.uuid4()
        invocation = Invocation.Invocation(method_name, call, *args)

        # Create a lock to get released when we get our response
        lock = threading.Lock()
        lock.acquire()

        # When we get a response, the lock will get released
        self._response_locks[call.bytes] = lock
        self._send_message(b"\x05" + invocation.serialise())

        # Acquire the lock again to block until we get a response
        lock.acquire()

        # Delete the lock
        del self._response_locks[call.bytes]

        # Get the response
        response = self._responses[call.bytes]

        # If it was an error response, raise the exception
        if(type(response) is ErrorResponse.ErrorResponse):
            raise RemoteCallException(response.message, response.error_no)

        # Otherwise return the response
        return response


    def close_connection(self):
        self._send_message(b"\x04")
        self.alive = False
        self.socket.close()

        
    def _send_message(self, raw_data: bytes):
        frame = struct.pack("!Q", len(raw_data))
        frame += raw_data
        self._socket.send(frame)

    def _receive_message(self):
        header = None
        while not header or len(header) < 8:
            header = self._socket.recv(8)

        message_size = struct.unpack("!Q", header)[0]
        return self._socket.recv(message_size)


    def _handle_message(self, message: bytes):
        message_type = message[0:1]

        if(message_type == b"\x06"):
            # Invocation Response
            self._handle_invocation_response(message[1:])

        elif(message_type == b"\x10"):
            # Event
            self._handle_event(message[1:])

        elif(message_type == b"\x16"):
            # Connection Acknowledge
            self.alive = True

        elif(message_type == b"\x04"):
            # Connection end
            self.alive = False

        elif(message_type == b"\x15"):
            # Error response
            self._handle_invocation_error_response(message[1:])



    def _handle_event(self, data: bytes):
        event = Event.Event.deserialise(data)
        self.event_received.on_next(event)

        
    def _handle_invocation_response(self, data: bytes):
        response: Response.Response = Response.Response.deserialise(data)
        if(response.call_id in self._response_locks):
            self._responses[response.call_id] = response
            self._response_locks[response.call_id].release()

    def _handle_invocation_error_response(self, data: bytes):
        error: ErrorResponse.ErrorResponse = ErrorResponse.ErrorResponse.deserialise(data)
        if(error.call_id in self._response_locks):
            self._responses[error.call_id] = error
            self._response_locks[error.call_id].release()


    def _listen(self):
        while(self.alive):
            # Receive messages
            message = self._receive_message()
            self._handle_message(message)


class RemoteCallException(Exception):
    def __init__(self, message, error_no = 0):
        self.error_no = error_no
        Exception.__init__(self, message)