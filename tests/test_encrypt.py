#!/bin/env python
#Copyright ReportLab Europe Ltd. 2000-2004
#see license.txt for license details
__version__='''$Id$'''
__doc__="""T4esting to encrypt a very minimal pdf."""

from reportlab.lib.testutils import setOutDir,makeSuiteForClasses, outputfile, printLocation
setOutDir(__name__)
import unittest
from reportlab.pdfgen.canvas import Canvas

class EncryptTestCase(unittest.TestCase):
    """
    Test generating an encrypted pdf.
    TODO: Automatiocally test that this pdf is really encrypted.
    """

    def test(self):
        c = Canvas(outputfile('test_encrypt.pdf'), userPass='User', ownerPass='Owner')
        c.setAuthor('\xe3\x83\x9b\xe3\x83\x86\xe3\x83\xab\xe3\x83\xbbe\xe3\x83\x91\xe3\x83\xb3\xe3\x83\x95\xe3\x83\xac\xe3\x83\x83\xe3\x83\x88')
        c.setFont('Helvetica-Bold', 36)
        c.drawString(100,700, 'Top secret')
        c.save()

def makeSuite():
    return makeSuiteForClasses(EncryptTestCase)


#noruntests
if __name__ == "__main__":
    unittest.TextTestRunner().run(makeSuite())
    printLocation()
