#!/usr/bin/env python

import argparse
import sys
import cdms2
import vcs
import os
from cdat_info import generateNotebook, generateCondaEnvironment
import json
import shlex
import requests
import tempfile
from subprocess import Popen, PIPE
parser = argparse.ArgumentParser(usage="Generates a notebook from a CDAT generated object")

parser.add_argument("-o", "-n", "--notebook", "--output", dest="notebook", help="name of notebook to generate")
parser.add_argument("-i", "--input", default=None, help="Path to CDAT generated input file")
parser.add_argument("-g", "--generate-conda", default=False, action="store_true", help="Turn on conda env generation")
parser.add_argument("-y", "--yaml", default=None, help="Name of yaml file to use to generate conda yaml environment")
parser.add_argument("-c", "--conda-name", default=None, help="Name of conda environment to generate")
parser.add_argument("-r", "--run", default=False, action="store_true", help="Run notebook after generating")


args = parser.parse_args(sys.argv[1:])


if not os.path.exists(args.input):  # File is not here
    # could it be an url?
    try:
        r = requests.get(args.input)
        if r.status_code == 404:
            raise RuntimeError("Input file `{}` does not exists or is not readable".format(args.input))
        local_file = tempfile.NamedTemporaryFile()
        for chunk in r.iter_content(chunk_size=1024):
            if chunk:  # filter local_filename keep-alive new chunks
                local_file.write(chunk)
        local_file.flush()
        input_filename = local_file.name
    except Exception:
        raise RuntimeError("Input file `{}` does not exists or is not readable".format(args.input))
else:
    input_filename = args.input

# Ok now loop through possible CDAT generated object
provenance = {}
try:
    print("Trying input file as cdms2 readable file")
    f = cdms2.open(input_filename)
    provenance = getattr(f,"provenance", {})
except Exception as err:
    # ok failed cdms, trying vcs
    print("Trying input file as vcs png file")
    metadata = vcs.png_read_metadata(input_filename)
    provenance = metadata.get("provenance", {})
if not isinstance(provenance, dict):
    provenance = json.loads(provenance)
conda = provenance.get("conda", {})
yaml_text = conda.get("yaml", "")
history = provenance.get("history", "")
header = """# Source file information\n
Name: {}\n
Generated on {}\n
By: {}\n
Platform: {} {} ({})\n
""".format(
    input_filename,
    provenance.get("date", "???"),
    provenance.get("userId", "???"),
    provenance.get("platform", {}).get("Name", "???"),
    provenance.get("platform", {}).get("OS", "???"),
    provenance.get("platform", {}).get("Version", "???"))

# Ok maybe it was a script?
script = provenance.get("script", "")
if script != "":
    history = script
    header += "\nGenerated via script, command line: `{}`\n\nScript sources pasted bellow\n\n".format(provenance["commandLine"])
if history == "":
    raise RuntimeError("Could not read history (or empty history) from `{}`".format(args.input))
header += "\nMore information probably available in file's provenance dictionary"
if args.generate_conda:
    if yaml_text == "":
        raise RuntimeError("Could not read conda environment from `{}`".format(args.input))
    generateCondaEnvironment(yaml_text, name=args.conda_name, yamlFile=args.yaml)

# Check file extension
notebook = args.notebook
print("NOTEBOOK OUT:", notebook)
if notebook is None:
    notebook = os.path.splitext(args.input)[0] + ".ipynb"
elif notebook[-6:].lower() != ".ipynb":
    notebook += ".ipynb"

generateNotebook(notebook, history, header=header)
    
if args.run:
    p = Popen(shlex.split("jupyter lab {}".format(notebook)), stdout=PIPE, stderr=PIPE)
    p.communicate()