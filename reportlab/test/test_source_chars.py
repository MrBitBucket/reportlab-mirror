#!/usr/bin/env python
#copyright ReportLab Inc. 2000-2001
#see license.txt for license details
#history http://cvs.sourceforge.net/cgi-bin/cvsweb.cgi/reportlab/test/test_source_chars.py?cvsroot=reportlab
#$Header: /tmp/reportlab/reportlab/test/test_source_chars.py,v 1.1 2002/07/17 22:46:24 andy_robinson Exp $

"""This tests for things in source files.  Initially, absence of tabs :-)
"""

import os, sys, glob, string, re
from types import ModuleType, ClassType, MethodType, FunctionType

import reportlab
from reportlab.test import unittest
from reportlab.test.utils import makeSuiteForClasses
from reportlab.test.utils import SecureTestCase, GlobDirectoryWalker


class SourceTester(SecureTestCase):
    def checkFileForTabs(self, filename):
        txt = open(filename, 'r').read()
        chunks = string.split(txt, '\t')
        tabCount = len(chunks) - 1
        if tabCount:
            #raise Exception, "File %s contains %d tab characters!" % (filename, tabCount)
            print "file %s contains %d tab characters!" % (filename, tabCount)
        
    def testForTabs(self):
        topDir = os.path.dirname(reportlab.__file__)
        w = GlobDirectoryWalker(topDir, '*.py')
        for filename in w:
            self.checkFileForTabs(filename)
            

            

def makeSuite():
    return makeSuiteForClasses(SourceTester)


#noruntests
if __name__ == "__main__":
    unittest.TextTestRunner().run(makeSuite())
