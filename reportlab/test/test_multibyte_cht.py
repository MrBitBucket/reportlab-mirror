#Copyright ReportLab Europe Ltd. 2000-2004
#see license.txt for license details
#history www.reportlab.co.uk/rl-cgi/viewcvs.cgi/rlextra/rlj/jpsupport.py
# Temporary japanese support for ReportLab.
"""
Test of traditional Chinese (as written in Taiwan)
"""


import string, os

from reportlab.test import unittest
from reportlab.test.utils import makeSuiteForClasses, outputfile, printLocation

from reportlab.pdfbase import pdfmetrics
from reportlab.pdfgen.canvas import Canvas
from reportlab.lib import colors
from reportlab.lib.codecharts import Big5CodeChart, hBoxText

global VERBOSE
VERBOSE = 0


class CHTFontTests(unittest.TestCase):

    def hDraw(self, c, msg, fnt, x, y):
        "Helper - draws it with a box around"
        c.setFont(fnt, 16, 16)
        c.drawString(x, y, msg)
        c.rect(x,y,pdfmetrics.stringWidth(msg, fnt, 16),16,stroke=1,fill=0)


    def test0(self):
        "A basic document drawing some strings"

        # if they do not have the Japanese font files, go away quietly
        from reportlab.pdfbase.cidfonts import UnicodeCIDFont, findCMapFile


##        enc = 'ETenms-B5-H'
##        try:
##            findCMapFile(enc)
##        except:
##            #they don't have the font pack, return silently
##            print 'CMap not found'
##            return
        pdfmetrics.registerFont(UnicodeCIDFont('MSung-Light'))

        c = Canvas(outputfile('test_multibyte_cht.pdf'))
        c.setFont('Helvetica', 24)
        c.drawString(100,700, 'Traditional Chinese Font Support')
        c.setFont('Helvetica', 10)
        c.drawString(100,680, 'Short sample: headline from Yahoo Hong Kong, 20 Oct 2001')

##        c.setFont('MSung-Light-' + enc, 12)
##        # this came from Yahoo Hong Kong leading story today
##        message1 = '\xa5\xac\xae\xed\xbbP\xa6\xbf\xbfA\xa5\xc1\xa6b\xad\xba\xa6\xb8\xb7|\xad\xb1\xab\xe1\xa4@\xa6P\xa8\xa3\xb0O\xaa\xcc\xa1A\xa5L\xbb\xa1\xa1A\xa8\xe2\xa4H\xaa\xba\xad\xba\xa6\xb8\xb7|\xad\xb1\xabD\xb1`'
##        message2 = '\xa6n\xa1A\xa8\xc3\xaa\xed\xa5\xdc\xb2@\xb5L\xba\xc3\xb0\xdd\xa4\xa4\xb0\xea\xa6b\xb3o\xad\xd3\xa5i\xa9\xc6\xaa\xba\xae\xc9\xa8\xe8\xa1A\xb7|\xbbP\xac\xfc\xb0\xea\xa4H\xa5\xc1\xaf\xb8\xa6b\xa4@\xb0_\xa1C'
##        message3 = '\xA7\x41\xA6\x6E\xB6\xDC'
##
##
##        c.drawString(100, 655, message1)
##        c.drawString(100, 639, message2)
##
##        hBoxText(message3 + ' MSung-Light' , c, 100, 600, 'MSung-Light', enc)
##        #hBoxText(message3 + ' MHei-Medium', c, 100, 580, 'MHei-Medium', enc)
##
##
##
##        c.setFont('Helvetica', 10)
##        tx = c.beginText(100, 500)
##        tx.textLines("""
##            This test document shows Traditional Chinese output from Reportlab PDF Library.
##            You may use one Chinese font, MSung-Light, and a number of different
##            encodings.
##
##            The available encoding names (with comments from the PDF specification) are:
##            encodings_cht = [
##                'B5pc-H',           # Macintosh, Big Five character set, Big Five encoding,
##                                    # Script Manager code 2
##                'B5pc-V',           # Vertical version of B5pc-H
##                'ETen-B5-H',        # Microsoft Code Page 950 (lfCharSet 0x88), Big Five
##                                    # character set with ETen extensions
##                'ETen-B5-V',        # Vertical version of ETen-B5-H
##                'ETenms-B5-H',      # Microsoft Code Page 950 (lfCharSet 0x88), Big Five
##                                    # character set with ETen extensions; this uses proportional
##                                    # forms for half-width Latin characters.
##                'ETenms-B5-V',      # Vertical version of ETenms-B5-H
##                'CNS-EUC-H',        # CNS 11643-1992 character set, EUC-TW encoding
##                'CNS-EUC-V',        # Vertical version of CNS-EUC-H
##                'UniCNS-UCS2-H',    # Unicode (UCS-2) encoding for the Adobe-CNS1
##                                    # character collection
##                'UniCNS-UCS2-V'    # Vertical version of UniCNS-UCS2-H.
##                ]
##
##            The next 32 pages show the complete character set available in the encoding
##            "ETen-B5-H".  This is Big5 with the ETen extensions.  ETen extensions are the
##            most common extension to Big5 and include circled and roman numbers, Japanese
##            hiragana and katakana, Cyrillic and fractions in rows C6-C8; and 7 extra characters
##            and some line drawing characters in row F9.
##            """)
##        c.drawText(tx)
##        c.setFont('Helvetica',10)
##        c.drawCentredString(297, 36, 'Page %d' % c.getPageNumber())
##
##        c.showPage()
##
##        # full Big5 code page
##        c.setFont('Helvetica', 18)
##        c.drawString(72,750, 'Characters available in Big 5')
##        y = 500
##        for row in range(0xA1,0xFF):
##            cc = Big5CodeChart(row, 'MSung-Light',enc)
##            cc.charsPerRow = 16
##            cc.rows = 10
##            cc.codePoints = 160
##            cc.drawOn(c, 72, y)
##            y = y - cc.height - 25
##            if y < 50:
##                c.setFont('Helvetica',10)
##                c.drawCentredString(297, 36, 'Page %d' % c.getPageNumber())
##                c.showPage()
##                y = 600
##
##
        c.save()
        if VERBOSE:
            print 'saved '+outputfile('test_multibyte_cht.pdf')


def makeSuite():
    return makeSuiteForClasses(CHTFontTests)


#noruntests
if __name__ == "__main__":
    VERBOSE = 1
    unittest.TextTestRunner().run(makeSuite())
    printLocation()
