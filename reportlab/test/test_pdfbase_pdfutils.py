"""Tests for utility functions in reportlab.pdfbase.pdfutils.
"""


import os

from reportlab.test import unittest
from reportlab.pdfbase.pdfutils import _AsciiHexEncode, _AsciiHexDecode
from reportlab.pdfbase.pdfutils import _AsciiBase85Encode, _AsciiBase85Decode


class PdfEncodingTestCase(unittest.TestCase):
    "Test various encodings used in PDF files."

    def testAsciiHex(self):
        "Test if the obvious test for whether ASCII-Hex encoding works."

        plainText = 'What is the average velocity of a sparrow?'
        encoded = _AsciiHexEncode(plainText)
        decoded = _AsciiHexDecode(encoded)
        
        msg = "Round-trip AsciiHex encoding failed."
        assert decoded == plainText, msg


    def testAsciiBase85(self):
        "Test if the obvious test for whether ASCII-Base85 encoding works."

        plainText = 'What is the average velocity of a sparrow?'
        encoded = _AsciiBase85Encode(plainText)
        decoded = _AsciiBase85Decode(encoded)
        
        msg = "Round-trip AsciiBase85 encoding failed."
        assert decoded == plainText, msg


def makeSuite():
    suite = unittest.TestSuite()
    
    suite.addTest(PdfEncodingTestCase('testAsciiHex'))
    suite.addTest(PdfEncodingTestCase('testAsciiBase85'))

    return suite


if __name__ == "__main__":
    unittest.TextTestRunner().run(makeSuite())
    
