import os
import sys
from cdat_info import TestRunnerBase


test_suite_name = 'testsrunner'

workdir = os.getcwd()

runner = TestRunnerBase(test_suite_name)
ret_code = runner.run(workdir)#, options="--subdir", options_files="tests/cdat_info_runtests.json")
sys.exit(ret_code)
