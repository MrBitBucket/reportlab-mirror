#copyright ReportLab Inc. 2000-2001
#see license.txt for license details
#history http://cvs.sourceforge.net/cgi-bin/cvsweb.cgi/reportlab/graphics/charts/spider.py?cvsroot=reportlab
#$Header: /tmp/reportlab/reportlab/graphics/charts/spider.py,v 1.1 2002/12/02 23:16:07 andy_robinson Exp $
# spider chart, also known as radar chart

"""Spider Chart

Normal use shows variation of 5-10 parameters against some 'norm' or target.
When there is more than one series, place the series with the largest
numbers first, as it will be overdrawn by each successive one.
"""
__version__=''' $Id: spider.py,v 1.1 2002/12/02 23:16:07 andy_robinson Exp $ '''

import copy
from math import sin, cos, pi

from reportlab.lib import colors
from reportlab.lib.validators import isColor, isNumber, isListOfNumbersOrNone,\
                                    isListOfNumbers, isColorOrNone, isString,\
                                    isListOfStringsOrNone, OneOf, SequenceOf,\
                                    isBoolean, isListOfColors,\
                                    isNoneOrListOfNoneOrStrings,\
                                    isNoneOrListOfNoneOrNumbers
from reportlab.lib.attrmap import *
from reportlab.pdfgen.canvas import Canvas
from reportlab.graphics.shapes import Group, Drawing, Line, Rect, Polygon, Ellipse, \
    Wedge, String, STATE_DEFAULTS
from reportlab.graphics.widgetbase import Widget, TypedPropertyCollection, PropHolder



class StrandProperties(PropHolder):
    """This holds descriptive information about concentric 'strands'.

    Line style, whether filled etc.
    """

    _attrMap = AttrMap(
        strokeWidth = AttrMapValue(isNumber),
        fillColor = AttrMapValue(isColorOrNone),
        strokeColor = AttrMapValue(isColorOrNone),
        strokeDashArray = AttrMapValue(isListOfNumbersOrNone),
        )

    def __init__(self):
        self.strokeWidth = 0
        self.fillColor = None
        self.strokeColor = STATE_DEFAULTS["strokeColor"]
        self.strokeDashArray = STATE_DEFAULTS["strokeDashArray"]


class SpiderChart(Widget):
    _attrMap = AttrMap(
        x = AttrMapValue(isNumber, desc='X position of the chart within its container.'),
        y = AttrMapValue(isNumber, desc='Y position of the chart within its container.'),
        width = AttrMapValue(isNumber, desc='width of spider bounding box. Need not be same as width.'),
        height = AttrMapValue(isNumber, desc='height of spider bounding box.  Need not be same as height.'),
        data = AttrMapValue(None, desc='Data to be plotted, list of (lists of) numbers.'),
        labels = AttrMapValue(isListOfStringsOrNone, desc="optional list of labels to use for each data point"),
        startAngle = AttrMapValue(isNumber, desc="angle of first slice; like the compass, 0 is due North"),
        direction = AttrMapValue( OneOf('clockwise', 'anticlockwise'), desc="'clockwise' or 'anticlockwise'"),
        strands = AttrMapValue(None, desc="collection of strand descriptor objects"),
        )

    def __init__(self):
        self.x = 0
        self.y = 0
        self.width = 100
        self.height = 100
        self.data = [[10,12,14,16,14,12], [6,8,10,12,9,11]]
        self.labels = None  # or list of strings
        self.startAngle = 90
        self.direction = "clockwise"

        self.strands = TypedPropertyCollection(StrandProperties)
        self.strands[0].fillColor = colors.cornsilk
        self.strands[1].fillColor = colors.cyan


    def demo(self):
        d = Drawing(200, 100)

        sp = SpiderChart()
        sp.x = 50
        sp.y = 10
        sp.width = 100
        sp.height = 80
        sp.data = [[10,12,14,16,18,20],[6,8,4,6,8,10]]
        sp.labels = ['a','b','c','d','e','f']

        d.add(sp)
        return d

    def normalizeData(self, outer = 0.0):
        """Turns data into normalized ones where each datum is < 1.0,
        and 1.0 = maximum radius.  Adds 10% at outside edge by default""" 
        data = self.data
        theMax = 0.0
        for row in data:
            for element in row:
                assert element >=0, "Cannot do spider plots of negative numbers!"
                if element > theMax:
                    theMax = element
        theMax = theMax * (1.0+outer)

        scaled = []
        for row in data:
            scaledRow = []
            for element in row:
                scaledRow.append(element / theMax)
            scaled.append(scaledRow)
        return scaled


    def polarToRect(self, r, theta):
        "Convert to rectangular based on current size"
        return (self._centerx + r * sin(theta),self._centery + r * cos(theta))
    
    def draw(self):
        # normalize slice data
        g = Group()


        # show bounding box
        g.add(Rect(self.x, self.y, self.width, self.height,
                   strokeColor=colors.red,
                   fillColor=None))


        xradius = self.width/2.0
        yradius = self.height/2.0
        self._radius = radius = min(xradius, yradius)
        self._centerx = centerx = self.x + xradius
        self._centery = centery = self.y + yradius

        data = self.normalizeData()
        
        n = len(self.data[0])
        angleBetween = (2 * pi)/n
        
        # make a list of all spoke angles
        angles = []
        a = (self.startAngle * pi / 180)
        for i in range(n):
            angles.append(a)
            a = a + angleBetween
            


        print '%d slices each of %0.2f radians here: %s' % (n, angleBetween, repr(angles))
        
        if self.direction == "anticlockwise":
            whichWay = 1
        else:
            whichWay = -1

        i = 0
        startAngle = self.startAngle
        spokes = []
        for angle in angles:
            spoke = Line(centerx,
                         centery,
                         centerx + radius * sin(angle),
                         centery + radius * cos(angle),
                         strokeWidth = 0.5
                         )
            print 'added spoke (%0.2f, %0.2f) -> (%0.2f, %0.2f)' % (spoke.x1,
                                                                    spoke.y1,
                                                                    spoke.x2,
                                                                    spoke.y2)
                         
            spokes.append(spoke)

        # now plot the polygons

        rowIdx = 0    
        for row in data:
            # series plot
            points = []
            theta = angles[-1]
            r = row[-1]
            x0, y0 = self.polarToRect(r*radius, theta)
            points.append(x0)
            points.append(y0)
            for i in range(n):
                theta = angles[i]
                r = row[i]
                x1, y1 = self.polarToRect(r*radius, theta)
                x0, y0 = x1, y1
                points.append(x0)
                points.append(y0)

                # make up the 'strand'
                strand = Polygon(points)
                strand.fillColor = self.strands[rowIdx].fillColor
                strand.strokeColor = self.strands[rowIdx].strokeColor
                strand.strokeWidth = self.strands[rowIdx].strokeWidth
                strand.strokeDashArray = self.strands[rowIdx].strokeDashArray

                g.add(strand)
                
            rowIdx = rowIdx + 1

        # spokes go over strands
        for spoke in spokes:
            g.add(spoke)
        return g




def sample1():
    "Make a simple spider chart"

    d = Drawing(400, 400)

    pc = SpiderChart()
    pc.x = 50
    pc.y = 50
    pc.width = 300
    pc.height = 300
    pc.data = [[10,12,14,16,14,12], [6,8,10,12,9,11]]
    pc.labels = ['a','b','c','d','e','f']
    
    d.add(pc)

    return d


if __name__=='__main__':
    d = sample1()
    from reportlab.graphics.renderPDF import drawToFile
    drawToFile(d, 'spider.pdf')
    print 'saved spider.pdf'