#!/usr/bin/env python
from reportlab.lib.testutils import setOutDir,makeSuiteForClasses, outputfile, printLocation
setOutDir(__name__)
from xml.dom import minidom
import unittest
from reportlab.graphics.shapes import *
from reportlab.graphics import renderPS


class RenderPSSimpleTestCase(unittest.TestCase):
    "Testing renderPS module."

    def test0(self):
        "Test two strings in drawing."

        path = outputfile("test_renderPS_simple_test0.ps")

        d = Drawing(200, 100)
        d.add(String(0, 0, "foo"))
        d.add(String(100, 0, "bar"))
        renderPS.drawToFile(d, path)

    def test1(self):
        "Test two strings in group in drawing."

        path = outputfile("test_renderPS_simple_test1.ps")

        d = Drawing(200, 100)
        g = Group()
        g.add(String(0, 0, "foo"))
        g.add(String(100, 0, "bar"))
        d.add(g)
        renderPS.drawToFile(d, path)

    def test2(self):
        "Test two strings in transformed group in drawing."

        path = outputfile("test_renderPS_simple_test2.ps")

        d = Drawing(200, 100)
        g = Group()
        g.add(String(0, 0, "foo"))
        g.add(String(100, 0, "bar"))
        g.scale(1.5, 1.2)
        g.translate(50, 0)
        d.add(g)
        renderPS.drawToFile(d, path)

    def test3(self):
        from reportlab.lib.units import cm
        from reportlab.lib import colors

        width=300
        height=60

        #Create fairly simple drawing object,
        drawing=Drawing(width, height)

        p=ArcPath(strokeColor=colors.darkgreen,
                          fillColor=colors.green,
                          hrefURL="http://en.wikipedia.org/wiki/Vector_path",
                          hrefTitle="This big letter C is actually a closed vector path.",
                          strokewidth=0)
        p.addArc(1*cm, 1*cm, 0.8*cm, 20, 340, moveTo=True)
        p.addArc(1*cm, 1*cm, 0.9*cm, 20, 340, reverse=True)
        p.closePath()
        drawing.add(p)

        drawing.add(Rect(2.25*cm, 0.1*cm, 1.5*cm, 0.8*cm, rx=0.25*cm, ry=0.25*cm,

        hrefURL="http://en.wikipedia.org/wiki/Rounded_rectangle",
                               hrefTitle="Rounded Rectangle",
                               strokeColor=colors.red,
                               fillColor=colors.yellow))

        drawing.add(String(1*cm, 1*cm, "Hello World!",
                                 hrefURL="http://en.wikipedia.org/wiki/Hello_world",
                                 hrefTitle="Why 'Hello World'?",
                                 fillColor=colors.darkgreen))
        drawing.add(Rect(4.5*cm, 0.5*cm, 5*cm, 1*cm,
                                hrefURL="http://en.wikipedia.org/wiki/Rectangle",
                                hrefTitle="Wikipedia page on rectangles",
                                strokeColor=colors.blue,
                                fillColor=colors.red))
        drawing.add(Ellipse(7*cm, 1*cm, 2*cm, 0.95*cm,
                                  hrefURL="http://en.wikipedia.org/wiki/Ellipse",
                                  strokeColor=colors.black,
                                  fillColor=colors.yellow))
        drawing.add(Circle(7*cm, 1*cm, 0.9*cm,
                                  hrefURL="http://en.wikipedia.org/wiki/Circle",
                                 strokeColor=colors.black,
                                 fillColor=colors.brown))
        drawing.add(Ellipse(7*cm, 1*cm, 0.5*cm, 0.9*cm,
                                  hrefTitle="Tooltip with no link?",
                                  strokeColor=colors.black,
                                  fillColor=colors.black))
        drawing.add(Polygon([4.5*cm, 1.25*cm, 5*cm, 0.1*cm, 4*cm, 0.1*cm],
                                  hrefURL="http://en.wikipedia.org/wiki/Polygon",
                                  hrefTitle="This triangle is a simple polygon.",
                                  strokeColor=colors.darkgreen,
                                  fillColor=colors.green))

        renderPS.drawToFile(drawing, outputfile("test_renderPS_simple_test3.ps"))

    def test4(self):
        "Test character encoding."

        path = outputfile("test_renderPS_simple_test4.ps")
        specialChar = u'\u2019'

        d = Drawing(200, 100)
        d.add(String(0, 0, "foo"+specialChar))
        d.add(String(100, 0, "bar"))
        renderPS.drawToFile(d, path)

    def test5(self):
        '''tests drawToString inspired by https://bitbucket.org/egillet/ 
        & https://bitbucket.org/johanndt/'''
        d = Drawing(1,1)
        self.assertTrue(isStr(renderPS.drawToString(d)),msg='renderPS.draweToString should return bytes')

    def tearDown(self):
        "When finished, make a little index page to view them in situ"
        
        body = """<html>
    <head><title>renderPS test output</title></head>
    <body>
        <h1>renderPS test output in a web page</h1>
        <p>We have four SVG diagrams embedded in this page.  Each is within a cyan-coloured div.
        The first 3 have a native size of 400x200, thus consume a height of 200 pixels on
        the page.  The last is 300x60.</p>

        <div style="background-color:cyan">
            <embed src="test_renderPS_simple_test0.ps" type="image/svg+xml" />
        </div>
        <hr/>
        <div style="background-color:cyan">
            <embed src="test_renderPS_simple_test1.ps" type="image/svg+xml" />
        </div>
        <hr/>
        <div style="background-color:cyan">
            <embed src="test_renderPS_simple_test2.ps" type="image/svg+xml" />
        </div>
        <hr/>
        <div style="background-color:cyan">
            <embed src="test_renderPS_simple_test3.ps" type="image/svg+xml" />
        </div>

        <hr>
        <p>Test of resizing:  the ones below are sized 50%, 100%, 150%. We did this by explicitly setting
        the width and height in the <code>embed</code> tag.</p>
        <div style="background-color:cyan">
            <embed src="test_renderPS_simple_test3.ps" type="image/svg+xml" width="150" height="45"/>
        </div>
        <hr/>
        <div style="background-color:cyan">
            <embed src="test_renderPS_simple_test3.ps" type="image/svg+xml" width="300" height="60"/>
        </div>
        <hr/>
        <div style="background-color:cyan">
            <embed src="test_renderPS_simple_test3.ps" type="image/svg+xml" width="450" height="90"/>
        </div>
        <hr/>

        <p>Test of resizing again:  the ones below are sized 50%, 100%, 150% by setting width only.</p>
        <div style="background-color:cyan">
            <embed src="test_renderPS_simple_test3.ps" type="image/svg+xml" width="150"/>
        </div>
        <hr/>
        <div style="background-color:cyan">
            <embed src="test_renderPS_simple_test3.ps" type="image/svg+xml" width="300"/>
        </div>
        <hr/>
        <div style="background-color:cyan">
            <embed src="test_renderPS_simple_test3.ps" type="image/svg+xml" width="450"/>
        </div>
        <hr/>

        
    </body>
<html>
"""
        with open('test_renderPS_output.html', 'w') as f:
            f.write(body)

class RenderPSAxesTestCase(unittest.TestCase):
    "Testing renderPS module on Axes widgets."

    def test0(self):
        "Test two strings in drawing."

        path = outputfile("axestest0.ps")
        from reportlab.graphics.charts.axes import XCategoryAxis

        d = XCategoryAxis().demo()
        renderPS.drawToFile(d, path)

def makeSuite():
    return makeSuiteForClasses(RenderPSSimpleTestCase, RenderPSAxesTestCase)

#noruntests
if __name__ == "__main__":
    unittest.TextTestRunner().run(makeSuite())
    printLocation()
