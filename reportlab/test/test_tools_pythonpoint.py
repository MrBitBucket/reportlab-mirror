"""Tests for the (soon to be) reportlab.tools.pythonpoint package.
"""
import os, sys, string
from reportlab.test import unittest
from reportlab.test.utils import SecureTestCase

if sys.platform == 'win32':
	def _quote(*args):
		fmt = max(map(lambda s: len(string.split(s)), args))>1 and '"%s"' or '%s'
		return fmt % string.join(map(lambda s: len(string.split(s))>1 and '"%s"' % s or s, args),' ')
else:
	def _quote(*args):
		return string.join(args,' ')

class PythonPointTestCase(SecureTestCase):
    "Some very crude tests on PythonPoint."
    
    def test1(self):
        "Test if pythonpoint.pdf can be created from pythonpoint.xml."
        import reportlab
        rlDir = os.path.dirname(reportlab.__file__)
        ppDir = os.path.join(rlDir, 'tools', 'pythonpoint')
        pdf = os.path.join(ppDir,'demos','pythonpoint.pdf')
        xml = os.path.join(ppDir,'demos','pythonpoint.xml')
        pp = os.path.join(ppDir,'pythonpoint.py')
        exe = os.path.abspath(os.path.join(rlDir,'..','pythonpoint.exe'))

        quiet = "-s"  # no output wanted
        try:
            os.remove(pdf)
        except OSError:
            pass

        if os.path.isfile(pp):
            os.system(_quote(sys.executable,pp,xml, quiet))
        elif os.path.isfile(exe):
            print _quote(exe,xml,quiet)
            os.system(_quote(exe,xml,quiet))

        assert os.path.exists(pdf)

def makeSuite():
    suite = unittest.TestSuite()
    suite.addTest(PythonPointTestCase('test1'))
    return suite

if __name__ == "__main__":  #NORUNTESTS
    unittest.TextTestRunner().run(makeSuite())
