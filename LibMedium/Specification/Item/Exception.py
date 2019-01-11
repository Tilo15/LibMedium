from LibMedium.Specification.Item import Item

class type_exception(Item):
    label = "exception"

    def __init__(self, name, code):
        self.name = name
        self.code = code