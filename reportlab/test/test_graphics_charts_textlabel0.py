"""
Tests for the text Label class.
"""

import os, sys, copy

from reportlab.test import unittest
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.pdfgen.canvas import Canvas
from reportlab.graphics.shapes import *
from reportlab.graphics.charts.textlabel0 import Label
from reportlab.graphics.renderPDF import drawToFile


class LabelTestCase(unittest.TestCase):
    "Test Label class."

    def _test0(self):
        "Perform original test function."

        pdfPath = 'test_graphics_charts_textlabel0.pdf'
        c = Canvas(pdfPath)

        label = Label()
        demoLabel = label.demo()
        demoLabel.drawOn(c, 0, 0)

        c.save()


    def test1(self):
        "Test all different box anchors."

        pdfPath = 'test_graphics_charts_textlabel0.pdf'
        c = Canvas(pdfPath)

        # Set drawing dimensions.
        w, h = drawWidth, drawHeight = 200, 100

        # Create labels by making variabtions of one prototype.
        protoLabel = Label()
        protoLabel.dx = 0
        protoLabel.dy = 0
        protoLabel.boxStrokeWidth = 0.1
        protoLabel.boxStrokeColor = colors.black
        protoLabel.boxFillColor = colors.lemonchiffon
        protoLabel.fontName = 'Helvetica'
        protoLabel.fontSize = 12
        # protoLabel.text = 'Hello World!' # Does not work as expected.
        protoLabel.setOrigin(drawWidth/2, drawHeight/2)

        y = 1*cm
        for boxAnchors in ('sw se nw ne', 'w e n s', 'c'):
            boxAnchors = string.split(boxAnchors, ' ')
            
            # Create drawing.
            d = Drawing(w, h)
            d.add(Line(0,h/2, w, h/2, strokeColor=colors.gray, strokeWidth=0.5))
            d.add(Line(w/2,0, w/2, h, strokeColor=colors.gray, strokeWidth=0.5))

            labels = []
            for boxAnchor in boxAnchors:
                # Modify label, put it on a drawing.
                label = copy.deepcopy(protoLabel)
                label.boxAnchor = boxAnchor
                label.setText('Hello World! (%s)' % boxAnchor)
                labels.append(label)
                
            for label in labels:
                d.add(label)

            lm = leftMargin = 2*cm
            d.drawOn(c, lm, y)

            y = y + drawHeight + 1*cm
            
        c.save()


def makeSuite():
    suite = unittest.TestSuite()
    suite.addTest(LabelTestCase('test1'))
    return suite


if __name__ == "__main__":
    unittest.TextTestRunner().run(makeSuite())
