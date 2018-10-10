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
        # kind of sad test 'cause we can't test the env gen since conda-forge version keep chaninging
        yml_string = 'name: widgets3\nchannels:\n  - cdat/label/nightly\n  - cdat\n  - conda-forge\n  - defaults\ndependencies:\n  - output_viewer=1.2.5=py36_0\n  - cdat_info=8.0.2018.08.30.07.08.ge7b080a=py36_0\n  - cdms2=3.0.2018.09.12.13.50.ga281159=py36hdde6e19_0\n  - cdp=1.3.3.2018.10.01.10.26=py36_0\n  - cdtime=3.0.2018.09.25.18.17.gf5ef3bc=py36hdc02c5d_0\n  - cdutil=8.0.2018.09.10.12.55.gfe08f16=py36_0\n  - dv3d=8.0.2018.07.17.08.45.ge79b355=py36_0\n  - genutil=8.1.2018.07.23.17.43.gc18c308.npy1.14=py36h776bbcc_0\n  - libcdms=3.0.2018.06.27.23.30.g51e6ae4=hdc02c5d_0\n  - libcf=3.0.2018.06.27.19.10.g994aa30=py36h1de35cc_0\n  - libdrs=3.0.2018.06.27.18.53.gb964d89=hdc02c5d_0\n  - libdrs_f=3.0.2018.06.27.18.53.gb964d89=hdc02c5d_0\n  - testsrunner=8.0.2018.10.01.06.55.gc694f88=py36_0\n  - vcs=8.0.2018.07.02.23.26.g5bc0c4f8=py36_0\n  - vtk-cdat=8.0.1.8.0=py36_3\n  - alembic=0.9.9=py_0\n  - appnope=0.1.0=py36_0\n  - asn1crypto=0.24.0=py36_3\n  - async_generator=1.10=py_0\n  - autopep8=1.4=py_0\n  - backcall=0.1.0=py_0\n  - bleach=2.1.4=py_1\n  - bokeh=0.13.0=py36_0\n  - bzip2=1.0.6=1\n  - ca-certificates=2018.8.24=ha4d7672_0\n  - certifi=2018.8.24=py36_1001\n  - cffi=1.11.5=py36h5e8e0c9_1\n  - chardet=3.0.4=py36_3\n  - clapack=3.2.1=h470a237_1\n  - click=7.0=py_0\n  - cloudpickle=0.5.6=py_0\n  - configurable-http-proxy=1.3.0=0\n  - cryptography=2.3.1=py36hdffb7b8_0\n  - cryptography-vectors=2.3.1=py36_0\n  - curl=7.61.0=h93b3f91_2\n  - cytoolz=0.9.0.1=py36h470a237_0\n  - dask=0.19.2=py_0\n  - dask-core=0.19.2=py_0\n  - decorator=4.3.0=py_0\n  - distarray=2.12.2=py36_0\n  - distributed=1.23.2=py36_0\n  - entrypoints=0.2.3=py36_2\n  - esmf=7.1.0r=h35eb876_3\n  - esmpy=7.1.0r=py36_1\n  - expat=2.2.5=hfc679d8_2\n  - ffmpeg=4.0.2=ha6a6e2b_0\n  - flake8=3.5.0=py36_1000\n  - freetype=2.8.1=hfa320df_1\n  - future=0.16.0=py36_2\n  - g2clib=1.6.0=3\n  - gettext=0.19.8.1=h1f1d5ed_1\n  - gmp=6.1.2=hfc679d8_0\n  - gnutls=3.5.19=h2a4e5f8_1\n  - hdf4=4.2.13=h951d187_2\n  - hdf5=1.10.3=hc401514_2\n  - heapdict=1.0.0=py36_1000\n  - html5lib=1.0.1=py_0\n  - icu=58.2=hfc679d8_0\n  - idna=2.7=py36_2\n  - ipykernel=4.9.0=py36_0\n  - ipython=6.5.0=py36_0\n  - ipython_genutils=0.2.0=py_1\n  - ipywidgets=7.4.2=py_0\n  - jasper=1.900.1=hff1ad4c_5\n  - jedi=0.12.1=py36_0\n  - jinja2=2.10=py_1\n  - jpeg=9c=h470a237_1\n  - jsonschema=2.6.0=py36_2\n  - jupyter=1.0.0=py_1\n  - jupyter_client=5.2.3=py_1\n  - jupyter_console=5.2.0=py36_1\n  - jupyter_core=4.4.0=py_0\n  - jupyterhub=0.9.4=py36_0\n  - jupyterlab=0.34.12=py36_0\n  - jupyterlab_launcher=0.13.1=py_2\n  - krb5=1.14.6=0\n  - lapack=3.6.1=1\n  - libffi=3.2.1=hfc679d8_5\n  - libiconv=1.15=h470a237_3\n  - libnetcdf=4.6.1=h350cafa_10\n  - libpng=1.6.35=ha92aebf_2\n  - libsodium=1.0.16=h470a237_1\n  - libssh2=1.8.0=h5b517e9_2\n  - libtiff=4.0.9=he6b73bb_2\n  - locket=0.2.0=py_2\n  - mako=1.0.7=py_1\n  - markupsafe=1.0=py36h470a237_1\n  - mccabe=0.6.1=py_1\n  - mistune=0.8.3=py36h470a237_2\n  - mkl_fft=1.0.6=py36_0\n  - mkl_random=1.0.1=py36_0\n  - mpi=1.0=mpich\n  - mpich=3.2.1=h26a2512_4\n  - msgpack-python=0.5.6=py36h2d50403_3\n  - nb_conda=2.2.1=py36_0\n  - nb_conda_kernels=2.1.1=py36_1\n  - nbconvert=5.3.1=py_1\n  - nbformat=4.4.0=py_1\n  - ncurses=6.1=hfc679d8_1\n  - netcdf-fortran=4.4.4=h71ea97b_10\n  - nettle=3.3=0\n  - nodejs=10.8.0=hfc679d8_1\n  - nose=1.3.7=py36_2\n  - notebook=5.7.0=py36_0\n  - openh264=1.7.0=0\n  - openssl=1.0.2p=h470a237_0\n  - ossuuid=1.6.2=hfc679d8_0\n  - packaging=18.0=py_0\n  - pamela=0.3.0=py36_0\n  - pandas=0.23.4=py36hf8a1672_0\n  - pandoc=2.3=0\n  - pandocfilters=1.4.2=py_1\n  - parso=0.3.1=py_0\n  - partd=0.3.8=py_1\n  - pexpect=4.6.0=py36_0\n  - pickleshare=0.7.5=py36_0\n  - pip=18.0=py36_1\n  - proj4=4.9.3=h470a237_8\n  - prometheus_client=0.3.1=py_1\n  - prompt_toolkit=1.0.15=py_1\n  - psutil=5.4.7=py36h470a237_1\n  - ptyprocess=0.6.0=py36_1000\n  - pycodestyle=2.3.1=py_1\n  - pycparser=2.19=py_0\n  - pyflakes=1.6.0=py_1\n  - pygments=2.2.0=py_1\n  - pyopenssl=18.0.0=py36_0\n  - pyparsing=2.2.2=py_0\n  - pyqt=5.6.0=py36h8210e8a_7\n  - pysocks=1.6.8=py36_2\n  - python=3.6.6=h5001a0f_0\n  - python-dateutil=2.7.3=py_0\n  - python-editor=1.0.3=py_0\n  - python-oauth2=1.1.0=py36_0\n  - pytz=2018.5=py_0\n  - pyyaml=3.13=py36h470a237_1\n  - pyzmq=17.1.2=py36hae99301_0\n  - qt=5.6.2=hd4c90f3_9\n  - qtconsole=4.4.1=py36_1\n  - readline=7.0=haf1bffa_1\n  - requests=2.19.1=py36_1\n  - send2trash=1.5.0=py_0\n  - setuptools=40.4.0=py36_1000\n  - simplegeneric=0.8.1=py_1\n  - sip=4.18.1=py36hfc679d8_0\n  - six=1.11.0=py36_1\n  - sortedcontainers=2.0.5=py_0\n  - sqlalchemy=1.2.12=py36h470a237_0\n  - sqlite=3.25.2=hb1c47c0_0\n  - tblib=1.3.2=py_1\n  - terminado=0.8.1=py36_1\n  - testpath=0.3.1=py36_1\n  - tk=8.6.8=ha92aebf_0\n  - toolz=0.9.0=py_0\n  - tornado=5.1.1=py36h470a237_0\n  - traitlets=4.3.2=py36_0\n  - udunits2=2.2.27.6=h3a4f0e9_1\n  - urllib3=1.23=py36_1\n  - wcwidth=0.1.7=py_1\n  - webencodings=0.5.1=py_1\n  - wheel=0.31.1=py36_1001\n  - widgetsnbextension=3.4.2=py36_0\n  - x264=1!152.20180717=h470a237_1\n  - xz=5.2.4=h470a237_1\n  - yaml=0.1.7=h470a237_1\n  - zeromq=4.2.5=hfc679d8_5\n  - zict=0.1.3=py_0\n  - zlib=1.2.11=h470a237_3\n  - blas=1.0=mkl\n  - intel-openmp=2019.0=118\n  - libcurl=7.61.0=hf30b1f0_0\n  - libgfortran=3.0.1=h93005f0_2\n  - mkl=2019.0=118\n  - numpy=1.15.1=py36h6a91979_0\n  - numpy-base=1.15.1=py36h8a80b8c_0\n  - pycurl=7.43.0.2=py36hdbc3d79_0\n  - pip:\n    - msgpack==0.5.6\n    - mv2==3.0.0\n    - regrid2==3.0.0\n    - sidecar==0.2.0\n    - testrunner==0.0.0\nprefix: /Users/doutriaux1/anaconda2/envs/widgets3\n\n'

        yml_name = cdat_info.generateCondaEnvironment(yml_string, yamlFile="test_yml_gen.yml", createEnvironment=False)
        self.assertTrue(os.path.exists(yml_name))
        with open(yml_name) as f:
            self.assertEqual(f.read(), yml_string)
        os.remove(yml_name)


    def test_generate_notebook(self):
        history = 'import vcs\nx=vcs.init()\nx.plot([1,2,3])\nx.png("testme", provenance=True)'
        cdat_info.generateNotebook("test_gen_nb", history=history, header="Test this CIRCLECI!!")
        self.assertTrue(os.path.exists("test_gen_nb.ipynb"))
        nb_good, nb_test = self.checkNB("tests/metadata_png.ipynb","test_gen_nb.ipynb")
        self.assertTrue("Test this CIRCLECI!!" in nb_test["cells"][0]["source"])
        os.remove("test_gen_nb.ipynb")