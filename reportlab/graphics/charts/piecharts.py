#copyright ReportLab Inc. 2000-2001
#see license.txt for license details
#history http://cvs.sourceforge.net/cgi-bin/cvsweb.cgi/reportlab/graphics/charts/piecharts.py?cvsroot=reportlab
#$Header: /tmp/reportlab/reportlab/graphics/charts/piecharts.py,v 1.2 2001/04/05 09:30:11 rgbecker Exp $
# experimental pie chart script.  Two types of pie - one is a monolithic
#widget with all top-level properties, the other delegates most stuff to
#a wedges collection whic lets you customize the group or every individual
#wedge.

"""Basic Pie Chart class.

This permits you to customize and pop out individual wedges;
supports elliptical and circular pies."""

import math

from reportlab.graphics.widgetbase import Widget, TypedPropertyCollection
from reportlab.graphics.shapes import *
from reportlab.graphics import renderPDF
from reportlab.lib import colors
from reportlab.pdfgen.canvas import Canvas


class WedgeFormatter(Widget):
    """This holds descriptive information about the wedges in a pie chart.
    
    It is not to be confused with the 'wedge itself'; this just holds
    a recipe for how to format one, and does not allow you to hack the
    angles.  It can format a genuine Wedge object for you with its
    format method. """
    _attrMap = {
        'strokeWidth':isNumber,
        'strokeColor':isColorOrNone,
        'strokeDashArray':isListOfNumbersOrNone,
        'popout':isNumber,
        'fontName':isString,
        'fontSize':isNumber,
        'fontColor':isColorOrNone,
        'labelRadius':isNumber
        }

    def __init__(self):
        self.strokeWidth = 0
        self.strokeColor = STATE_DEFAULTS["strokeColor"]
        self.strokeDashArray = STATE_DEFAULTS["strokeDashArray"]
        self.popout = 0
        self.fontName = STATE_DEFAULTS["fontName"]
        self.fontSize = STATE_DEFAULTS["fontSize"]
        self.fontColor = STATE_DEFAULTS["fillColor"]
        self.labelRadius = 1.2


class Pie(Widget):
    defaultColors = [colors.darkcyan,
                     colors.blueviolet,
                     colors.blue,
                     colors.cyan]

    _attrMap = {
        'x':isNumber,
        'y':isNumber,
        'width':isNumber,
        'height':isNumber,
        'data':isListOfNumbers,
        'labels':isListOfStringsOrNone,
        'startAngle':isNumber,
        'direction': lambda x: x in ['clockwise','anticlockwise'],
        'wedges':None,   # could be improved,
        'defaultColors':SequenceOf(isColor)
        }
    
    def __init__(self):
        self.x = 0
        self.y = 0
        self.width = 100
        self.height = 100
        self.data = [1]
        self.labels = None  # or list of strings
        self.startAngle = 90
        self.direction = "clockwise"
        
        self.wedges = TypedPropertyCollection(WedgeFormatter)
        # no need to change the defaults for a WedgeFormatter; if we did,
        ## we would do e.g.
        #self.wedges.strokeColor = colors.blueviolet
        

    def demo(self):
        d = Drawing(200, 100)
        pc = Pie()
        pc.x = 50
        pc.y = 10
        pc.width = 100
        pc.height = 80
        pc.data = [10,20,30,40,50,60]
        pc.labels = ['a','b','c','d','e','f']
        pc.wedges.strokeWidth=0.5
        pc.wedges[3].popout = 10
        pc.wedges[3].strokeWidth = 2
        pc.wedges[3].strokeDashArray = [2,2]
        pc.wedges[3].labelRadius = 1.75
        pc.wedges[3].fontColor = colors.red
        d.add(pc)
        return d


    def draw(self):
        # normalize slice data
        sum = 0.0
        for number in self.data:
            sum = sum + number
        normData = []
        for number in self.data:
            normData.append(360.0 * number / sum)

        #labels
        if self.labels is None:
            labels = [''] * len(normData)
        else:
            labels = self.labels
        assert len(labels) == len(self.data), "Number of labels does not match number of data points!"
        
        xradius = self.width/2.0
        yradius = self.height/2.0
        centerx = self.x + xradius
        centery = self.y + yradius

        if self.direction == "anticlockwise":
            whichWay = 1
        else:
            whichWay = -1
        i = 0
        colorCount = len(self.defaultColors)
        
        g = Group()
        startAngle = self.startAngle #% 360
        for angle in normData:
            thisWedgeColor = self.defaultColors[i % colorCount]
            endAngle = (startAngle + (angle * whichWay)) #% 360
            if startAngle < endAngle:
                a1 = startAngle
                a2 = endAngle
            elif endAngle < startAngle:
                a1 = endAngle
                a2 = startAngle
            else:  #equal, do not draw
                continue

            # is it a popout?
            cx, cy = centerx, centery
            if self.wedges[i].popout <> 0:
                # pop out the wedge
                averageAngle = (a1+a2)/2.0
                aveAngleRadians = averageAngle*math.pi/180.0
                popdistance = self.wedges[i].popout
                cx = centerx + popdistance * math.cos(aveAngleRadians)
                cy = centery + popdistance * math.sin(aveAngleRadians)

            theWedge = Wedge(cx,
                             cy,
                             xradius,
                             a1,
                             a2,
                             yradius=yradius)
            theWedge.fillColor = thisWedgeColor
            theWedge.strokeColor = self.wedges[i].strokeColor
            theWedge.strokeWidth = self.wedges[i].strokeWidth
            theWedge.strokeDashArray = self.wedges[i].strokeDashArray
            g.add(theWedge)
            # now draw a label
            if labels[i] <> "":
                averageAngle = (a1+a2)/2.0
                aveAngleRadians = averageAngle*math.pi/180.0
                labelX = centerx + (0.5 * self.width * math.cos(aveAngleRadians) * self.wedges[i].labelRadius)
                labelY = centery + (0.5 * self.height * math.sin(aveAngleRadians) * self.wedges[i].labelRadius)
                
                theLabel = String(labelX, labelY, labels[i])
                theLabel.textAnchor = "middle"
                theLabel.fontSize = self.wedges[i].fontSize
                theLabel.fontName = self.wedges[i].fontName
                theLabel.fillColor = self.wedges[i].fontColor

                g.add(theLabel)
                
            startAngle = endAngle
            i = i + 1

        return g


def test():
    d = Drawing(400, 200)
    pc = Pie()
    pc.x = 150
    pc.y = 50
    pc.data = [10,20,30,40,50,60]
    pc.labels = ['a','b','c','d','e','f']
    pc.wedges.strokeWidth=0.5
    pc.wedges[3].popout = 20
    pc.wedges[3].strokeWidth = 2
    pc.wedges[3].strokeDashArray = [2,2]
    pc.wedges[3].labelRadius = 1.75
    pc.wedges[3].fontColor = colors.red
    
    d.add(pc)

    d.drawOn(c, 100, 200)

    c.setFont('Times-Roman', 20)
    c.drawString(100, 420, "Pie chart with wedges collection")
    c.setFont('Times-Roman', 12)
    c.drawString(100, 405, "Allows customisation of individual slices (but not their angles!)")
    
    c.save()
    print 'saved piechart.pdf'


if __name__=='__main__':
    test()        
