#copyright ReportLab Inc. 2000
#see license.txt for license details
#history http://cvs.sourceforge.net/cgi-bin/cvsweb.cgi/reportlab/test/test_pdfgen_pagemodes.py?cvsroot=reportlab
#$Header: /tmp/reportlab/reportlab/test/test_pdfgen_pagemodes.py,v 1.4 2001/04/05 09:30:12 rgbecker Exp $
# full screen test

"""Tests for PDF page modes support in reportlab.pdfgen.
"""


import os

from reportlab.test import unittest
from reportlab.pdfgen.canvas import Canvas


def fileDoesExist(path):
    "Check if a file does exist."

    return os.path.exists(path)

    
class PdfPageModeTestCase(unittest.TestCase):
    "Testing different page modes for opening a file in Acrobat Reader."

    baseFileName = 'test_pdfgen_pagemode_'
    
    def _doTest(self, filename, mode, desc):        
        "A generic method called by all test real methods."

        filename = self.baseFileName + filename
        c = Canvas(filename)

        # Handle different modes.
        if mode == 'FullScreen':
            c.showFullScreen0()
        elif mode == 'Outline':
            c.bookmarkPage('page1')
            c.addOutlineEntry('Token Outline Entry', 'page1')
            c.showOutline()
        elif mode == 'UseNone':
            pass

        c.setFont('Helvetica', 20)
        c.drawString(100, 700, desc)
        c.save()

        assert fileDoesExist(filename)


    def test1(self):
        "This should open in full screen mode."
        
        self._doTest('FullScreen.pdf', 'FullScreen', self.test1.__doc__)


    def test2(self):
        "This should open with outline visible."

        self._doTest('Outline.pdf', 'Outline', self.test2.__doc__)


    def test3(self):
        "This should open in the user's default mode."

        self._doTest('UseNone.pdf', 'UseNone', self.test3.__doc__)


def makeSuite():
    suite = unittest.TestSuite()
    
    suite.addTest(PdfPageModeTestCase('test1'))
    suite.addTest(PdfPageModeTestCase('test2'))
    suite.addTest(PdfPageModeTestCase('test3'))

    return suite


#noruntests
if __name__ == "__main__":
    unittest.TextTestRunner().run(makeSuite())
    
