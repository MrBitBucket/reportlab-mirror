#!/bin/env python
# coding=utf8
#Copyright ReportLab Europe Ltd. 2025
#see license.txt for license details
__version__='3.3.0'
__doc__="""Exercising basic Canvas operations and libraries involved in Arabic/Hebrew


This is really to build up oour own understanding at the moment.
"""
from reportlab.lib.testutils import setOutDir,makeSuiteForClasses, outputfile, printLocation
setOutDir(__name__)
import unittest
from reportlab.pdfgen.canvas import Canvas
from reportlab.platypus.paraparser import _greekConvert
from reportlab.pdfbase import pdfmetrics 
from reportlab.pdfbase.ttfonts import TTFont


try:
    import pyfribidi
except ImportError:
    pyfribidi = None

try:
    import uharfbuzz
except ImportError:
    uharfbuzz = None

class RtlTestCase(unittest.TestCase):
    "Simplest test that makes PDF"

    def test(self):
        c = Canvas(outputfile('test_arabic.pdf'))

        pdfmetrics.registerFont(TTFont("DejaVuSans", "DejaVuSans.ttf"))

        c.setFont('Helvetica-Bold', 18)
        c.drawString(100,800, 'Tests relating to RTL, Hebrew and Arabic')
        c.setFont('Helvetica', 12)


        if pyfribidi:  # essential for these tests
            msg = f"Using pyfrbidi version {pyfribidi.__version__}"
            c.drawString(100,750, msg)

        else:
            msg = "pyfribidi not imported, exiting"
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

        logicalchars = pyfribidi.log2vis(phrase)
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


def makeSuite():

    return makeSuiteForClasses(RtlTestCase)


#noruntests
if __name__ == "__main__":
    unittest.TextTestRunner().run(makeSuite())
    printLocation()
