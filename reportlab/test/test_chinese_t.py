#copyright ReportLab Inc. 2000
#see license.txt for license details
#history www.reportlab.co.uk/rl-cgi/viewcvs.cgi/rlextra/rlj/jpsupport.py
#$Header: /tmp/reportlab/reportlab/test/Attic/test_chinese_t.py,v 1.1 2001/10/20 20:42:14 andy_robinson Exp $
# Temporary japanese support for ReportLab.
"""
Test of traditional Chinese (as written in Taiwan)
"""


import string, os

from reportlab.test import unittest

from reportlab.pdfbase import pdfmetrics
from reportlab.pdfgen.canvas import Canvas
from reportlab.lib import colors

global VERBOSE
VERBOSE = 0


class CHTFontTests(unittest.TestCase):
    def hDraw(self, c, msg, fnt, x, y):
        "Helper - draws it with a box around"
        c.setFont(fnt, 16, 16)
        c.drawString(x, y, msg)
        c.rect(x,y,pdfmetrics.stringWidth(msg, fnt, 16),16,stroke=1,fill=0)
        
    def test1(self):
        "A basic document drawing some strings"

        # if they do not have the Japanese font files, go away quietly
        from reportlab.pdfbase.cidfonts import CIDFont, findCMapFile

        
        enc = 'ETen-B5-H'
        try:
            findCMapFile(enc)
        except:
            #they don't have the font pack, return silently
            return
        pdfmetrics.registerFont(CIDFont('MSungStd-Light-Acro',enc))
    
        c = Canvas('test_chinese_traditional.pdf')
        c.setFont('Helvetica', 30)
        c.drawString(100,700, 'Traditional Chinese Font Support')
        c.setFont('Helvetica', 10)
        c.drawString(100,680, 'News headline from Yahoo Hong Kong, 20 Oct 2001.  Big5 Encoding')
        
        c.setStrokeColor(colors.red)

        c.setFont('MSungStd-Light-Acro-' + enc, 14)
        # this came from Yahoo Hong Kong leading story today
        message1 = '\xa5\xac\xae\xed\xbbP\xa6\xbf\xbfA\xa5\xc1\xa6b\xad\xba\xa6\xb8\xb7|\xad\xb1\xab\xe1\xa4@\xa6P\xa8\xa3\xb0O\xaa\xcc\xa1A\xa5L\xbb\xa1\xa1A\xa8\xe2\xa4H\xaa\xba\xad\xba\xa6\xb8\xb7|\xad\xb1\xabD\xb1`'
        message2 = '\xa6n\xa1A\xa8\xc3\xaa\xed\xa5\xdc\xb2@\xb5L\xba\xc3\xb0\xdd\xa4\xa4\xb0\xea\xa6b\xb3o\xad\xd3\xa5i\xa9\xc6\xaa\xba\xae\xc9\xa8\xe8\xa1A\xb7|\xbbP\xac\xfc\xb0\xea\xa4H\xa5\xc1\xaf\xb8\xa6b\xa4@\xb0_\xa1C'
        c.drawString(100, 655, message1)
        c.drawString(100, 639, message2)
        c.setPageCompression(0)
        c.save()
        if VERBOSE:
            print 'saved test_chinese_traditional.pdf'

def makeSuite():
    return unittest.makeSuite(CHTFontTests,'test')

#noruntests
if __name__ == "__main__":
    VERBOSE = 1
    unittest.TextTestRunner().run(makeSuite())
    



