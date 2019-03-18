from __future__ import print_function
import cdat_info
import unittest
import os
from testsrunner import run_command
 
CONDA = os.environ.get("CONDA_PYTHON_EXE","")
if CONDA != "":
    CONDA = os.path.join(os.path.dirname(CONDA), "conda")
else:
    CONDA = "conda"

class ProvTest(unittest.TestCase):
    def test_generate_conda_provenance(self):
        provenance = cdat_info.generateProvenance(extra_pairs={"testsrunner":"testsrunner"})
        # Check packages were created
        packages = provenance["packages"]
        self.assertTrue("cdat_info" in provenance["packages"])
        self.assertTrue("testsrunner" in provenance["packages"])
        yml_string = provenance["conda"]["yaml"]
        yml_name = cdat_info.generateCondaEnvironment(yml_string,
                                                      name="test_Conda",
                                                      yamlFile="test_yml_gen.yml",
                                                      createEnvironment=True)
        self.assertTrue(os.path.exists(yml_name))
        code, out = run_command(CONDA + " env list")
        self.assertTrue("test_Conda" in "".join(out))