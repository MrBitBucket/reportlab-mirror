#!/bin/env python
#Copyright ReportLab Europe Ltd. 2000-2004
#see license.txt for license details
#history http://www.reportlab.co.uk/cgi-bin/viewcvs.cgi/public/reportlab/trunk/reportlab/docs/reference/genreference.py
__version__=''' $Id$ '''
__doc__ = """
This module contains the script for building the reference.
"""
def run(verbose=None, outDir=None):
    import os, sys, shutil
    if verbose is None: verbose=('-s' not in sys.argv)
    cwd = os.getcwd()
    docsDir=os.path.dirname(os.path.dirname(sys.argv[0]) or cwd)
    topDir=os.path.dirname(docsDir)
    sys.path.insert(0,topDir)
    from tools.docco import yaml2pdf
    yaml2pdf.run('reference.yml','reference.pdf')
    if verbose: print 'Saved reference.pdf'
    if not outDir: outDir = os.path.join(topDir,'docs')
    destfn = os.path.join(outDir,'reference.pdf')
    shutil.copyfile('reference.pdf', destfn)
    if verbose: print 'copied to %s' % destfn

def makeSuite():
    "standard test harness support - run self as separate process"
    from reportlab.test.utils import ScriptThatMakesFileTest
    return ScriptThatMakesFileTest('../docs/reference', 'genreference.py', 'reference.pdf')


if __name__=='__main__':
    run()
