#!/bin/env python
#Copyright ReportLab Europe Ltd. 2000-2004
#see license.txt for license details
#history http://www.reportlab.co.uk/cgi-bin/viewcvs.cgi/public/reportlab/trunk/reportlab/test/test_hello.py
__version__=''' $Id'''
__doc__="""most basic test possible that makes a PDF.

Useful if you want to test that a really minimal PDF is healthy,
since the output is about the smallest thing we can make."""

from reportlab.test import unittest
from reportlab.test.utils import makeSuiteForClasses, outputfile, printLocation
from reportlab.pdfgen.canvas import Canvas


class HelloTestCase(unittest.TestCase):
    "Simplest test that makes PDF"

    def test(self):
        c = Canvas(outputfile('test_hello.pdf'))
        c.setAuthor('\xe3\x83\x9b\xe3\x83\x86\xe3\x83\xab\xe3\x83\xbbe\xe3\x83\x91\xe3\x83\xb3\xe3\x83\x95\xe3\x83\xac\xe3\x83\x83\xe3\x83\x88')
        c.setFont('Helvetica-Bold', 36)
        c.drawString(100,700, 'Hello World')
        c.save()

    def test_rl_config_reset(self):
        from reportlab import rl_config
        from reportlab.pdfbase import pdfmetrics, _fontdata
        tfd = pdfmetrics._typefaces
        fbn = _fontdata.fontsByName
        tfd[' a ']=1
        fbn[' b ']=1
        ntfd = len(tfd)
        nfbn = len(fbn)
        from reportlab.lib import sequencer
        seq = sequencer.getSequencer()
        seq._dingo = 1
        rl_config._reset()
        assert not hasattr(seq,'_dingo')
        assert not tfd.has_key(' a ') and len(tfd)<ntfd
        assert not fbn.has_key(' a ') and len(fbn)<nfbn

def makeSuite():
    return makeSuiteForClasses(HelloTestCase)


#noruntests
if __name__ == "__main__":
    unittest.TextTestRunner().run(makeSuite())
    printLocation()
