#!/bin/env python
#copyright ReportLab Inc. 2000
#see license.txt for license details
#history http://cvs.sourceforge.net/cgi-bin/cvsweb.cgi/reportlab/pdfgen/test/test_images.py?cvsroot=reportlab
#$Header: /tmp/reportlab/reportlab/test/test_images.py,v 1.2 2003/09/08 16:09:51 rgbecker Exp $
__version__=''' $Id'''
__doc__="""Tests to do with image handling.

Most of them make use of test\pythonpowereed.gif."""
import os,md5

from reportlab.test import unittest
from reportlab.test.utils import makeSuiteForClasses
from reportlab.lib.utils import ImageReader

class ReaderTestCase(unittest.TestCase):
    "Simplest tests to import images, work under Jython or PIL"

    def test(self):
        import reportlab.test
        imageFileName = os.path.dirname(reportlab.test.__file__) + os.sep + 'pythonpowered.gif'
        assert os.path.isfile(imageFileName), "%s not found!" % imageFileName

        ir = ImageReader(imageFileName)
        assert ir.getSize() == (110,44)        
        pixels = ir.getRGBData()
        assert md5.md5(pixels).hexdigest() == '02e000bf3ffcefe9fc9660c95d7e27cf'
        

def makeSuite():
    return makeSuiteForClasses(ReaderTestCase)


#noruntests
if __name__ == "__main__":
    unittest.TextTestRunner().run(makeSuite())
