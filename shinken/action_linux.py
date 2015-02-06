
import os
import shlex
import signal
import subprocess
import sys
import time


from .log import logger


class _Action(object):

    # We allow direct launch only for 2.7 and higher version
    # because if a direct launch crash, under this the file handles
    # are not releases, it's not good.
    def execute(self, force_shell=sys.version_info < (2, 7)):
        # If the command line got shell characters, we should go
        # in a shell mode. So look at theses parameters
        force_shell |= self.got_shell_characters()

        # 2.7 and higher Python version need a list of args for cmd
        # and if not force shell (if, it's useless, even dangerous)
        # 2.4->2.6 accept just the string command
        if sys.version_info < (2, 7) or force_shell:
            cmd = self.command.encode('utf8', 'ignore')
        else:
            try:
                cmd = shlex.split(self.command.encode('utf8', 'ignore'))
            except Exception, exp:
                self.output = 'Not a valid shell command: ' + exp.__str__()
                self.exit_status = 3
                self.status = 'done'
                self.execution_time = time.time() - self.check_time
                return


        # Now: GO for launch!
        # logger.debug("Launching: %s" % (self.command.encode('utf8', 'ignore')))

        # The preexec_fn=os.setsid is set to give sons a same
        # process group. See
        # http://www.doughellmann.com/PyMOTW/subprocess/ for
        # detail about this.
        try:
            self.process = subprocess.Popen(
                cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                close_fds=True, shell=force_shell, env=self.local_env,
                preexec_fn=os.setsid)
        except OSError, exp:
            logger.error("Fail launching command: %s %s %s",
                         self.command, exp, force_shell)
            # Maybe it's just a shell we try to exec. So we must retry
            if (not force_shell and exp.errno == 8
               and exp.strerror == 'Exec format error'):
                return self.execute__(True)
            self.output = exp.__str__()
            self.exit_status = 2
            self.status = 'done'
            self.execution_time = time.time() - self.check_time

            # Maybe we run out of file descriptor. It's not good at all!
            if exp.errno == 24 and exp.strerror == 'Too many open files':
                return 'toomanyopenfiles'

    def kill__(self):
        # We kill a process group because we launched them with
        # preexec_fn=os.setsid and so we can launch a whole kill
        # tree instead of just the first one
        os.killpg(self.process.pid, signal.SIGKILL)
        # Try to force close the descriptors, because python seems to have problems with them
        for fd in [self.process.stdout, self.process.stderr]:
            try:
                fd.close()
            except Exception:
                pass
