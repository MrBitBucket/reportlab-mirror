#copyright ReportLab Inc. 2000
#see license.txt for license details
#history www.reportlab.co.uk/rl-cgi/viewcvs.cgi/rlextra/rlj/jpsupport.py
#$Header: /tmp/reportlab/reportlab/test/Attic/test_chinese_s.py,v 1.3 2001/10/21 17:05:01 andy_robinson Exp $
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


class CHSFontTests(unittest.TestCase):
    
    def hDraw(self, c, msg, fnt, x, y):
        "Helper - draws it with a box around"
        c.setFont(fnt, 16, 16)
        c.drawString(x, y, msg)
        c.rect(x,y,pdfmetrics.stringWidth(msg, fnt, 16),16,stroke=1,fill=0)
        
    def test1(self):
        "A basic document drawing some strings"

        # if they do not have the Japanese font files, go away quietly
        from reportlab.pdfbase.cidfonts import CIDFont, findCMapFile

        
        enc = 'GB-EUC-H'
        try:
            findCMapFile(enc)
        except:
            #they don't have the font pack, return silently
            return
        pdfmetrics.registerFont(CIDFont('STSongStd-Light-Acro',enc))
    
        c = Canvas('test_chinese_simplified.pdf')
        c.setFont('Helvetica', 30)
        c.drawString(100,700, 'Simplified Chinese Font Support')

        c.setStrokeColor(colors.red)

        # the two typefaces
        c.setFont('STSongStd-Light-Acro-' + enc, 16)
        message1 = '\xce\xc4\xbd\xa1\xb5\xc3\xb5\xbd\xc1\xcb \xc4\xc7\xd5\xfd\xba\xc3\xb0\xa2  \xce\xd2 \xba\xdc\xcf\xb2\xbb\xb6.'
        c.drawString(100, 675, message1)
        c.setPageCompression(0)
        c.save()
        if VERBOSE:
            print 'saved test_chinese_simplified.pdf'

def makeSuite():
    return unittest.makeSuite(CHSFontTests,'test')

#noruntests
if __name__ == "__main__":
    VERBOSE = 1
    unittest.TextTestRunner().run(makeSuite())
    



