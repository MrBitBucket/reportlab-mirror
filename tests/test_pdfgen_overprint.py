#Copyright ReportLab Europe Ltd. 2000-2008
#see license.txt for license details
# full screen test
"""Tests for overprint/knockout.

This has been placed in a separate file so output can be passed to printers
"""
__version__='''$Id$'''
from reportlab.lib.testutils import setOutDir,makeSuiteForClasses, outputfile, printLocation
setOutDir(__name__)
import unittest

class OverprintTestCase(unittest.TestCase):
    "Testing overprint/knockout."


    def test0(self):
        "This should open in full screen mode."
        import os
        from reportlab.pdfgen.canvas import Canvas
        from reportlab.lib.colors import PCMYKColor, PCMYKColorSep
        filename = 'test_pdfgen_overprint.pdf'
        desc = "Overprint/knockout tests for ReportLab library"

        black = PCMYKColor(0,0,0,100)
        cyan = PCMYKColorSep(100,0,0,0,spotName='myCyan')
        magenta = PCMYKColorSep(0,100,0,0,spotName='myMagenta')

        c = Canvas(filename)
        c.setFillColor(black)
        c.setFont('Helvetica', 20)
        c.drawString(100, 700, desc)

        c.setFont('Helvetica', 10)
        c.drawString(100, 670, "To understand these you need a tool like Illustrator, Quark or Acrobat to separate plates.")
        c.drawString(100, 658, "In the top example, the magenta rectangle overprints. In the lower one, it 'knocks out'.")
        c.drawString(100, 646, "In Acrobat Reader or on a cheap printer, both will probably look the same - magenta on cyan.")
        c.drawString(100, 634, "In high end tools like Illustrator, the top overlap will show blue on cyan, because the two colours merge,")
        c.drawString(100, 622, "and the bottom overlap will show magenta on cyan, because there's no cyan left underneath.")
        c.drawString(100, 610, "A separated cyan plate will show a hole in the lower rectangle.")

        c.setFillOverprint(True)
        c.setFillColor(cyan)
        c.rect(100, 450, 200, 100, fill=True, stroke=False)
        c.setFillColor(magenta)
        c.rect(200, 500, 200, 100, fill=True, stroke=False)

        c.setFillOverprint(False)
        c.setFillColor(cyan)
        c.rect(100, 250, 200, 100, fill=True, stroke=False)
        c.setFillColor(magenta)
        c.rect(150, 300, 200, 100, fill=True, stroke=False)

        c.save()
        assert os.path.exists(filename)


def makeSuite():
    return makeSuiteForClasses(OverprintTestCase)


#noruntests
if __name__ == "__main__":
    unittest.TextTestRunner().run(makeSuite())
    printLocation()
