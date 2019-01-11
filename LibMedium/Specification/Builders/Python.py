from LibMedium.Specification.Builders import Builder

import os

class PythonBuilder(Builder):

    type_map = {
        "boolean": "bool",
        "int8": "int",
        "uint8": "int",
        "int16": "int",
        "uint16": "int",
        "int32": "int",
        "uint32": "int",
        "int64": "int",
        "uint64": "int",
        "float": "float",
        "double": "float",
        "string": "str",
        "binary": "bytes"
    }

    def get_type(self, type_name):
        if(type_name in self.type_map):
            return self.type_map[type_name]
        else:
            return type_name


    def get_type_abs(self, type_name):
        if(type_name in self.type_map):
            return self.type_map[type_name]
        else:
            return "%s.Models.%s" % (self.class_name, type_name)

    def get_serialiser(self, item):
        if(item.label in self.type_map):
            return "Primitives.type_%s.serialise(%s)" % (item.label, item.name)
        else:
            return "%s.serialise()" % item.name

    def get_deserialiser(self, type_name, value):
        if(type_name in self.type_map):
            return "Primitives.type_%s.deserialise(%s)" % (type_name, value)
        else:
            return "%s.deserialise(%s)" % (self.get_type_abs(type_name), value)


    def create_interface(self, models, exceptions, methods, events):
        # Create the module folder
        module_dir = "%s/%s" % (self.output_dir, self.class_name)
        os.mkdir(module_dir)

        # Create the models
        f = open("%s/Models.py" % module_dir, 'w')
        for model in models:
            f.write(self._create_model(model))

        f.close()

        # Create the exceptions
        f = open("%s/Exceptions.py" % module_dir, 'w')
        for exception in exceptions:
            f.write(self._create_exception(exception))

        # And a translator for the exceptions
        f.write(self._create_exception_translator(exceptions))
        f.close()

        # Create the main class
        f = open("%s/__init__.py" % module_dir, 'w')
        f.write(self._create_main_class(methods, events))
        f.close()

        # Create the server 




    def _create_model(self, model):
        data = "from LibMedium.Specification.Item import Primitives\n"
        data += "import LibMedium.Util\n\n"

        # Create class
        data = "class %s:\n" % model.name

        # Init function
        data += "\tdef __init__(self"
        
        for item in model.members:
            data += ", %s: %s" % (item.name, self.get_type(item.label))

        data += "):\n"

        for item in model.memebrs:
            data += "\t\tself.%s: %s = %s\n" % (item.name, self.get_type(item.label), item.name)

        data += "\t\n\t\n"

        # Serialise function
        data += "\tdef serialise(self):\n"
        data += "\t\titems = [\n"

        for item in model.members:
            data += "\t\t\tPrimitives.type_%s.serialise(self.%s),\n"

        data += "\t\t]\n\t\t\n"

        data += "\t\treturn LibMedium.Util.pack_list(items)\n\t\n"

        # Deserialise function
        data += "\t@staticmethod"
        data += "\tdef deserialise(data: bytes) -> %s:\n" % model.name
        data += "\t\titems = LibMedium.Util.unpack_list(data)\n\t\t\n"
        data += "return %s(*items)\n\n\n" % model.name

        return data

    
    def _create_exception(self, exception):
        return "class %s(Exception):\n\tpass\n\n" % exception.name


    def _create_exception_translator(self, exceptions):
        data = "from LibMedium.Medium import RemoteCallException\n\n"

        data += "ERROR_MAP = {\n"
        
        for exception in exceptions:
            data += "\t%i: %s\n" % (exception.code, exception.name)

        data += "}\n\n\n"

        data += "def throw(error: RemoteCallException):\n"
        data += "\tif(error.error_no in ERROR_MAP):\n"
        data += "\t\traise ERROR_MAP[error.error_no](str(error))\n"
        data += "\traise(error)\n\n"

        return data

    
    def _create_main_class(self, methods, events):
        data = "from LibMedium.Daemon import Daemon\n"
        data += "from LibMedium.Medium import RemoteCallException\n"
        data += "from LibMedium.Specification.Item import Primitives\n\n"
        data += "import rx\n\n"
        data += "import %s.Exceptions\n" % self.class_name
        data += "import %s.Models\n\n" % self.class_name

        data += "class %sConnection:\n" % self.class_name

        # Create the initialiser
        data += "\tdef __init__(self):\n"

        for event in events:
            data += "\t\tself.%s: rx.subjects.Subject = rx.subjects.Subject()\n" % event.name

        data += "\t\t\n"

        data += "\t\tself._event_map = {\n"
        for event in events:
            data += "\t\t\tb'%s': self._handle_%s_event,\n" % (event.name, event.name)

        data += "\t\t}\n\t\t\n"
        
        data += "\t\tself._daemon = Daemon('%s')\n" % self.namespace
        data += "\t\tself._medium = self._daemon.summon()\n"
        data += "\t\tself._medium.event_received.subscribe(self._handle_event)\n\t\n"

        # Create the method calls
        for method in methods:
            data += "\tdef %s(self" % method.name

            for number, paramater in enumerate(method.paramaters):
                data += ", "
                data += "%s: %s" % (paramater.name, self.get_type_abs(paramater.label))

            if(method.return_type):
                data += ") -> %s:\n" % self.get_type_abs(method.return_type)
            else:
                data += "):\n"

            # Do the call
            data += "\t\ttry:\n"
            call = "self._medium.invoke(b'%s'" % method.name

            for paramater in method.paramaters:
                call += ", "
                # Serialise the data
                call += self.get_serialiser(paramater)

            call += ").response"

            if(method.return_type):
                data += "\t\t\treturn %s" % self.get_deserialiser(method.return_type, call)
            else:
                data += "\t\t\t%s" % call

            data += "\n\t\texcept RemoteCallException as e:\n"
            data += "\t\t\t%s.Exceptions.throw(e)\n\t\n" % self.class_name

        # Create the event handlers
        for event in events:
            data += "\tdef _handle_%s_event(self, params):\n" % event.name
            data += "\t\targs = ["
            for i, param in enumerate(event.paramaters):
                data += "\n\t\t\t%s," % self.get_deserialiser(param.label, "params[%i]" % i)

            data += "\n\t\t]\n\t\t\n"
            data += "\t\tself.%s.on_next(args)\n\t\n" % event.name

        data += "\tdef _handle_event(self, event):\n"
        data += "\t\tself._event_map[event.name](event.args)\n\t\n"

        data += "\n"

        return data


    # def _create_server_events(self, events):
    #     data = "from LibMedium.Messages.Event import Event\n\n"
    #     for event in events:
    #         data += "class "


    # def _create_server_class(self, exceptions, methods, events):
    #     data = "from LibMedium.Daemon import Daemon\n"
    #     data += "from LibMedium.Medium.Listener import Listener\n"
    #     data += "from LibMedium.Medium.Listener.Application import InvocationEvent\n"

            


    




