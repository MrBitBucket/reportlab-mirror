#copyright ReportLab Inc. 2000-2001
#see license.txt for license details
#history http://cvs.sourceforge.net/cgi-bin/cvsweb.cgi/reportlab/test/test_pdfbase_pdfutils.py?cvsroot=reportlab
#$Header: /tmp/reportlab/reportlab/test/test_pdfbase_pdfutils.py,v 1.4 2001/09/05 11:47:21 rgbecker Exp $
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

        msg = "Round-trip AsciiBase85 encoding failed."
        plain = 'What is the average velocity of a sparrow?'

        #the remainder block can be absent or from 1 to 4 bytes
        for i in xrange(55):
            encoded = _AsciiBase85Encode(plain)
            decoded = _AsciiBase85Decode(encoded)
            assert decoded == plain, msg
            plain = plain + chr(i)


def makeSuite():
    suite = unittest.TestSuite()
    
    suite.addTest(PdfEncodingTestCase('testAsciiHex'))
    suite.addTest(PdfEncodingTestCase('testAsciiBase85'))

    return suite


#noruntests
if __name__ == "__main__":
    unittest.TextTestRunner().run(makeSuite())
    
