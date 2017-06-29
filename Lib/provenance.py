import collections
import os
import sys
import datetime
import subprocess
import shlex

# Platform
def populate_prov(prov, cmd, pairs, sep=None, index=1, fill_missing=False):
    try:
        p = subprocess.Popen(shlex.split(cmd), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except:
        return
    out, stde = p.communicate()
    if stde != '':
        return
    for strBit in out.splitlines():
        for key, value in pairs.iteritems():
            if value in strBit:
                prov[key] = strBit.split(sep)[index].strip()
    if fill_missing is not False:
        for k in pairs:
            if k not in prov:
                prov[k] = fill_missing
    return


def generateProvenance(extra_pairs={}):
    """Generates provenance info for your CDAT distribution
    extra_pairs is a dictionary of format: {"name_in_provenance_list" : "python_package"}
    """
    prov = collections.OrderedDict()
    platform = os.uname()
    platfrm = collections.OrderedDict()
    platfrm["OS"] = platform[0]
    platfrm["Version"] = platform[2]
    platfrm["Name"] = platform[1]
    prov["platform"] = platfrm
    try:
        logname = os.getlogin()
    except:
        try:
            import pwd
            logname = pwd.getpwuid(os.getuid())[0]
        except:
            try:
                logname = os.environ.get('LOGNAME', 'unknown')
            except:
                logname = 'unknown-loginname'
    prov["userId"] = logname
    prov["osAccess"] = bool(os.access('/', os.W_OK) * os.access('/', os.R_OK))
    prov["commandLine"] = " ".join(sys.argv)
    prov["date"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    prov["conda"] = collections.OrderedDict()
    pairs = {
        'Platform': 'platform ',
        'Version': 'conda version ',
        'IsPrivate': 'conda is private ',
        'envVersion': 'conda-env version ',
        'buildVersion': 'conda-build version ',
        'PythonVersion': 'python version ',
        'RootEnvironment': 'root environment ',
        'DefaultEnvironment': 'default environment '
    }
    populate_prov(prov["conda"], "conda info", pairs, sep=":", index=-1)
    pairs = {
        'blas': 'blas',
        'cdp': 'cdp ',
        'cdat_info': 'cdat_info ',
        'cdms': 'cdms2 ',
        'cdtime': 'cdtime ',
        'cdutil': 'cdutil ',
        'clapack': 'clapack ',
        'esmf': 'esmf ',
        'esmpy': 'esmpy ',
        'genutil': 'genutil ',
        'lapack': 'lapack ',
        'mesalib': 'mesalib ',
        'numpy': 'numpy ',
        'python': 'python ',
        'uvcdat': 'uvcdat ',
        'vcs': 'vcs ',
        'vtk': 'vtk-cdat ',
    }
    prov["packages"] = collections.OrderedDict()
    populate_prov(prov["packages"], "conda list", pairs, fill_missing=None)
    populate_prov(prov["packages"], "conda list", extra_pairs, fill_missing=None)
    # Trying to capture glxinfo
    pairs = {
        "vendor": "OpenGL vendor string",
        "renderer": "OpenGL renderer string",
        "version": "OpenGL version string",
        "shading language version": "OpenGL shading language version string",
    }
    prov["openGL"] = collections.OrderedDict()
    populate_prov(prov["openGL"], "glxinfo", pairs, sep=":", index=-1)
    prov["openGL"]["GLX"] = {"server": collections.OrderedDict(), "client": collections.OrderedDict()}
    pairs = {
        "version": "GLX version",
    }
    populate_prov(prov["openGL"]["GLX"], "glxinfo", pairs, sep=":", index=-1)
    pairs = {
        "vendor": "server glx vendor string",
        "version": "server glx version string",
    }
    populate_prov(prov["openGL"]["GLX"]["server"], "glxinfo", pairs, sep=":", index=-1)
    pairs = {
        "vendor": "client glx vendor string",
        "version": "client glx version string",
    }
    populate_prov(prov["openGL"]["GLX"]["client"], "glxinfo", pairs, sep=":", index=-1)
    return prov
