#copyright ReportLab Inc. 2000-2002
#see license.txt for license details
"""
Tests for RLG Image shapes.
"""

import os

from reportlab.test import unittest
from reportlab.graphics.shapes import Image, Drawing
from reportlab.graphics import renderPDF


class ImageTestCase(unittest.TestCase):
    "Test RLG Image shape."

    def test1(self):
        "Test simple RLG Image shape."

        d = Drawing(100, 50)
        inPath = "pythonpowered.gif"
        img = Image(0, 0, 110, 44, inPath)
        d.add(img)
        outPath = os.path.splitext(inPath)[0] + '.pdf'
        renderPDF.drawToFile(d, outPath, '')
        assert os.path.exists(outPath) == 1


def makeSuite():
    suite = unittest.TestSuite()
    suite.addTest(ImageTestCase('test1'))
    return suite


#noruntests
if __name__ == "__main__":
    unittest.TextTestRunner().run(makeSuite())
