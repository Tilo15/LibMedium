from LibMedium.Specification.Item import Item

class type_event(Item):
    label = "event"

    def __init__(self, name, paramaters):
        self.name = name
        self.paramaters = paramaters