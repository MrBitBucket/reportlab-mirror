#copyright ReportLab Inc. 2000
#see license.txt for license details
#history www.reportlab.co.uk/rl-cgi/viewcvs.cgi/rlextra/rlj/jpsupport.py
#$Header: /tmp/reportlab/reportlab/test/test_multibyte_chs.py,v 1.3 2002/07/04 09:24:49 dinu_gherman Exp $
# Temporary japanese support for ReportLab.
"""
The code in this module will disappear any day now and be replaced
by classes in reportlab.pdfbase.cidfonts
"""


import string, os

from reportlab.test import unittest
from reportlab.test.utils import makeSuiteForClasses

from reportlab.pdfbase import pdfmetrics
from reportlab.pdfgen.canvas import Canvas
from reportlab.lib import colors
from reportlab.lib.codecharts import KutenRowCodeChart, hBoxText

global VERBOSE
VERBOSE = 0


class CHSFontTests(unittest.TestCase):
    
    def test0(self):
        "A basic document drawing some strings"

        # if they do not have the Japanese font files, go away quietly
        from reportlab.pdfbase.cidfonts import CIDFont, findCMapFile


        enc = 'GB-EUC-H'
        try:
            findCMapFile(enc)
        except:
            #they don't have the font pack, return silently
            return
        pdfmetrics.registerFont(CIDFont('STSong-Light',enc))
    
        c = Canvas('test_multibyte_chs.pdf')
        c.setFont('Helvetica', 30)
        c.drawString(100,700, 'Simplified Chinese Font Support')


        c.setFont('Helvetica', 10)
        c.drawString(100,680, 'Short sample: "Reportlab is cool!" (or so we are told)')
        # the two typefaces

        hBoxText('\xce\xc4\xbd\xa1\xb5\xc3\xb5\xbd\xc1\xcb \xc4\xc7\xd5\xfd\xba\xc3\xb0\xa2  \xce\xd2 \xba\xdc\xcf\xb2\xbb\xb6. Cool!',
                 c,
                 100,
                 660,
                 'STSong-Light',
                 enc)
        

        c.setFont('Helvetica', 10)
        tx = c.beginText(100, 500)
        tx.textLines("""
            This test document shows Simplified Chinese output from the Reportlab PDF Library.
            You may use one Chinese font, STSong-Light, and a number of different encodings.

            The available encoding names (with comments from the PDF specification) are:
            encodings_chs = [
                'GB-EUC-H',         # Microsoft Code Page 936 (lfCharSet 0x86), GB 2312-80
                                    # character set, EUC-CN encoding
                'GB-EUC-V',         # Vertical version of GB-EUC-H
                'GBpc-EUC-H',       # Macintosh, GB 2312-80 character set, EUC-CN encoding,
                                    # Script Manager code 2
                'GBpc-EUC-V',       # Vertical version of GBpc-EUC-H
                'GBK-EUC-H',        # Microsoft Code Page 936 (lfCharSet 0x86), GBK character
                                    # set, GBK encoding
                'GBK-EUC-V',        # Vertical version of GBK-EUC-V
                'UniGB-UCS2-H',     # Unicode (UCS-2) encoding for the Adobe-GB1
                                    # character collection
                'UniGB-UCS2-V'     # Vertical version of UniGB-UCS2-H.
                ]

            The next few pages show the complete character set available in the encoding
            "GB-EUC-H".  This is the GB 2312-80 character set.
            """)
        c.drawText(tx)
        
        c.setFont('Helvetica',10)
        c.drawCentredString(297, 36, 'Page %d' % c.getPageNumber())
        c.showPage()
        
        # full kuten chart in EUC
        c.setFont('Helvetica', 18)
        c.drawString(72,750, 'Characters available in GB 2312-80, EUC encoding')
        y = 600
        for row in range(1, 95):
            KutenRowCodeChart(row, 'STSong-Light',enc).drawOn(c, 72, y)
            y = y - 125
            if y < 50:
                c.setFont('Helvetica',10)
                c.drawCentredString(297, 36, 'Page %d' % c.getPageNumber())
                c.showPage()
                y = 700

        c.save()
        if VERBOSE:
            print 'saved test_multibyte_chs.pdf'


def makeSuite():
    return makeSuiteForClasses(CHSFontTests)


#noruntests
if __name__ == "__main__":
    VERBOSE = 1
    unittest.TextTestRunner().run(makeSuite())

