
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

        localFontName = 'HYSMyeongJoStd-Medium-Acro'
        c = Canvas('test_korean.pdf')
        c.setFont('Helvetica', 30)
        c.drawString(100,700, 'Korean Font Support')

        pdfmetrics.registerFont(CIDFont(localFontName,'KSCms-UHC-H'))
        pdfmetrics.registerFont(CIDFont(localFontName,'KSC-EUC-H'))
        c.setFont('%s-KSCms-UHC-H' % localFontName, 16)
        message1 = '\xB9\xD9\xC5\xC1\xC3\xBC'
        c.drawString(100, 675, message1)

        c.showPage()
        # kuten table.  Much of the character set is based on a 94x94 grid
        # which is encoded through various transformations.
        c.setFont('Helvetica', 24)
        c.drawString(100,700, 'Characters available in KSX 1001:1992')
        tx = c.beginText(100, 650)
        tx.setFont('Helvetica',12)
        tx.textLines("""This shows a 94x94 block of glyphs constructed
        programmatically.  The double-byte characters in the KSX 100:1992
        standard are all defined within this space.  Depending on the
        exact encoding used, certain extra vendor specific characters
        may be present.  See the CJKV book for details.
            """)
        c.drawText(tx)        
        c.setFont('%s-KSC-EUC-H' % localFontName,4.2)
        x0 = 100
        y0 = 500
        dx = 4.5
        dy = 4
        for row in range(94):
            y = y0 - row*dy
            c.drawString(50, y, str(row))
            for cell in range(94):
                s = chr(row+161) + chr(cell+161)
                x = x0 + cell*dx
                c.drawString(x,y,s)
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
    



