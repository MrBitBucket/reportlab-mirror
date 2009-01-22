#copyright ReportLab Europe Limited. 2000-2006
#see license.txt for license details
import os, sys
import unittest
from reportlab.lib.testutils import setOutDir,makeSuiteForClasses, outputfile, printLocation
setOutDir(__name__)
from reportlab.pdfgen import canvas
from reportlab.lib import pdfencrypt


def makedoc(fileName, userPass="User", ownerPass="Owner"):
    """
    Creates a simple encrypted pdf.
    """
    encrypt = pdfencrypt.StandardEncryption(userPass, ownerPass)
    encrypt.setAllPermissions(0)
    encrypt.canPrint = 1

    c = canvas.Canvas(fileName)
    c._doc.encrypt = encrypt

    c.drawString(100, 500, "hello world")

    c.save()

def parsedoc(fileName):
    """
    Using PDFParseContext object from Pagecatcher module to check for encryption.
    """
    
    try:
        from rlextra.pageCatcher.pageCatcher import PDFParseContext
    except ImportError:
        return
    pdfContent = open(fileName, 'rb').read()
    p = PDFParseContext(pdfContent, prefix="PageForms")
    p.parse()
    assert p.encrypt

class ManualTestCase(unittest.TestCase):
    "Runs manual encrypted file builders."

    def test(self):
        filepath = outputfile('test_pdfencryption.pdf')
        makedoc(filepath)
        parsedoc(filepath)

def makeSuite():
    return makeSuiteForClasses(ManualTestCase)

if __name__ == "__main__":
    unittest.TextTestRunner().run(makeSuite())
