"""Tests for the PythonPoint tool.
"""

import os, sys, string

from reportlab.test import unittest
from reportlab.test.utils import makeSuiteForClasses

import reportlab


class PythonPointTestCase(unittest.TestCase):
    "Some very crude tests on PythonPoint."

    def test0(self):
        "Test if pythonpoint.pdf can be created from pythonpoint.xml."

        join, dirname, isfile, abspath = os.path.join, os.path.dirname, os.path.isfile, os.path.abspath
        rlDir = abspath(dirname(reportlab.__file__))
        from reportlab.tools.pythonpoint import pythonpoint
        ppDir = dirname(pythonpoint.__file__)
        xml = join(ppDir, 'demos', 'pythonpoint.xml')
        outDir = join(rlDir, 'test')
        pdf = join(outDir, 'pythonpoint.pdf')
        if isfile(pdf): os.remove(pdf)

        cwd = os.getcwd()
        os.chdir(join(ppDir, 'demos'))
        pythonpoint.process(xml, outDir=outDir, verbose=0)
        os.chdir(cwd)

        assert os.path.exists(pdf)
        os.remove(pdf)


def makeSuite():
    return makeSuiteForClasses(PythonPointTestCase)


#noruntests
if __name__ == "__main__":
    unittest.TextTestRunner().run(makeSuite())