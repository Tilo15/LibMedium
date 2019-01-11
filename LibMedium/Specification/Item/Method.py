from LibMedium.Specification.Item import Item

class type_method(Item):
    label = "method"

    def __init__(self, name, paramaters, return_type):
        self.name = name
        self.paramaters = paramaters
        self.return_type = return_type