#!/bin/env python
#copyright ReportLab Inc. 2000
#see license.txt for license details
#history http://cvs.sourceforge.net/cgi-bin/cvsweb.cgi/reportlab/pdfgen/test/test_hello.py?cvsroot=reportlab
#$Header: /tmp/reportlab/reportlab/test/test_pdfbase_postscript.py,v 1.2 2004/01/20 22:50:32 andy_robinson Exp $
__version__=''' $Id'''
__doc__="""Tests Postscript XObjects.

Nothing visiblke in Acrobat, but the resulting files
contain graphics and tray commands if exported to
a Postscript device in Acrobat 4.0"""

from reportlab.test import unittest
from reportlab.test.utils import makeSuiteForClasses
from reportlab.pdfgen.canvas import Canvas


class PostScriptTestCase(unittest.TestCase):
    "Simplest test that makes PDF"

    def testVisible(self):
        "Makes a document with extra text - should export and distill"
        c = Canvas('test_pdfbase_postscript_visible.pdf')
        c.setPageCompression(0)

        c.setFont('Helvetica-Bold', 18)
        c.drawString(100,700, 'Hello World. This is page 1 of a 2 page document.')
        c.showPage()

        c.setFont('Helvetica-Bold', 16)
        c.drawString(100,700, 'Page 2. This has some postscript drawing code.')
        c.drawString(100,680, 'If you print it using a PS device and Acrobat 4/5,')
        c.drawString(100,660, 'or export to Postscript, you should see the word')
        c.drawString(100,640, '"Hello PostScript" below.  In ordinary Acrobat Reader')
        c.drawString(100,620, 'we expect to see nothing.')
        c.addPostScriptCommand('/Helvetica findfont 48 scalefont setfont 100 400 moveto (Hello PostScript) show')


        c.save()

    def testTray(self):
        "Makes a document with tray command - only works on printers supporting it"
        c = Canvas('test_pdfbase_postscript_tray.pdf')
        c.setPageCompression(0)

        c.setFont('Helvetica-Bold', 18)
        c.drawString(100,700, 'Hello World. This is page 1 of a 2 page document.')
        c.drawString(100,680, 'This also has a tray command ("5 setpapertray").')
        c.addPostScriptCommand('5 setpapertray')
        c.showPage()

        c.setFont('Helvetica-Bold', 16)
        c.drawString(100,700, 'Page 2. This should come from a different tray.')
        c.drawString(100,680, 'Also, if you print it using a PS device and Acrobat 4/5,')
        c.drawString(100,660, 'or export to Postscript, you should see the word')
        c.drawString(100,640, '"Hello PostScript" below.  In ordinary Acrobat Reader')
        c.drawString(100,620, 'we expect to see nothing.')
        c.addPostScriptCommand('/Helvetica findfont 48 scalefont setfont 100 400 moveto (Hello PostScript) show')


        c.save()

def makeSuite():
    return makeSuiteForClasses(PostScriptTestCase)


#noruntests
if __name__ == "__main__":
    unittest.TextTestRunner().run(makeSuite())
    print 'saved test_pdfgen_postscript_visible.pdf'
    print 'saved test_pdfgen_postscript_tray.pdf'

