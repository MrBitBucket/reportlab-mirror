#!/usr/bin/env python

import string
import unittest
from xml.dom import minidom

from reportlab.graphics.shapes import *
from reportlab.graphics import renderSVG



def load(path):
    "Helper function to read the generated SVG again."

    doc = minidom.parse(path)
    doc.normalize()
    return doc.documentElement



class RenderSvgSimpleTestCase(unittest.TestCase):
    "Testing renderSVG module."

    def test0(self):
        "Test two strings in drawing."

        path = "test_renderSVG_simple_test0.svg"

        d = Drawing(200, 100)
        d.add(String(0, 0, "foo"))
        d.add(String(100, 0, "bar"))
        renderSVG.drawToFile(d, path)

        svg = load(path)
        fg = svg.getElementsByTagName('g')[0]           # flipping group
        dg = fg.getElementsByTagName('g')[0]            # diagram group
        textChildren = dg.getElementsByTagName('text')  # text nodes
        t0 = string.strip(textChildren[0].childNodes[0].nodeValue)
        t1 = string.strip(textChildren[1].childNodes[0].nodeValue)
        assert t0 == 'foo'
        assert t1 == 'bar'


    def test1(self):
        "Test two strings in group in drawing."

        path = "test_renderSVG_simple_test1.svg"

        d = Drawing(200, 100)
        g = Group()
        g.add(String(0, 0, "foo"))
        g.add(String(100, 0, "bar"))
        d.add(g)
        renderSVG.drawToFile(d, path)

        svg = load(path)
        fg = svg.getElementsByTagName('g')[0]           # flipping group
        dg = fg.getElementsByTagName('g')[0]            # diagram group
        g = dg.getElementsByTagName('g')[0]             # custom group
        textChildren = g.getElementsByTagName('text')   # text nodes
        t0 = string.strip(textChildren[0].childNodes[0].nodeValue)
        t1 = string.strip(textChildren[1].childNodes[0].nodeValue)

        assert t0 == 'foo'
        assert t1 == 'bar'


    def test2(self):
        "Test two strings in transformed group in drawing."

        path = "test_renderSVG_simple_test2.svg"

        d = Drawing(200, 100)
        g = Group()
        g.add(String(0, 0, "foo"))
        g.add(String(100, 0, "bar"))
        g.scale(1.5, 1.2)
        g.translate(50, 0)
        d.add(g)
        renderSVG.drawToFile(d, path)

        svg = load(path)
        fg = svg.getElementsByTagName('g')[0]           # flipping group
        dg = fg.getElementsByTagName('g')[0]            # diagram group
        g = dg.getElementsByTagName('g')[0]             # custom group
        textChildren = g.getElementsByTagName('text')   # text nodes
        t0 = string.strip(textChildren[0].childNodes[0].nodeValue)
        t1 = string.strip(textChildren[1].childNodes[0].nodeValue)

        assert t0 == 'foo'
        assert t1 == 'bar'


class RenderSvgAxesTestCase(unittest.TestCase):
    "Testing renderSVG module on Axes widgets."

    def test0(self):
        "Test two strings in drawing."

        path = "axestest0.svg"
        from reportlab.graphics.charts.axes import XCategoryAxis

        d = XCategoryAxis().demo()
        renderSVG.drawToFile(d, path)




def makeSuite():
    suite = unittest.TestSuite()

    suite.addTest(RenderSvgSimpleTestCase('test0'))
    suite.addTest(RenderSvgSimpleTestCase('test1'))
    suite.addTest(RenderSvgSimpleTestCase('test2'))

    suite.addTest(RenderSvgAxesTestCase('test0'))

    return suite




if __name__ == "__main__":
    unittest.TextTestRunner().run(makeSuite())
