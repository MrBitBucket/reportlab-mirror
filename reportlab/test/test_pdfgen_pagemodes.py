#copyright ReportLab Inc. 2000
#see license.txt for license details
#history http://cvs.sourceforge.net/cgi-bin/cvsweb.cgi/reportlab/pdfgen/test/testPageMode.py?cvsroot=reportlab
#$Header: /tmp/reportlab/reportlab/test/test_pdfgen_pagemodes.py,v 1.1 2001/02/14 11:29:36 dinu_gherman Exp $
# full screen test


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


if __name__ == "__main__":
    unittest.TextTestRunner().run(makeSuite())
    
