#copyright ReportLab Inc. 2000-2001
#see license.txt for license details
#history http://cvs.sourceforge.net/cgi-bin/cvsweb.cgi/reportlab/graphics/charts/piecharts.py?cvsroot=reportlab
#$Header: /tmp/reportlab/reportlab/graphics/charts/piecharts.py,v 1.13 2001/05/18 16:24:25 rgbecker Exp $
# experimental pie chart script.  Two types of pie - one is a monolithic
#widget with all top-level properties, the other delegates most stuff to
#a wedges collection whic lets you customize the group or every individual
#wedge.

"""Basic Pie Chart class.

This permits you to customize and pop out individual wedges;
supports elliptical and circular pies.
"""

import copy
from math import sin, cos, pi

from reportlab.lib import colors
from reportlab.lib.validators import isColor, isNumber, isListOfNumbersOrNone, isListOfNumbers, isColorOrNone, isString, isListOfStringsOrNone, OneOf, SequenceOf
from reportlab.lib.attrmap import *
from reportlab.pdfgen.canvas import Canvas
from reportlab.graphics.shapes import Group, Drawing, Ellipse, Wedge, String, STATE_DEFAULTS
from reportlab.graphics.widgetbase import Widget, TypedPropertyCollection, PropHolder


class WedgeProperties(PropHolder):
    """This holds descriptive information about the wedges in a pie chart.
    
    It is not to be confused with the 'wedge itself'; this just holds
    a recipe for how to format one, and does not allow you to hack the
    angles.  It can format a genuine Wedge object for you with its
    format method.
    """

    _attrMap = AttrMap(
        strokeWidth = AttrMapValue(isNumber),
        fillColor = AttrMapValue(isColorOrNone),
        strokeColor = AttrMapValue(isColorOrNone),
        strokeDashArray = AttrMapValue(isListOfNumbersOrNone),
        popout = AttrMapValue(isNumber),
        fontName = AttrMapValue(isString),
        fontSize = AttrMapValue(isNumber),
        fontColor = AttrMapValue(isColorOrNone),
        labelRadius = AttrMapValue(isNumber),
        )

    def __init__(self):
        self.strokeWidth = 0
        self.fillColor = None
        self.strokeColor = STATE_DEFAULTS["strokeColor"]
        self.strokeDashArray = STATE_DEFAULTS["strokeDashArray"]
        self.popout = 0
        self.fontName = STATE_DEFAULTS["fontName"]
        self.fontSize = STATE_DEFAULTS["fontSize"]
        self.fontColor = STATE_DEFAULTS["fillColor"]
        self.labelRadius = 1.2


class Pie(Widget):
    _attrMap = AttrMap(
        x = AttrMapValue(isNumber, desc='X position of the chart.'),
        y = AttrMapValue(isNumber, desc='Y position of the chart.'),
        width = AttrMapValue(isNumber),
        height = AttrMapValue(isNumber),
        data = AttrMapValue(isListOfNumbers),
        labels = AttrMapValue(isListOfStringsOrNone),
        startAngle = AttrMapValue(isNumber),
        direction = AttrMapValue( OneOf(('clockwise', 'anticlockwise'))),
        defaultStyles = AttrMapValue(None),
        )
    
    def __init__(self):
        self.x = 0
        self.y = 0
        self.width = 100
        self.height = 100
        self.data = [1]
        self.labels = None  # or list of strings
        self.startAngle = 90
        self.direction = "clockwise"
        
        self.defaultStyles = TypedPropertyCollection(WedgeProperties)
        self.defaultStyles[0].fillColor = colors.darkcyan
        self.defaultStyles[1].fillColor = colors.blueviolet
        self.defaultStyles[2].fillColor = colors.blue
        self.defaultStyles[3].fillColor = colors.cyan

        
    def demo(self):
        d = Drawing(200, 100)
    
        pc = Pie()
        pc.x = 50
        pc.y = 10
        pc.width = 100
        pc.height = 80
        pc.data = [10,20,30,40,50,60]
        pc.labels = ['a','b','c','d','e','f']

        pc.defaultStyles.strokeWidth=0.5
        pc.defaultStyles[3].popout = 10
        pc.defaultStyles[3].strokeWidth = 2
        pc.defaultStyles[3].strokeDashArray = [2,2]
        pc.defaultStyles[3].labelRadius = 1.75
        pc.defaultStyles[3].fontColor = colors.red
        pc.defaultStyles[0].fillColor = colors.darkcyan
        pc.defaultStyles[1].fillColor = colors.blueviolet
        pc.defaultStyles[2].fillColor = colors.blue
        pc.defaultStyles[3].fillColor = colors.cyan
        pc.defaultStyles[4].fillColor = colors.aquamarine
        pc.defaultStyles[5].fillColor = colors.cadetblue
        pc.defaultStyles[6].fillColor = colors.lightcoral

        d.add(pc)
        return d


    def normalizeData(self):
        sum = 0.0
        for number in self.data:
            sum = sum + number

        normData = []
        for number in self.data:
            normData.append(360.0 * number / sum)

        return normData
    

    def makeWedges(self):
        # normalize slice data
        normData = self.normalizeData()

        #labels
        if self.labels is None:
            labels = [''] * len(normData)
        else:
            labels = self.labels
        msg = "Number of labels does not match number of data points!"
        assert len(labels) == len(self.data), msg

        xradius = self.width/2.0
        yradius = self.height/2.0
        centerx = self.x + xradius
        centery = self.y + yradius

        if self.direction == "anticlockwise":
            whichWay = 1
        else:
            whichWay = -1

        g = Group()
        i = 0
        wedgeCount = len(self.defaultStyles)
        
        startAngle = self.startAngle #% 360
        for angle in normData:
            ### ATTENTION: MUST USE i = i % wedgeCount HERE,
            ### OTHERWISE THE NUMBER OF SLICES GETS CHANGED!!!
            i = i % wedgeCount

            endAngle = (startAngle + (angle * whichWay)) #% 360
            if startAngle < endAngle:
                a1 = startAngle
                a2 = endAngle
            elif endAngle < startAngle:
                a1 = endAngle
                a2 = startAngle
            else:  #equal, do not draw
                continue

            wedgeStyle = self.defaultStyles[i]

            # is it a popout?
            cx, cy = centerx, centery
            if wedgeStyle.popout <> 0:
                # pop out the wedge
                averageAngle = (a1+a2)/2.0
                aveAngleRadians = averageAngle * pi/180.0
                popdistance = wedgeStyle.popout
                cx = centerx + popdistance * cos(aveAngleRadians)
                cy = centery + popdistance * sin(aveAngleRadians)

            if len(normData) > 1:
                theWedge = Wedge(cx, cy, xradius, a1, a2, yradius=yradius)
            elif len(normData) == 1:
                theWedge = Ellipse(cx, cy, xradius, yradius)

            theWedge.fillColor = wedgeStyle.fillColor
            theWedge.strokeColor = wedgeStyle.strokeColor
            theWedge.strokeWidth = wedgeStyle.strokeWidth
            theWedge.strokeDashArray = wedgeStyle.strokeDashArray

            g.add(theWedge)
                
            # now draw a label
            if labels[i] <> "":
                averageAngle = (a1+a2)/2.0
                aveAngleRadians = averageAngle*pi/180.0
                labelRadius = wedgeStyle.labelRadius
                labelX = centerx + (0.5 * self.width * cos(aveAngleRadians) * labelRadius)
                labelY = centery + (0.5 * self.height * sin(aveAngleRadians) * labelRadius)
                
                theLabel = String(labelX, labelY, labels[i])
                theLabel.textAnchor = "middle"
                theLabel.fontSize = wedgeStyle.fontSize
                theLabel.fontName = wedgeStyle.fontName
                theLabel.fillColor = wedgeStyle.fontColor

                g.add(theLabel)

            startAngle = endAngle
            i = i + 1

        return g


    def draw(self):
        g = Group()
        g.add(self.makeWedges())
        return g


def sample0a():
    "Make a degenerated pie chart with only one slice."

    d = Drawing(400, 200)

    pc = Pie()
    pc.x = 150
    pc.y = 50
    pc.data = [10]
    pc.labels = ['a']
    pc.defaultStyles.strokeWidth=1#0.5
    
    d.add(pc)

    return d


def sample0b():
    "Make a degenerated pie chart with only one slice."

    d = Drawing(400, 200)

    pc = Pie()
    pc.x = 150
    pc.y = 50
    pc.width = 120
    pc.height = 100
    pc.data = [10]
    pc.labels = ['a']
    pc.defaultStyles.strokeWidth=1#0.5
    
    d.add(pc)

    return d


def sample1():
    "Make a typical pie chart with with one slice treated in a special way."

    d = Drawing(400, 200)

    pc = Pie()
    pc.x = 150
    pc.y = 50
    pc.data = [10, 20, 30, 40, 50, 60]
    pc.labels = ['a', 'b', 'c', 'd', 'e', 'f']

    pc.defaultStyles.strokeWidth=1#0.5
    pc.defaultStyles[3].popout = 20
    pc.defaultStyles[3].strokeWidth = 2
    pc.defaultStyles[3].strokeDashArray = [2,2]
    pc.defaultStyles[3].labelRadius = 1.75
    pc.defaultStyles[3].fontColor = colors.red
    
    d.add(pc)

    return d


def sample2():
    "Make a pie chart with nine slices."

    d = Drawing(400, 200)

    pc = Pie()
    pc.x = 125
    pc.y = 25
    pc.data = [0.31, 0.148, 0.108,
               0.076, 0.033, 0.03,
               0.019, 0.126, 0.15]
    pc.labels = ['1', '2', '3', '4', '5', '6', '7', '8', 'X']

    pc.width = 150
    pc.height = 150
    pc.defaultStyles.strokeWidth=1#0.5

    pc.defaultStyles[0].fillColor = colors.steelblue
    pc.defaultStyles[1].fillColor = colors.thistle
    pc.defaultStyles[2].fillColor = colors.cornflower
    pc.defaultStyles[3].fillColor = colors.lightsteelblue
    pc.defaultStyles[4].fillColor = colors.aquamarine
    pc.defaultStyles[5].fillColor = colors.cadetblue
    pc.defaultStyles[6].fillColor = colors.lightcoral
    pc.defaultStyles[7].fillColor = colors.tan
    pc.defaultStyles[8].fillColor = colors.darkseagreen

    d.add(pc)

    return d


def sample3():
    "Make a pie chart with a very slim slice."

    d = Drawing(400, 200)

    pc = Pie()
    pc.x = 125
    pc.y = 25

    pc.data = [74, 1, 25]

    pc.width = 150
    pc.height = 150
    pc.defaultStyles.strokeWidth=1#0.5
    pc.defaultStyles[0].fillColor = colors.steelblue
    pc.defaultStyles[1].fillColor = colors.thistle
    pc.defaultStyles[2].fillColor = colors.cornflower

    d.add(pc)

    return d


def sample4():
    "Make a pie chart with several very slim slices."

    d = Drawing(400, 200)

    pc = Pie()
    pc.x = 125
    pc.y = 25

    pc.data = [74, 1, 1, 1, 1, 22]

    pc.width = 150
    pc.height = 150
    pc.defaultStyles.strokeWidth=1#0.5
    pc.defaultStyles[0].fillColor = colors.steelblue
    pc.defaultStyles[1].fillColor = colors.thistle
    pc.defaultStyles[2].fillColor = colors.cornflower
    pc.defaultStyles[3].fillColor = colors.lightsteelblue
    pc.defaultStyles[4].fillColor = colors.aquamarine
    pc.defaultStyles[5].fillColor = colors.cadetblue

    d.add(pc)

    return d
