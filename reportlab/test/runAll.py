#!/usr/bin/env python
#copyright ReportLab Inc. 2000-2001
#see license.txt for license details
#history http://cvs.sourceforge.net/cgi-bin/cvsweb.cgi/reportlab/test/runAll.py?cvsroot=reportlab
#$Header: /tmp/reportlab/reportlab/test/runAll.py,v 1.7 2001/07/13 16:06:44 dinu_gherman Exp $

"""Runs all test files in all subfolders.
"""


import os, glob, sys, string

from reportlab.test import unittest
from reportlab.test.utils import GlobDirectoryWalker


def makeSuite(folder):
    "Build a test suite of all available test files."
    
    allTests = unittest.TestSuite()

    sys.path.insert(0, folder)
    for filename in GlobDirectoryWalker(folder, 'test_*.py'):
        modname = os.path.splitext(os.path.basename(filename))[0]
        try:
            module = __import__(modname)
            allTests.addTest(module.makeSuite())
        except ImportError:
            pass
    del sys.path[0]
            
    return allTests


#noruntests
if __name__ == '__main__':
    folder = os.path.dirname(sys.argv[0])
    
    # special case for reportlab/test directory - clean up
    # all PDF & log files before starting run.  You don't
    # want this if reusing runAll anywhere else.
    if string.find(folder, 'reportlab' + os.sep + 'test') > -1:
        #print 'cleaning up previous output'
        for pattern in ('*.pdf', '*.log'):
            for filename in GlobDirectoryWalker(folder, pattern):
                os.remove(filename)

    testSuite = makeSuite(folder)
    unittest.TextTestRunner().run(testSuite)
    for filename in GlobDirectoryWalker(folder, '*.pyc'):
        os.remove(filename)
