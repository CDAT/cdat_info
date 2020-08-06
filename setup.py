from __future__ import print_function
from setuptools import setup, find_packages
import subprocess

Version = "8.2.1"
p = subprocess.Popen(
    ("git",
     "describe",
     "--tags"),
    stdin=subprocess.PIPE,
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE)
try:
    descr = p.stdout.readlines()[0].strip()
    Version = "-".join(descr.split("-")[:-2])
    if Version == "":
        Version = descr
except Exception:
    descr = Version

with open("cdat_info/cdat_git_version.py", "w") as f:
    print("__version__ = '%s'" % Version, file=f)
    print("__describe__ = '%s'" % descr, file=f)

setup(name="cdat_info",
      version=Version,
      packages=find_packages(),
      data_files = [ ('share/cdat', ['share/cdat_runtests.json'])],
      scripts=['scripts/generate_cdat_notebook.py']
      )
