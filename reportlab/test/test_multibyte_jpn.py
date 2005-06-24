#Copyright ReportLab Europe Ltd. 2000-2004
#see license.txt for license details
#history www.reportlab.co.uk/rl-cgi/viewcvs.cgi/rlextra/rlj/jpsupport.py
# Temporary japanese support for ReportLab.
"""
The code in this module will disappear any day now and be replaced
by classes in reportlab.pdfbase.cidfonts
"""


import string, os

from reportlab.test import unittest
from reportlab.test.utils import makeSuiteForClasses, outputfile, printLocation

from reportlab.pdfbase import pdfmetrics
from reportlab.pdfgen.canvas import Canvas
from reportlab.lib import colors
from reportlab.lib.codecharts import KutenRowCodeChart
global VERBOSE
VERBOSE = 0


class JapaneseFontTests(unittest.TestCase):

    def hDraw(self, c, msg, fnt, x, y):
        "Helper - draws it with a box around"
        c.setFont(fnt, 16, 16)
        c.drawString(x, y, msg)
        c.rect(x,y,pdfmetrics.stringWidth(msg, fnt, 16),16,stroke=1,fill=0)

    def test0(self):
        "A basic document drawing some strings"

        # if they do not have the Japanese font files, go away quietly
        try:
            from reportlab.pdfbase.cidfonts import CIDFont, findCMapFile
            findCMapFile('90ms-RKSJ-H')
            findCMapFile('90msp-RKSJ-H')
            findCMapFile('UniJIS-UCS2-H')
            findCMapFile('EUC-H')
        except:
            #don't have the font pack.  return silently
            return

        pdfmetrics.registerFont(CIDFont('HeiseiMin-W3','90ms-RKSJ-H'))
        pdfmetrics.registerFont(CIDFont('HeiseiKakuGo-W5','90ms-RKSJ-H'))

        c = Canvas(outputfile('test_multibyte_jpn.pdf'))
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
        wid = pdfmetrics.stringWidth(message2, 'HeiseiKakuGo-W5-90ms-RKSJ-H', 16)
        c.rect(100,650,wid,16,stroke=1,fill=0)



        self.hDraw(c, '\223\214\213\236 says Tokyo in Shift-JIS', 'HeiseiMin-W3-90ms-RKSJ-H', 100, 600)


        pdfmetrics.registerFont(CIDFont('HeiseiMin-W3','90msp-RKSJ-H'))
        self.hDraw(c, '\223\214\213\236, but in proportional Shift-JIS.', 'HeiseiMin-W3-90msp-RKSJ-H', 100, 575)

        pdfmetrics.registerFont(CIDFont('HeiseiMin-W3','EUC-H'))
        self.hDraw(c, '\xC5\xEC\xB5\xFE says Tokyo in EUC', 'HeiseiMin-W3-EUC-H', 100, 550)

        if 0:
            #this is super-slow until we do encoding caching.
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
        height = c.stringWidth('\223\214\213\236 vertical Shift-JIS', 'HeiseiMin-W3-90ms-RKSJ-V', 16)
        c.rect(400-8,650,16,-height)

        pdfmetrics.registerFont(CIDFont('HeiseiMin-W3','EUC-V'))
        c.setFont('HeiseiMin-W3-EUC-V', 16)
        c.drawString(425, 650, '\xC5\xEC\xB5\xFE vertical EUC')
        height = c.stringWidth('\xC5\xEC\xB5\xFE vertical EUC', 'HeiseiMin-W3-EUC-V', 16)
        c.rect(425-8,650,16,-height)

        c.setFillColor(colors.purple)
        tx = c.beginText(100, 250)
        tx.setFont('Helvetica', 12)
        tx.textLines("""This document shows sample output in Japanese
        from the Reportlab PDF library.  This page shows the two fonts
        available and tests our ability to measure the width of glyphs
        in both horizontal and vertical writing, with proportional and
        fixed-width characters. The red boxes should be the same width
        (or height) as the character strings they surround.
        The next pages show more samples and information.
        """)
        c.drawText(tx)
        c.setFont('Helvetica',10)
        c.drawCentredString(297, 36, 'Page %d' % c.getPageNumber())
        c.showPage()

        # realistic text sample
        sample = """Adobe Acrobat
\x83h\x83L\x83\x85\x83\x81\x83\x93\x83g\x82\xaa\x8aJ\x82\xa9\x82\xc8\x82\xad\x82\xc4\x8d\xa2\x82\xc1\x82\xbd\x82\xb1\x82\xc6\x82\xcd
\x82\xa0\x82\xe8\x82\xdc\x82\xb9\x82\xf1\x82\xa9\x81B\x8e\x96\x8b\xc6\x8cv\x89\xe6\x8f\x91\x81A\x89c\x8b\xc6\x83\x8c\x83|\x81[\x83g
\x81A\x83J\x83^\x83\x8d\x83O\x82\xe2\x83p\x83\x93\x83t\x83\x8c\x83b\x83g\x82\xc8\x82\xc7\x90\xa7\x8d\xec\x95\xa8\x82\xcc\x8e\xed
\x97\xde\x82\xc9\x82\xa9\x82\xa9\x82\xed\x82\xe7\x82\xb8\x81A
\x83h\x83L\x83\x85\x83\x81\x83\x93\x83g\x82\xcdAdobe&reg; Acrobat&reg; 5.0\x82\xf0\x8eg\x82\xc1\x82\xc4Adobe PDF\x81iPortable Document
Format\x81j\x83t\x83@\x83C\x83\x8b\x82\xc9\x95\xcf\x8a\xb7\x82\xb5\x82\xdc\x82\xb5\x82\xe5\x82\xa4\x81B\x96\xb3\x8f\x9e\x94z\x95z\x82\xcc
Adobe Acrobat Reader\x82\xf0\x8eg\x82\xa6\x82\xce\x81A\x83n\x81[\x83h\x83E\x83F\x83A\x81A\x83\\\x83t\x83g\x83E\x83F\x83A\x82\xc9\x82\xa9
\x82\xa9\x82\xed\x82\xe7\x82\xb8\x81A\x92N\x82\xc5\x82\xe0\x82\xa0\x82\xc8\x82\xbd\x82\xcc\x83h\x83L\x83\x85\x83\x81\x83\x93\x83g\x82\xf0
\x83I\x83\x8a\x83W\x83i\x83\x8b\x82\xcc\x91\xcc\x8d\xd9\x82\xc5\x8aJ\x82\xad\x82\xb1\x82\xc6\x82\xaa\x82\xc5\x82\xab\x82\xdc\x82\xb7\x81B
\x82\xa0\x82\xc8\x82\xbd\x82\xcc\x88\xd3\x90}\x82\xb5\x82\xbd\x82\xc6\x82\xa8\x82\xe8\x82\xc9\x8f\xee\x95\xf1\x82\xf0\x93`\x82\xa6\x82\xe9
\x82\xb1\x82\xc6\x82\xaa\x82\xc5\x82\xab\x82\xdc\x82\xb7\x81B
\x82\xb3\x82\xe7\x82\xc9\x81AAdobe Acrobat 5.0\x82\xc5\x82\xcd\x81AWeb\x83u\x83\x89\x83E\x83U\x82\xa9\x82\xe7\x83R\x83\x81\x83\x93\x83g\x82\xe2
\x83}\x81[\x83N\x83A\x83b\x83v\x82\xf0\x8f\x91\x82\xab\x8d\x9e\x82\xf1\x82\xbe\x82\xe8\x81A\x93d\x8eq\x8f\x90\x96\xbc\x82\xf0\x8f\x91\x82\xab
\x8d\x9e\x82\xdd\x81A\x8c\xb4\x96{\x82\xc6\x82\xb5\x82\xc4\x83\x8d\x81[\x83J\x83\x8b\x82\xc9\x95\xdb\x91\xb6\x82\xb7\x82\xe9\x82\xb1\x82\xc6\x82\xe0\x89\xc2\x94\\\x82\xc5\x82\xb7\x81B
\x8a\xe9\x8b\xc6\x93\xe0\x82\xa0\x82\xe9\x82\xa2\x82\xcd\x8a\xe9\x8b\xc6\x82\xcc\x98g\x82\xf0\x92\xb4\x82\xa6\x82\xc4\x83`\x81[\x83\x80\x82\xc5
\x82\xcc\x83h\x83L\x83\x85\x83\x81\x83\x93\x83g\x83\x8f\x81[\x83N\x82\xcc\x90\xb6\x8eY\x90\xab\x82\xf0\x8c\xfc\x8f\xe3\x82\xb3\x82\xb9\x82\xe9\x82\xb1\x82\xc6\x82\xaa\x82\xc5\x82\xab\x82\xdc\x82\xb7\x81B

Adobe Acrobat 5.0\x82\xc5\x8d\xec\x90\xac\x82\xb5\x82\xbdAdobe PDF\x82\xcd\x81A(Acrobat 5.0\x82\xc5\x82\xcc\x82\xdd\x83T\x83|\x81[\x83g
\x82\xb5\x82\xc4\x82\xa2\x82\xe9\x88\xc3\x8d\x86\x89\xbb\x90\xdd\x92\xe8\x82\xf0\x8f\x9c\x82\xa2\x82\xc4\x82\xcd)\x8f]\x97\x88\x82\xdc
\x82\xc5\x82\xcc\x83o\x81[\x83W\x83\x87\x83\x93(3\x82\xa8\x82\xe6\x82\xd1\x82S)\x82\xccAcrobat Reader\x82\xc5\x82\xe0\x8aJ\x82\xad
\x82\xb1\x82\xc6\x82\xaa\x82\xc5\x82\xab\x82\xdc\x82\xb7\x81B\x8f\xee\x95\xf1\x8b\xa4\x97L\x82\xcc\x83c\x81[\x83\x8b\x82\xc6\x82\xb5
\x82\xc4\x81A\x82\xb3\x82\xe7\x82\xc9\x90i\x95\xe0\x82\xb5\x82\xbdAdobe Acrobat 5.0\x82\xf0\x81A\x8f]\x97\x88\x82\xcc\x8a\xc2\x8b\xab
\x82\xc5\x82\xe0\x88\xc0\x90S\x82\xb5\x82\xc4\x82\xb2\x97\x98\x97p\x82\xa2\x82\xbd\x82\xbe\x82\xaf\x82\xdc\x82\xb7\x81B

\x96{\x90\xbb\x95i\x82\xf0\x83l\x83b\x83g\x83\x8f\x81[\x83N\x82\xc8\x82\xc7\x82\xf0\x89\xee\x82\xb5\x82\xc4\x92\xbc\x90\xda\x82\xa0\x82\xe9
\x82\xa2\x82\xcd\x8a\xd4\x90\xda\x82\xc9\x95\xa1\x90\x94\x82\xcc\x92[\x96\x96\x82\xa9\x82\xe7\x8eg\x97p\x82\xb7\x82\xe9\x8f\xea\x8d\x87\x81A
\x82\xbb\x82\xcc\x92[\x96\x96\x82\xc6\x93\xaf\x90\x94\x82\xcc\x83\x89\x83C\x83Z\x83\x93\x83X\x82\xf0\x82\xb2\x8dw\x93\xfc\x82\xad\x82\xbe
\x82\xb3\x82\xa2\x81B\x96{\x90\xbb\x95i\x82\xcd\x83N\x83\x89\x83C\x83A\x83\x93\x83g\x97p\x83\\\x83t\x83g\x83E\x83F\x83A\x82\xc5\x82\xa0\x82\xe8
\x81A\x83T\x81[\x83o\x97p\x83\\\x83t\x83g\x83E\x83F\x83A\x82\xc6\x82\xb5\x82\xc4\x82\xa8\x8eg\x82\xa2\x82\xa2\x82\xbd\x82\xbe\x82\xad\x82\xb1\x82\xc6
\x82\xcd\x81A\x8f\xe3\x8bL\x95\xfb\x96@\x82\xc9\x82\xe6\x82\xe9\x88\xc8\x8aO\x81A\x8b\x96\x91\xf8\x82\xb3\x82\xea\x82\xc4\x82\xa2\x82\xdc\x82\xb9
\x82\xf1\x81B\x95\xa1\x90\x94\x82\xcc\x83\x89\x83C\x83Z\x83\x93\x83X\x82\xf0\x82\xb2\x8dw\x93\xfc\x82\xb3\x82\xea\x82\xe9\x8f\xea\x8d\x87\x82\xc9
\x82\xcd\x83\x89\x83C\x83Z\x83\x93\x83X\x83v\x83\x8d\x83O\x83\x89\x83\x80\x82\xf0\x82\xb2\x97\x98\x97p\x82\xc9\x82\xc8\x82\xe9\x82\xc6\x82\xa8\x93\xbe\x82\xc5\x82\xb7\x81B


\x81y\x82\xa8\x92m\x82\xe7\x82\xb9\x81zMicrosoft Office XP\x82\xa9\x82\xe7PDF\x82\xf0\x8d\xec\x90\xac\x82\xb7\x82\xe9\x82\xc9\x82\xcd
"""
        c.setFont('Helvetica', 24)
        c.drawString(100,750, "Sample text from Adobe's web site")
        tx = c.beginText(100,700)
        tx.setFont('Helvetica', 10)
        tx.textLine('Note: line wrapping has not been preserved and some lines may be wrapped in mid-word.')
        tx.textLine('We are just testing that we see Japanese and not random characters!')
        tx.setFont('HeiseiMin-W3-90ms-RKSJ-H',6)
        tx.textLines(sample)
        tx.setFont('Helvetica', 8)
        tx.textLine()
        tx.textLine()
        tx.textLines("""
            This test document shows Japanese output from the Reportlab PDF Library.
            You may use two fonts, HeiseiMin-W3 and HeiseiKakuGo-W5, and a number of
            different encodings.

            The available encoding names (with comments from the PDF specification) are:
            encodings_jpn = [
                # official encoding names, comments taken verbatim from PDF Spec
                '83pv-RKSJ-H',      #Macintosh, JIS X 0208 character set with KanjiTalk6
                                    #extensions, Shift-JIS encoding, Script Manager code 1
                '90ms-RKSJ-H',      #Microsoft Code Page 932 (lfCharSet 0x80), JIS X 0208
                                    #character set with NEC and IBM extensions
                '90ms-RKSJ-V',      #Vertical version of 90ms-RKSJ-H
                '90msp-RKSJ-H',     #Same as 90ms-RKSJ-H, but replaces half-width Latin
                                    #characters with proportional forms
                '90msp-RKSJ-V',     #Vertical version of 90msp-RKSJ-H
                '90pv-RKSJ-H',      #Macintosh, JIS X 0208 character set with KanjiTalk7
                                    #extensions, Shift-JIS encoding, Script Manager code 1
                'Add-RKSJ-H',       #JIS X 0208 character set with Fujitsu FMR extensions,
                                    #Shift-JIS encoding
                'Add-RKSJ-V',       #Vertical version of Add-RKSJ-H
                'EUC-H',            #JIS X 0208 character set, EUC-JP encoding
                'EUC-V',            #Vertical version of EUC-H
                'Ext-RKSJ-H',       #JIS C 6226 (JIS78) character set with NEC extensions,
                                    #Shift-JIS encoding
                'Ext-RKSJ-V',       #Vertical version of Ext-RKSJ-H
                'H',                #JIS X 0208 character set, ISO-2022-JP encoding,
                'V',                #Vertical version of H
                'UniJIS-UCS2-H',    #Unicode (UCS-2) encoding for the Adobe-Japan1 character
                                    #collection
                'UniJIS-UCS2-V',    #Vertical version of UniJIS-UCS2-H
                'UniJIS-UCS2-HW-H', #Same as UniJIS-UCS2-H, but replaces proportional Latin
                                    #characters with half-width forms
                'UniJIS-UCS2-HW-V'  #Vertical version of UniJIS-UCS2-HW-H
                ]

            The next few pages show the complete character set available in the encoding
            "90ms-RKSJ-H" - Shift-JIS with the standard Microsoft extensions.
            """)
        c.drawText(tx)

        c.setFont('Helvetica',10)
        c.drawCentredString(297, 36, 'Page %d' % c.getPageNumber())

        c.showPage()
        # full kuten chart in EUC
        c.setFont('Helvetica', 24)
        c.drawString(72,750, 'Characters available in JIS 0208-1997')
        y = 600
        for row in range(1, 95):
            KutenRowCodeChart(row, 'HeiseiMin-W3','EUC-H').drawOn(c, 72, y)
            y = y - 125
            if y < 50:
                c.setFont('Helvetica',10)
                c.drawCentredString(297, 36, 'Page %d' % c.getPageNumber())
                c.showPage()
                y = 700

        c.save()


        if VERBOSE:
            print 'saved test_multibyte_jpn.pdf'


    def ___test2_all(self):
        """Dumps out ALl GLYPHS in a CID font.

        Reach for your microscope :-)"""
        try:
            from reportlab.pdfbase.cidfonts import CIDFont, findCMapFile
            findCMapFile('90ms-RKSJ-H')
            findCMapFile('Identity-H')
        except:
            #don't have the font pack.  return silently
            return

        pdfmetrics.registerFont(CIDFont('HeiseiMin-W3','Identity-H'))

        c = Canvas('test_japanese_2.pdf')
        c.setFont('Helvetica', 30)
        c.drawString(100,800, 'All Glyphs in Adobe-Japan-1-2 collection!')

        # the two typefaces
        c.setFont('HeiseiMin-W3-Identity-H', 2)

        x0 = 50
        y0 = 700
        dx = 2
        dy = 2
        for row in range(256):
            for cell in range(256):
                s = chr(row) + chr(cell)
                x = x0 + cell*dx
                y = y0 - row*dy
                c.drawString(x,y,s)

        c.save()
        if VERBOSE:
            print 'saved '+outputfile('test_multibyte_jpn.pdf')


def makeSuite():
    return makeSuiteForClasses(JapaneseFontTests)


#noruntests
if __name__ == "__main__":
    VERBOSE = 1
    unittest.TextTestRunner().run(makeSuite())
    printLocation()
