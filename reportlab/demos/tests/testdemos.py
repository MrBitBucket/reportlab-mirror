#!/bin/env python
#copyright ReportLab Inc. 2000
#see license.txt for license details
#history http://cvs.sourceforge.net/cgi-bin/cvsweb.cgi/reportlab/demos/tests/testdemos.py?cvsroot=reportlab
#$Header: /tmp/reportlab/reportlab/demos/tests/testdemos.py,v 1.7 2002/07/24 19:56:35 andy_robinson Exp $
__version__=''' $Id: testdemos.py,v 1.7 2002/07/24 19:56:35 andy_robinson Exp $ '''
__doc__='Test all demos'
_globals=globals().copy()
import os, sys
from reportlab import pdfgen

for p in ('pythonpoint/pythonpoint.py','stdfonts/stdfonts.py','odyssey/odyssey.py', 'gadflypaper/gfe.py'):
    fn = os.path.normcase(os.path.normpath(os.path.join(os.path.dirname(pdfgen.__file__),'..','demos',p)))
    os.chdir(os.path.dirname(fn))
    execfile(fn,_globals.copy())