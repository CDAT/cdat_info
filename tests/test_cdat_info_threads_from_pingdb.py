import cdat_info
import os
import unittest
from subprocess import PIPE, Popen

class ThreadsTest(unittest.TestCase):
    def testTooManyThreads(self):
        pid = os.getpid()
        n = 0
        maximum_num_threads = 0
        while n < 100:
            n += 1
            cdat_info.pingPCMDIdb("cdat", "cdms2")
            p = Popen("ps -T -p {}".format(pid).split(),stdin=PIPE, stdout=PIPE, stderr=PIPE)
            o,e = p.communicate()
            maximum_num_threads = max(len(o.split("\n")), maximum_num_threads)
        self.assertLess(maximum_num_threads, 15)



