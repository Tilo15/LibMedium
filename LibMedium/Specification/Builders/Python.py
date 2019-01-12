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

    def get_serialiser(self, item, value = None):
        reference = item.name
        if(value):
            reference = value

        return self.get_serialiser_by_label(item.label, reference)
        

    def get_serialiser_by_label(self, label, value):
        if(label in self.type_map):
            return "Primitives.type_%s.serialise(%s)" % (label, value)
        else:
            return "%s.serialise()" % value


    def get_deserialiser(self, type_name, value):
        if(type_name in self.type_map):
            return "Primitives.type_%s.deserialise(%s)" % (type_name, value)
        else:
            return "%s.deserialise(%s)" % (self.get_type_abs(type_name), value)

    def get_deserialiser_relative(self, type_name, value):
        if(type_name in self.type_map):
            return "Primitives.type_%s.deserialise(%s)" % (type_name, value)
        else:
            return "%s.deserialise(%s)" % (self.get_type(type_name), value)


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
        f = open("%s/Server.py" % module_dir, 'w')
        f.write(self._create_server_class(methods, events))
        f.close()

        # Create server template
        f = open("%s/%sServer.py" % (self.output_dir, self.class_name), 'w')
        f.write(self._create_server_template(methods))
        f.close()




    def _create_model(self, model):
        data = "from LibMedium.Specification.Item import Primitives\n"
        data += "import LibMedium.Util\n\n"

        # Create class
        data += "class %s:\n" % model.name

        # Init function
        data += "\tdef __init__(self"
        
        for item in model.members:
            data += ", %s: %s" % (item.name, self.get_type(item.label))

        data += "):\n"

        for item in model.members:
            data += "\t\tself.%s: %s = %s\n" % (item.name, self.get_type(item.label), item.name)

        data += "\t\n\t\n"

        # Serialise function
        data += "\tdef serialise(self):\n"
        data += "\t\titems = [\n"

        for item in model.members:
            data += "\t\t\t%s,\n" % self.get_serialiser(item, "self.%s" % item.name)

        data += "\t\t]\n"

        data += "\t\treturn LibMedium.Util.pack_list(items)\n\t\n"

        # Deserialise function
        data += "\t@staticmethod\n"
        data += "\tdef deserialise(data: bytes):\n"
        data += "\t\titems = LibMedium.Util.unpack_list(data)\n"
        data += "\t\treturn %s(" % model.name
        for i, item in enumerate(model.members):
            data += "\n\t\t\t%s" % self.get_deserialiser_relative(item.label, "items[%i]" % i)
            if(i != len(model.members) -1):
                data += ","

        data += "\n\t\t)\n\n"

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

        data += "REV_ERROR_MAP = {\n"
        for exception in exceptions:
            data += "\t%s: %u\n" % (exception.name, exception.code)
        data += "}\n\n\n"

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
        
        if(self.socket_dir):
            data += "\t\tself._daemon = Daemon('%s', '%s')\n" % (self.namespace, self.socket_dir)
        else:
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

    def _create_server_class(self, methods, events):
        data = "from LibMedium.Daemon import Daemon\n"
        data += "from LibMedium.Medium.Listener import Listener\n"
        data += "from LibMedium.Medium.Listener.Application import InvocationEvent\n"
        data += "from LibMedium.Medium.Listener.Application import Application\n"
        data += "from LibMedium.Messages.Event import Event\n"
        data += "from LibMedium.Specification.Item import Primitives\n\n"
        data += "import %s.Exceptions\n" % self.class_name
        data += "import %s.Models\n\n" % self.class_name


        data += "class %sServerBase:\n" % self.class_name
        data += "\tdef __init__(self):\n"
        data += "\t\tself.applications = set()\n"

        if(self.socket_dir):
            data += "\t\tself._daemon = Daemon('%s', '%s')\n" % (self.namespace, self.socket_dir)
        else:
            data += "\t\tself._daemon = Daemon('%s')\n" % self.namespace

        data += "\t\tself._listener = Listener(self._daemon)\n\t\t\n"
        data += "\t\tself._listener.invoked.subscribe(self._handle_invocation)\n"
        data += "\t\tself._listener.new_connection.subscribe(self._handle_connection)\n\t\t\n"

        data += "\t\tself._invocation_handlers = {\n\t\t\t"
        for i, method in enumerate(methods):
            if(i != 0):
                data += ",\n\t\t\t"
            data += "b'%s': self._handle_%s_invocation" % (method.name, method.name)

        data += "\n\t\t}\n\t\t\n"

        data += "\t\tself.run()\n\t\n"
        data += "\tdef _handle_invocation(self, event):\n"
        data += "\t\tif(event.invocation.function in self._invocation_handlers):\n"
        data += "\t\t\tself._invocation_handlers[event.invocation.function](event)\n"
        data += "\t\telse:\n"
        data += "\t\t\tevent.error('The invoked method does not exist on this service')\n\t\n"

        data += "\tdef _handle_connection(self, application):\n"
        data += "\t\tself.applications.add(application)\n\t\n"

        data += "\tdef _broadcast_event(self, event):\n"
        data += "\t\tfor app in self.applications:\n"
        data += "\t\t\tif(app.alive):\n"
        data += "\t\t\t\ttry:\n"
        data += "\t\t\t\t\tapp.send_event(event)\n"
        data += "\t\t\t\texcept:\n"
        data += "\t\t\t\t\tpass\n\t\n"

        # Invocation handler functions
        for method in methods:
            data += "\tdef _handle_%s_invocation(self, event):\n" % method.name

            if(len(method.paramaters) == 0):
                data += "\t\tvalues = []\n"
            else:
                data += "\t\tvalues = [\n\t\t\t"
                for i, param in enumerate(method.paramaters):
                    if(i != 0):
                        data += ",\n\t\t\t"
                    data += self.get_deserialiser(param.label, "event.invocation.args[%i]" % i)
                data += "\n\t\t]\n\t\t\n"

            data += "\t\ttry:\n"
            data += "\t\t\tresult = self.%s(*values)\n" % method.name
            if(method.return_type):
                data += "\t\t\tevent.complete(%s)\n\t\t\n" % self.get_serialiser_by_label(method.return_type, "result")
            else:
                data += "\t\t\tevent.complete(b'')\n"
            data += "\t\texcept Exception as e:\n"
            data += "\t\t\terror_num = 0\n"
            data += "\t\t\tif(type(e) in %s.Exceptions.REV_ERROR_MAP):\n" % self.class_name
            data += "\t\t\t\terror_num = %s.Exceptions.REV_ERROR_MAP[type(e)]\n" % self.class_name
            data += "\t\t\tevent.error(str(e), error_num)\n\t\n"

        data += "\n\t\n"

        # Event calls
        for event in events:
            data += "\tdef %s(self" % event.name
            for paramater in event.paramaters:
                data += ", "
                data += "%s: %s" % (paramater.name, self.get_type_abs(paramater.label))

            data += ", application: Application = None):\n"
            data += "\t\tevent = Event(b'%s'" % event.name
            for paramater in event.paramaters:
                data += ",\n\t\t\t%s" % self.get_serialiser(paramater)

            data += ")\n\t\t\n"

            data += "\t\tif(application):\n"
            data += "\t\t\tapplication.send_event(event)\n"
            data += "\t\telse:\n"
            data += "\t\t\tself._broadcast_event(event)\n\t\n"
        
        data += "\n\t\n"

        # Abstratct method calls
        for method in methods:
            data += "\tdef %s(self" % method.name
            for paramater in method.paramaters:
                data += ", "
                data += "%s: %s" % (paramater.name, self.get_type_abs(paramater.label))

            if(method.return_type):
                data += ") -> %s:\n" % self.get_type_abs(method.return_type)
            else:
                data += "):\n"

            data += "\t\traise NotImplementedError\n\t\n"


        # The run function
        data += "\tdef run(self):\n"
        data += "\t\traise NotImplementedError\n\t\n"

        return data

    def _create_server_template(self, methods):
        data = "from %s.Server import %sServerBase\n" % (self.class_name, self.class_name)
        data += "import %s.Exceptions\n" % self.class_name
        data += "import %s.Models\n\n" % self.class_name

        data += "class %sServer(%sServerBase):\n    \n" % (self.class_name, self.class_name)
        data += "    def run(self):\n"
        data += "        # This is called when the daemon is ready to communicate. Do your background tasks in here.\n"
        data += "        # Communication is managed in a different thread, so feel free to place your infinate loop here.\n"
        data += "        # A set of application connections can be found at 'self.applications'.\n"
        data += "        # All your events are available to fire off at any time using 'self.event_name(*params)'.\n"
        data += "        # To fire an event to a single application instance, pass in the application as the last\n"
        data += "        # paramater in the event call, eg. 'self.event_name(param1, param2, application)'\n"
        data += "        pass\n    \n    \n"

        data += "    # Below are all the method calls you will need to handle.\n"
        
        for method in methods:
            data += "    def %s(self" % method.name
            for paramater in method.paramaters:
                data += ", "
                data += "%s: %s" % (paramater.name, self.get_type_abs(paramater.label))

            if(method.return_type):
                data += ") -> %s:\n" % self.get_type_abs(method.return_type)
            else:
                data += "):\n"

            data += "        pass\n    \n    \n"

        data += "# If you run this module, it will run your daemon class above\n"
        data += "if __name__ == '__main__':\n"
        data += "    daemon = %sServer()\n\n" % self.class_name

        return data


            


    




