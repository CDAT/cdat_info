from __future__ import print_function
from distutils.core import setup
import subprocess

Version = "8.0"
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
except:
    descr = Version
f = open("Lib/cdat_git_version.py", "w")
print("__version__ = '%s'" % Version, file=f)
print("__describe__ = '%s'" % descr, file=f)
f.close()
setup (name = "cdat_info",
       packages = ['cdat_info'],
       package_dir = {'cdat_info': "Lib"},
       data_files = [ ('share/cdat', ['share/cdat_runtests.json'])]
      )
