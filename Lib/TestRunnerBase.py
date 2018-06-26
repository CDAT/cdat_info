from __future__ import print_function
from functools import partial
import glob
import sys
import os
import testsrunner
import codecs
import time
import webbrowser
import shlex
import cdp
import warnings

SUCCESS = 0
FAILURE = 1


class TestRunnerBase(testsrunner.TestRunnerBase):

    """
    This is a base class for a test runner.
    Each test project's run_tests.py should instantiate this TestRunnerBase class,
    and call the run() method. For example:

      runner = TestRunnerBase.TestRunnerBase(test_suite_name, valid_options, 
         args, get_sample_data)
      runner.run(workdir, args.tests)
    """

    def __init__(self, test_suite_name, options=[], options_files=[], get_sample_data=False,
                 test_data_files_info=None):
        """
           test_suite_name: test suite name
           options        : options to use (in addition of default options always here)
           options_files  : json files defining cdp/addparse argument definitions
           get_sample_data: specifies whether sample data should be downloaded
                            for the test run.
           test_data_files_info: file name of a text file containing list of 
                            data files needed for the test suite.
        """
        options_files.insert(0, os.path.join(
            sys.prefix, "share", "cdat", "cdat_runtests.json"))
        super(TestRunnerBase, self).__init__(test_suite_name,
                                                         options, options_files,
                                                         get_sample_data, test_data_files_info)
