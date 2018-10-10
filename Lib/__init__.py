from .cdat_git_version import __describe__
from .cdat_info_src import *  # noqa
from .provenance import generateProvenance, generateNotebook, generateCondaEnvironment  # noqa
try:  # is testsrunner installed?
    from testsrunner import run_command, get_sampledata_path, download_sample_data_files  # noqa
    from testsrunner import checkImage
    from testsrunner.checkimage import defaultThreshold
    from .TestRunnerBase import TestRunnerBase
except Exception:
    pass
