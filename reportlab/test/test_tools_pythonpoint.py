"""Tests for the PythonPoint tool.
"""

import os, sys, string

import reportlab
from reportlab.test import unittest
from reportlab.tools.pythonpoint import pythonpoint


class PythonPointTestCase(unittest.TestCase):
    "Some very crude tests on PythonPoint."
    
    def test1(self):
        "Test if pythonpoint.pdf can be created from pythonpoint.xml."

        join = os.path.join

        rlDir = os.path.dirname(reportlab.__file__)
        ppDir = join(rlDir, 'tools', 'pythonpoint')
        xml = join(ppDir, 'demos', 'pythonpoint.xml')
        pp = join(ppDir, 'pythonpoint.py')
        outDir = join(rlDir, 'test')
        pdf = join(outDir, 'pythonpoint.pdf')

        try:
            os.remove(pdf)
        except OSError:
            pass

        if os.path.isfile(pp):
            pythonpoint.process(xml, outDir=outDir, verbose=0)

        assert os.path.exists(pdf)


def makeSuite():
    suite = unittest.TestSuite()
    suite.addTest(PythonPointTestCase('test1'))
    return suite


if __name__ == "__main__":  #NORUNTESTS
    unittest.TextTestRunner().run(makeSuite())
