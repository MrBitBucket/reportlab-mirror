#copyright ReportLab Inc. 2000
#see license.txt for license details
#history www.reportlab.co.uk/rl-cgi/viewcvs.cgi/rlextra/rlj/jpsupport.py
#$Header: /tmp/reportlab/reportlab/test/Attic/test_japanese.py,v 1.1 2001/09/04 08:52:13 andy_robinson Exp $
# Temporary japanese support for ReportLab.
"""
The code in this module will disappear any day now and be replaced
by classes in reportlab.pdfbase.cidfonts
"""


import string, os

from reportlab.test import unittest

from reportlab.pdfbase import pdfmetrics
from reportlab.pdfgen.canvas import Canvas
from reportlab.lib import colors

from reportlab.pdfbase.cidfonts import CIDFont


class JapaneseFontTests(unittest.TestCase):
    def test1(self):
        "A basic document drawing some strings"
        c = Canvas('test_japanese.pdf')
        c.setFont('Helvetica', 30)
        c.drawString(100,700, 'Japanese Font Support')

        pdfmetrics.registerFont(CIDFont('HeiseiMin-W3','90ms-RKSJ-H'))
        pdfmetrics.registerFont(CIDFont('HeiseiKakuGo-W5','90ms-RKSJ-H'))

        # the two typefaces
        c.setFont('HeiseiMin-W3-90ms-RKSJ-H', 16)
        # this says "This is HeiseiMincho" in shift-JIS.  Not all our readers
        # have a Japanese PC, so I escaped it. On a Japanese-capable
        # system, print the string to see Kanji
        message1 = '\202\261\202\352\202\315\225\275\220\254\226\276\222\251\202\305\202\267\201B'
        c.drawString(100, 675, message1)

        c.setFont('HeiseiKakuGo-W5-90ms-RKSJ-H', 16)
        # this says "This is HeiseiKakugo" in shift-JIS
        message2 = '\202\261\202\352\202\315\225\275\220\254\212p\203S\203V\203b\203N\202\305\202\267\201B'
        c.drawString(100, 650, message2) 
        

        #print 'width of message1 = %0.2f' % pdfmetrics.stringWidth(message1, 'HeiseiMin-W3-90ms-RKSJ-H', 16)

        c.setFont('HeiseiMin-W3-90ms-RKSJ-H', 16)
        c.drawString(100, 600, '\223\214\213\236 says Tokyo in Shift-JIS')

        pdfmetrics.registerFont(CIDFont('HeiseiMin-W3','90msp-RKSJ-H'))
        c.setFont('HeiseiMin-W3-90msp-RKSJ-H', 16)
        c.drawString(100, 575, '\223\214\213\236 proportional Shift-JIS')

        pdfmetrics.registerFont(CIDFont('HeiseiMin-W3','EUC-H'))
        c.setFont('HeiseiMin-W3-EUC-H', 16)
        c.drawString(100, 550, '\xC5\xEC\xB5\xFE says Tokyo in EUC')

        pdfmetrics.registerFont(CIDFont('HeiseiMin-W3','UniJIS-UCS2-H'))
        c.setFont('HeiseiMin-W3-UniJIS-UCS2-H', 16)
        def asciiToUCS2(text):
            s = ''
            for ch in text:
                s = s + chr(0) + ch
            return s
        c.drawString(100, 525, '\x67\x71\x4E\xAC' + asciiToUCS2(' says Tokyo in UCS2'))

        # now try verticals
        pdfmetrics.registerFont(CIDFont('HeiseiMin-W3','90ms-RKSJ-V'))
        c.setFont('HeiseiMin-W3-90ms-RKSJ-V', 16)
        c.drawString(400, 650, '\223\214\213\236 vertical Shift-JIS')
        
        pdfmetrics.registerFont(CIDFont('HeiseiMin-W3','EUC-V'))
        c.setFont('HeiseiMin-W3-EUC-V', 16)
        c.drawString(425, 650, '\xC5\xEC\xB5\xFE vertical EUC')

        pdfmetrics.registerFont(CIDFont('HeiseiMin-W3','UniJIS-UCS2-V'))
        c.setFont('HeiseiMin-W3-UniJIS-UCS2-V', 16)
        c.drawString(450, 650, '\x67\x71\x4E\xAC' + asciiToUCS2(' vertical UCS2'))

        c.setFillColor(colors.purple)
        tx = c.beginText(100, 200)
        tx.setFont('Helvetica',12)
        tx.textLines("""Warning - this is preliminary and subject to change.
            To finish it we need to
            - review overall API for adding fonts of all kinds
            - get the text metrics working (which means codec conversion to
            "Adobe CID encoding" and thus probably fixing Python's Asian codecs)
            - recode the codecs and metrics in C for speed
            - make lots of sample code page charts and test
            - repeat for Chinese and Korean, and find people to check them
            """)
        c.drawText(tx)

        c.save()
        

def makeSuite():
    suite = unittest.TestSuite()
    suite.addTest(JapaneseFontTests('test1'))
    return suite

#noruntests
if __name__ == "__main__":
    unittest.TextTestRunner().run(makeSuite())
    print 'saved test_japanese.pdf'    



