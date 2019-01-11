from LibMedium.Specification.Item import Item

class type_model(Item):
    label = "model"

    def __init__(self, name, members):
        self.name = name
        self.members = members