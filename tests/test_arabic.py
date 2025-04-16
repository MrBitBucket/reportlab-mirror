#!/bin/env python
# coding=utf8
#Copyright ReportLab Europe Ltd. 2025
#see license.txt for license details
__version__='3.3.0'
__doc__="""Exercising basic Canvas operations and libraries involved in Arabic/Hebrew


This is really to build up oour own understanding at the moment.
"""
from reportlab.lib.testutils import (setOutDir,makeSuiteForClasses, outputfile,
                                    printLocation, rlSkipUnless, haveDejaVu, )
setOutDir(__name__)
import unittest
from reportlab.pdfgen.canvas import Canvas
from reportlab.pdfgen.textobject import rtlSupport, log2vis, bidiWordList, BidiStr, bidiShapedText, bidiText
from reportlab.platypus.paraparser import _greekConvert
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont, uharfbuzz, freshTTFont, ShapedStr, shapeFragWord, shapeStr
from reportlab.platypus.paragraph import Paragraph
from reportlab.lib.styles import getSampleStyleSheet, TA_RIGHT
from reportlab.lib.abag import ABag

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

    @rlSkipUnless(rtlSupport and haveDejaVu(),'miss RTL and/or DejaVu')
    def test_bidiWordList(self):
        c = Canvas(outputfile('test_arabic_bidiWordList.pdf'))
        fontName = 'DejaVuSans'
        fontSize = 12
        leading = 14.4
        pdfmetrics.registerFont(freshTTFont("DejaVuSans", "DejaVuSans.ttf"))
        sss = getSampleStyleSheet()
        W,H = c._pagesize
        styN = sss.Normal.clone('Normal',fontName='DejaVuSans',bulletFontName='DejaVuSans',
                          fontSize=12,leading=leading,allowOrphans=True)
        styNRTL = styN.clone('NormalRTL',wordWrap='RTL', alignment=TA_RIGHT)#, backColor=(0,0.2,0))
        c.setFont(fontName, fontSize, leading=leading)
        class ExampleP:
            def __init__(self, x, y, p, aW, aH, sC):
                self.w, self.h = p.wrap(aW,aH)
                self.params = x, y, p, aW, aH, sC
            def draw(self):
                x, y, p, aW, aH, sC = self.params
                y -= self.h
                c.saveState()
                c.setStrokeColor(sC)
                c.rect(x,y-0.2*styNRTL.fontSize,aW,self.h)
                c.restoreState()
                p.drawOn(c, x=x, y=y)

        def example(eng, arabic, dw=0):
            fW = W - 72 #ie width - 2*36
            x = 36
            y = H - 36
            w = pdfmetrics.stringWidth(eng,fontName,fontSize)
            if w>fW:
                c.saveState()
                c.setFontSize(fontSize*fW/w)
                c.drawString(x,y,eng)
                c.restoreState()
            else:
                c.drawString(x,y,eng)
            p = ExampleP(x, y, Paragraph(arabic,style=styNRTL), fW,H-72,(1,0,0))
            p.draw()

            rW = W/3
            x = W - 36 - rW
            y -= p.h + leading
            p = ExampleP(x, y, Paragraph(arabic,style=styNRTL), rW, H-72,(1,0,0))
            p.draw()
            y -= p.h+2*leading
            c.drawString(x,y,'Splitting the arabic')
            P = Paragraph(arabic,style=styNRTL)
            P1, P2 = P.split(rW, leading+1)
            p = ExampleP(x, y, P1,rW,leading+.1,(0,0.8,0))
            p.draw()
            y -= leading
            p = ExampleP(x+dw, y, P2,rW-dw,leading+.1,(0,0,0.8))
            p.draw()
            c.showPage()
        example('Al Riyadh is an Arab football team with 123 expensive players',
                '\u0627\u0644\u0631\u064a\u0627\u0636 \u0647\u0648 \u0641\u0631'
                '\u064a\u0642 \u0643\u0631\u0629 \u0642\u062f\u0645 \u0639\u0631'
                '\u0628\u064a \u064a\u0636\u0645 123 \u0644\u0627\u0639\u0628\u064b'
                '\u0627 \u0628\u0627\u0647\u0638 \u0627\u0644\u062b\u0645\u0646',
                )

        example('Al Riyadh is an Arab football team with 123 expensive players including a'
                ' Golden Boot winner and other foreign internationals.',
                '\u0627\u0644\u0631\u064a\u0627\u0636 \u0647\u0648 \u0641\u0631\u064a\u0642'
                ' \u0643\u0631\u0629 \u0642\u062f\u0645 \u0639\u0631\u0628\u064a \u064a\u0636'
                '\u0645 123 \u0644\u0627\u0639\u0628\u0627\u064b \u0628\u0627\u0647\u0638'
                ' \u0627\u0644\u062b\u0645\u0646 \u0628\u0645\u0627 \u0641\u064a \u0630'
                '\u0644\u0643 \u0627\u0644\u0641\u0627\u0626\u0632 \u0628\u0627\u0644'
                '\u062d\u0630\u0627\u0621 \u0627\u0644\u0630\u0647\u0628\u064a \u0648'
                '\u0639\u062f\u062f \u0645\u0646 \u0627\u0644\u0644\u0627\u0639\u0628'
                '\u064a\u0646 \u0627\u0644\u0623\u062c\u0627\u0646\u0628 \u0627\u0644'
                '\u062f\u0648\u0644\u064a\u064a\u0646.',
                dw = 15
                )
        c.save()

    @rlSkipUnless(rtlSupport,'miss RTL support')
    def test_bidiStrWrap(self):
        from reportlab.platypus.paragraph import _SHYStr, _SplitWordH, _SplitWordEnd
        from reportlab.pdfgen.textobject import BidiStr, bidiStrWrap, _bidiKS

        for i,klass in enumerate((_SHYStr, _SplitWordH, _SplitWordEnd)):
            s = 'abc\xaddef' if klass==_SHYStr else 'ABCDEF'
            orig = BidiStr('dontcare',bidiV=79+i)
            ks = klass(s)
            instw = bidiStrWrap(ks,orig)
            self.assertTrue(hasattr(instw,'__bidiV__'))
            self.assertTrue(instw.__bidiV__==orig.__bidiV__)
            self.assertTrue(instw==ks)
            self.assertTrue(bidiStrWrap(instw,orig) is instw)
            if hasattr(ks,'__dict__'):
                for k in ks.__dict__:
                    self.assertEqual(getattr(ks,k),getattr(instw,k),
                                    f'ks.{k}={getattr(ks,k)} not equal to instw.{k}={getattr(instw,k)}') 

    words0 = 'الرياض هو فريق كرة قدم عربي يضم 123 لاعبًا باهظ الثمن'.split()
    words0 = '\u0627\u0644\u0631\u064a\u0627\u0636 \u0647\u0648 \u0641\u0631\u064a\u0642 \u0643\u0631\u0629 \u0642\u062f\u0645 \u0639\u0631\u0628\u064a \u064a\u0636\u0645 123 \u0644\u0627\u0639\u0628\u064b\u0627 \u0628\u0627\u0647\u0638 \u0627\u0644\u062b\u0645\u0646'.split()

    @rlSkipUnless(rtlSupport,'miss RTL support')
    def test_making_words(self):
        bwl = bidiWordList(self.words0)
        self.assertEqual(bwl,['\ufebd\ufe8e\ufef3\ufeae\ufedf\ufe8d', '\ufeee\ufeeb', '\ufed6\ufef3\ufeae\ufed3', '\ufe93\ufeae\ufedb', '\ufee1\ufeaa\ufed7', '\ufef2\ufe91\ufeae\ufecb', '\ufee2\ufec0\ufef3', '123', '\ufe8e\ufe92\u064b\ufecb\ufefb', '\ufec6\ufeeb\ufe8e\ufe91', '\ufee6\ufee4\ufe9c\ufedf\ufe8d'])
        rt = set([_.__class__.__name__ for _ in bwl])
        xt = set(['BidiStr'])
        self.assertEqual(rt, xt, f"bidiWordList returned wrong types {rt} not expected {xt}")
        xx = [10, 9, 8, 7, 6, 5, 4, 3, 2, 1, 0]
        rx = [getattr(_,'__bidiV__','?') for _ in bwl]
        self.assertEqual(xx, rx, f"bidiWordList returned wrong indeces {rx} not expected {xx}")
        wx = bidiWordList(self.words0,wx=True)
        self.assertEqual(xx, wx, f"bidiWordList(wx=True) returned wrong indeces {wx} not expected {xx}")

    @rlSkipUnless(rtlSupport and haveDejaVu(),'miss RTL and/or DejaVu')
    def test_bidiShapedText(self):
        c = Canvas(outputfile('test_arabic_bidiShapedText.pdf'))
        fontName = 'DejaVuSans'
        fontSize = 12
        leading = 1.2*fontSize
        pdfmetrics.registerFont(freshTTFont("DejaVuSans", "DejaVuSans.ttf", shapable=True))
        c.setFont(fontName, fontSize, leading)
        x = 36
        y = c._pagesize[1] - 36
        dx = max((pdfmetrics.stringWidth(f'{_}: ',fontName,fontSize) for _ in ('raw rtl','raw rtl shaped')))
        def example(x,y,words):
            raw = ' '.join(words)
            x1 = x+dx
            for direction in ('','rtl'):
                for shaping in (False,True):
                    label = f"raw{' rtl' if direction else ''}{' shaped' if shaping else ''}"
                    c.drawString(x,y,label)
                    c.drawString(x1,y,raw, direction=direction, shaping=shaping)
                    y -= leading
            return y

        y = example(x,y,self.words0)

        if False:
            #Ben's example
            y -= leading
            city = "Jizan"
            ar_month = "ﻣﺎﺭﺱ"
            ar_date = f"13-16 {ar_month} 2025"
            start_time = "START TIME: 23:00"
            benWithParen = f'({city}) - {ar_date} - {start_time}'
            benNoParen = f'{city} - {ar_date} - {start_time}'
            y = example(x,y,benWithParen.split())
            y -= leading
            y = example(x,y,benNoParen.split())
            y -= leading
            google = "جيزان - 13-16 مارس 2025 - وقت البدء: 23:00"
            y = example(x,y,google.split())
            y -= leading
    
        c.save()

def makeSuite():
    return makeSuiteForClasses(RtlTestCase)

#noruntests
if __name__ == "__main__":
    unittest.TextTestRunner().run(makeSuite())
    printLocation()
