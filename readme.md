# LibMedium
A (currently) Python 3 library and toolset to aid IPC between applications and daemons

## Dependancies:
 * RxPy
 * Unix sockets

## Usage
This project has two major components, the library, and the build system.

Using the built in build system, LibMedium can generate a library that a Daemon and Application can use to communicate with each other using a defined specification file. Currently only Python 3 code generation is supported, but support for other programming languages can be added in future.

The library is used by the library that the build system creates - the LibMedium handles the actual IPC heavy lifting, while the built library offers a simple API for applications to use when communicating with the daemon.

## Specification file
In order to build a library for your specific daemon, a specification file must be made. The specification file defines some basic information about the library to be built. Such as a namespace, class name, and optionally a custom location for the Unix socket.

The specification file also defines the protocol that the application and the daemon will use to understand each other. This protocol is defined with methods, events, models, and exceptions.

The protocols are not designed to be backwards compatable with other versions. Normally, any change to the protocol will require the library to be updated for all users of the library.

An example of a simple interface for getting and setting student information might look like this:

```
namespace com.pcthingz.libmedium.student
class StudentSystem

model Student{
    id: string
    first_name: string
    last_name: string
    age: uint8
    photo: binary
}

exception StudentNotFound

method get_student(id: string): Student

method update_student(info: Student)

event student_added(time: double, info: Student)
```

When built using the Build module `python3 -m LibMedium.Specification.Build student.lmspc python3 output_folder`.

A `StudentSystem` Python 3 package is made inside the output folder, as well as a template 'server' script. For our above example, this script would look like this:
```Python
from StudentSystem.Server import StudentSystemServerBase
import StudentSystem.Exceptions
import StudentSystem.Models

class StudentSystemServer(StudentSystemServerBase):
    
    def run(self):
        # This is called when the daemon is ready to communicate. Do your background tasks in here.
        # Communication is managed in a different thread, so feel free to place your infinate loop here.
        # A set of application connections can be found at 'self.applications'.
        # All your events are available to fire off at any time using 'self.event_name(*params)'.
        # To fire an event to a single application instance, pass in the application as the last
        # paramater in the event call, eg. 'self.event_name(param1, param2, application)'
        pass
    
    
    # Below are all the method calls you will need to handle.
    def get_student(self, id: str) -> StudentSystem.Models.Student:
        pass
    
    
    def update_student(self, info: StudentSystem.Models.Student):
        pass
    
    
# If you run this module, it will run your daemon class above
if __name__ == '__main__':
    daemon = StudentSystemServer()

```
It is hoped that this will speed up daemon development by creating all the code stubs required to fully implement the protocol as defined by the specification. Note that these can be used like normal functions, nothing special is required. Throw an exception, and it will be thrown in the application. Return a value, and it will be returned at the application call.

No 'client' or application template is made, but the usage is still simple. A basic application that prints out student information from the daemon might look like this:

```Python
from StudentSystem import StudentSystemConnection
from StudentSystem.Exceptions import StudentNotFound

import sys

# Error if too few arguments
if(len(sys.argv) != 2):
    print("Usage: find_student.py student_id")
    exit()

# Get connection to the Student System
ss = StudentSystemConnection()

try:
    # Get the student
    student = ss.get_student(sys.argv[1])

    # Print student details
    print("Name: %s, %s" % (student.last_name, student.first_name))
    print("Age: %i" % student.age)

except StudentNotFound:
    # Daemon threw an exception
    print("Could not find the student with id '%s'" % sys.argv[1]) 
```
