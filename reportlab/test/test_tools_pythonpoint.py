"""Tests for the PythonPoint tool.
"""
import os, sys, string
import reportlab
from reportlab.test import unittest

class PythonPointTestCase(unittest.TestCase):
	"Some very crude tests on PythonPoint."

	def test1(self):
		"Test if pythonpoint.pdf can be created from pythonpoint.xml."
		join, dirname, isfile, abspath = os.path.join, os.path.dirname, os.path.isfile, os.path.abspath
		rlDir = abspath(dirname(reportlab.__file__))
		from reportlab.tools.pythonpoint import pythonpoint
		ppDir = dirname(pythonpoint.__file__)
		xml = join(ppDir, 'demos', 'pythonpoint.xml')
		outDir = join(rlDir, 'test')
		pdf = join(outDir, 'pythonpoint.pdf')
		if isfile(pdf): os.remove(pdf)
		pythonpoint.process(xml, outDir=outDir, verbose=0)
		assert os.path.exists(pdf)
		os.remove(pdf)

def makeSuite():
	suite = unittest.TestSuite()
	suite.addTest(PythonPointTestCase('test1'))
	return suite

if __name__ == "__main__":	#NORUNTESTS
	unittest.TextTestRunner().run(makeSuite())
