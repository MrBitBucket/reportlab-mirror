#!/bin/env python
#copyright ReportLab Inc. 2001
#see license.txt for license details
#history http://cvs.sourceforge.net/cgi-bin/cvsweb.cgi/docs/reference/genreference.py?cvsroot=reportlab
#$Header: /tmp/reportlab/reportlab/docs/reference/genreference.py,v 1.3 2001/10/28 21:18:03 andy_robinson Exp $
__version__=''' $Id: genreference.py,v 1.3 2001/10/28 21:18:03 andy_robinson Exp $ '''
__doc__ = """
This module contains the script for building the reference.
"""
import os
import sys
import shutil
import reportlab


def run(verbose=1):
    sys.path.insert(0, '../tools')
    from reportlab.tools.docco import yaml2pdf
    yaml2pdf.run('reference.yml','reference.pdf')
    if verbose: print 'Saved reference.pdf'
    docdir = os.path.dirname(reportlab.__file__) + os.sep + 'docs'
    destfn = docdir + os.sep + 'reference.pdf'
    shutil.copyfile('reference.pdf',
                    destfn)
    if verbose: print 'copied to %s' % destfn

def makeSuite():
    "standard test harness support - run self as separate process"
    from reportlab.test.utils import ScriptThatMakesFileTest
    return ScriptThatMakesFileTest('../docs/reference',
                                   'genreference.py',
                                   'reference.pdf')


if __name__=='__main__':
    run(verbose=('-s' not in sys.argv))
    