import lazy_import
from .cdat_git_version import __describe__
from .cdat_info_src import *  # noqa

# from .provenance import generateProvenance, generateNotebook, generateCondaEnvironment  # noqa
generateProvenance = lazy_import.lazy_function("cdat_info.provenance.generateProvenance")
generateNotebook = lazy_import.lazy_function("cdat_info.provenance.generateNotebook")
generateCondaEnvironment = lazy_import.lazy_function("cdat_info.provenance.generateCondaEnvironment")


try:  # is testsrunner installed?
#    from testsrunner import run_command, get_sampledata_path, download_sample_data_files  # noqa
#    from testsrunner import checkImage
#    from testsrunner.checkimage import defaultThreshold
    run_command = lazy_import.lazy_function("testsrunner.run_command")
    get_sampledata_path = lazy_import.lazy_function("testsrunner.get_sampledata_path")
    download_sample_data_files = lazy_import.lazy_function("testsrunner.download_sample_data_files")
    checkImage = lazy_import.lazy_function("testsrunner.checkImage")
    defaultThreshold = lazy_import.lazy_function("testsrunner.checkimage.defaultThreshold")
    from .TestRunnerBase import TestRunnerBase
except Exception:
    pass
