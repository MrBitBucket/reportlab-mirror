
import string, os

from reportlab.test import unittest

from reportlab.pdfbase import pdfmetrics
from reportlab.pdfgen.canvas import Canvas
from reportlab.lib import colors

global VERBOSE
VERBOSE = 0



class KoreanFontTests(unittest.TestCase):
    def test1(self):

        # if they do not have the font files or encoding, go away quietly
        try:
            from reportlab.pdfbase.cidfonts import CIDFont, findCMapFile
            findCMapFile('KSCms-UHC-H')
        except:
            #don't have the font pack.  return silently
            return
        
        c = Canvas('test_korean.pdf')
        c.setFont('Helvetica', 30)
        c.drawString(100,700, 'Korean Font Support')

        pdfmetrics.registerFont(CIDFont('\xB9\xD9\xC5\xC1\xC3\xBC','KSCms-UHC-H'))
        c.setFont('\xB9\xD9\xC5\xC1\xC3\xBC-KSCms-UHC-H', 16)
        message1 = '\xB9\xD9\xC5\xC1\xC3\xBC'
        c.drawString(100, 675, message1)
        c.save()
        if VERBOSE:
            print 'saved test_korean.pdf'    
        

def makeSuite():
    suite = unittest.TestSuite()
    suite.addTest(KoreanFontTests('test1'))
    return suite

#noruntests
if __name__ == "__main__":
    VERBOSE = 1
    unittest.TextTestRunner().run(makeSuite())
    



