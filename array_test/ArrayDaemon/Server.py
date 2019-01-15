from LibMedium.Daemon import Daemon
from LibMedium.Medium.Listener import Listener
from LibMedium.Medium.Listener.Application import InvocationEvent
from LibMedium.Medium.Listener.Application import Application
from LibMedium.Messages.Event import Event
from LibMedium.Specification.Item import Primitives

import ArrayDaemon.Exceptions
import ArrayDaemon.Models

class ArrayDaemonServerBase:
	def __init__(self):
		self.applications = set()
		self._daemon = Daemon('com.pcthingz.libmedium.arrays')
		self._listener = Listener(self._daemon)
		
		self._listener.invoked.subscribe(self._handle_invocation)
		self._listener.new_connection.subscribe(self._handle_connection)
		
		self._invocation_handlers = {
			b'new_list': self._handle_new_list_invocation,
			b'get_list_items': self._handle_get_list_items_invocation,
			b'get_lists_item_names': self._handle_get_lists_item_names_invocation,
			b'get_2d_array': self._handle_get_2d_array_invocation
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
	
	def _handle_new_list_invocation(self, event):
		values = [
			[Primitives.type_string.deserialise(x) for x in Primitives.type_array.deserialise(event.invocation.args[0])]
		]
		
		try:
			result = self.new_list(*values)
			event.complete(result.serialise())
		
		except Exception as e:
			error_num = 0
			if(type(e) in ArrayDaemon.Exceptions.REV_ERROR_MAP):
				error_num = ArrayDaemon.Exceptions.REV_ERROR_MAP[type(e)]
			event.error(str(e), error_num)
	
	def _handle_get_list_items_invocation(self, event):
		values = [
			ArrayDaemon.Models.ShoppingList.deserialise(event.invocation.args[0])
		]
		
		try:
			result = self.get_list_items(*values)
			event.complete(Primitives.type_array.serialise([x.serialise() for x in result]))
		
		except Exception as e:
			error_num = 0
			if(type(e) in ArrayDaemon.Exceptions.REV_ERROR_MAP):
				error_num = ArrayDaemon.Exceptions.REV_ERROR_MAP[type(e)]
			event.error(str(e), error_num)
	
	def _handle_get_lists_item_names_invocation(self, event):
		values = [
			[ArrayDaemon.Models.ShoppingList.deserialise(x) for x in Primitives.type_array.deserialise(event.invocation.args[0])]
		]
		
		try:
			result = self.get_lists_item_names(*values)
			event.complete(Primitives.type_array.serialise([Primitives.type_string.serialise(x) for x in result]))
		
		except Exception as e:
			error_num = 0
			if(type(e) in ArrayDaemon.Exceptions.REV_ERROR_MAP):
				error_num = ArrayDaemon.Exceptions.REV_ERROR_MAP[type(e)]
			event.error(str(e), error_num)
	
	def _handle_get_2d_array_invocation(self, event):
		values = [
			Primitives.type_uint32.deserialise(event.invocation.args[0])
		]
		
		try:
			result = self.get_2d_array(*values)
			event.complete(Primitives.type_array.serialise([Primitives.type_array.serialise([Primitives.type_uint32.serialise(x) for x in x]) for x in result]))
		
		except Exception as e:
			error_num = 0
			if(type(e) in ArrayDaemon.Exceptions.REV_ERROR_MAP):
				error_num = ArrayDaemon.Exceptions.REV_ERROR_MAP[type(e)]
			event.error(str(e), error_num)
	

	
	def tick(self, ticks: list, application: Application = None):
		event = Event(b'tick',
			Primitives.type_array.serialise([Primitives.type_uint32.serialise(x) for x in ticks]))
		
		if(application):
			application.send_event(event)
		else:
			self._broadcast_event(event)
	

	
	def new_list(self, items: list) -> ArrayDaemon.Models.ShoppingList:
		raise NotImplementedError
	
	def get_list_items(self, list: ArrayDaemon.Models.ShoppingList) -> list:
		raise NotImplementedError
	
	def get_lists_item_names(self, lists: list) -> list:
		raise NotImplementedError
	
	def get_2d_array(self, start: int) -> list:
		raise NotImplementedError
	
	def run(self):
		raise NotImplementedError
	
