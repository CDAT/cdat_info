import os
import sys
from cdat_info import TestRunnerBase


test_suite_name = 'cdatinfo'

workdir = os.getcwd()

runner = TestRunnerBase(test_suite_name)
ret_code = runner.run(workdir)
sys.exit(ret_code)
