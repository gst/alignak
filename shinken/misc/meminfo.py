
from __future__ import print_function

import os
import sys
import threading


def print_mem(a):
    print('%s(%s): %s : %s' % (
        threading.currentThread().name,
        threading.currentThread().ident,
        a,
        mem()))


def memory_usage_resource():
    return mem()

def mem2():
    import resource
    rusage_denom = 1024.
    if sys.platform == 'darwin':
        # ... it seems that in OSX the output is different units ...
        rusage_denom = rusage_denom * rusage_denom
    mem = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / rusage_denom
    return mem

def mem():
    import subprocess
    return subprocess.check_output(
        ['ps', '--no-headers', '-o', 'vsz,pmem', '--pid', str(os.getpid())]
    ).strip()
