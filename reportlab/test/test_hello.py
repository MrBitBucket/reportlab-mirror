#!/bin/env python
#copyright ReportLab Inc. 2000
#see license.txt for license details
#history http://cvs.sourceforge.net/cgi-bin/cvsweb.cgi/reportlab/pdfgen/test/test_hello.py?cvsroot=reportlab
#$Header: /tmp/reportlab/reportlab/test/test_hello.py,v 1.3 2002/07/24 19:56:38 andy_robinson Exp $
__version__=''' $Id'''
__doc__="""most basic test possible that makes a PDF.

Useful if you want to test that a really minimal PDF is healthy,
since the output is about the smallest thing we can make."""

from reportlab.test import unittest
from reportlab.test.utils import makeSuiteForClasses
from reportlab.pdfgen.canvas import Canvas


class HelloTestCase(unittest.TestCase):
    "Simplest test that makes PDF"

    def test(self):
        c = Canvas('test_hello.pdf')
        c.setFont('Helvetica-Bold', 36)
        c.drawString(100,700, 'Hello World')
        c.save()


def makeSuite():
    return makeSuiteForClasses(HelloTestCase)


#noruntests
if __name__ == "__main__":
    unittest.TextTestRunner().run(makeSuite())