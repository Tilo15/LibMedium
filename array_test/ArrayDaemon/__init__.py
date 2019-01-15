from LibMedium.Daemon import Daemon
from LibMedium.Medium import RemoteCallException
from LibMedium.Specification.Item import Primitives

import rx

import ArrayDaemon.Exceptions
import ArrayDaemon.Models

class ArrayDaemonConnection:
	def __init__(self):
		self.tick: rx.subjects.Subject = rx.subjects.Subject()
		
		self._event_map = {
			b'tick': self._handle_tick_event,
		}
		
		self._daemon = Daemon('com.pcthingz.libmedium.arrays')
		self._medium = self._daemon.summon()
		self._medium.event_received.subscribe(self._handle_event)
	
	def new_list(self, items: list) -> ArrayDaemon.Models.ShoppingList:
		try:
			return ArrayDaemon.Models.ShoppingList.deserialise(self._medium.invoke(b'new_list', Primitives.type_array.serialise([Primitives.type_string.serialise(x) for x in items])).response)
		except RemoteCallException as e:
			ArrayDaemon.Exceptions.throw(e)
	
	def get_list_items(self, list: ArrayDaemon.Models.ShoppingList) -> list:
		try:
			return [ArrayDaemon.Models.ShoppingListItem.deserialise(x) for x in Primitives.type_array.deserialise(self._medium.invoke(b'get_list_items', list.serialise()).response)]
		except RemoteCallException as e:
			ArrayDaemon.Exceptions.throw(e)
	
	def get_lists_item_names(self, lists: list) -> list:
		try:
			return [Primitives.type_string.deserialise(x) for x in Primitives.type_array.deserialise(self._medium.invoke(b'get_lists_item_names', Primitives.type_array.serialise([x.serialise() for x in lists])).response)]
		except RemoteCallException as e:
			ArrayDaemon.Exceptions.throw(e)
	
	def get_2d_array(self, start: int) -> list:
		try:
			return [[Primitives.type_uint32.deserialise(x) for x in Primitives.type_array.deserialise(x)] for x in Primitives.type_array.deserialise(self._medium.invoke(b'get_2d_array', Primitives.type_uint32.serialise(start)).response)]
		except RemoteCallException as e:
			ArrayDaemon.Exceptions.throw(e)
	
	def _handle_tick_event(self, params):
		args = [
			[Primitives.type_uint32.deserialise(x) for x in Primitives.type_array.deserialise(params[0])],
		]
		
		self.tick.on_next(args)
	
	def _handle_event(self, event):
		self._event_map[event.name](event.args)
	

