#!/bin/env python
#copyright ReportLab Inc. 2001
#see license.txt for license details
#history http://cvs.sourceforge.net/cgi-bin/cvsweb.cgi/docs/reference/genreference.py?cvsroot=reportlab
#$Header: /tmp/reportlab/reportlab/docs/reference/genreference.py,v 1.1 2001/10/05 12:33:33 rgbecker Exp $
__version__=''' $Id: genreference.py,v 1.1 2001/10/05 12:33:33 rgbecker Exp $ '''
__doc__ = """
This module contains the script for building the reference.
"""
import os
import sys
import shutil
import reportlab


def run():
    sys.path.insert(0, '../tools')
    import yaml2pdf
    yaml2pdf.run('reference.yml','reference.pdf')
    docdir = os.path.dirname(reportlab.__file__) + os.sep + 'docs'
    destfn = docdir + os.sep + 'reference.pdf'
    shutil.copyfile('reference.pdf',
                    destfn)
    print 'copied to %s' % destfn

def makeSuite():
    "standard test harness support - run self as separate process"
    from reportlab.test.utils import ScriptThatMakesFileTest
    return ScriptThatMakesFileTest('../docs/reference',
                                   'genreference.py',
                                   'reference.pdf')


if __name__=='__main__':
    run()
    