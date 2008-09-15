__version__=''' $Id$ '''
"""Tests that all manuals can be built.
"""
from reportlab.lib.testutils import setOutDir,SecureTestCase, printLocation, testsFolder
setOutDir(__name__)
import os, sys, unittest

class ManualTestCase(SecureTestCase):
    "Runs all 3 manual-builders from the top."

    def test0(self):
        "Test if all manuals buildable from source."
        docsFolder = os.path.join(testsFolder,'..','docs')
        cwd = os.getcwd()
        os.chdir(docsFolder)
        try:
            if os.path.isfile('userguide.pdf'):
                os.remove('userguide.pdf')
            if os.path.isfile('graphguide.pdf'):
                os.remove('graphguide.pdf')
            if os.path.isfile('reference.pdf'):
                os.remove('reference.pdf')
            if os.path.isfile('graphics_reference.pdf'):
                os.remove('graphics_reference.pdf')

            os.system("%s genAll.py -s" % sys.executable)

            assert os.path.isfile('userguide.pdf'), 'genAll.py failed to generate userguide.pdf!'
            assert os.path.isfile('graphguide.pdf'), 'genAll.py failed to generate graphguide.pdf!'
            assert os.path.isfile('reference.pdf'), 'genAll.py failed to generate reference.pdf!'
            assert os.path.isfile('graphics_reference.pdf'), 'genAll.py failed to generate graphics_reference.pdf!'
        finally:
            os.chdir(cwd)

def makeSuite():
    suite = unittest.TestSuite()
    loader = unittest.TestLoader()
    if sys.platform[:4] != 'java':
        suite.addTest(loader.loadTestsFromTestCase(ManualTestCase))
    return suite

#noruntests
if __name__ == "__main__":
    unittest.TextTestRunner().run(makeSuite())
    printLocation()
