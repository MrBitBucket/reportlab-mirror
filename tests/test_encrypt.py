#!/bin/env python
#Copyright ReportLab Europe Ltd. 2000-2012
#see license.txt for license details
__version__='''$Id$'''
__doc__="""Testing to encrypt a very minimal pdf using a Canvas and a DocTemplate.
TODO: Automatiocally test that this pdf is really encrypted.
"""

import unittest
from reportlab.lib.testutils import setOutDir,makeSuiteForClasses, outputfile, printLocation
setOutDir(__name__)
from reportlab.pdfgen.canvas import Canvas
from reportlab.lib import pdfencrypt
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph
from test_pdfencryption import parsedoc

class EncryptTestCase(unittest.TestCase):

    def test_canvas(self):
        "Test generating an encrypted pdf by setting a user password on the Canvas."
        fname = outputfile('test_encrypt_canvas.pdf')
        c = Canvas(fname, encrypt='User')
        c.setAuthor('Anonymous')
        c.setFont('Helvetica-Bold', 36)
        c.drawString(100,700, 'Top secret')
        c.save()
        parsedoc(fname)

    def test_standardencryption(self):
        "Test generating an encrypted pdf by passing a StandardEncryption object to the Canvas."
        encrypt = pdfencrypt.StandardEncryption(userPassword='User', ownerPassword='Owner')
        encrypt.setAllPermissions(0)
        encrypt.canPrint = 1
        fname = outputfile('test_encrypt_canvas2.pdf')
        c = Canvas(fname, encrypt=encrypt)
        c.setAuthor('Anonymous')
        c.setFont('Helvetica-Bold', 36)
        c.drawString(100,700, 'Top secret')
        c.save()
        parsedoc(fname)

    def test_doctemplate(self):
        "Test generating an encrypted pdf by setting a user password on the DocTemplate."
        header = ParagraphStyle(name='Heading', fontSize=36)
        story = [Paragraph("Top secret", header)]
        fname = outputfile('test_encrypt_doctemplate.pdf')
        doc = SimpleDocTemplate(fname, encrypt='User')
        doc.build(story)
        parsedoc(fname)

def makeSuite():
    return makeSuiteForClasses(EncryptTestCase)


#noruntests
if __name__ == "__main__":
    unittest.TextTestRunner().run(makeSuite())
    printLocation()
