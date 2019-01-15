from LibMedium.Specification.Item import Primitives
import LibMedium.Util

class TestModel:
	def __init__(self, message: str, count: int):
		self.message: str = message
		self.count: int = count
	
	
	def serialise(self):
		items = [
			Primitives.type_string.serialise(self.message),
			Primitives.type_uint32.serialise(self.count),
		]
		return LibMedium.Util.pack_list(items)
	
	@staticmethod
	def deserialise(data: bytes):
		items = LibMedium.Util.unpack_list(data)
		return TestModel(
			Primitives.type_string.deserialise(items[0]),
			Primitives.type_uint32.deserialise(items[1])
		)

from LibMedium.Specification.Item import Primitives
import LibMedium.Util

class TestModelWrapper:
	def __init__(self, name: str, value: TestModel):
		self.name: str = name
		self.value: TestModel = value
	
	
	def serialise(self):
		items = [
			Primitives.type_string.serialise(self.name),
			self.value.serialise(),
		]
		return LibMedium.Util.pack_list(items)
	
	@staticmethod
	def deserialise(data: bytes):
		items = LibMedium.Util.unpack_list(data)
		return TestModelWrapper(
			Primitives.type_string.deserialise(items[0]),
			TestModel.deserialise(items[1])
		)

