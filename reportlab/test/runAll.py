#!/usr/bin/env python
#copyright ReportLab Inc. 2000-2001
#see license.txt for license details
#history http://cvs.sourceforge.net/cgi-bin/cvsweb.cgi/reportlab/test/runAll.py?cvsroot=reportlab
#$Header: /tmp/reportlab/reportlab/test/runAll.py,v 1.17 2004/03/26 14:26:50 rgbecker Exp $
"""Runs all test files in all subfolders.
"""
import os, glob, sys, string, traceback
from reportlab.test import unittest
from reportlab.test.utils import GlobDirectoryWalker, outputfile

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
    _dbg = open('/tmp/_runAll.dbg','w')
    print >>_dbg, "outputfile('')",outputfile('')

    def cleanup(folder,patterns=('*.pdf', '*.log','*.svg','runAll.txt', 'test_*.txt')):
        for pat in patterns:
            for filename in GlobDirectoryWalker(folder, pattern=pat):
                try:
                    os.remove(filename)
                except:
                    pass

    # special case for reportlab/test directory - clean up
    # all PDF & log files before starting run.  You don't
    # want this if reusing runAll anywhere else.
    if string.find(folder, 'reportlab' + os.sep + 'test') > -1: cleanup(folder)
    cleanup(outputfile(''))

    NI = []
    testSuite = makeSuite(folder,nonImportable=NI,pattern=pattern+(not haveSRC and 'c' or ''))
    unittest.TextTestRunner().run(testSuite)
    if haveSRC: cleanup(folder,patterns=('*.pyc','*.pyo'))
    if NI:
        sys.stderr.write('\n###################### the following tests could not be imported\n')
        for f,tb in NI:
            print 'file: "%s"\n%s\n' % (f,string.join(tb,''))

if __name__ == '__main__': #noruntests
    main()
