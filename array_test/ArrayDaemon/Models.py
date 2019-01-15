from LibMedium.Specification.Item import Primitives
import LibMedium.Util

class ShoppingListItem:
	def __init__(self, item: str, quantity: int):
		self.item: str = item
		self.quantity: int = quantity
	
	
	def serialise(self):
		items = [
			Primitives.type_string.serialise(self.item),
			Primitives.type_uint8.serialise(self.quantity),
		]
		return LibMedium.Util.pack_list(items)
	
	@staticmethod
	def deserialise(data: bytes):
		items = LibMedium.Util.unpack_list(data)
		return ShoppingListItem(
			Primitives.type_string.deserialise(items[0]),
			Primitives.type_uint8.deserialise(items[1])
		)

from LibMedium.Specification.Item import Primitives
import LibMedium.Util

class ShoppingList:
	def __init__(self, store: str, items: list):
		self.store: str = store
		self.items: list = items
	
	
	def serialise(self):
		items = [
			Primitives.type_string.serialise(self.store),
			Primitives.type_array.serialise([x.serialise() for x in self.items]),
		]
		return LibMedium.Util.pack_list(items)
	
	@staticmethod
	def deserialise(data: bytes):
		items = LibMedium.Util.unpack_list(data)
		return ShoppingList(
			Primitives.type_string.deserialise(items[0]),
			[ShoppingListItem.deserialise(x) for x in Primitives.type_array.deserialise(items[1])]
		)

