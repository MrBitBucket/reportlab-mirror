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
		rlDir = os.path.dirname(reportlab.__file__)
		ppDir = os.path.join(rlDir, 'tools', 'pythonpoint')
		pdf = os.path.join(ppDir,'demos','pythonpoint.pdf')
		xml = os.path.join(ppDir,'demos','pythonpoint.xml')
		pp = os.path.join(ppDir,'pythonpoint.py')
		exe = os.path.abspath(os.path.join(rlDir,'..','pythonpoint.exe'))

		try:
			os.remove(pdf)
		except OSError:
			pass

		if os.path.isfile(pp):
			os.system("%s %s %s" % (sys.executable,pp,xml))
		elif os.path.isfile(exe):
			os.system("%s %s" % (exe,xml))

		assert os.path.exists(pdf)

def makeSuite():
	suite = unittest.TestSuite()
	suite.addTest(PythonPointTestCase('test1'))
	return suite

if __name__ == "__main__":	#NORUNTESTS
	unittest.TextTestRunner().run(makeSuite())
