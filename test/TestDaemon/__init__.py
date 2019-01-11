from LibMedium.Daemon import Daemon
from LibMedium.Medium import RemoteCallException
from LibMedium.Specification.Item import Primitives

import rx

import TestDaemon.Exceptions
import TestDaemon.Models

class TestDaemonConnection:
	def __init__(self):
		self.tick: rx.subjects.Subject = rx.subjects.Subject()
		
		self._event_map = {
			b'tick': self._handle_tick_event,
		}
		
		self._daemon = Daemon('com.pcthingz.libmedium.test')
		self._medium = self._daemon.summon()
		self._medium.event_received.subscribe(self._handle_event)
	
	def hello_world(self) -> bytes:
		try:
			return Primitives.type_binary.deserialise(self._medium.invoke(b'hello_world').response)
		except RemoteCallException as e:
			TestDaemon.Exceptions.throw(e)
	
	def error_maker(self):
		try:
			self._medium.invoke(b'error_maker').response
		except RemoteCallException as e:
			TestDaemon.Exceptions.throw(e)
	
	def delay_echo(self, message: bytes) -> bytes:
		try:
			return Primitives.type_binary.deserialise(self._medium.invoke(b'delay_echo', Primitives.type_binary.serialise(message)).response)
		except RemoteCallException as e:
			TestDaemon.Exceptions.throw(e)
	
	def _handle_tick_event(self, params):
		args = [
			Primitives.type_uint32.deserialise(params[0]),
		]
		
		self.tick.on_next(args)
	
	def _handle_event(self, event):
		self._event_map[event.name](event.args)
	

