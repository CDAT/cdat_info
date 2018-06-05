from __future__ import print_function
from functools import partial

import glob
import sys
import os
import multiprocessing
import subprocess
import image_compare
import codecs
import time
import webbrowser
import shlex

from Util import *
from Const import *

class TestRunnerBase:

    """
    This is a base class for a test runner.
    Each test project's run_tests.py should instantiate this TestRunnerBase class,
    and call the run() method. For example:

      runner = TestRunnerBase.TestRunnerBase(test_suite_name, valid_options, 
         args, get_sample_data)
      runner.run(workdir, args.tests)
    """
    def __init__(self, test_suite_name, options, args, get_sample_data=False, 
                 test_data_files_info=None):
        """
           test_suite_name: test suite name
           options        : valid options (32 bit integer) for the testsuite.
                            See Const.py for valid bits that can be set.
           args           : arguments to run_tests.py -- this is the 
                            return value of argparse,parse_args()
           get_sample_data: specifies whether sample data should be downloaded
                            for the test run.
           test_data_files_info: file name of a text file containing list of 
                            data files needed for the test suite.
        """
        self.test_suite_name = test_suite_name
        self.run_options = 0x00000000

        if options & OPT_GENERATE_HTML and args.html:
            self.run_options |= OPT_GENERATE_HTML
        if options & OPT_PACKAGE_RESULT and args.package:
            self.run_options |= OPT_PACKAGE_RESULT
        if options & OPT_GET_BASELINE and args.git:
            self.run_options |= OPT_GET_BASELINE
        if options & OPT_FAILED_ONLY and args.failed_only:
            self.run_options |= OPT_FAILED_ONLY
        if options & OPT_NO_VTK_UI and args.no_vtk_ui:
            self.run_options |= OPT_NO_VTK_UI
        if options & OPT_VERBOSITY and args.verbosity:
            self.verbosity = args.verbosity
        else:
            self.verbosity = 1

        if options & OPT_VTK and args.vtk:
            self.vtk_channels = args.vtk
        else:
            self.vtk_channels = None

        if options & OPT_NCPUS and args.cpus:
            self.ncpus = args.cpus
        else:
            self.ncpus = 1

        if options & OPT_NOSETEST_ATTRS and args.attributes:
            self.nosetest_attrs = args.attributes
        else:
            self.nosetests_attr = []

        if get_sample_data == True:
            download_sample_data_files(os.path.join(test_data_files_info,
                                                    get_sampledata_path())
            
    def __set_run_options(self, options, args):
        if options & OPT_GENERATE_HTML and args.html:
            self.run_options |= OPT_GENERATE_HTML

        if options & OPT_PACKAGE_RESULT and args.package:
            self.run_options |= OPT_PACKAGE_RESULT

        if options & OPT_GET_BASELINE and args.git:
            self.run_options |= OPT_GET_BASELINE

        if options & OPT_FAILED_ONLY and args.failed_only:
            self.run_options |= OPT_FAILED_ONLY

        if options & OPT_COVERAGE and args.coverage:
            self.run_options |= OPT_COVERAGE

        if options & OPT_NO_VTK_UI and args.no_vtk_ui:
            self.run_options |= OPT_NO_VTK_UI

        if options & OPT_VERBOSITY and args.verbosity:
            self.verbosity = args.verbosity
        else:
            self.verbosity = 1

        if options & OPT_VTK and args.vtk:
            self.vtk_channels = args.vtk
        else:
            self.vtk_channels = None

        self.ncpus = args.cpus
        self.nosetests_attr = args.attributes
        

    def __is_option_set(self, option):
        return self.run_options & option
    
    def __get_tests(self, failed_only=False, tests=None):
        """
        get_tests() gets the list of test names to run.
        If <failed_only> is False, returns the set of the specified
        test names. If <tests> is not specified, returns a set of all tests
        under 'tests' sub directory.
        If <failed_only> is True, returns the set of failed test names
        from previous run.
        If <failed_only> is True, and <tests> is specified, returns 
        the set of failed test names that is listed in <tests>
        """
        if tests is None or len(tests) == 0:
            # run all tests
            test_names = glob.glob("tests/test_*py")
        else:
            test_names = set(tests)

        if failed_only and os.path.exists(os.path.join("tests",".last_failure")):
            f = open(os.path.join("tests", ".last_failure"))
            failed = set(eval(f.read().strip()))
            f.close()
            new_tests = []
            for failed_test in failed:
                if failed_test in test_names:
                    new_tests.append(failed_test)
            test_names = new_tests

        return(test_names)


    def __get_baseline(self, workdir):
        """
        __get_baseline(self, workdir):
        <workdir> : should be repo dir of the test
        """    
        os.chdir(workdir)
        ret_code, cmd_output = self.__run_cmd('git rev-parse --abbrev-ref HEAD')
        o = "".join(cmd_output)
        branch = o.strip()
        if not os.path.exists("uvcdat-testdata"):
            cmd = "git clone git://github.com/cdat/uvcdat-testdata"
            ret_code, cmd_output = self.__run_cmd(cmd)
            if ret_code != SUCCESS:
                return ret_code
        os.chdir("uvcdat-testdata")
        ret_code, cmd_output = self.__run_cmd("git pull")
        if ret_code != SUCCESS:
            return ret_code
        print("BRANCH WE ARE TRYING TO CHECKOUT is (%s)" % branch)
        ret_code, cmd_output = self.__run_cmd("git checkout %s" % (branch))
        os.chdir(workdir)
        return(ret_code)

    def __install_vtk_cdat(self):
        #
        # assumption: conda is in PATH
        #
        vtk_name = "vtk-cdat"
        cmd = "conda install -f -y -c %s %s" % (self.vtk_channels, vtk_name)
        ret_code, output = self.__run_cmd(cmd)
        return ret_code

    def __run_cmd(self, cmd):
        ret_code, cmd_output = run_command(cmd, True, self.verbosity)
        return ret_code, cmd_output

    def __do_run_tests(self, test_names):
        ret_code = SUCCESS
        p = multiprocessing.Pool(self.ncpus)
        try:
            func = partial(run_nose, self.run_options, self.nosetests_attr, 
                           self.verbosity)
            outs = p.map_async(func, test_names).get(3600)
        except KeyboardInterrupt:
            sys.exit(1)
        results = {}
        failed = []
        for d in outs:
            results.update(d)
            test_name = list(d.keys())[0]
            if d[test_name]["result"] != 0:
                failed.append(test_name)
        f = open(os.path.join("tests",".last_failure"),"w")
        f.write(repr(failed))
        f.close()

        if self.verbosity > 0:
            print("Ran %i tests, %i failed (%.2f%% success)" %\
                      (len(outs), len(failed), 100. - float(len(failed)) / len(outs) * 100.))
            if len(failed) > 0:
                print("Failed tests:")
                for f in failed:
                    print("\t", f)

        self.results = results
        if len(failed) > 0:
            ret_code = FAILURE
        return ret_code

    def __abspath(self, path, name, prefix):
        import shutil
        full_path = os.path.abspath(os.path.join(os.getcwd(), "..", path))
        if not os.path.exists(name):
            os.makedirs(name)
        new_path = os.path.join(name, prefix + "_" + os.path.basename(full_path))
        try:
            shutil.copy(full_path, new_path)
        except:
            pass
        return new_path

    def __findDiffFiles(self, log):
        i = -1
        file1 = ""
        file2 = ""
        diff = ""
        N = len(log)
        while log[i].find("Source file") == -1 and i > -N:
            i -= 1
        if i > -N:
            file1 = log[i - 1].split()[-1]
            for j in range(i, N):
                if log[j].find("New best!") > -1:
                    if log[j].find("Comparing") > -1:
                        file2 = log[j].split()[2]
                    else:
                        k = j - 1
                        while log[k].find("Comparing") == -1 and k > -N:
                            k -= 1
                        try:
                            file2 = log[k].split()[2]
                        except:
                            file2 = log[k].split()[1][:-1]+log[j].split()[0]
                            print("+++++++++++++++++++++++++",file2)
                if log[j].find("Saving image diff") > -1:
                    diff = log[j].split()[-1]
                    # break
        return file1, file2, diff

    def __generate_html(self, workdir):
        os.chdir(workdir)
        if not os.path.exists("tests_html"):
            os.makedirs("tests_html")
        os.chdir("tests_html")

        js = image_compare.script_data()

        fi = open("index.html", "w")
        print("<!DOCTYPE html>", file=fi)
        print("""<html><head><title>%s Test Results %s</title>
    <link rel="stylesheet" type="text/css" href="http://cdn.datatables.net/1.10.13/css/jquery.dataTables.css">
    <script type="text/javascript" src="http://code.jquery.com/jquery-1.12.4.js"></script>
    <script type="text/javascript" charset="utf8"
    src="https://cdn.datatables.net/1.10.13/js/jquery.dataTables.min.js"></script>
    <script>
    $(document).ready( function () {
            $('#table_id').DataTable({
            "order":[[1,'asc'],[0,'asc']],
            "scrollY":"70vh","paging":false,"scrollCollapse":false
            });
                } );
    </script>
    </head>""" % (self.test_suite_name, time.asctime()), file=fi)
        print("<body><h1>%s Test results: %s</h1>" % (self.test_suite_name, time.asctime()), file=fi)
        print("<table id='table_id' class='display'>", file=fi)
        print("<thead><tr><th>Test</th><th>Result</th><th>Start Time</th><th>End Time</th><th>Time</th></tr></thead>", file=fi)
        print("<tfoot><tr><th>Test</th><th>Result</th><th>Start Time</th><th>End Time</th><th>Time</th></tr></tfoot>", file=fi)

        for t in sorted(self.results.keys()):
            result = self.results[t]
            nm = t.split("/")[-1][:-3]
            print("<tr><td>%s</td>" % nm, end=' ', file=fi)
            fe = codecs.open("%s.html" % nm, "w", encoding="utf-8")
            print("<!DOCTYPE html>", file=fe)
            print("<html><head><title>%s</title>" % nm, file=fe)
            if result["result"] == 0:
                print("<td><a href='%s.html'>OK</a></td>" % nm, end=' ', file=fi)
                print("</head><body>", file=fe)
                print("<a href='index.html'>Back To Results List</a>", file=fe)
            else:
                print("<td><a href='%s.html'>Fail</a></td>" % nm, end=' ', file=fi)
                print("<script type='text/javascript'>%s</script></head><body>" % js, file=fe)
                print("<a href='index.html'>Back To Results List</a>", file=fe)
                print("<h1>Failed test: %s on %s</h1>" % (nm, time.asctime()), file=fe)
                file1, file2, diff = self.__findDiffFiles(result["log"])
                if file1 != "":
                    print('<div id="comparison"></div><script type="text/javascript"> ImageCompare.compare(' +\
                              'document.getElementById("comparison"), "%s", "%s"); </script>' % (
                            abspath(file2, nm, "test"), abspath(file1, nm, "source")), file=fe)
                    print("<div><a href='index.html'>Back To Results List</a></div>", file=fe)
                    print("<div id='diff'><img src='%s' alt='diff file'></div>" % abspath(
                                diff, nm, "diff"), file=fe)
                    print("<div><a href='index.html'>Back To Results List</a></div>", file=fe)
            print('<div id="output"><h1>Log</h1><pre>%s</pre></div>' % "\n".join(result[
                        "log"]), file=fe)
            print("<a href='index.html'>Back To Results List</a>", file=fe)
            print("</body></html>", file=fe)
            fe.close()
            t = result["times"]
            print("<td>%s</td><td>%s</td><td>%s</td></tr>" % (
                    time.ctime(t["start"]), time.ctime(t["end"]), t["end"] - t["start"]), file=fi)
            
        print("</table></body></html>", file=fi)
        fi.close()
        os.chdir(workdir)
        webbrowser.open("file://%s/tests_html/index.html" % workdir)


    def __package_results(self, workdir):
        os.chdir(workdir)
        import tarfile
        tnm = "results_%s_%s_%s.tar.bz2" % (os.uname()[0],os.uname()[1],time.strftime("%Y-%m-%d_%H:%M"))
        t = tarfile.open(tnm, "w:bz2")
        t.add("tests_html")
        t.add("tests_html")
        t.close()
        if self.verbosity > 0:
            print("Packaged Result Info in:", tnm)
            

    def run(self, workdir, tests=None):
        """
        runs the specified test cases. If tests is None, runs the whole testsuite.

        workdir: top level project repo directory
        tests  : a space separated list of test cases
        """
        os.chdir(workdir)
        test_names = self.__get_tests(self.__is_option_set(OPT_FAILED_ONLY), tests)

        if self.__is_option_set(OPT_GET_BASELINE):
            ret_code = self.__get_baseline(workdir)
            if ret_code != SUCCESS:
                return(ret_code)

        ret_code = self.__do_run_tests(test_names)

        if self.__is_option_set(OPT_GENERATE_HTML) or self.__is_option_set(OPT_PACKAGE_RESULT):
            self.__generate_html(workdir)

        if self.__is_option_set(OPT_PACKAGE_RESULT):
            self.__package_results(workdir)

            
