# signsandsymbols.py
# A collection of new widgets
# author: John Precedo (johnp@reportlab.com)

from reportlab.lib import colors
from reportlab.graphics import shapes
from reportlab.graphics.widgetbase import Widget
from reportlab.graphics import renderPDF

"""This file is a collection of widgets.

Widgets include:
- ETriangle (an equilateral triangle),
- RTriangle (a right angled triangle),
- Octagon,
- Crossbox,
- Tickbox,
- SmileyFace,
- StopSign,
- NoEntry,
- NotAllowed (the red roundel from 'no smoking' signs),
- NoSmoking,
- DangerSign (a black exclamation point in a yellow triangle),
- YesNo (returns a tickbox or a crossbox depending on a testvalue),
- FloppyDisk,
- ArrowOne, and
- ArrowTwo

"""


class ETriangle(Widget):
    """This draws an equilateral triangle.

        possible attributes:
        'x', 'y', 'size', 'color', 'strokecolor'

        """

    _attrMap = {
        'x': shapes.isNumber,
        'y': shapes.isNumber,
        'size': shapes.isNumber,
        'color': shapes.isColorOrNone,
        'strokecolor': shapes.isColorOrNone
        }

    def __init__(self):
        self.x = 0
        self.y = 0
        self.size = 100 
        self.color = colors.red
        self.strokecolor = None

    def demo(self):
        D = shapes.Drawing(140, 140)
        et = ETriangle()
        et.x=20
        et.y=20
        et.draw()
        D.add(et)
        labelFontSize = 10
        D.add(shapes.String(et.x+(et.size/2),(et.y-(1.2*labelFontSize)),
                            'Sample ETriangle', fillColor=colors.black, textAnchor='middle',
                            fontSize=labelFontSize))
        return D
     
    def draw(self):
        # general widget bits
        s = self.size  # abbreviate as we will use this a lot 
        g = shapes.Group()
        
        # Triangle specific bits
        ae = s*0.125            #(ae = 'an eighth')
        triangle = shapes.Polygon(points = [
            self.x, self.y,
            self.x+s, self.y,
            self.x+(s/2),self.y+s],
               fillColor = self.color,
               strokeColor = self.strokecolor,
               strokeWidth=s/50)
        g.add(triangle)
        return g

class RTriangle(Widget):
    """This draws a right-angled triangle.

        possible attributes:
        'x', 'y', 'size', 'color', 'strokecolor'

        """

    _attrMap = {
        'x': shapes.isNumber,
        'y': shapes.isNumber,
        'size': shapes.isNumber,
        'color': shapes.isColorOrNone,
        'strokecolor': shapes.isColorOrNone
        }

    def __init__(self):
        self.x = 0
        self.y = 0
        self.size = 100 
        self.color = colors.green
        self.strokecolor = None

    def demo(self):
        D = shapes.Drawing(140, 140)
        et = ETriangle()
        et.x=20
        et.y=20
        et.draw()
        D.add(et)
        labelFontSize = 10
        D.add(shapes.String(et.x+(et.size/2),(et.y-(1.2*labelFontSize)),
                            'Sample RTriangle', fillColor=colors.black, textAnchor='middle',
                            fontSize=labelFontSize))
        return D
     
    def draw(self):
        # general widget bits
        s = self.size  # abbreviate as we will use this a lot 
        g = shapes.Group()
        
        # Triangle specific bits
        ae = s*0.125            #(ae = 'an eighth')
        triangle = shapes.Polygon(points = [
            self.x, self.y,
            self.x+s, self.y,
            self.x,self.y+s],
               fillColor = self.color,
               strokeColor = self.strokecolor,
               strokeWidth=s/50)
        g.add(triangle)
        return g  

class Octagon(Widget):
    """This draws an Octagon.

        possible attributes:
        'x', 'y', 'size', 'color', 'strokecolor'

        """ 

    _attrMap = {
        'x': shapes.isNumber,
        'y': shapes.isNumber,
        'size': shapes.isNumber,
        'color': shapes.isColorOrNone,
        'strokecolor': shapes.isColorOrNone
        }

    def __init__(self):
        self.x = 0
        self.y = 0
        self.size = 100 
        self.color = colors.yellow
        self.strokecolor = None
        
    def demo(self):
        D = shapes.Drawing(140, 140)
        o = Octagon()
        o.x=20
        o.y=20
        o.draw()
        D.add(o)
        labelFontSize = 10
        D.add(shapes.String(o.x+(o.size/2),(o.y-(1.2*labelFontSize)),
                            'Sample Octagon', fillColor=colors.black, textAnchor='middle',
                            fontSize=labelFontSize))
        return D

     
    def draw(self):
        # general widget bits
        s = self.size  # abbreviate as we will use this a lot 
        g = shapes.Group() 
        
        # stop-sign specific bits
        athird=s/3

        octagon = shapes.Polygon(points=[self.x+athird, self.y,
                                              self.x, self.y+athird,
                                              self.x, self.y+(athird*2),
                                              self.x+athird, self.y+s,
                                              self.x+(athird*2), self.y+s,
                                              self.x+s, self.y+(athird*2),
                                              self.x+s, self.y+athird,
                                              self.x+(athird*2), self.y],
                                      strokeColor = self.strokecolor,
                                      fillColor = self.color,
                                      strokeWidth=10)
        g.add(octagon)
        return g

class Crossbox(Widget):
    """This draws a black box with a red cross in it - a 'checkbox'.

        possible attributes:
        'x', 'y', 'size', 'crossColor', 'boxColor', 'crosswidth'

    """ 

    _attrMap = {
        'x': shapes.isNumber,
        'y': shapes.isNumber,
        'size': shapes.isNumber,
        'crossColor': shapes.isColorOrNone,
        'boxColor': shapes.isColorOrNone, 
        'crosswidth': shapes.isNumber 
        }

    def __init__(self):
        self.x = 0
        self.y = 0
        self.size = 100 
        self.crossColor = colors.red
        self.boxColor = colors.black
        self.crosswidth = 10
        
    def demo(self):
        D = shapes.Drawing(140, 140)
        cb = Crossbox()
        cb.x=20
        cb.y=20
        cb.draw()
        D.add(cb)
        labelFontSize = 10
        D.add(shapes.String(cb.x+(cb.size/2),(cb.y-(1.2*labelFontSize)),
                            'Sample Crossbox', fillColor=colors.black, textAnchor='middle',
                            fontSize=labelFontSize))
        return D
     
    def draw(self):
        # general widget bits
        s = self.size  # abbreviate as we will use this a lot 
        g = shapes.Group() 
        
        # crossbox specific bits
        box = shapes.Rect(self.x, self.y, s, s,
               fillColor = None,
               strokeColor = self.boxColor,
               strokeWidth=2)
        g.add(box)
        
        crossLine1 = shapes.Line(self.x+(s*0.15), self.y+(s*0.15), self.x+(s*0.85), self.y+(s*0.85),
               fillColor = self.crossColor,
               strokeColor = self.crossColor,
               strokeWidth = self.crosswidth)
        g.add(crossLine1)
        
        crossLine2 = shapes.Line(self.x+(s*0.15), self.y+(s*0.85), self.x+(s*0.85) ,self.y+(s*0.15),
               fillColor = self.crossColor,
               strokeColor = self.crossColor,
               strokeWidth = self.crosswidth)
        g.add(crossLine2)

        return g


class Tickbox(Widget):
    """This draws a black box with a red tick in it - another 'checkbox'.

        possible attributes:
        'x', 'y', 'size', 'tickColor', 'boxColor', 'tickwidth'

""" 

    _attrMap = {
        'x': shapes.isNumber,
        'y': shapes.isNumber,
        'size': shapes.isNumber,
        'tickColor': shapes.isColorOrNone,
        'boxColor': shapes.isColorOrNone, 
        'tickwidth': shapes.isNumber 
        }

    def __init__(self):
        self.x = 0
        self.y = 0
        self.size = 100 
        self.tickColor = colors.red
        self.boxColor = colors.black
        self.tickwidth = 10
        
    def demo(self):
        D = shapes.Drawing(140, 140)
        tb = Tickbox()
        tb.x=20
        tb.y=20
        tb.draw()
        D.add(tb)
        labelFontSize = 10
        D.add(shapes.String(tb.x+(tb.size/2),(tb.y-(1.2*labelFontSize)),
                            'Sample Tickbox', fillColor=colors.black, textAnchor='middle',
                            fontSize=labelFontSize))
        return D

     
    def draw(self):
        # general widget bits
        s = self.size  # abbreviate as we will use this a lot 
        g = shapes.Group() 
        
        # tickbox specific bits
        box = shapes.Rect(self.x, self.y, s, s,
               fillColor = None,
               strokeColor = self.boxColor,
               strokeWidth=2)
        g.add(box)

        tickLine = shapes.PolyLine(points = [self.x+(s*0.15), self.y+(s*0.35), self.x+(s*0.35), self.y+(s*0.15),
                                             self.x+(s*0.35), self.y+(s*0.15), self.x+(s*0.85) ,self.y+(s*0.85)],
               fillColor = self.tickColor,
               strokeColor = self.tickColor,
               strokeWidth = self.tickwidth)
        g.add(tickLine)

        return g

class SmileyFace(Widget):
    """This draws a classic smiley face.
    
        possible attributes:
        'x', 'y', 'size'

""" 

    _attrMap = {
        'x': shapes.isNumber,
        'y': shapes.isNumber,
        'size': shapes.isNumber,
        }

    def __init__(self):
        self.x = 0
        self.y = 0
        self.size = 100 
        
    def demo(self):
        D = shapes.Drawing(140, 140)
        sf = SmileyFace()
        sf.x=20
        sf.y=20
        sf.draw()
        D.add(sf)
        labelFontSize = 10
        D.add(shapes.String(ne.x+(ne.size/2),(ne.y-(1.2*labelFontSize)),
                            'Sample SmileyFace', fillColor=colors.black, textAnchor='middle',
                            fontSize=labelFontSize))
        return D

     
    def draw(self):
        # general widget bits
        s = self.size  # abbreviate as we will use this a lot 
        g = shapes.Group() 
        
        # SmileyFace specific bits
        outerCircle = shapes.Circle(cx = (self.x+(s/2)), cy = (self.y+(s/2)), r = s/2,
               fillColor = colors.yellow,
               strokeColor = colors.black,
               strokeWidth=s/38)
        g.add(outerCircle)

        leftEye = shapes.Ellipse(self.x+(s/3),self.y+(s/3)*2, s/30, s/10, fillColor=colors.black)
        g.add(leftEye)

        rightEye = shapes.Ellipse(self.x+(s/3)*2, self.y+(s/3)*2, s/30, s/10, fillColor=colors.black)
        g.add(rightEye)

        # calculate a pointslist for the mouth
        # THIS IS A HACK! - don't use if there is a 'shapes.Arc'

        centerx=self.x+(s/2)
        centery=self.y+(s/2)
        radius=s/3
        yradius = radius
        xradius = radius
        startangledegrees=200
        endangledegrees=340
        degreedelta = 1
        pointslist = []
        a = pointslist.append
#        a(centerx); a(centery)
        from math import sin, cos, pi
        degreestoradians = pi/180.0
        radiansdelta = degreedelta*degreestoradians
        startangle = startangledegrees*degreestoradians
        endangle = endangledegrees*degreestoradians
        while endangle<startangle:
              endangle = endangle+2*pi
        angle = startangle
        while angle<endangle:
            x = centerx + cos(angle)*radius
            y = centery + sin(angle)*yradius
            a(x); a(y)
            angle = angle+radiansdelta
        
        # make the mouth
        smile = shapes.PolyLine(pointslist,
               fillColor = colors.black,
               strokeColor = colors.black,
               strokeWidth = s/40)
        g.add(smile)

        return g



class StopSign(Widget):
    """This draws a (British) stop sign.

        possible attributes:
        'x', 'y', 'size'

        """ 

    _attrMap = {
        'x': shapes.isNumber,
        'y': shapes.isNumber,
        'size': shapes.isNumber
        }

    def __init__(self):
        self.x = 0
        self.y = 0
        self.size = 100 
        
    def demo(self):
        D = shapes.Drawing(140, 140)
        ss = StopSign()
        ss.x=20
        ss.y=20
        ss.draw()
        D.add(ss)
        labelFontSize = 10
        D.add(shapes.String(ss.x+(ss.size/2),(ss.y-(1.2*labelFontSize)),
                            'Sample StopSign', fillColor=colors.black, textAnchor='middle',
                            fontSize=labelFontSize))
        return D

     
    def draw(self):
        # general widget bits
        s = self.size  # abbreviate as we will use this a lot 
        g = shapes.Group() 
        
        # stop-sign specific bits
        athird=s/3

        outerOctagon = shapes.Polygon(points=[self.x+athird, self.y,
                                              self.x, self.y+athird,
                                              self.x, self.y+(athird*2),
                                              self.x+athird, self.y+s,
                                              self.x+(athird*2), self.y+s,
                                              self.x+s, self.y+(athird*2),
                                              self.x+s, self.y+athird,
                                              self.x+(athird*2), self.y],
                                      strokeColor = colors.black,
                                      fillColor = None,
                                      strokeWidth=1)
        g.add(outerOctagon)
 
        innerOctagon = shapes.Polygon(points=[self.x+athird+(s/75), self.y+(s/75),
                                              self.x+(s/75), self.y+athird+(s/75),
                                              self.x+(s/75), self.y+(athird*2)-(s/75),
                                              self.x+athird+(s/75), self.y+s-(s/75),
                                              self.x+(athird*2)-(s/75), (self.y+s)-(s/75),
                                              (self.x+s)-(s/75), self.y+(athird*2)-(s/75),
                                              (self.x+s)-(s/75), self.y+athird+(s/75),
                                              self.x+(athird*2)-(s/75), self.y+(s/75)],
                                      strokeColor = None,
                                      fillColor = colors.orangered,
                                      strokeWidth=0)
        g.add(innerOctagon)

        g.add(shapes.String(self.x+(s*0.5),self.y+(s*0.4),
                            'STOP', fillColor=colors.ghostwhite, textAnchor='middle',
                            fontSize=s/3, fontName="Helvetica-Bold"))
 
        return g


class NoEntry(Widget):
    """This draws a (British) No Entry sign - a red circle with a white line on it.
    
        possible attributes:
        'x', 'y', 'size'

        """

    _attrMap = {
        'x': shapes.isNumber,
        'y': shapes.isNumber,
        'size': shapes.isNumber,
        }

    def __init__(self):
        self.x = 0
        self.y = 0
        self.size = 100 
        
    def demo(self):
        D = shapes.Drawing(140, 140)
        ne = NoEntry()
        ne.x=20
        ne.y=20
        ne.draw()
        D.add(ne)
        labelFontSize = 10
        D.add(shapes.String(ne.x+(ne.size/2),(ne.y-(1.2*labelFontSize)),
                            'Sample NoEntry', fillColor=colors.black, textAnchor='middle',
                            fontSize=labelFontSize))
        return D

     
    def draw(self):
        # general widget bits
        s = self.size  # abbreviate as we will use this a lot 
        g = shapes.Group() 
        
        # no-entry-sign specific bits
        outerCircle = shapes.Circle(cx = (self.x+(s/2)), cy = (self.y+(s/2)), r = s/2,
               fillColor = None,
               strokeColor = colors.black,
               strokeWidth=1)
        g.add(outerCircle)

        innerCircle = shapes.Circle(cx = (self.x+(s/2)), cy =(self.y+(s/2)), r = ((s/2)-(s/50)),
               fillColor = colors.orangered,
               strokeColor = None,
               strokeWidth=0)
        g.add(innerCircle)

        innerBar = shapes.Rect(self.x+(s*0.1), self.y+(s*0.4),
                               width=s*0.8,
                               height=s*0.2,
               fillColor = colors.ghostwhite,
               strokeColor = colors.ghostwhite,
               strokeLineCap = 1,
               strokeWidth = 0)
        g.add(innerBar)

        return g

class NotAllowed(Widget):
    """This draws a 'forbidden' roundel (as used in the no-smoking sign).
    
        possible attributes:
        'x', 'y', 'size'

        """

    _attrMap = {
        'x': shapes.isNumber,
        'y': shapes.isNumber,
        'size': shapes.isNumber,
        }

    def __init__(self):
        self.x = 0
        self.y = 0
        self.size = 100 
        
    def demo(self):
        D = shapes.Drawing(140, 140)
        na = NotAllowed()
        na.x=20
        na.y=20
        na.draw()
        D.add(ne)
        labelFontSize = 10
        D.add(shapes.String(ne.x+(ne.size/2),(ne.y-(1.2*labelFontSize)),
                            'Sample NotAllowed', fillColor=colors.black, textAnchor='middle',
                            fontSize=labelFontSize))
        return D

     
    def draw(self):
        # general widget bits
        s = self.size  # abbreviate as we will use this a lot 
        g = shapes.Group() 
        
        # not=allowed specific bits
        outerCircle = shapes.Circle(cx = (self.x+(s/2)), cy = (self.y+(s/2)), r = (s/2)-(s/10),
               fillColor = None,
               strokeColor = colors.red,
               strokeWidth=s/10)
        g.add(outerCircle)
        
        centerx=self.x+s
        centery=self.y+(s/2)-(s/6)
        radius=s-(s/6)
        yradius = radius/2
        xradius = radius/2
        startangledegrees=100
        endangledegrees=-80
        degreedelta = 90
        pointslist = []
        a = pointslist.append
        from math import sin, cos, pi
        degreestoradians = pi/180.0
        radiansdelta = degreedelta*degreestoradians
        startangle = startangledegrees*degreestoradians
        endangle = endangledegrees*degreestoradians
        while endangle<startangle:
              endangle = endangle+2*pi
        angle = startangle
        while angle<endangle:
            x = centerx + cos(angle)*radius
            y = centery + sin(angle)*yradius
            a(x); a(y)
            angle = angle+radiansdelta
        
        crossbar = shapes.PolyLine(pointslist,
               fillColor = colors.red,
               strokeColor = colors.red,
               strokeWidth = s/10)

        g.add(crossbar)

        return g


class NoSmoking(NotAllowed):
    """This draws a no-smoking sign.
    
        possible attributes:
        'x', 'y', 'size'

        """

    _attrMap = {
        'x': shapes.isNumber,
        'y': shapes.isNumber,
        'size': shapes.isNumber,
        }

    def __init__(self):
        self.x = 0
        self.y = 0
        self.size = 100 
        
    def demo(self):
        D = shapes.Drawing(140, 140)
        na = StopSign()
        na.x=20
        na.y=20
        na.draw()
        D.add(ne)
        labelFontSize = 10
        D.add(shapes.String(ne.x+(ne.size/2),(ne.y-(1.2*labelFontSize)),
                            'Sample NoSmoking', fillColor=colors.black, textAnchor='middle',
                            fontSize=labelFontSize))
        return D

     
    def draw(self):
        # general widget bits
        s = self.size  # abbreviate as we will use this a lot 
        g = shapes.Group() 
        
        # no-smoking-sign specific bits
        newx = self.x+(s/2)-(s/3.5)
        newy = self.y+(s/2)-(s/32)
        cigarrette1 = shapes.Rect(x = newx, y = newy, width = (s/2), height =(s/16),
               fillColor = colors.ghostwhite,
               strokeColor = colors.gray,
               strokeWidth=0)
        newx=newx+(s/2)+(s/64)
        g.add(cigarrette1)
        
        
        cigarrette2 = shapes.Rect(x = newx, y = newy, width = (s/80), height =(s/16),
           fillColor = colors.orangered,
           strokeColor = None,
           strokeWidth=0)
        newx= newx+(s/35)
        g.add(cigarrette2)

        cigarrette3 = shapes.Rect(x = newx, y = newy, width = (s/80), height =(s/16),
           fillColor = colors.orangered,
           strokeColor = None,
           strokeWidth=0)
        newx= newx+(s/35)
        g.add(cigarrette3)

        cigarrette4 = shapes.Rect(x = newx, y = newy, width = (s/80), height =(s/16),
           fillColor = colors.orangered,
           strokeColor = None,
           strokeWidth=0)
        newx= newx+(s/35)
        g.add(cigarrette4)
            
        roundel = NotAllowed()
        roundel.draw()
        roundel.x = self.x
        roundel.y = self.y
        roundel.size = self.size
        g.add(roundel)

            

##        cigarrette3 = shapes.Rect(x = newx, y = (self.y+(s/2)-(s/8)), width = (s/64), height =(s/16),
##               fillColor = colors.orangered,
##               strokeColor = None,
##               strokeWidth=0)
##        newx= newx+(s/32)
##        g.add(cigarrette3)


##        cigarrette3 = shapes.Rect(x = ((self.x+(s/2)-(s/4))), y = (self.y+(s/2)-(s/8)), width = (s/2), height =(s/4),
##               fillColor = colors.orangered,
##               strokeColor = Nonegray,
##               strokeWidth=0)
##        g.add(cigarrette1)
##
##        cigarrette4 = shapes.Rect(x = ((self.x+(s/2)-(s/4))), y = (self.y+(s/2)-(s/8)), width = (s/2), height =(s/4),
##               fillColor = colors.orangered,
##               strokeColor = None,
##               strokeWidth=0)
##        g.add(cigarrette1)

        return g


class DangerSign(Widget):
    """This draws a 'danger' sign: a yellow box with a black exclamation point.

        possible attributes:
        'x', 'y', 'size', 'exmarkColor', 'backColor', 'exmarkWidth'

        """

    _attrMap = {
        'x': shapes.isNumber,
        'y': shapes.isNumber,
        'size': shapes.isNumber,
        'exmarkColor': shapes.isColorOrNone,
        'backColor': shapes.isColorOrNone, 
        'exmarkWidth': shapes.isNumber 
        }

    def __init__(self):
        self.x = 0
        self.y = 0
        self.size = 100 
        self.exmarkColor = colors.black
        self.backColor = colors.gold
        self.exmarkWidth = self.size*0.125

    def demo(self):
        D = shapes.Drawing(140, 140)
        ds = DangerSign()
        ds.x=20
        ds.y=20
        ds.draw()
        D.add(ds)
        labelFontSize = 10
        D.add(shapes.String(ds.x+(ds.size/2),(ds.y-(1.2*labelFontSize)),
                            'Sample Dangersign', fillColor=colors.black, textAnchor='middle',
                            fontSize=labelFontSize))
        return D
     
    def draw(self):
        # general widget bits
        s = self.size  # abbreviate as we will use this a lot 
        g = shapes.Group()
        ew = self.exmarkWidth
        ae = s*0.125            #(ae = 'an eighth')
        

        # danger sign specific bits

        ew = self.exmarkWidth
        ae = s*0.125            #(ae = 'an eighth')

        outerTriangle = shapes.Polygon(points = [
            self.x, self.y,
            self.x+s, self.y,
            self.x+(s/2),self.y+s],
               fillColor = None,
               strokeColor = self.exmarkColor,
               strokeWidth=0)
        g.add(outerTriangle)

        innerTriangle = shapes.Polygon(points = [
            self.x+(s/50), self.y+(s/75),
            (self.x+s)-(s/50), self.y+(s/75),
            self.x+(s/2),(self.y+s)-(s/50)],
               fillColor = self.backColor,
               strokeColor = None,
               strokeWidth=0)
        g.add(innerTriangle)
                
        exmark = shapes.Polygon(points=[
            ((self.x+s/2)-ew/2), self.y+ae*2.5,
            ((self.x+s/2)+ew/2), self.y+ae*2.5,
            ((self.x+s/2)+((ew/2))+(ew/6)), self.y+ae*5.5,
            ((self.x+s/2)-((ew/2))-(ew/6)), self.y+ae*5.5],
               fillColor = self.exmarkColor,
               strokeColor = None)
        g.add(exmark)
        
        exdot = shapes.Polygon(points=[
            ((self.x+s/2)-ew/2), self.y+ae,
            ((self.x+s/2)+ew/2), self.y+ae,
            ((self.x+s/2)+ew/2), self.y+ae*2,
            ((self.x+s/2)-ew/2), self.y+ae*2],
               fillColor = self.exmarkColor,
               strokeColor = None)
        g.add(exdot)

        return g


class YesNo(Widget):
    """This widget draw a tickbox or crossbox depending on 'testValue'.

        If this widget is supplied with a 'True' or 1 as a value for
        testValue, it will use the tickbox widget. Otherwise, it will
        produce a crossbox.
    
        possible attributes:
        'x', 'y', 'size', 'tickcolor', 'crosscolor', 'testValue'

"""

    _attrMap = {
        'x': shapes.isNumber,
        'y': shapes.isNumber,
        'tickcolor': shapes.isColor,
        'crosscolor': shapes.isColor,
        'size': shapes.isNumber,
        'testValue': shapes.isBoolean,
        }

    def __init__(self):
        self.x = 0
        self.y = 0
        self.size = 100 
        self.tickcolor = colors.green 
        self.crosscolor = colors.red 
        self.testValue = 1

    def draw(self):
        if self.testValue:
            yn=Tickbox()
            yn.tickColor=self.tickcolor
        else:
            yn=Crossbox()
            yn.crossColor=self.crosscolor
        yn.x=self.x
        yn.y=self.y
        yn.size=self.size
        yn.draw()
        return yn

        
    def demo(self):
        D = shapes.Drawing(140, 140)
        yn = YesNo()
        yn.x = 20
        yn.y = 20
        yn.testValue = 1
        yn.draw()
        D.add(yn)
        labelFontSize = 10
        D.add(shapes.String(cb.x+(cb.size/2),(cb.y-(1.2*labelFontSize)),
                            'Sample YesNo', fillColor=colors.black, textAnchor='middle',
                            fontSize=labelFontSize))
        return D
     
class FloppyDisk(Widget):
    """This widget draws an icon of a floppy disk.

        possible attributes:
        'x', 'y', 'size', 'exmarkColor', 'backColor', 'exmarkWidth'

        """

    _attrMap = {
        'x': shapes.isNumber,
        'y': shapes.isNumber,
        'size': shapes.isNumber,
        'diskColor': shapes.isColor
        }

    def __init__(self):
        self.x = 0
        self.y = 0
        self.size = 100 
        self.diskColor = colors.black

    def demo(self):
        D = shapes.Drawing(140, 140)
        fd = FloppyDisk()
        fd.x=20
        fd.y=20
        fd.draw()
        D.add(ds)
        labelFontSize = 10
        D.add(shapes.String(ds.x+(fd.size/2),(fd.y-(1.2*labelFontSize)),
                            'Sample FloppyDisk', fillColor=colors.black, textAnchor='middle',
                            fontSize=labelFontSize))
        return D
     
    def draw(self):
        # general widget bits
        s = self.size  # abbreviate as we will use this a lot 
        g = shapes.Group()
        

        # floppy disk specific bits
        diskBody = shapes.Rect(x=self.x, y=self.y, width=s, height=s,
               fillColor = self.diskColor,
               strokeColor = None,
               strokeWidth=0)
        g.add(diskBody)

        label = shapes.Rect(x=self.x+(s*0.1), y=(self.y+s)-(s*0.5), width=s*0.8, height=s*0.48,
               fillColor = colors.whitesmoke,
               strokeColor = None,
               strokeWidth=0)
        g.add(label)

        labelsplash = shapes.Rect(x=self.x+(s*0.1), y=(self.y+s)-(s*0.1), width=s*0.8, height=s*0.08,
               fillColor = colors.royalblue,
               strokeColor = None,
               strokeWidth=0)
        g.add(labelsplash)


        line1 = shapes.Line(x1=self.x+(s*0.15), y1=self.y+(0.6*s), x2=self.x+(s*0.85), y2=self.y+(0.6*s),
               fillColor = colors.black,
               strokeColor = colors.black,
               strokeWidth=0)
        g.add(line1)

        line2 = shapes.Line(x1=self.x+(s*0.15), y1=self.y+(0.7*s), x2=self.x+(s*0.85), y2=self.y+(0.7*s),
               fillColor = colors.black,
               strokeColor = colors.black,
               strokeWidth=0)
        g.add(line2)

        line3 = shapes.Line(x1=self.x+(s*0.15), y1=self.y+(0.8*s), x2=self.x+(s*0.85), y2=self.y+(0.8*s),
               fillColor = colors.black,
               strokeColor = colors.black,
               strokeWidth=0)
        g.add(line3)

        metalcover = shapes.Rect(x=self.x+(s*0.2), y=(self.y)-(s*0.01), width=s*0.5, height=s*0.35,
               fillColor = colors.silver,
               strokeColor = None,
               strokeWidth=0)
        g.add(metalcover)

        coverslot = shapes.Rect(x=self.x+(s*0.28), y=(self.y)+(s*0.03), width=s*0.12, height=s*0.28,
               fillColor = self.diskColor,
               strokeColor = None,
               strokeWidth=0)
        g.add(coverslot)

        return g

class ArrowOne(Widget):
    """This widget draws an arrow.

        possible attributes:
        'x', 'y', 'size', 'color'

        """

    _attrMap = {
        'x': shapes.isNumber,
        'y': shapes.isNumber,
        'size': shapes.isNumber,
        'color': shapes.isColor
        }

    def __init__(self):
        self.x = 0
        self.y = 0
        self.size = 100 
        self.color = colors.red

    def demo(self):
        D = shapes.Drawing(140, 140)
        a1 = ArrowOne()
        a1.x=20
        a1.y=20
        a1.draw()
        D.add(a1)
        labelFontSize = 10
        D.add(shapes.String(a1.x+(a1.size/2),(a1.y-(1.2*labelFontSize)),
                            'Sample ArrowOne', fillColor=colors.black, textAnchor='middle',
                            fontSize=labelFontSize))
        return D
     
    def draw(self):
        # general widget bits
        s = self.size  # abbreviate as we will use this a lot 
        g = shapes.Group()
        

        # arrow specific bits
        body = shapes.Rect(x=self.x, y=(self.y+(s/2))-(s/6), width=2*(s/3), height=(s/3),
               fillColor = self.color,
               strokeColor = None,
               strokeWidth=0)
        g.add(body)

        head = shapes.Polygon(points = [self.x+(3*(s/6)), (self.y+(s/2)),
                                       self.x+(3*(s/6)), self.y+8*(s/10),
                                       self.x+s, self.y+(s/2),
                                       self.x+(3*(s/6)), self.y+2*(s/10)],
               fillColor = self.color,
               strokeColor = None,
               strokeWidth=0)
        g.add(head)

        return g

class ArrowTwo(Widget):
    """This widget draws an arrow.

        possible attributes:
        'x', 'y', 'size', 'color'

        """

    _attrMap = {
        'x': shapes.isNumber,
        'y': shapes.isNumber,
        'size': shapes.isNumber,
        'color': shapes.isColor
        }

    def __init__(self):
        self.x = 0
        self.y = 0
        self.size = 100 
        self.color = colors.blue

    def demo(self):
        D = shapes.Drawing(140, 140)
        a2 = ArrowOne()
        a2.x=20
        a2.y=20
        a2.draw()
        D.add(a2)
        labelFontSize = 10
        D.add(shapes.String(a1.x+(a1.size/2),(a1.y-(1.2*labelFontSize)),
                            'Sample ArrowTwo', fillColor=colors.black, textAnchor='middle',
                            fontSize=labelFontSize))
        return D
     
    def draw(self):
        # general widget bits
        s = self.size  # abbreviate as we will use this a lot 
        g = shapes.Group()
        

        # arrow specific bits
        body = shapes.Rect(x=self.x, y=(self.y+(s/2))-(s/24), width=9*(s/10), height=(s/12),
               fillColor = self.color,
               strokeColor = None,
               strokeWidth=0)
        g.add(body)

        head = shapes.Polygon(points = [self.x+(2.5*(s/3)), (self.y+(s/2)),
                                       self.x+(4*(s/6)), self.y+4*(s/6),
                                       self.x+s, self.y+(s/2),
                                       self.x+(4*(s/6)), self.y+2*(s/6)],
               fillColor = self.color,
               strokeColor = None,
               strokeWidth=0)
        g.add(head)

        return g



    
if __name__=='__main__':
    labelFontSize = 10
    D = shapes.Drawing(450,650)
    cb = Crossbox()
    cb.x = 20
    cb.y = 530
    cb.demo()
    D.add(cb)
    D.add(shapes.String(cb.x+(cb.size/2),(cb.y-(1.2*labelFontSize)),
                            'Sample Crossbox', fillColor=colors.black, textAnchor='middle',
                            fontSize=labelFontSize))
    tb = Tickbox()
    tb.x = 170
    tb.y = 530
    tb.demo()
    D.add(tb)
    D.add(shapes.String(tb.x+(tb.size/2),(tb.y-(1.2*labelFontSize)),
                            'Sample Tickbox', fillColor=colors.black, textAnchor='middle',
                            fontSize=labelFontSize))


    yn = YesNo()
    yn.x = 320
    yn.y = 530
    yn.demo()
    D.add(yn)
    D.add(shapes.String(yn.x+(tb.size/2),(yn.y-(1.2*labelFontSize)),
                            'Sample YesNo *', fillColor=colors.black, textAnchor='middle',
                            fontSize=labelFontSize))
    D.add(shapes.String(130,6,
                            "(The 'YesNo' widget returns a tickbox if testvalue=1, and a crossbox if testvalue=0)", fillColor=colors.black, textAnchor='middle',
                            fontSize=labelFontSize*0.75))


    ss = StopSign()
    ss.x = 20
    ss.y = 400
    ss.demo()
    D.add(ss)
    D.add(shapes.String(ss.x+(ss.size/2), ss.y-(1.2*labelFontSize),
                            'Sample StopSign', fillColor=colors.black, textAnchor='middle',
                            fontSize=labelFontSize))

    ne = NoEntry()
    ne.x = 170
    ne.y = 400
    ne.demo()
    D.add(ne)
    D.add(shapes.String(ne.x+(ne.size/2),(ne.y-(1.2*labelFontSize)),
                            'Sample NoEntry', fillColor=colors.black, textAnchor='middle',
                            fontSize=labelFontSize))

    sf = SmileyFace()
    sf.x = 320
    sf.y = 400
    sf.demo()
    D.add(sf)
    D.add(shapes.String(sf.x+(sf.size/2),(sf.y-(1.2*labelFontSize)),
                            'Sample SmileyFace', fillColor=colors.black, textAnchor='middle',
                            fontSize=labelFontSize))

    ds = DangerSign()
    ds.x = 20
    ds.y = 270
    ds.demo()
    D.add(ds)
    D.add(shapes.String(ds.x+(ds.size/2),(ds.y-(1.2*labelFontSize)),
                            'Sample DangerSign', fillColor=colors.black, textAnchor='middle',
                            fontSize=labelFontSize))    
    
    na = NotAllowed()
    na.x = 170
    na.y = 270
    na.demo()
    D.add(na)
    D.add(shapes.String(na.x+(na.size/2),(na.y-(1.2*labelFontSize)),
                            'Sample NotAllowed', fillColor=colors.black, textAnchor='middle',
                            fontSize=labelFontSize))    

    ns = NoSmoking()
    ns.x = 320
    ns.y = 270
    ns.demo()
    D.add(ns)
    D.add(shapes.String(ns.x+(ns.size/2),(ns.y-(1.2*labelFontSize)),
                            'Sample NoSmoking', fillColor=colors.black, textAnchor='middle',
                            fontSize=labelFontSize))    

    a1 = ArrowOne()
    a1.x = 20
    a1.y = 140
    a1.demo()
    D.add(a1)
    D.add(shapes.String(a1.x+(a1.size/2),(a1.y-(1.2*labelFontSize)),
                            'Sample ArrowOne', fillColor=colors.black, textAnchor='middle',
                            fontSize=labelFontSize)) 

    a2 = ArrowTwo()
    a2.x = 170
    a2.y = 140
    a2.demo()
    D.add(a2)
    D.add(shapes.String(a2.x+(a2.size/2),(a2.y-(1.2*labelFontSize)),
                            'Sample ArrowTwo', fillColor=colors.black, textAnchor='middle',
                            fontSize=labelFontSize)) 

    fd = FloppyDisk()
    fd.x = 320
    fd.y = 140
    fd.demo()
    D.add(fd)
    D.add(shapes.String(fd.x+(fd.size/2),(fd.y-(1.2*labelFontSize)),
                            'Sample FloppyDisk', fillColor=colors.black, textAnchor='middle',
                            fontSize=labelFontSize)) 

    renderPDF.drawToFile(D, 'jwidgets_sample.pdf', 'Example Widgets (jwidgets.py)')
    print 'wrote file: jwidgets_sample.pdf'
