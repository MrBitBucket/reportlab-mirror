#!/bin/env python
#copyright ReportLab Inc. 2000
#see license.txt for license details
#history http://cvs.sourceforge.net/cgi-bin/cvsweb.cgi/reportlab/pdfgen/test/test_hello.py?cvsroot=reportlab
#$Header: /tmp/reportlab/reportlab/test/test_hello.py,v 1.1 2001/11/26 21:49:01 andy_robinson Exp $
__version__=''' $Id'''
__doc__="""most basic test possible that makes a PDF.

Useful if you want to test that a really minimal PDF is healthy,
since the output is about the smallest thing we can make."""

from reportlab.test import unittest
from reportlab.pdfgen.canvas import Canvas

def run():
    c = Canvas('test_hello.pdf')
    c.setFont('Helvetica-Bold', 36)
    c.drawString(100,700, 'Hello World')
    c.save()


class HelloTestCase(unittest.TestCase):
    "Simplest test that makes PDF"
    def test(self):
        run()

def makeSuite():
    suite = unittest.TestSuite()
    suite.addTest(HelloTestCase('test'))
    return suite

if __name__ == "__main__": #NORUNTESTS
    unittest.TextTestRunner().run(makeSuite())

