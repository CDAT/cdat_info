import cdat_info
import unittest
import nbformat
import os
from testsrunner import run_command

class NBTest(unittest.TestCase):
    def checkNB(self, good, test):
        nb_good = nbformat.read(good, nbformat.NO_CONVERT)
        nb_test = nbformat.read(test, nbformat.NO_CONVERT)
        good_cells = nb_good["cells"]
        test_cells = nb_test["cells"]
        self.assertEqual(len(good_cells), len(test_cells))
        for good_cell, test_cell in zip(good_cells, test_cells):
            self.assertEqual(good_cell["cell_type"], test_cell["cell_type"])
            if good_cell["cell_type"] == "code":
                self.assertEqual(good_cell["source"], test_cell["source"])
        return nb_good, nb_test

    def test_generate_notebook_from_png(self):
        try:
            import vcs
        except Exception:
            # Only works if vcs is here
            return
        cmd = "generate_cdat_notebook.py -i tests/metadata.png -o test_metadata_png"
        code, msg = run_command(cmd)
        self.assertEqual(code, 0)
        self.assertTrue(os.path.exists("test_metadata_png.ipynb"))
        self.checkNB("tests/metadata_png.ipynb", "test_metadata_png.ipynb")
        os.remove("test_metadata_png.ipynb")

    def test_generate_conda_env(self):
        yml_string = cdat_info.generateProvenance()["conda"]["yaml"]
        yml_name = cdat_info.generateCondaEnvironment(yml_string,
                                                      name="test_Conda",
                                                      yamlFile="test_yml_gen.yml",
                                                      createEnvironment=True)
        self.assertTrue(os.path.exists(yml_name))
        code, out = run_command("conda env list")
        self.assertTrue("test_Conda" in "".join(out))


    def test_generate_notebook(self):
        history = 'import vcs\nx=vcs.init()\nx.plot([1,2,3])\nx.png("testme", provenance=True)'
        cdat_info.generateNotebook("test_gen_nb", history=history, header="Test this CIRCLECI!!")
        self.assertTrue(os.path.exists("test_gen_nb.ipynb"))
        nb_good, nb_test = self.checkNB("tests/metadata_png.ipynb","test_gen_nb.ipynb")
        self.assertTrue("Test this CIRCLECI!!" in nb_test["cells"][0]["source"])
        os.remove("test_gen_nb.ipynb")