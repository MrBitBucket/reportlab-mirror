#copyright ReportLab Inc. 2000
#see license.txt for license details
#history www.reportlab.co.uk/rl-cgi/viewcvs.cgi/rlextra/rlj/jpsupport.py
#$Header: /tmp/reportlab/reportlab/test/Attic/test_japanese.py,v 1.4 2001/09/19 22:38:13 andy_robinson Exp $
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

global VERBOSE
VERBOSE = 0



class JapaneseFontTests(unittest.TestCase):
    def hDraw(self, c, msg, fnt, x, y):
        "Helper - draws it with a box around"
        c.setFont(fnt, 16)
        c.drawString(x, y, msg)
        c.rect(x,y,pdfmetrics.stringWidth(msg, fnt, 16),16,stroke=1,fill=0)
        
    def test1(self):
        "A basic document drawing some strings"

        # if they do not have the Japanese font files, go away quietly
        try:
            from reportlab.pdfbase.cidfonts import CIDFont, findCMapFile
            findCMapFile('90ms-RKSJ-H')
            findCMapFile('90msp-RKSJ-H')
            findCMapFile('UCS2-H')
            findCMapFile('EUC-H')
        except:
            #don't have the font pack.  return silently
            return

        pdfmetrics.registerFont(CIDFont('HeiseiMin-W3','90ms-RKSJ-H'))
        pdfmetrics.registerFont(CIDFont('HeiseiKakuGo-W5','90ms-RKSJ-H'))
    
        c = Canvas('test_japanese.pdf')
        c.setFont('Helvetica', 30)
        c.drawString(100,700, 'Japanese Font Support')

        c.setStrokeColor(colors.red)

        # the two typefaces
        c.setFont('HeiseiMin-W3-90ms-RKSJ-H', 16)
        # this says "This is HeiseiMincho" in shift-JIS.  Not all our readers
        # have a Japanese PC, so I escaped it. On a Japanese-capable
        # system, print the string to see Kanji
        message1 = '\202\261\202\352\202\315\225\275\220\254\226\276\222\251\202\305\202\267\201B'
        c.drawString(100, 675, message1)
        wid = pdfmetrics.stringWidth(message1, 'HeiseiMin-W3-90ms-RKSJ-H', 16)
        c.rect(100,675,wid,16,stroke=1,fill=0)

        c.setFont('HeiseiKakuGo-W5-90ms-RKSJ-H', 16)
        # this says "This is HeiseiKakugo" in shift-JIS
        message2 = '\202\261\202\352\202\315\225\275\220\254\212p\203S\203V\203b\203N\202\305\202\267\201B'
        c.drawString(100, 650, message2) 
        wid = pdfmetrics.stringWidth(message1, 'HeiseiKakuGo-W5-90ms-RKSJ-H', 16)
        c.rect(100,650,wid,16,stroke=1,fill=0)

        

        self.hDraw(c, '\223\214\213\236 says Tokyo in Shift-JIS', 'HeiseiMin-W3-90ms-RKSJ-H', 100, 600)


        pdfmetrics.registerFont(CIDFont('HeiseiMin-W3','90msp-RKSJ-H'))
        self.hDraw(c, '\223\214\213\236 proportional Shift-JIS', 'HeiseiMin-W3-90msp-RKSJ-H', 100, 575)
        
        pdfmetrics.registerFont(CIDFont('HeiseiMin-W3','EUC-H'))
        self.hDraw(c, '\xC5\xEC\xB5\xFE says Tokyo in EUC', 'HeiseiMin-W3-EUC-H', 100, 550)

        pdfmetrics.registerFont(CIDFont('HeiseiMin-W3','UniJIS-UCS2-H'))
        def asciiToUCS2(text):
            s = ''
            for ch in text:
                s = s + chr(0) + ch
            return s
        self.hDraw(c, '\x67\x71\x4E\xAC' + asciiToUCS2(' says Tokyo in UCS2'),
                   'HeiseiMin-W3-UniJIS-UCS2-H', 100, 525)
                    

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
        if VERBOSE:
            print 'saved test_japanese.pdf'
        

def makeSuite():
    suite = unittest.TestSuite()
    suite.addTest(JapaneseFontTests('test1'))
    return suite

#noruntests
if __name__ == "__main__":
    VERBOSE = 1
    unittest.TextTestRunner().run(makeSuite())
    



