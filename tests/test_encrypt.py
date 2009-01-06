#!/bin/env python
#Copyright ReportLab Europe Ltd. 2000-2004
#see license.txt for license details
__version__='''$Id$'''
__doc__="""Testing to encrypt a very minimal pdf.
TODO: Automatiocally test that this pdf is really encrypted.
"""

import unittest
from reportlab.lib.testutils import setOutDir,makeSuiteForClasses, outputfile, printLocation
setOutDir(__name__)
from reportlab.pdfgen.canvas import Canvas
from reportlab.lib import pdfencrypt

class EncryptTestCase(unittest.TestCase):
    "Test generating an encrypted pdf by setting a user password."

    def test(self):
        c = Canvas(outputfile('test_encrypt.pdf'), encrypt='User')
        c.setAuthor('\xe3\x83\x9b\xe3\x83\x86\xe3\x83\xab\xe3\x83\xbbe\xe3\x83\x91\xe3\x83\xb3\xe3\x83\x95\xe3\x83\xac\xe3\x83\x83\xe3\x83\x88')
        c.setFont('Helvetica-Bold', 36)
        c.drawString(100,700, 'Top secret')
        c.save()

class PreciseEncryptTestCase(unittest.TestCase):
    "Test generating an encrypted pdf by passing a StandardEncryption object to the Canvas."

    def test(self):
        encrypt = pdfencrypt.StandardEncryption(userPassword='User', ownerPassword='Owner')
        encrypt.setAllPermissions(0)
        encrypt.canPrint = 1
        c = Canvas(outputfile('test_encrypt2.pdf'), encrypt=encrypt)
        c.setAuthor('\xe3\x83\x9b\xe3\x83\x86\xe3\x83\xab\xe3\x83\xbbe\xe3\x83\x91\xe3\x83\xb3\xe3\x83\x95\xe3\x83\xac\xe3\x83\x83\xe3\x83\x88')
        c.setFont('Helvetica-Bold', 36)
        c.drawString(100,700, 'Top secret')
        c.save()

def makeSuite():
    return makeSuiteForClasses(EncryptTestCase, PreciseEncryptTestCase)


#noruntests
if __name__ == "__main__":
    unittest.TextTestRunner().run(makeSuite())
    printLocation()
