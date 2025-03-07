#!/bin/env python
# coding=utf8
#Copyright ReportLab Europe Ltd. 2025
#see license.txt for license details
__version__='3.3.0'
__doc__="""Exercising basic Canvas operations and libraries involved in Arabic/Hebrew


This is really to build up oour own understanding at the moment.
"""
from reportlab.lib.testutils import (setOutDir,makeSuiteForClasses, outputfile,
                                    printLocation, rlSkipUnless, haveDejaVu)
setOutDir(__name__)
import unittest
from reportlab.pdfgen.canvas import Canvas
from reportlab.pdfgen.textobject import rtlSupport, log2vis, bidiWordList, BidiIndexStr
from reportlab.platypus.paraparser import _greekConvert
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont, uharfbuzz, freshTTFont
from reportlab.platypus.paragraph import Paragraph
from reportlab.lib.styles import getSampleStyleSheet, TA_RIGHT

class RtlTestCase(unittest.TestCase):
    "Simplest test that makes PDF"

    @rlSkipUnless(rtlSupport and haveDejaVu() and uharfbuzz,'miss RTL and/or DejaVu/uharfbuzz')
    def test_arabic(self):
        c = Canvas(outputfile('test_arabic.pdf'))

        pdfmetrics.registerFont(TTFont("DejaVuSans", "DejaVuSans.ttf"))

        c.setFont('Helvetica-Bold', 18)
        c.drawString(100,800, 'Tests relating to RTL, Hebrew and Arabic')
        c.setFont('Helvetica', 12)


        if rtlSupport:  # essential for these tests
            import rlbidi
            msg = f"Using rlbidi version {rlbidi.__version__}"
            c.drawString(100,750, msg)

        else:
            msg = "rlbidi not imported, exiting"
            c.drawString(100, 750, msg)
            c.save()
            return

        if uharfbuzz:
            msg = f"Using uharfbuzz version {uharfbuzz.__version__}"
        else:
            msg = "uharfbuzz not imported, this may not matter"
        c.drawString(100, 730, msg)


        phrase = "أنت مجنون"
        unichars = [hex(ord(ch)) for ch in phrase]
        c.drawString(100, 715, "Our test phrase is taken from the Rowan Atkinson Barclaycard advert in 2011.")
        c.drawString(100, 700, "https://www.youtube.com/watch?v=WEDCGCwY8zg")

        c.drawString(100, 685, '          "\'ant majnun", meaning "you\'re crazy"')
        c.drawString(100, 670, "The characters in this in Helvetica are not defined:" + str(repr(list(phrase))))

        c.setFont("DejaVuSans", 12)
        c.drawString(100, 655, "The characters in this in DejaVuSans are" + str(repr(list(phrase))))
        c.drawString(100, 640, "That's 3 characters, a space and 5 characters in the input.")

        c.drawString(100, 625, "Byte values (unicode) = " + repr(unichars))

        c.drawString(100, 610, "Raw left to right display (VERY wrong)" + phrase)

        logicalchars = log2vis(phrase)
        c.drawString(100, 595, "Output of log2vis = " + logicalchars)
        unichars = [hex(ord(ch)) for ch in logicalchars]
        c.drawString(100, 580, "Char values in log2vis = " + repr(unichars))

        c.drawString(100, 565, "This appears correct (although DejaVu is less pretty than Arial)")

        width_raw = pdfmetrics.stringWidth(phrase, "DejaVuSans", 12)
        width_log = pdfmetrics.stringWidth(logicalchars, "DejaVuSans", 12)

        c.drawString(100, 550, f"Raw string width = {width_raw}, Modified string width = {width_log}")
        c.drawString(100, 535, f"We will always overestimate the width, ")
        c.drawString(100, 520, f"so will mess it up when centered or right-aligned")
        c.save()

    text0 = '\u0627\u0644\u0631\u064a\u0627\u0636 \u0647\u0648 \u0641\u0631\u064a\u0642 \u0643\u0631\u0629 \u0642\u062f\u0645 \u0639\u0631\u0628\u064a \u064a\u0636\u0645 123 \u0644\u0627\u0639\u0628\u064b\u0627 \u0628\u0627\u0647\u0638 \u0627\u0644\u062b\u0645\u0646'
    @rlSkipUnless(rtlSupport and haveDejaVu(),'miss RTL and/or DejaVu')
    def test_bidiWordList(self):
        c = Canvas(outputfile('test_arabic_bidiWordList.pdf'))
        pdfmetrics.registerFont(freshTTFont("DejaVuSans", "DejaVuSans.ttf"))
        sss = getSampleStyleSheet()
        W,H = c._pagesize
        leading = 14.4
        styN = sss.Normal.clone('Normal',fontName='DejaVuSans',bulletFontName='DejaVuSans',
                          fontSize=12,leading=leading,allowOrphans=True)
        styNRTL = styN.clone('NormalRTL',wordWrap='RTL', alignment=TA_RIGHT)#, backColor=(0,0.2,0))
        c.setFont('DejaVuSans',12,leading=leading)
        x = 36
        y = H - 36
        c.drawString(x,y,'Al Riyadh is an Arab football team with 123 expensive players')
        y -= 2*14.4
        P = Paragraph(self.text0,style=styNRTL)
        def drawP(p,aW,aH,sC):
            w, h = p.wrap(aW,aH)
            c.saveState()
            c.setStrokeColor(sC)
            c.rect(x,y-0.2*styNRTL.fontSize,aW,h)
            c.restoreState()
            p.drawOn(c, x=x, y=y)
        drawP(P,W-72,H-72,(1,0,0))
        y -= 4*leading
        P = Paragraph(self.text0,style=styNRTL)
        rW = W/3
        x = W - 36 - rW
        drawP(P, rW, H-72,(1,0,0))

        y -= leading
        c.drawString(x,y,'Splitting the arabic')
        y -= leading
        P = Paragraph(self.text0,style=styNRTL)
        P1, P2 = P.split(rW, leading+1)
        drawP(P1,rW,leading+.1,(0,0.8,0))
        y -= leading
        drawP(P2,rW,leading+.1,(0,0,0.8))
        c.showPage()
        c.save()

    @rlSkipUnless(rtlSupport,'miss RTL support')
    def test_bidiIndexWrap(self):
        from reportlab.platypus.paragraph import _SHYStr, _SplitWordH, _SplitWordEnd
        from reportlab.pdfgen.textobject import BidiIndexStr, bidiIndexWrap, _bidiKS

        for i,klass in enumerate((_SHYStr, _SplitWordH, _SplitWordEnd)):
            s = 'abc\xaddef' if klass==_SHYStr else 'ABCDEF'
            orig = BidiIndexStr('dontcare',bidiIndex=79+i)
            ks = klass(s)
            instw = bidiIndexWrap(ks,orig)
            self.assertTrue(hasattr(instw,'__bidiIndex__'))
            self.assertTrue(instw.__bidiIndex__==orig.__bidiIndex__)
            self.assertTrue(instw==ks)
            self.assertTrue(bidiIndexWrap(instw,orig) is instw)
            if hasattr(ks,'__dict__'):
                for k in ks.__dict__:
                    self.assertEqual(getattr(ks,k),getattr(instw,k),
                                    f'ks.{k}={getattr(ks,k)} not equal to instw.{k}={getattr(instw,k)}') 

    words0 = '\u0627\u0644\u0631\u064a\u0627\u0636 \u0647\u0648 \u0641\u0631\u064a\u0642 \u0643\u0631\u0629 \u0642\u062f\u0645 \u0639\u0631\u0628\u064a \u064a\u0636\u0645 123 \u0644\u0627\u0639\u0628\u064b\u0627 \u0628\u0627\u0647\u0638 \u0627\u0644\u062b\u0645\u0646'.split()
    words0 = 'الرياض هو فريق كرة قدم عربي يضم 123 لاعبًا باهظ الثمن'.split()

    @rlSkipUnless(rtlSupport,'miss RTL support')
    def test_making_words(self):
        bwl = bidiWordList(self.words0)
        self.assertEqual(bwl,['\ufebd\ufe8e\ufef3\ufeae\ufedf\ufe8d', '\ufeee\ufeeb', '\ufed6\ufef3\ufeae\ufed3', '\ufe93\ufeae\ufedb', '\ufee1\ufeaa\ufed7', '\ufef2\ufe91\ufeae\ufecb', '\ufee2\ufec0\ufef3', '123', '\ufe8e\ufe92\u064b\ufecb\ufefb', '\ufec6\ufeeb\ufe8e\ufe91', '\ufee6\ufee4\ufe9c\ufedf\ufe8d'])
        rt = set([_.__class__.__name__ for _ in bwl])
        xt = set(['BidiIndexStr'])
        self.assertEqual(rt, xt, f"bidiWordList returned wrong types {rt} not expected {xt}")
        xx = [10, 9, 8, 7, 6, 5, 4, 3, 2, 1, 0]
        rx = [getattr(_,'__bidiIndex__','?') for _ in bwl]
        self.assertEqual(xx, rx, f"bidiWordList returned wrong indeces {rx} not expected {xx}")

def makeSuite():
    return makeSuiteForClasses(RtlTestCase)

#noruntests
if __name__ == "__main__":
    unittest.TextTestRunner().run(makeSuite())
    printLocation()
