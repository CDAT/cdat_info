from __future__ import print_function
import cdat_info
import unittest
from testsrunner import run_command

class ProvTest(unittest.TestCase):
    def test_generate_conda_provenance(self):
        provenance = cdat_info.generateProvenance()
        # Check packages were created
        packages = provenance["packages"]
        self.assertTrue("cdat_info" in provenance["packages"])
        yml_string = provenance["conda"]["yaml"]
        yml_name = cdat_info.generateCondaEnvironment(yml_string,
                                                      name="test_Conda",
                                                      yamlFile="test_yml_gen.yml",
                                                      createEnvironment=True)
        self.assertTrue(os.path.exists(yml_name))
        code, out = run_command("conda env list")
        self.assertTrue("test_Conda" in "".join(out))