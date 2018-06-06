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

def run_nose(run_options, attrs, verbosity, test_name):
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
