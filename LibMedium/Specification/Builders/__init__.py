class Builder:
    def __init__(self, namespace, class_name, output_dir):
        self.namespace = namespace
        self.class_name = class_name
        self.output_dir = output_dir

    def create_interface(self, models, exceptions, methods, events):
        raise NotImplementedError