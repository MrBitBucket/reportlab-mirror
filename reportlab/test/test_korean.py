
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

        pdfmetrics.registerFont(CIDFont('HYSMyeongJoStd-Medium-Acro','KSCms-UHC-H'))
        pdfmetrics.registerFont(CIDFont('HYSMyeongJoStd-Medium-Acro','KSC-EUC-H'))
        c.setFont('HYSMyeongJoStd-Medium-Acro-KSCms-UHC-H', 16)
        message1 = '\xB9\xD9\xC5\xC1\xC3\xBC'
        c.drawString(100, 675, message1)

        sample = """From Adobe's Acrobat web page:

\xbf\xad \xbc\xf6 \xbe\xf8\xb4\xc2 \xb9\xae\xbc\xad\xb4\xc2 \xbe\xc6\xb9\xab\xb7\xb1 \xbc\xd2\xbf\xeb\xc0\xcc \xbe\xf8\xbd\xc0\xb4\xcf\xb4\xd9. \xbb\xe7\xbe\xf7 \xb0\xe8\xc8\xb9\xbc\xad, \xbd\xba\xc7\xc1\xb7\xb9\xb5\xe5\xbd\xc3\xc6\xae, \xb1\xd7\xb7\xa1\xc7\xc8\xc0\xcc \xb8\xb9\xc0\xcc \xc6\xf7\xc7\xd4\xb5\xc8 \xbc\xd2\xc3\xa5\xc0\xda \xb6\xc7\xb4\xc2 \xc0\xa5
\xbb\xe7\xc0\xcc\xc6\xae\xb8\xa6 \xc0\xdb\xbc\xba\xc7\xcf\xb4\xc2 \xb0\xe6\xbf\xec Adobe\xa2\xe7 Acrobat\xa2\xe7 5.0 \xbc\xd2\xc7\xc1\xc6\xae\xbf\xfe\xbe\xee\xb8\xa6 \xbb\xe7\xbf\xeb\xc7\xd8\xbc\xad \xc7\xd8\xb4\xe7 \xb9\xae\xbc\xad\xb8\xa6 Adobe
Portable Document Format (PDF) \xc6\xc4\xc0\xcf\xb7\xce \xba\xaf\xc8\xaf\xc7\xd2 \xbc\xf6 \xc0\xd6\xbd\xc0\xb4\xcf\xb4\xd9. \xb4\xa9\xb1\xb8\xb3\xaa \xb1\xa4\xb9\xfc\xc0\xa7\xc7\xd1 \xc1\xbe\xb7\xf9\xc0\xc7
\xc7\xcf\xb5\xe5\xbf\xfe\xbe\xee\xbf\xcd \xbc\xd2\xc7\xc1\xc6\xae\xbf\xfe\xbe\xee\xbf\xa1\xbc\xad \xb9\xae\xbc\xad\xb8\xa6 \xbf\xad \xbc\xf6 \xc0\xd6\xc0\xb8\xb8\xe7 \xb7\xb9\xc0\xcc\xbe\xc6\xbf\xf4, \xc6\xf9\xc6\xae, \xb8\xb5\xc5\xa9, \xc0\xcc\xb9\xcc\xc1\xf6 \xb5\xee\xc0\xbb \xbf\xf8\xba\xbb \xb1\xd7\xb4\xeb\xb7\xce \xc0\xc7\xb5\xb5\xc7\xd1 \xb9\xd9 \xb4\xeb\xb7\xce
\xc7\xa5\xbd\xc3\xc7\xd2 \xbc\xf6 \xc0\xd6\xbd\xc0\xb4\xcf\xb4\xd9. Acrobat 5.0\xc0\xbb \xbb\xe7\xbf\xeb\xc7\xcf\xbf\xa9 \xc0\xa5 \xba\xea\xb6\xf3\xbf\xec\xc0\xfa\xbf\xa1\xbc\xad \xb9\xae\xbc\xad\xb8\xa6 \xbd\xc2\xc0\xce\xc7\xcf\xb0\xed \xc1\xd6\xbc\xae\xc0\xbb \xc3\xdf\xb0\xa1\xc7\xcf\xb4\xc2 \xb9\xe6\xbd\xc4\xc0\xb8\xb7\xce
\xb1\xe2\xbe\xf7\xc0\xc7 \xbb\xfd\xbb\xea\xbc\xba\xc0\xbb \xc7\xe2\xbb\xf3\xbd\xc3\xc5\xb3 \xbc\xf6 \xc0\xd6\xbd\xc0\xb4\xcf\xb4\xd9.


\xc0\xfa\xc0\xdb\xb1\xc7 &copy; 2001 Adobe Systems Incorporated. \xb8\xf0\xb5\xe7 \xb1\xc7\xb8\xae\xb0\xa1 \xba\xb8\xc8\xa3\xb5\xcb\xb4\xcf\xb4\xd9.
\xbb\xe7\xbf\xeb\xc0\xda \xbe\xe0\xb0\xfc
\xbf\xc2\xb6\xf3\xc0\xce \xbb\xe7\xbf\xeb\xc0\xda \xba\xb8\xc8\xa3 \xb1\xd4\xc1\xa4
Adobe\xc0\xc7 \xc0\xe5\xbe\xd6\xc0\xda \xc1\xf6\xbf\xf8
\xbc\xd2\xc7\xc1\xc6\xae\xbf\xfe\xbe\xee \xba\xd2\xb9\xfd \xc0\xcc\xbf\xeb \xb9\xe6\xc1\xf6

"""
        tx = c.beginText(100,600)
        tx.setFont('HYSMyeongJoStd-Medium-Acro-KSC-EUC-H', 10)
        tx.textLines(sample)
        c.drawText(tx)
        
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
        c.setFont('HYSMyeongJoStd-Medium-Acro-KSC-EUC-H',4.2)
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
    



