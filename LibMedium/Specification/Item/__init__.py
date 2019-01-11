class Item:
    def __init__(self, name):
        self.name = name


class model_type:
    def __init__(self, label):
        self.label = label

    def __call__(self, name):
        return model_instance(name, self.label)


class model_instance(Item):
    def __init__(self, name, label):
        self.name = name
        self.label = label