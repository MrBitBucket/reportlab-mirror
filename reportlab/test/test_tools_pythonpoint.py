"""Tests for the (soon to be) reportlab.tools.pythonpoint package.
"""


import os, sys

from reportlab.test import unittest
from reportlab.test.utils import SecureTestCase


class PythonPointTestCase(SecureTestCase):
    "Some very crude tests on PythonPoint."
    
    def test1(self):
        "Test if pythonpoint.pdf can be created from pythonpoint.xml."

        import reportlab
        rlFolder = os.path.dirname(reportlab.__file__)
        ppFolder = os.path.join(rlFolder, 'tools', 'pythonpoint')
        os.chdir(ppFolder)

        try:
            os.remove('pythonpoint.pdf')
        except OSError:
            pass

##        sys.argv.insert(0, ppFolder)
##        import pythonpoint
##        pythonpoint.process('pythonpoint.xml')
        os.system("python pythonpoint.py demos" + os.sep + "pythonpoint.xml")

        assert os.path.exists(os.path.join('demos','pythonpoint.pdf'))


def makeSuite():
    suite = unittest.TestSuite()
    
    suite.addTest(PythonPointTestCase('test1'))
##    suite.addTest(ColorTestCase('test2'))
##    suite.addTest(ColorTestCase('test3'))
##    suite.addTest(ColorTestCase('test4'))
##    suite.addTest(ColorTestCase('test5'))
##    suite.addTest(ColorTestCase('test6'))

    return suite


#noruntests
if __name__ == "__main__":
    unittest.TextTestRunner().run(makeSuite())
