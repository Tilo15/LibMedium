from LibMedium.Messages.Invocation import Invocation
from LibMedium.Messages.Response import Response
from LibMedium.Messages.Event import Event
from LibMedium.Messages.ErrorResponse import ErrorResponse

import socket
import rx
import uuid
import struct

class Application:
    def __init__(self, sock: socket.socket):
        self._socket = sock
        self.alive = True
        self.invoked = rx.subjects.Subject()
        self.closed = rx.subjects.Subject()
        

    def _send_message(self, raw_data: bytes):
        if(not self.alive):
            raise IOError("The connection to the application is not active")

        frame = struct.pack("!Q", len(raw_data))
        frame += raw_data

        try:
            self._socket.send(frame)

        except Exception as e:
            self.alive = False
            raise e
            
            


    def _receive_message(self):
        header = None
        while not header or len(header) != 8:
            header = self._socket.recv(8)

        message_size = struct.unpack("!Q", header)[0]
        return self._socket.recv(message_size)

    
    def _handle_message(self, message: bytes):
        message_type = message[0:1]

        if(message_type == b"\x01"):
            # Application connected
            self._send_message(b"\x16")
            self.alive = True

        if(message_type == b"\x05"):
            # Invocation
            self._handle_invocation(message[1:])

        elif(message_type == b"\x04"):
            # Connection end
            self.alive = False

    
    def _handle_invocation(self, data: bytes):
        invocation = Invocation.deserialise(data)
        event = InvocationEvent(self, invocation)
        self.invoked.on_next(event)


    def _listen(self):
        try:
            while self.alive:
                message = self._receive_message()
                self._handle_message(message)
        except:
            self.alive = False
            self.closed.on_next()


    def send_response(self, response: Response):
        self._send_message(b"\x06" + response.serialise())


    def send_event(self, event: Event):
        self._send_message(b"\x10" + event.serialise())


    def send_error_response(self, error: ErrorResponse):
        self._send_message(b"\x15" + error.serialise())

    
    def close_connection(self):
        self._send_message(b"\x04")
        self.alive = False
        self.socket.close()


class InvocationEvent:
    def __init__(self, app: Application, invocation: Invocation):
        self.application: Application = app
        self.invocation: Invocation = invocation


    def complete(self, data: bytes):
        # Construct a response
        response = Response(uuid.UUID(bytes=self.invocation.call_id), data)

        # Send the response
        self.application.send_response(response)

    
    def error(self, message: str, error_number: int):
        # Construct a response
        response = ErrorResponse(uuid.UUID(bytes=self.invocation.call_id), message, error_number)

        # Send the response
        self.application.send_error_response(response)