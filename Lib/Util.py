import os
import sys
import subprocess
import shlex
import Const
import hashlib
import time
import multiprocessing
import requests

from Const import *

def run_command(command, join_stderr=True, verbosity=2):

    if isinstance(command, str):
        command = shlex.split(command)
    if verbosity > 0:
        print("Executing %s in %s" % (" ".join(command), os.getcwd()))
    if join_stderr:
        stderr = subprocess.STDOUT
    else:
        stderr = subprocess.PIPE

    P = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=stderr,
                         bufsize=0, cwd=os.getcwd())
    out = []
    while P.poll() is None:
        read = P.stdout.readline().rstrip()
        decoded_str = read.decode('utf-8')
        out.append(str(decoded_str))
        if verbosity > 1 and len(read) != 0:
            print(read)

    ret_code = P.returncode
    if ret_code != SUCCESS:
        print("FAILED...cmd: {c}".format(c=command))
    return ret_code, out

def get_sampledata_path():
    try:
        return os.path.join(os.environ.get("UVCDAT_SETUP_PATH", sys.prefix),
                            "share", "uvcdat", "sample_data")
    except KeyError:
        raise RuntimeError(
            "UVCDAT environment not configured. Please source the setup_runtime script.")

def download_sample_data_files(files_md5, path=None):
    """ Downloads sample data listed in <files_md5>
    into the specified <path>.
    If <path> is not set, it will download it to a default download
    directory specified by os.environ["UVCDAT_SETUP_PATH"].
    
    :Example:
    
    ... doctest:: download_sample_data
    
    >>> import os # use this to check if sample data already exists
    >>> if not os.path.isdir(os.environ['UVCDAT_SETUP_PATH']):
    ...     cdat_info.download_sample_data_files()
    
    :param path: String of a valid filepath.
    If None, sample data will be downloaded into the
    vcs.sample_data directory.
    :type path: `str`_ or `None`_
    """
    if not os.path.exists(files_md5) or os.path.isdir(files_md5):
        raise RuntimeError(
            "Invalid file type for list of files: %s" %
            files_md5)
    if path is None:
        path = get_sampledata_path()

    samples = open(files_md5).readlines()

    if len(samples[0].strip().split()) > 1:
        # Old style 
        download_url_root = "https://cdat.llnl.gov/cdat/sample_data/"
        n0 = 0
    else:
        download_url_root = samples[0].strip()  
        n0 = 1

    for sample in samples[n0:]:
        good_md5, name = sample.split()
        local_filename = os.path.join(path, name)
        try:
            os.makedirs(os.path.dirname(local_filename))
        except BaseException:
            pass
        attempts = 0
        while attempts < 3:
            md5 = hashlib.md5()
            if os.path.exists(local_filename):
                f = open(local_filename,"rb")
                md5.update(f.read())
                if md5.hexdigest() == good_md5:
                    attempts = 5
                    continue
            print("Downloading: '%s' from '%s' in: %s" % (name, download_url_root, local_filename))
            r = requests.get("%s/%s" % (download_url_root, name), stream=True)
            with open(local_filename, 'wb') as f:
                for chunk in r.iter_content(chunk_size=1024):
                    if chunk:  # filter local_filename keep-alive new chunks
                        f.write(chunk)
                        md5.update(chunk)
            f.close()
            if md5.hexdigest() == good_md5:
                attempts = 5
            else:
                attempts += 1

def run_nose(arguments):

    run_options, attrs, verbosity, test_name = arguments
    opts = []
    if run_options & OPT_COVERAGE:
        opts += ["--with-coverage"]
    if run_options & OPT_NO_VTK_UI:
        opts += ["-A", 'not vtk_ui']
    for att in attrs:
        opts += ["-A", att]
    command = ["nosetests", ] + opts + ["-s", test_name]
    start = time.time()
    ret_code, out = run_command(command, True, verbosity)
    end = time.time()
    return {test_name: {"result": ret_code, "log": out, "times": {
                "start": start, "end": end}}}

def add_arguments(parser, options):
    """
    This function does add_argument() method on parser where 
    parser isargparse.ArgumentParser().
    This function is called from test suite's run_tests.py
    """
    if options & OPT_GENERATE_HTML:
        parser.add_argument("-H", "--html", action="store_true", 
                            help="create and show html result page")
    if options & OPT_PACKAGE_RESULT:
        parser.add_argument("-p", "--package", action="store_true",
                            help="package test results")

    if options & OPT_GET_BASELINE:
        parser.add_argument("-g", "--git", action="store_true", default=False,
                            help="run git checkout calls")

    if options & OPT_FAILED_ONLY:
        parser.add_argument("-f", "--failed_only", action="store_true",
                            default=False,
                            help="runs only tests that failed last time and are in the list you provide")

    if options & OPT_NO_VTK_UI:
        parser.add_argument("--no_vtk_ui", action="store_true", default=False,
                            help="do not vtk_ui tests")

    if options & OPT_VERBOSITY:
        parser.add_argument("-v", "--verbosity", default=1, choices=[0, 1, 2],
                            type=int, help="verbosity output level")

    if options & OPT_VTK:
        parser.add_argument("-V", "--vtk", default=None,
                            help="conda channel and extras to use for vtk. Command will be 'conda install -c [VTK] vtk-cdat'")
    if options & OPT_NCPUS:
        ncpus = multiprocessing.cpu_count()
        parser.add_argument("-n", "--cpus", default=ncpus, type=int, 
                            help="number of cpus to use")

    if options & OPT_NOSETEST_ATTRS:
        parser.add_argument("-A","--attributes", default=[], action="append",
                            help="attribute-based runs")

    # TEST this default = None
    parser.add_argument("tests", nargs="*", default=None, help="tests to run")
