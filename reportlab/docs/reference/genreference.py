#!/bin/env python
#copyright ReportLab Inc. 2001
#see license.txt for license details
#history http://cvs.sourceforge.net/cgi-bin/cvsweb.cgi/docs/reference/genreference.py?cvsroot=reportlab
#$Header: /tmp/reportlab/reportlab/docs/reference/genreference.py,v 1.6 2004/04/28 14:39:23 rgbecker Exp $
__version__=''' $Id: genreference.py,v 1.6 2004/04/28 14:39:23 rgbecker Exp $ '''
__doc__ = """
This module contains the script for building the reference.
"""
def run(verbose=1, outDir=None):
    import os, sys, shutil
    from reportlab.tools.docco import yaml2pdf
    from reportlab.lib.utils import _RL_DIR
    yaml2pdf.run('reference.yml','reference.pdf')
    if verbose: print 'Saved reference.pdf'
    docdir = os.path.join(_RL_DIR,'docs')
    if outDir: docDir = outDir
    destfn = docdir + os.sep + 'reference.pdf'
    shutil.copyfile('reference.pdf', destfn)
    if verbose: print 'copied to %s' % destfn

def makeSuite():
    "standard test harness support - run self as separate process"
    from reportlab.test.utils import ScriptThatMakesFileTest
    return ScriptThatMakesFileTest('../docs/reference', 'genreference.py', 'reference.pdf')


if __name__=='__main__':
    run(verbose=('-s' not in sys.argv))
