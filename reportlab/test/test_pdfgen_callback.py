#!/bin/env python
#copyright ReportLab Inc. 2000
#see license.txt for license details
#history http://cvs.sourceforge.net/cgi-bin/cvsweb.cgi/reportlab/pdfgen/test/test_pdfgen_callback.py?cvsroot=reportlab
#$Header: /tmp/reportlab/reportlab/test/test_pdfgen_callback.py,v 1.4 2004/03/26 14:20:44 rgbecker Exp $
__version__=''' $Id: test_pdfgen_callback.py,v 1.4 2004/03/26 14:20:44 rgbecker Exp $ '''
__doc__='checks callbacks work'

from reportlab.test import unittest
from reportlab.test.utils import makeSuiteForClasses, outputfile

from reportlab.pdfgen.canvas import Canvas
from reportlab.test.test_pdfgen_general import makeDocument

_PAGE_COUNT = 0


class CallBackTestCase(unittest.TestCase):
    "checks it gets called"

    def callMe(self, pageNo):
        self.pageCount = pageNo

    def test0(self):
        "Make a PDFgen document with most graphics features"

        self.pageCount = 0
        makeDocument(outputfile('test_pdfgen_callback.pdf'), pageCallBack=self.callMe)
        #no point saving it!
        assert self.pageCount >= 7, 'page count not called!'


def makeSuite():
    return makeSuiteForClasses(CallBackTestCase)


#noruntests
if __name__ == "__main__":
    unittest.TextTestRunner().run(makeSuite())
