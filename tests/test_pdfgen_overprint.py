#Copyright ReportLab Europe Ltd. 2000-2008
#see license.txt for license details
# full screen test
"""Tests for overprint/knockout.

This has been placed in a separate file so output can be passed to printers
"""
__version__='''$Id$'''
from reportlab.lib.testutils import setOutDir,makeSuiteForClasses, outputfile, printLocation
setOutDir(__name__)
import os
import unittest
from reportlab.pdfgen.canvas import Canvas
from reportlab.lib.colors import CMYKColor

def fileDoesExist(path):
    "Check if a file does exist."
    return os.path.exists(path)


class OverprintTestCase(unittest.TestCase):
    "Testing overprint/knockout."


    def test0(self):
        "This should open in full screen mode."
        filename = 'test_pdfgen_overprint.pdf'
        desc = "Overprint/knockout tests for ReportLab library"
        
        black = CMYKColor(0,0,0,1)
        
        cyan = CMYKColor(1,0,0,0)
        magenta = CMYKColor(0,1,0,0)
        c = Canvas(filename)
        c.setFillColor(black)
        c.setFont('Helvetica', 20)
        c.drawString(100, 700, desc)
        
        c.setFont('Helvetica', 10)
        c.drawString(100, 670, "To understand these you need a tool like Illustrator, Quark or Acrobat to separate plates.")
        c.drawString(100, 658, "In the top example, the smaller rectangle overprints. In the lower one, it 'knocks out'.")
        c.drawString(100, 646, "In Acrobat Reader or on a cheap printer, both will probably look the same - magenta on cyan.")
        c.drawString(100, 634, "In high end tools like Illustrator, the top will show blue on cyan, because the two colours merge,")
        c.drawString(100, 622, "and the bottom will show magenta on cyan, because there's no cyan left underneath.")
        c.drawString(100, 610, "A separated cyan plate will show a hole in the lower rectangle.")



        c.setFillOverprint(True)
        c.setFillColor(cyan)
        c.rect(100, 450, 400, 100, fill=True, stroke=False)
        c.setFillColor(magenta)
        c.rect(200, 475, 200, 50, fill=True, stroke=False)
        
        
        c.setFillOverprint(False)
        c.setFillColor(cyan)
        c.rect(100, 250, 400, 100, fill=True, stroke=False)
        c.setFillColor(magenta)
        c.rect(200, 275, 200, 50, fill=True, stroke=False)
        
        
        c.save()

        assert fileDoesExist(filename)


def makeSuite():
    return makeSuiteForClasses(OverprintTestCase)


#noruntests
if __name__ == "__main__":
    unittest.TextTestRunner().run(makeSuite())
    printLocation()
