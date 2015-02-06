
import ctypes


import shlex
import subprocess
import sys
import time


from shinken.log import logger


TerminateProcess = ctypes.windll.kernel32.TerminateProcess


class _Action(object):

    def execute(self):
        # 2.7 and higher Python version need a list of args for cmd
        # 2.4->2.6 accept just the string command
        if sys.version_info < (2, 7):
            cmd = self.command
        else:
            try:
                cmd = shlex.split(self.command.encode('utf8', 'ignore'))
            except Exception, exp:
                self.output = 'Not a valid shell command: ' + exp.__str__()
                self.exit_status = 3
                self.status = 'done'
                self.execution_time = time.time() - self.check_time
                return

        try:
            self.process = subprocess.Popen(
                cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                env=self.local_env, shell=True)
        except WindowsError, exp:
            logger.info("We kill the process: %s %s", exp, self.command)
            self.status = 'timeout'
            self.execution_time = time.time() - self.check_time

    def kill__(self):
        TerminateProcess(int(self.process._handle), -1)