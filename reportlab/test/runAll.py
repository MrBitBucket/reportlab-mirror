#!/usr/bin/env python
#copyright ReportLab Inc. 2000-2001
#see license.txt for license details
#history http://cvs.sourceforge.net/cgi-bin/cvsweb.cgi/reportlab/test/runAll.py?cvsroot=reportlab
#$Header: /tmp/reportlab/reportlab/test/runAll.py,v 1.6 2001/05/30 15:10:56 rgbecker Exp $


"""Runs all test files in all subfolders.
"""


import os, glob, sys, string
from reportlab.test import unittest


def subFoldersOfFolder(folder):
    "Return a list of full paths of all subfolders."

    files = os.listdir(folder)
    files = map(lambda f,folder=folder:os.path.join(folder, f), files)
    subFolders = filter(lambda f: os.path.isdir(f), files)

    return subFolders

    
def removeFiles(rootFolder, ext):
    "Remove in a directory tree all files with some extension."

    subFolders = subFoldersOfFolder(rootFolder)
    for sub in [rootFolder] + subFolders:
        for f in glob.glob(os.path.join(sub, '*' + ext)):
            os.remove(f)
            

def makeSuite(folder):
    "Build a test suite of all test files found."
    
    allTests = unittest.TestSuite()

    # Do not use subfolders, right now...   
    # subFolders = subFoldersOfFolder(folder)
    subFolders = [folder]
    for sub in subFolders:
        files = glob.glob(os.path.join(sub, 'test_*.py'))
        files.sort()
        modulesToTest = map(lambda f:os.path.basename(f)[:-3], files)
        sys.path.insert(0, sub)
        
        for module in map(__import__, modulesToTest):
            allTests.addTest(module.makeSuite())
            
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
        removeFiles(folder, '.pdf')
        removeFiles(folder, '.log')

    testSuite = makeSuite(folder)
    unittest.TextTestRunner().run(testSuite)
    removeFiles(folder, '.pyc')
