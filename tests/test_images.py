#!/bin/env python
#Copyright ReportLab Europe Ltd. 2000-2017
#see license.txt for license details
__version__='3.3.0'
__doc__="""Tests to do with image handling.

Most of them make use of test\\pythonpowereed.gif."""
from reportlab.lib.testutils import setOutDir,makeSuiteForClasses, printLocation
setOutDir(__name__)
import os
import unittest
from hashlib import md5
from reportlab.lib.utils import ImageReader


"""To avoid depending on external stuff, I made a small 5x5 image and
attach its 'file contents' here in several formats.

The image looks like this, with K=black, R=red, G=green, B=blue, W=white.
    K R G B W
    K R G B W
    K R G B W
    K R G B W
    K R G B W
"""
sampleRAW = '\x00\x00\x00\xff\x00\x00\x00\xff\x00\x00\x00\xff\xff\xff\xff\x00\x00\x00\xff\x00\x00\x00\xff\x00\x00\x00\xff\xff\xff\xff\x00\x00\x00\xff\x00\x00\x00\xff\x00\x00\x00\xff\xff\xff\xff\x00\x00\x00\xff\x00\x00\x00\xff\x00\x00\x00\xff\xff\xff\xff\x00\x00\x00\xff\x00\x00\x00\xff\x00\x00\x00\xff\xff\xff\xff'
samplePNG = '\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x05\x00\x00\x00\x05\x08\x02\x00\x00\x00\x02\r\xb1\xb2\x00\x00\x00:IDATx\x9cb```\xf8\x0f\xc3\xff\xff\xff\x07\x00\x00\x00\xff\xffbb@\x05\x00\x00\x00\x00\xff\xffB\xe7\x03\x00\x00\x00\xff\xffB\xe7\x03\x00\x00\x00\xff\xffB\xe7\x03\x00\x00\x00\xff\xff\x03\x00\x9e\x01\x06\x03\x03\xc4A\xb4\x00\x00\x00\x00IEND\xaeB`\x82'

class ReaderTestCase(unittest.TestCase):
    "Simplest tests to import images, work under Jython or PIL"

    def test(self):
        from reportlab.lib.testutils import testsFolder
        from reportlab.lib.utils import rl_isfile
        imageFileName = os.path.join(testsFolder,'pythonpowered.gif')
        assert rl_isfile(imageFileName), "%s not found!" % imageFileName
        ir = ImageReader(imageFileName)
        assert ir.getSize() == (110,44)
        pixels = ir.getRGBData()
        assert md5(pixels).hexdigest() == '02e000bf3ffcefe9fc9660c95d7e27cf'

    def testUseA85(self):
        '''test for bitbucket PR #59 by Vytis Banaitis'''
        from reportlab import rl_config
        from reportlab.pdfgen.canvas import Canvas
        old = rl_config.useA85
        try:    
            for v in 1, 0:
                rl_config.useA85 = v
                c = Canvas('test_useA85%s.pdf' % v)
                c.drawImage('test-rgba.png', 0,0)
                c.showPage()
                c.save()
        finally:
            rl_config.useA85 = old

def makeSuite():
    return makeSuiteForClasses(ReaderTestCase)

#noruntests
if __name__ == "__main__":
    unittest.TextTestRunner().run(makeSuite())
    printLocation()
