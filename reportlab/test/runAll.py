#!/usr/bin/env python
#copyright ReportLab Inc. 2000-2001
#see license.txt for license details
#history http://cvs.sourceforge.net/cgi-bin/cvsweb.cgi/reportlab/test/runAll.py?cvsroot=reportlab
#$Header: /tmp/reportlab/reportlab/test/runAll.py,v 1.15 2004/03/23 14:46:35 rgbecker Exp $
"""Runs all test files in all subfolders.
"""
import os, glob, sys, string, traceback
from reportlab.test import unittest
from reportlab.test.utils import GlobDirectoryWalker

def makeSuite(folder, exclude=[],nonImportable=[],pattern='test_*.py'):
    "Build a test suite of all available test files."

    allTests = unittest.TestSuite()

    if os.path.isdir(folder): sys.path.insert(0, folder)
    for filename in GlobDirectoryWalker(folder, pattern):
        modname = os.path.splitext(os.path.basename(filename))[0]
        if modname not in exclude:
            try:
                exec 'import %s as module' % modname
                allTests.addTest(module.makeSuite())
            except:
                tt, tv, tb = sys.exc_info()[:]
                nonImportable.append((filename,traceback.format_exception(tt,tv,tb)))
                del tt,tv,tb
    del sys.path[0]

    return allTests


def main(pattern='test_*.py'):
    try:
        folder = os.path.dirname(__file__)
    except:
        folder = os.path.dirname(sys.argv[0]) or os.getcwd()
    from reportlab.lib.utils import isSourceDistro
    haveSRC = isSourceDistro()

    # special case for reportlab/test directory - clean up
    # all PDF & log files before starting run.  You don't
    # want this if reusing runAll anywhere else.
    if string.find(folder, 'reportlab' + os.sep + 'test') > -1:
        #print 'cleaning up previous output'
        for pat in ('*.pdf', '*.log'):
            for filename in GlobDirectoryWalker(folder, pattern=pat):
                os.remove(filename)

    NI = []
    testSuite = makeSuite(folder,nonImportable=NI,pattern=pattern+(not haveSRC and 'c' or ''))
    unittest.TextTestRunner().run(testSuite)
    if haveSRC:
        for filename in GlobDirectoryWalker(folder, '*.pyc'):
            try:
                os.remove(filename)
            except:
                pass
    if NI:
        sys.stderr.write('\n###################### the following tests could not be imported\n')
        for f,tb in NI:
            print 'file: "%s"\n%s\n' % (f,string.join(tb,''))

if __name__ == '__main__': #noruntests
    main()
