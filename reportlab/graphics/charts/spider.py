    #copyright ReportLab Inc. 2000-2001
#see license.txt for license details
#history http://cvs.sourceforge.net/cgi-bin/cvsweb.cgi/reportlab/graphics/charts/spider.py?cvsroot=reportlab
#$Header: /tmp/reportlab/reportlab/graphics/charts/spider.py,v 1.7 2003/06/09 17:41:25 johnprecedo Exp $
# spider chart, also known as radar chart

"""Spider Chart

Normal use shows variation of 5-10 parameters against some 'norm' or target.
When there is more than one series, place the series with the largest
numbers first, as it will be overdrawn by each successive one.
"""
__version__=''' $Id: spider.py,v 1.7 2003/06/09 17:41:25 johnprecedo Exp $ '''

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
from reportlab.graphics.charts.areas import PlotArea
from textlabels import Label
from reportlab.graphics.widgets.markers import Marker

_ANGLE2ANCHOR={0:'w', 45:'sw', 90:'s', 135:'se', 180:'e', 225:'ne', 270:'n', 315: 'nw'}
def _findNearestAngleValue(angle,D):
    angle =  angle % 360
    m = 900
    for k in D.keys():
        d = min((angle-k)%360,(k-angle)%360)
        if d<m:
            m, v = d, k
    return D[v]

class StrandProperties(PropHolder):
    """This holds descriptive information about concentric 'strands'.

    Line style, whether filled etc.
    """

    _attrMap = AttrMap(
        strokeWidth = AttrMapValue(isNumber),
        fillColor = AttrMapValue(isColorOrNone),
        strokeColor = AttrMapValue(isColorOrNone),
        strokeDashArray = AttrMapValue(isListOfNumbersOrNone),
        fontName = AttrMapValue(isString),
        fontSize = AttrMapValue(isNumber),
        fontColor = AttrMapValue(isColorOrNone),
        labelRadius = AttrMapValue(isNumber),
        markers = AttrMapValue(isBoolean),
        markerType = AttrMapValue(isAnything),
        markerSize = AttrMapValue(isNumber)
        )

    def __init__(self):
        self.strokeWidth = 0
        self.fillColor = None
        self.strokeColor = STATE_DEFAULTS["strokeColor"]
        self.strokeDashArray = STATE_DEFAULTS["strokeDashArray"]
        self.fontName = STATE_DEFAULTS["fontName"]
        self.fontSize = STATE_DEFAULTS["fontSize"]
        self.fontColor = STATE_DEFAULTS["fillColor"]
        self.labelRadius = 1.2
        self.markers = 0
        self.markerType = None
        self.markerSize = 0

class SpiderChart(PlotArea):
    _attrMap = AttrMap(BASE=PlotArea,
        data = AttrMapValue(None, desc='Data to be plotted, list of (lists of) numbers.'),
        labels = AttrMapValue(isListOfStringsOrNone, desc="optional list of labels to use for each data point"),
        startAngle = AttrMapValue(isNumber, desc="angle of first slice; like the compass, 0 is due North"),
        direction = AttrMapValue( OneOf('clockwise', 'anticlockwise'), desc="'clockwise' or 'anticlockwise'"),
        strands = AttrMapValue(None, desc="collection of strand descriptor objects"),
        )

    def __init__(self):
        PlotArea.__init__(self)

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


    def draw(self):
        # normalize slice data
        g = self.makeBackground() or Group()

        xradius = self.width/2.0
        yradius = self.height/2.0
        self._radius = radius = min(xradius, yradius)
        centerx = self.x + xradius
        centery = self.y + yradius

        data = self.normalizeData()

        n = len(data[0])

        #labels
        if self.labels is None:
            labels = [''] * n
        else:
            labels = self.labels
            #there's no point in raising errors for less than enough errors if
            #we silently create all for the extreme case of no labels.
            i = n-len(labels)
            if i>0:
                labels = labels + ['']*i

        spokes = []
        csa = []
        angle = self.startAngle*pi/180
        direction = self.direction == "clockwise" and -1 or 1
        angleBetween = direction*(2 * pi)/n
        labels = self.labels
        markers = self.strands.markers
        for i in xrange(n):
            car = cos(angle)*radius
            sar = sin(angle)*radius
            csa.append((car,sar,angle))
            spoke = Line(centerx, centery, centerx + car, centery + sar, strokeWidth = 0.5)
            #print 'added spoke (%0.2f, %0.2f) -> (%0.2f, %0.2f)' % (spoke.x1, spoke.y1, spoke.x2, spoke.y2)
            spokes.append(spoke)
            if labels:
                text = labels[i]
                if text:
                    si = self.strands[i]
                    labelRadius = si.labelRadius
                    ex = centerx + labelRadius*car
                    ey = centery + labelRadius*sar
                    L = Label()
                    L.setText(text)
                    L.x = ex
                    L.y = ey
                    L.boxAnchor = _findNearestAngleValue(angle*180/pi,_ANGLE2ANCHOR)
                    L.fontName = si.fontName
                    L.fontSize = si.fontSize
                    L.fillColor = si.fontColor
                    L.textAnchor = 'boxauto'
                    spokes.append(L)
            angle = angle + angleBetween

        # now plot the polygons

        rowIdx = 0
        for row in data:
            # series plot
            points = []
            car, sar = csa[-1][:2]
            r = row[-1]
            points.append(centerx+car*r)
            points.append(centery+sar*r)
            for i in xrange(n):
                car, sar = csa[i][:2]
                r = row[i]
                points.append(centerx+car*r)
                points.append(centery+sar*r)

                # make up the 'strand'
                strand = Polygon(points)
                strand.fillColor = self.strands[rowIdx].fillColor
                strand.strokeColor = self.strands[rowIdx].strokeColor
                strand.strokeWidth = self.strands[rowIdx].strokeWidth
                strand.strokeDashArray = self.strands[rowIdx].strokeDashArray

                g.add(strand)

                # put in a marker, if it needs one
                if markers:
                    marker = Marker(kind = self.strands[rowIdx].markerType,
                                    size = self.strands[rowIdx].markerSize,
                                    x =  centerx+car*r,
                                    y = centery+sar*r,
                                    fillColor = self.strands[rowIdx].fillColor,
                                    strokeColor = self.strands[rowIdx].strokeColor,
                                    strokeWidth = self.strands[rowIdx].strokeWidth,
                                    angle = 0,
                                    )
                    g.add(marker)

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
    pc.data = [[10,12,14,16,14,12], [6,8,10,12,9,15],[7,8,17,4,12,8,3]]
    pc.labels = ['a','b','c','d','e','f']
    pc.strands[2].fillColor=colors.palegreen

    d.add(pc)

    return d


def sample2():
    "Make a spider chart with markers, but no fill"

    d = Drawing(400, 400)

    pc = SpiderChart()
    pc.x = 50
    pc.y = 50
    pc.width = 300
    pc.height = 300
    pc.data = [[10,12,14,16,14,12], [6,8,10,12,9,15],[7,8,17,4,12,8,3]]
    pc.labels = ['U','V','W','X','Y','Z']
    pc.strands.strokeWidth = 2
    pc.strands[0].fillColor = None
    pc.strands[1].fillColor = None
    pc.strands[2].fillColor = None
    pc.strands[0].strokeColor = colors.red
    pc.strands[1].strokeColor = colors.blue
    pc.strands[2].strokeColor = colors.green
    pc.strands.markers = 1
    pc.strands.markerType = "FilledDiamond"
    pc.strands.markerSize = 6

    d.add(pc)

    return d


if __name__=='__main__':
    d = sample1()
    from reportlab.graphics.renderPDF import drawToFile
    drawToFile(d, 'spider.pdf')
    d = sample2()
    drawToFile(d, 'spider2.pdf')
    #print 'saved spider.pdf'
