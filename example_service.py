"""
Example of a Windows service implemented in Python.

The service depends on the `pywin32` Python package. This module is
modeled primarily after the demonstration modules `pipeTestService`
and `serviceEvents` distributed with that package. Additional
information concerning Python implementations of Windows services
was gleaned from various blog and Stack Overflow postings.
Information about Windows services themselves is available from
[MSDN](http://msdn.microsoft.com).

This file is a script that can be invoked with various arguments to
install, start, stop, update, remove, etc. its service. The script
must run with administrator privileges. Some example command lines
are:

python example_service.py --startup auto install
python example_service.py start
python example_service.py stop
python example_service.py remove

Invoke the script with no arguments for more detailed documentation.

By default, when a service runs it logs into Windows as the special
non-administrative user "LocalService". If the service is to run
a Python script, the appropriate Python interpreter must be on that
user's path. The only way I know of to accomplish this is to add
the directory containing the appropriate python.exe to the *system*
path. This is unsatisfactory, however, since it affects all users'
paths and requires that all services implemented as Python scripts
use the same Python interpreter. I would like to find a way to run
various services under the LocalService account using the Python
interpreters of different virtual environments. Perhaps py2exe can
help?

Purportedly one can run a service as a particular user with a
command like:

    python example_service.py --username \Bobo --password bobo install

The "\" before the username indicates that the user account is a
local account as opposed to a domain account. I have not been able
to run a service in this way under my user account, however.
Installation of the service seems to go fine, but when I try to
start it I get the message:

    Error starting service: The dependency service or group failed to start.
    
Perhaps this is because my account is an administrator account?

TODO: Try to figure out how to run services that use different
Python virtual environments. It would be fine to require that they be
packaged using py2exe.

TODO: Try to install and start a service under a non-administrator
user account.
"""


import time
 
import servicemanager
import win32event
import win32service
import win32serviceutil
 
 
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
               
            result = win32event.WaitForSingleObject(self._stop_event, 3000)
              
            if result == win32event.WAIT_OBJECT_0:
                # stop requested
                  
                log('is stopping')
                break
              
            else:
                # stop not requested
                  
                log('is running')
                time.sleep(1)
 
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
    win32serviceutil.HandleCommandLine(ExampleService)
    