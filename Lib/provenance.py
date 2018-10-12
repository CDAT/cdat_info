import collections
import os
import sys
from datetime import datetime
from subprocess import Popen, PIPE
import shlex
import tempfile

# Platform
def populate_prov(prov, cmd, pairs, sep=None, index=1, fill_missing=False):
    try:
        p = Popen(shlex.split(cmd), stdout=PIPE, stderr=PIPE)
    except Exception as err:
        print("ERROR running {} was {}".format(cmd,err))
        return
    out, stde = p.communicate()
    if stde.decode("utf-8") != '':
        print("STDE NOT EMPYTY:{}".format(stde))
        return
    for strBit in out.decode("utf-8").splitlines():
        for key, value in pairs.items():
            if value in strBit:
                prov[key] = strBit.split(sep)[index].strip()
    if fill_missing is not False:
        for k in pairs:
            if k not in prov:
                prov[k] = fill_missing
    return


def generateProvenance(extra_pairs={}, history=True):
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
    prov["date"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
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
    # Actual environement used
    p = Popen(shlex.split("conda env export"), stdout=PIPE, stderr=PIPE)
    o,e = p.communicate()
    prov["conda"]["yaml"] = o.decode("utf-8")
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

    # Now the history if requested
    if history:
        session_history = ""
        try:
            import IPython
            profile_hist=IPython.core.history.HistoryAccessor()
            session = profile_hist.get_last_session_id()
            cursor = profile_hist.get_range(session)
            for session_id, line, cmd in cursor.fetchall():
                    session_history += "{}\n".format(cmd)
        except Exception as err:
            # Fallback but does not seem to always work
            import readline
            for i in range(readline.get_current_history_length()):
                session_history += "{}\n".format(readline.get_history_item(i + 1))
            pass
        prov["history"] = session_history
    return prov


def generateCondaEnvironment(yaml, name=None, yamlFile=None, createEnvironment=True):
    """Generates a conda environement, based on compressed yaml string

    :param yaml: string containing conda yaml info
    :type name: `str`_

    :param name: Possible new name for generated yaml environement
    :type name: `str`_

    :param yamlFile: If you wish to preserve the generated yaml env file
    :type name: `str`_


    :param createEnvironment: If you only want the yaml to be generated but not the enviroment
    :type name: `bool`_

    :return: Path to yaml file used.
    :rtype: `str`_
    """

    # First prepare yaml file
    if yamlFile is None:  # User does not care about where yamlFile goes
        yamlFile = tempfile.NamedTemporaryFile(mode="w", suffix=".yaml")
    else:
        yamlFile = open(yamlFile, "w")

    yamlFile.write(yaml)
    yamlFile.flush()

    # Now try to generate environment if user did not truned it off
    if createEnvironment:
        if name is not None:
            environmentName = "-n {}".format(name)
        else:
            environmentName = ""
        cmd = "conda env create -f {} {}".format(yamlFile.name, environmentName)
        print("Creating conda envirnoment:\n",cmd)
        p = Popen(shlex.split(cmd), stdout=PIPE, stderr=PIPE)
        o, e = p.communicate()
        if e != []:
            print("Error creating conda environment\n", e.decode("utf8"))
    yamlFile.close()
    return yamlFile.name


def generateNotebook(notebook, history, header=""):
    """Tries to inject  history into a notebook
    :param notebook: name of notebook file
    :type notebook: `str`_
    
    :param history: history string
    :type history: `str`_
    
    :param header: markdown header string to add in header
    :type history: `str`_
    
    :return: None
    """

    import nbformat as nbf

    nb = nbf.v4.new_notebook()

    nb_header = """\
# Notebook autogenerated by CDAT on {:%Y-%m-%d %H:%M:%S}
""".format(datetime.now())
    if header is not None:
        nb_header += "\n{}".format(header)

    cells = [
        nbf.v4.new_markdown_cell(nb_header),
        nbf.v4.new_code_cell(history)
    ]

    nb['cells'] = cells

    # Check file extension
    if notebook[-6:].lower() != ".ipynb":
        notebook += ".ipynb"

    nbf.write(nb, notebook)

