from LibMedium.Daemon import Daemon
from LibMedium.Medium.Listener import Listener
from LibMedium.Medium.Listener.Application import InvocationEvent
from LibMedium.Medium.Listener.Application import Application
from LibMedium.Messages.Event import Event
from LibMedium.Specification.Item import Primitives

import TestDaemon.Exceptions
import TestDaemon.Models

class TestDaemonServerBase:
	def __init__(self):
		self.applications = set()
		self._daemon = Daemon('com.pcthingz.libmedium.test')
		self._listener = Listener(self._daemon)
		
		self._listener.invoked.subscribe(self._handle_invocation)
		self._listener.new_connection.subscribe(self._handle_connection)
		
		self._invocation_handlers = {
			b'hello_world': self._handle_hello_world_invocation,
			b'error_maker': self._handle_error_maker_invocation,
			b'delay_echo': self._handle_delay_echo_invocation,
			b'wrapper': self._handle_wrapper_invocation
		}
		
		self.run()
	
	def _handle_invocation(self, event):
		if(event.invocation.function in self._invocation_handlers):
			self._invocation_handlers[event.invocation.function](event)
		else:
			event.error('The invoked method does not exist on this service')
	
	def _handle_connection(self, application):
		self.applications.add(application)
	
	def _broadcast_event(self, event):
		for app in self.applications:
			if(app.alive):
				try:
					app.send_event(event)
				except:
					pass
	
	def _handle_hello_world_invocation(self, event):
		values = []
		try:
			result = self.hello_world(*values)
			event.complete(Primitives.type_binary.serialise(result))
		
		except Exception as e:
			error_num = 0
			if(type(e) in TestDaemon.Exceptions.REV_ERROR_MAP):
				error_num = TestDaemon.Exceptions.REV_ERROR_MAP[type(e)]
			event.error(str(e), error_num)
	
	def _handle_error_maker_invocation(self, event):
		values = []
		try:
			result = self.error_maker(*values)
			event.complete(b'')
		except Exception as e:
			error_num = 0
			if(type(e) in TestDaemon.Exceptions.REV_ERROR_MAP):
				error_num = TestDaemon.Exceptions.REV_ERROR_MAP[type(e)]
			event.error(str(e), error_num)
	
	def _handle_delay_echo_invocation(self, event):
		values = [
			Primitives.type_binary.deserialise(event.invocation.args[0])
		]
		
		try:
			result = self.delay_echo(*values)
			event.complete(Primitives.type_binary.serialise(result))
		
		except Exception as e:
			error_num = 0
			if(type(e) in TestDaemon.Exceptions.REV_ERROR_MAP):
				error_num = TestDaemon.Exceptions.REV_ERROR_MAP[type(e)]
			event.error(str(e), error_num)
	
	def _handle_wrapper_invocation(self, event):
		values = [
			TestDaemon.Models.TestModel.deserialise(event.invocation.args[0]),
			Primitives.type_string.deserialise(event.invocation.args[1])
		]
		
		try:
			result = self.wrapper(*values)
			event.complete(result.serialise())
		
		except Exception as e:
			error_num = 0
			if(type(e) in TestDaemon.Exceptions.REV_ERROR_MAP):
				error_num = TestDaemon.Exceptions.REV_ERROR_MAP[type(e)]
			event.error(str(e), error_num)
	

	
	def tick(self, count: int, application: Application = None):
		event = Event(b'tick',
			Primitives.type_uint32.serialise(count))
		
		if(application):
			application.send_event(event)
		else:
			self._broadcast_event(event)
	

	
	def hello_world(self) -> bytes:
		raise NotImplementedError
	
	def error_maker(self):
		raise NotImplementedError
	
	def delay_echo(self, message: bytes) -> bytes:
		raise NotImplementedError
	
	def wrapper(self, data: TestDaemon.Models.TestModel, name: str) -> TestDaemon.Models.TestModelWrapper:
		raise NotImplementedError
	
	def run(self):
		raise NotImplementedError
	
