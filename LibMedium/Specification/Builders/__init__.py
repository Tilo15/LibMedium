class Builder:
    def __init__(self, namespace, class_name, socket_dir, output_dir):
        self.namespace = namespace
        self.class_name = class_name
        self.socket_dir = socket_dir
        self.output_dir = output_dir

    def create_interface(self, models, exceptions, methods, events):
        raise NotImplementedError