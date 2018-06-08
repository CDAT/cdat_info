
SUCCESS = 0
FAILURE = 1

#
# The following constants are bits for storing run_tests.py argument options.
# If user can run the testsuite and specify -H (for generate html), then 
# the valid_options passed to TestRunnerBase constructor should have
# OPT_GENERATE_HTML bit set.
#
# for boolean option arguments
#
OPT_GENERATE_HTML  = 0x00000001
OPT_PACKAGE_RESULT = 0x00000002
OPT_GET_BASELINE   = 0x00000004
OPT_FAILED_ONLY    = 0x00000008
OPT_COVERAGE       = 0x00000010
OPT_NO_VTK_UI      = 0x00000020 

#
# for argument options that take values
#
OPT_VERBOSITY      = 0x00010000
OPT_VTK            = 0x00020000
OPT_NCPUS          = 0x00040000
OPT_NOSETEST_ATTRS = 0x00080000

