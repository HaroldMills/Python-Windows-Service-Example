# Python-Windows-Service-Example
Example of a Windows service implemented in Python

The service should be built in a Python environment that includes the
`pywin32` and `pyinstaller` packages. Note that as of this writing
(2016-03-37), PyInstaller supports Python versions only through 3.5.

The command for building the service is:

        pyinstaller example_service.spec
        
and should be issued from the root repo directory. The built service will
be in the directory `build\example_service`.

To install and start the service, issue the commands:

        example_service.exe install
        example_service.exe start
        
from the `build\example_service` directory. *Note that the commands
must be issued from a command prompt that was run as administrator.*

To stop and uninstall the service, issue the commands:

        example_service.exe stop
        example_service.exe remove
        
again from an administrator command prompt and from the
`build\example_service` directory.
