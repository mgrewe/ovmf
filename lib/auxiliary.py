import time
import pathlib
import os
import ctypes

# Windows
# https://docs.microsoft.com/en-us/windows/win32/api/sysinfoapi/nf-sysinfoapi-gettickcount64
# Linux
# https://linux.die.net/man/3/clock_gettime
# Python
# https://www.python.org/dev/peps/pep-0418/#time-monotonic
def get_time_ms():
    #return int(time.clock_gettime(time.CLOCK_MONOTONIC)*1000)
    
    if os.name == 'nt':
        return  ctypes.windll.kernel32.GetTickCount64()
    elif os.name == 'posix':
        return int(time.monotonic() * 1000 )
    else:
        raise RuntimeError('No monotonic timer implemented for this platform.')

def compute_elapsed_time(data, path):
    now = get_time_ms()
    name = pathlib.Path(path).stem
    if ('times' not in data.keys()):
        data['times'] = {}
    
    if ('timestamp_last_computation' not in data.keys()):
        data['times'][name] = now - data['timestamp']
    else:
        data['times'][name] = now - data['timestamp_last_computation']
    data['timestamp_last_computation'] = now
    
    #print("Time elapsed: " + str(data['times'][name]))

