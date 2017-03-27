"""
Example of a Windows service implemented in Python.

This module implements a simple Windows service, and can be invoked as
a script with various arguments to install, start, stop, update, remove,
etc. the service. The script (but not the service) must run with
administrator privileges.

To run a Windows command prompt that has administrator privileges,
right-click on it in a Windows Explorer window (the path of the program
is C:\Windows\System32\cmd.exe) and select "Run as administrator". Or, if
you have installed the command prompt in the Windows taskbar, right click
on its icon, right-click on "Command Prompt" in the resulting menu, and
select "Run as administrator".

The service logs messages when it starts and stops, and every five seconds
while running. You can see the messages using the Windows Event Viewer
(suggestion: filter for messages from the source "Python Example"). The
service does not do anything else.

This module depends on the `pywin32` Python package, and is modeled
primarily after the demonstration modules `pipeTestService` and
`serviceEvents` distributed with that package. Additional information
concerning Python implementations of Windows services was gleaned from
various blog and Stack Overflow postings. Information about Windows
services themselves is available from [MSDN](http://msdn.microsoft.com).

This module can be used either by invoking it as a script, for example:

    python example_service.py start
    
or by building a [PyInstaller](http://http://www.pyinstaller.org)
executable from it and then invoking the executable, for example:

    example_service.exe start
    
A typical sequence of commands to test the module's service is:

    python example_service.py install
    python example_service.py start
    python example_service.py stop
    python example_service.py remove

For more complete usage information, invoke the script or the
executable with the single argument "help".

I chose to use PyInstaller rather than py2exe to create an executable
version of this script since as of this writing (January 2017) py2exe
does not yet support Python 3.5. PyInstaller is also cross-platform
while py2exe is not. (That doesn't matter for Windows services, of
course, but I would like something that I also can use with other,
cross-platform Python code.)

It appears that if the service of this module is installed with the
command:

    python example_service.py install
    
then in order for the service to be able to start, the path of the
directory containing the Python interpreter that should be used for
the service must be on the Windows system path, i.e. included in the
value of the system `Path` environment variable. Otherwise, if you
try to start the service with:

    python example_service.py start
    
the command will fail with a message like:

    Error starting service: The service did not respond to the
        start or control request in a timely fashion.

Having to include the path of a particular Python environment on
the system path is undesirable. One workaround is to create an
executable for the service using PyInstaller, and install and
control the service using that executable. Since PyInstaller
packages the executable with the appropriate Python environment,
no system path modifications are needed, and different services
can be packaged with different Python environments.
"""


import sys
 
import servicemanager
import win32event
import win32service
import win32serviceutil
 

def _main():
    
    if len(sys.argv) == 1 and \
            sys.argv[0].endswith('.exe') and \
            not sys.argv[0].endswith(r'win32\PythonService.exe'):
        # invoked as non-pywin32-PythonService.exe executable without
        # arguments
        
        # We assume here that we were invoked by the Windows Service
        # Control Manager (SCM) as a PyInstaller executable in order to
        # start our service.
        
        # Initialize the service manager and start our service.
        servicemanager.Initialize()
        servicemanager.PrepareToHostSingle(ExampleService)
        servicemanager.StartServiceCtrlDispatcher()
    
    else:
        # invoked with arguments, or without arguments as a regular
        # Python script
  
        # We support a "help" command that isn't supported by
        # `win32serviceutil.HandleCommandLine` so there's a way for
        # users who run this script from a PyInstaller executable to see
        # help. `win32serviceutil.HandleCommandLine` shows help when
        # invoked with no arguments, but without the following that would
        # never happen when this script is run from a PyInstaller
        # executable since for that case no-argument invocation is handled
        # by the `if` block above.
        if len(sys.argv) == 2 and sys.argv[1] == 'help':
            sys.argv = sys.argv[:1]
             
        win32serviceutil.HandleCommandLine(ExampleService)


    
class ExampleService(win32serviceutil.ServiceFramework):
    
    
    _svc_name_ = 'PythonExample'
    _svc_display_name_ = 'Python Example'
    _svc_description_ = 'Example of a Windows service implemented in Python.'
 
 
    def __init__(self, args):
        win32serviceutil.ServiceFramework.__init__(self, args)
        self._stop_event = win32event.CreateEvent(None, 0, 0, None)
 
 
    def GetAcceptedControls(self):
        result = win32serviceutil.ServiceFramework.GetAcceptedControls(self)
        result |= win32service.SERVICE_ACCEPT_PRESHUTDOWN
        return result

    
    def SvcDoRun(self):
        
        log = self._log_info_message
        
        log('has started')
        
        while True:
               
            result = win32event.WaitForSingleObject(self._stop_event, 5000)
              
            if result == win32event.WAIT_OBJECT_0:
                # stop requested
                  
                log('is stopping')
                break
              
            else:
                # stop not requested
                
                log('is running')
 
        log('has stopped')
        
        
    def _log_info_message(self, fragment):
        servicemanager.LogInfoMsg(
            'The {} service {}.'.format(self._svc_name_, fragment))
 
 
    def SvcOtherEx(self, control, event_type, data):
        
        # See the MSDN documentation for "HandlerEx callback" for a list
        # of control codes that a service can respond to.
        #
        # We respond to `SERVICE_CONTROL_PRESHUTDOWN` instead of
        # `SERVICE_CONTROL_SHUTDOWN` since it seems that we can't log
        # info messages when handling the latter.
        
        log = self._log_info_message
        
        if control == win32service.SERVICE_CONTROL_PRESHUTDOWN:
            log('received a pre-shutdown notification')
            self._stop()
        else:
            log('received an event: code={}, type={}, data={}'.format(
                    control, event_type, data))
    

    def _stop(self):
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        win32event.SetEvent(self._stop_event)


    def SvcStop(self):
        self._stop()
 

if __name__ == '__main__':
    _main()
