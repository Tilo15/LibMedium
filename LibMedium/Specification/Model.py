from LibMedium.Specification.Item import model_type
from LibMedium.Specification.Item.Event import type_event
from LibMedium.Specification.Item.Exception import type_exception
from LibMedium.Specification.Item.Method import type_method
from LibMedium.Specification.Item.Model import type_model
from LibMedium.Specification.Item.Primitives import *

class SpecificationModel:
    def __init__(self, spec: str):
        self._spec = "\n".join([s for s in spec.splitlines() if s and not s.isspace()]) + "\n"

        self.namespace = ""
        self.class_name = ""
        self.events = []
        self.exceptions = []
        self.methods = []
        self.models = []

        self.names = set()

        self.types = {
            type_boolean.label: type_boolean,
            type_int8.label: type_int8,
            type_uint8.label: type_uint8,
            type_int16.label: type_int16,
            type_uint16.label: type_uint16,
            type_int32.label: type_int32,
            type_uint32.label: type_uint32,
            type_int64.label: type_int64,
            type_uint64.label: type_uint64,
            type_float.label: type_float,
            type_double.label: type_double,
            type_string.label: type_string,
            type_binary.label: type_binary
        }

        while len(self._spec) != 0:
            # Get the label of the line
            label = self._read_until(" ")

            if(label == "namespace"):
                if(self.namespace != ""):
                    raise Exception("Namespace can not be defined more than once")
                self.namespace = self._read_until("\n")

            if(label == "class"):
                if(self.class_name != ""):
                    raise Exception("Class name can not be defined more than once")
                self.class_name = self._read_until("\n")

            if(label == "event"):
                name = self._read_until("(")
                params = self._get_paramaters(name)

                # Read until the end of the line
                value = self._read_until("\n")
                if(len(value) != 0):
                    raise Exception("Expected newline after ')' but got '%s'" % value)
                
                self._register_name(name)

                self.events.append(type_event(name, params))

            if(label == "exception"):
                # Create a unique number for this exception
                error_number = len(self.exceptions) + 1

                name = self._read_until("\n")

                if(len(name) == 0):
                    raise Exception("Exception name expected")

                self._register_name(name)

                self.exceptions.append(type_exception(name, error_number))

            if(label == "method"):
                name = self._read_until("(")
                params = self._get_paramaters(name)

                # Check for return type delimiter
                d, value = self._read_until_first("\n", ":")

                return_type = None
                
                if(d == "\n" and len(value) != 0):
                    raise Exception("Expected newline or ':' after ')' but got '%s'" % value)

                elif(d == ":"):
                    return_type = self._read_until("\n")

                if(return_type and return_type not in self.types):
                    raise Exception("No such primitive or defined model '%s'" % label)

                self._register_name(name)

                self.methods.append(type_method(name, params, return_type))

            if(label == "model"):
                name = self._read_until("{")
                members = []
                member_names = set()

                # Get all the members
                while True:
                    d, prop_name = self._read_until_first(":", "}")

                    if(d == "}" and len(prop_name) != 0):
                        raise Exception("End of model reached before type definition of member '%s' on model '%s'" % (prop_name, name))

                    elif(d == "}"):
                        break

                    prop_type = self._read_until("\n")

                    if(prop_name in member_names):
                        raise Exception("Member name '%s' already defined for model '%s'" % (prop_name, name))

                    member_names.add(prop_name)
                    members.append(self._get_type_instance(prop_name, prop_type))

                self._register_name(name)

                self.models.append(type_model(name, members))
                self.types[name] = model_type(name)      


    def _register_name(self, name):
        if(name in self.names):
            raise Exception("Name '%s' already defined")
        
        self.names.add(name)


    def _get_paramaters(self, name):
        params = []
        while True:
            # Get paramater name
            d, paramater_name = self._read_until_first(":", ",", ")")

            if(d == ")" and len(paramater_name) != 0):
                raise Exception("':' expected, but got ')' in definition of event '%s'" % name)

            if(d == ","):
                raise Exception("':' excpected, but got ',' in definition of event '%s'" % name)
            
            if(d == ")" and len(paramater_name) == 0):
                break

            # Get paramater type
            d, paramater_type = self._read_until_first(":", ",", ")")

            if(d == ":"):
                raise Exception("',' or ')' excpected, but got ':' in definition of event '%s'" % name)

            # Add the paramater to the list
            params.append(self._get_type_instance(paramater_name, paramater_type))

            # Is there more?
            if(d == ")"):
                break

        return params

                
    def _get_type_instance(self, name, label):
        if(label in self.types):
            return self.types[label](name)
        else:
            raise Exception("No such primitive or defined model '%s'" % label)


    def _read_until(self, delimiter: str):
        i = len(self._spec)
        try:
            i = self._spec.index(delimiter)
        except:
            pass

        if(i == len(self._spec)):
            raise Exception("End of document reached while looking for '%s'" % delimiter)

        value = self._spec[:i]
        self._spec = self._spec[i+len(delimiter):]

        return value.strip()

    def _read_until_first(self, *delimiters):
        delimiter = ""
        index = len(self._spec)

        for d in delimiters:
            try:
                i = self._spec.index(d)
                if(i < index):
                    index = i
                    delimiter = d
            except:
                pass

        if(delimiter == ""):
            raise Exception("End of document reached while looking for tokens '%s'" % "', '".join(delimiters))

        value = self._spec[:index]
        self._spec = self._spec[index+len(delimiter):]
        return (delimiter, value.strip())

    

    
