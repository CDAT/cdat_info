import os
os.environ["CDAT_ANONYMOUS_LOG"] = "true"
import sys
import cdat_info
import unittest
from subprocess import PIPE, Popen

class ThreadsTest(unittest.TestCase):
    def testTooManyThreads(self):
        pid = os.getpid()
        print("PID:",pid)
        n = 0
        maximum_num_threads = 0
        if sys.platform == "darwin":
            thread_option = "-M"
        else:
            thread_option = "-T"
        while n < 100:
            n += 1
            cdat_info.pingPCMDIdb("cdat", "cdms2")
            p = Popen("ps {} -p {}".format(thread_option, pid).split(),stdin=PIPE, stdout=PIPE, stderr=PIPE)
            o,e = p.communicate()
            maximum_num_threads = max(len(o.decode().split("\n")), maximum_num_threads)
            print(maximum_num_threads)
            self.assertLess(maximum_num_threads, 15)
