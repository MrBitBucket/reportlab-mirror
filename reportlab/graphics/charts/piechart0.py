# experimental pie chart script

from reportlab.graphics.widgetbase import Widget, Face
from reportlab.graphics.shapes import *
from reportlab.graphics import renderPDF
from reportlab.lib import colors
from reportlab.pdfgen.canvas import Canvas
import math

class Pie0(Widget):
    """This is the pie which appears in the middle of a pie chart.
    It does NOT include legends, titles and other furniture.
    The rectangle is the 'bounding box' for the circle of
    ellipse; if one uses exploded slices or labels, they
    will typically stick out from the definign rectangle."""
    
    #there is no design at all between this color choice;
    # we need a palette with some reasoning behind it.
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
        'startAngle':isNumber,
        'direction': lambda x: x in ['clockwise','anticlockwise'],
        'popouts': lambda x: type(x) == type({}) and isListOfNumbers(x.keys()) and isListOfNumbers(x.values()),
        'strokeColor':isColorOrNone,
        'strokeWidth':isNumber
        }
    def __init__(self):
        self.x = 0
        self.y = 0
        self.width = 100
        self.height = 100
        self.data = [1]
        self.startAngle = 90
        self.direction = "clockwise"
        self.popouts = {}
        self.strokeColor = colors.black
        self.strokeWidth = 0
        
                     
    def draw(self):
        # normalize slice data
        sum = 0.0
        for number in self.data:
            sum = sum + number
        normData = []
        for number in self.data:
            normData.append(360.0 * number / sum)
        
        
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
            if self.popouts.has_key(i):
                # pop out the wedge
                averageAngle = (a1+a2)/2.0
                aveAngleRadians = averageAngle*math.pi/180.0
                popdistance = self.popouts[i]
                cx = centerx + popdistance * math.cos(aveAngleRadians)
                cy = centery + popdistance * math.sin(aveAngleRadians)

                
            theWedge = Wedge(cx,
                             cy,
                             xradius,
                             a1,
                             a2,
                             yradius=yradius)
            theWedge.fillColor = thisWedgeColor
            theWedge.strokeColor = self.strokeColor
            theWedge.strokeWidth = self.strokeWidth

            startAngle = endAngle
            i = i + 1

            g.add(theWedge)
        return g

 

if __name__=='__main__':
    d = Drawing(400,200)

    pc = Pie0()
    pc.data = [10,20,30,40,50,60]
    pc.popouts[0] = 5
    pc.dumpProperties()
    d.add(pc, 'pie')
    
    c = Canvas('piechart0.pdf')
    d.drawOn(c, 100, 400)
    c.save()
    print 'saved piechart0.pdf'
    