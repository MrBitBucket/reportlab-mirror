#copyright ReportLab Inc. 2000-2001
#see license.txt for license details
#history http://cvs.sourceforge.net/cgi-bin/cvsweb.cgi/reportlab/graphics/widgets/signsandsymbols.py?cvsroot=reportlab
#$Header: /tmp/reportlab/reportlab/graphics/widgets/signsandsymbols.py,v 1.10 2001/05/10 08:41:11 dinu_gherman Exp $
# signsandsymbols.py
# A collection of new widgets
# author: John Precedo (johnp@reportlab.com)

"""This file is a collection of widgets to produce some common signs and symbols.

Widgets include:
- ETriangle0 (an equilateral triangle),
- RTriangle0 (a right angled triangle),
- Octagon0,
- Crossbox0,
- Tickbox0,
- SmileyFace0,
- StopSign0,
- NoEntry0,
- NotAllowed0 (the red roundel from 'no smoking' signs),
- NoSmoking0,
- DangerSign0 (a black exclamation point in a yellow triangle),
- YesNo0 (returns a tickbox or a crossbox depending on a testvalue),
- FloppyDisk0,
- ArrowOne0, and
- ArrowTwo0

"""

from reportlab.lib import colors
from reportlab.lib.validators import *
from reportlab.graphics import shapes
from reportlab.graphics.widgetbase import Widget
from reportlab.graphics import renderPDF


class ETriangle0(Widget):
    """This draws an equilateral triangle.

        possible attributes:
        'x', 'y', 'size', 'color', 'strokecolor'

        """

    _attrMap = {
        'x': isNumber,
        'y': isNumber,
        'size': isNumber,
        'color': isColorOrNone,
        'strokecolor': isColorOrNone
        }

    def __init__(self):
        self.x = 0
        self.y = 0
        self.size = 100 
        self.color = colors.red
        self.strokecolor = None

    def demo(self):
        D = shapes.Drawing(200, 100)
        et = ETriangle0()
        et.x=50
        et.y=0
        et.draw()
        D.add(et)
        labelFontSize = 10
        D.add(shapes.String(et.x+(et.size/2),(et.y-(1.2*labelFontSize)),
                            self.__class__.__name__, fillColor=colors.black, textAnchor='middle',
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
               strokeWidth=s/50.)
        g.add(triangle)
        return g

class RTriangle0(Widget):
    """This draws a right-angled triangle.

        possible attributes:
        'x', 'y', 'size', 'color', 'strokecolor'

        """

    _attrMap = {
        'x': isNumber,
        'y': isNumber,
        'size': isNumber,
        'color': isColorOrNone,
        'strokecolor': isColorOrNone
        }

    def __init__(self):
        self.x = 0
        self.y = 0
        self.size = 100 
        self.color = colors.green
        self.strokecolor = None

    def demo(self):
        D = shapes.Drawing(200, 100)
        et = RTriangle0()
        et.x=50
        et.y=0
        et.draw()
        D.add(et)
        labelFontSize = 10
        D.add(shapes.String(et.x+(et.size/2),(et.y-(1.2*labelFontSize)),
                            self.__class__.__name__, fillColor=colors.black, textAnchor='middle',
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
               strokeWidth=s/50.)
        g.add(triangle)
        return g  

class Octagon0(Widget):
    """This widget draws an Octagon.

        possible attributes:
        'x', 'y', 'size', 'color', 'strokecolor'

        """ 

    _attrMap = {
        'x': isNumber,
        'y': isNumber,
        'size': isNumber,
        'color': isColorOrNone,
        'strokecolor': isColorOrNone
        }

    def __init__(self):
        self.x = 0
        self.y = 0
        self.size = 100 
        self.color = colors.yellow
        self.strokecolor = None
        
    def demo(self):
        D = shapes.Drawing(200, 100)
        o = Octagon0()
        o.x=50
        o.y=0
        o.draw()
        D.add(o)
        labelFontSize = 10
        D.add(shapes.String(o.x+(o.size/2),(o.y-(1.2*labelFontSize)),
                            self.__class__.__name__, fillColor=colors.black, textAnchor='middle',
                            fontSize=labelFontSize))
        return D

     
    def draw(self):
        # general widget bits
        s = self.size  # abbreviate as we will use this a lot 
        g = shapes.Group() 
        
        # Octagon specific bits
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

class Crossbox0(Widget):
    """This draws a black box with a red cross in it - a 'checkbox'.

        possible attributes:
        'x', 'y', 'size', 'crossColor', 'boxColor', 'crosswidth'

    """ 

    _attrMap = {
        'x': isNumber,
        'y': isNumber,
        'size': isNumber,
        'crossColor': isColorOrNone,
        'boxColor': isColorOrNone, 
        'crosswidth': isNumber 
        }

    def __init__(self):
        self.x = 0
        self.y = 0
        self.size = 100 
        self.crossColor = colors.red
        self.boxColor = colors.black
        self.crosswidth = 10
        
    def demo(self):
        D = shapes.Drawing(200, 100)
        labelFontSize = 10
        cb = Crossbox0()
        cb.x=50
        cb.y=0
        cb.draw()
        D.add(cb)
        D.add(shapes.String(cb.x+(cb.size/2),(cb.y-(1.2*labelFontSize)),
                            self.__class__.__name__, fillColor=colors.black, textAnchor='middle',
                            fontSize=labelFontSize))
        return D
     
    def draw(self):
        # general widget bits
        s = self.size  # abbreviate as we will use this a lot 
        g = shapes.Group() 
        
        # crossbox specific bits
        box = shapes.Rect(self.x+1, self.y+1, s-2, s-2,
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


class Tickbox0(Widget):
    """This draws a black box with a red tick in it - another 'checkbox'.

        possible attributes:
        'x', 'y', 'size', 'tickColor', 'boxColor', 'tickwidth'

""" 

    _attrMap = {
        'x': isNumber,
        'y': isNumber,
        'size': isNumber,
        'tickColor': isColorOrNone,
        'boxColor': isColorOrNone, 
        'tickwidth': isNumber 
        }

    def __init__(self):
        self.x = 0
        self.y = 0
        self.size = 100 
        self.tickColor = colors.red
        self.boxColor = colors.black
        self.tickwidth = 10
        
    def demo(self):
        D = shapes.Drawing(200, 100)
        tb = Tickbox0()
        tb.x=50
        tb.y=0
        tb.draw()
        D.add(tb)
        labelFontSize = 10
        D.add(shapes.String(tb.x+(tb.size/2),(tb.y-(1.2*labelFontSize)),
                            self.__class__.__name__, fillColor=colors.black, textAnchor='middle',
                            fontSize=labelFontSize))
        return D

     
    def draw(self):
        # general widget bits
        s = self.size  # abbreviate as we will use this a lot 
        g = shapes.Group() 
        
        # tickbox specific bits
        box = shapes.Rect(self.x+1, self.y+1, s-2, s-2,
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

class SmileyFace0(Widget):
    """This draws a classic smiley face.
    
        possible attributes:
        'x', 'y', 'size', 'color'

""" 

    _attrMap = {
        'x': isNumber,
        'y': isNumber,
        'size': isNumber,
        'color': isColor
        }

    def __init__(self):
        self.x = 0
        self.y = 0
        self.size = 100 
        self.color = colors.yellow 
        
    def demo(self):
        D = shapes.Drawing(200, 100)
        sf = SmileyFace0()
        sf.x=50
        sf.y=0
        sf.draw()
        D.add(sf)
        labelFontSize = 10
        D.add(shapes.String(sf.x+(sf.size/2),(sf.y-(1.2*labelFontSize)),
                            self.__class__.__name__, fillColor=colors.black, textAnchor='middle',
                            fontSize=labelFontSize))
        return D

     
    def draw(self):
        # general widget bits
        s = self.size  # abbreviate as we will use this a lot 
        g = shapes.Group() 
        
        # SmileyFace specific bits
        outerCircle = shapes.Circle(cx = (self.x+(s/2)), cy = (self.y+(s/2)), r = s/2,
               fillColor = self.color,
               strokeColor = colors.black,
               strokeWidth=s/38.)
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
               strokeWidth = s/40.)
        g.add(smile)

        return g



class StopSign0(Widget):
    """This draws a (British) stop sign.

        possible attributes:
        'x', 'y', 'size'

        """ 

    _attrMap = {
        'x': isNumber,
        'y': isNumber,
        'size': isNumber
        }

    def __init__(self):
        self.x = 0
        self.y = 0
        self.size = 100 
        
    def demo(self):
        D = shapes.Drawing(200, 100)
        ss = StopSign0()
        ss.x=50
        ss.y=0
        ss.draw()
        D.add(ss)
        labelFontSize = 10
        D.add(shapes.String(ss.x+(ss.size/2),(ss.y-(1.2*labelFontSize)),
                            self.__class__.__name__, fillColor=colors.black, textAnchor='middle',
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


class NoEntry0(Widget):
    """This draws a (British) No Entry sign - a red circle with a white line on it.
    
        possible attributes:
        'x', 'y', 'size'

        """

    _attrMap = {
        'x': isNumber,
        'y': isNumber,
        'size': isNumber,
        }

    def __init__(self):
        self.x = 0
        self.y = 0
        self.size = 100 
        
    def demo(self):
        D = shapes.Drawing(200, 100)
        ne = NoEntry0()
        ne.x=50
        ne.y=0
        ne.draw()
        D.add(ne)
        labelFontSize = 10
        D.add(shapes.String(ne.x+(ne.size/2),(ne.y-(1.2*labelFontSize)),
                            self.__class__.__name__, fillColor=colors.black, textAnchor='middle',
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

class NotAllowed0(Widget):
    """This draws a 'forbidden' roundel (as used in the no-smoking sign).
    
        possible attributes:
        'x', 'y', 'size'

        """

    _attrMap = {
        'x': isNumber,
        'y': isNumber,
        'size': isNumber,
        }

    def __init__(self):
        self.x = 0
        self.y = 0
        self.size = 100 
        
    def demo(self):
        D = shapes.Drawing(200, 100)
        na = NotAllowed0()
        na.x=50
        na.y=0
        na.draw()
        D.add(na)
        labelFontSize = 10
        D.add(shapes.String(na.x+(na.size/2),(na.y-(1.2*labelFontSize)),
                            self.__class__.__name__, fillColor=colors.black, textAnchor='middle',
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
               strokeWidth=s/10.)
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
               strokeWidth = s/10.)

        g.add(crossbar)

        return g


class NoSmoking0(NotAllowed0):
    """This draws a no-smoking sign.
    
        possible attributes:
        'x', 'y', 'size'

        """

    _attrMap = {
        'x': isNumber,
        'y': isNumber,
        'size': isNumber,
        }

    def __init__(self):
        self.x = 0
        self.y = 0
        self.size = 100 
        
    def demo(self):
        D = shapes.Drawing(200, 100)
        ns = NoSmoking0()
        ns.x=50
        ns.y=0
        ns.draw()
        D.add(ns)
        labelFontSize = 10
        D.add(shapes.String(ns.x+(ns.size/2),(ns.y-(1.2*labelFontSize)),
                            self.__class__.__name__, fillColor=colors.black, textAnchor='middle',
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
            
        roundel = NotAllowed0()
        roundel.draw()
        roundel.x = self.x
        roundel.y = self.y
        roundel.size = self.size
        g.add(roundel)

        return g


class DangerSign0(Widget):
    """This draws a 'danger' sign: a yellow box with a black exclamation point.

        possible attributes:
        'x', 'y', 'size', 'exmarkColor', 'backColor', 'exmarkWidth'

        """

    _attrMap = {
        'x': isNumber,
        'y': isNumber,
        'size': isNumber,
        'exmarkColor': isColorOrNone,
        'backColor': isColorOrNone, 
        'exmarkWidth': isNumber 
        }

    def __init__(self):
        self.x = 0
        self.y = 0
        self.size = 100 
        self.exmarkColor = colors.black
        self.backColor = colors.gold
        self.exmarkWidth = self.size*0.125

    def demo(self):
        D = shapes.Drawing(200, 100)
        ds = DangerSign0()
        ds.x=50
        ds.y=0
        ds.draw()
        D.add(ds)
        labelFontSize = 10
        D.add(shapes.String(ds.x+(ds.size/2),(ds.y-(1.2*labelFontSize)),
                            self.__class__.__name__, fillColor=colors.black, textAnchor='middle',
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


class YesNo0(Widget):
    """This widget draw a tickbox or crossbox depending on 'testValue'.

        If this widget is supplied with a 'True' or 1 as a value for
        testValue, it will use the tickbox widget. Otherwise, it will
        produce a crossbox.
    
        possible attributes:
        'x', 'y', 'size', 'tickcolor', 'crosscolor', 'testValue'

"""

    _attrMap = {
        'x': isNumber,
        'y': isNumber,
        'tickcolor': isColor,
        'crosscolor': isColor,
        'size': isNumber,
        'testValue': isBoolean,
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
            yn=Tickbox0()
            yn.tickColor=self.tickcolor
        else:
            yn=Crossbox0()
            yn.crossColor=self.crosscolor
        yn.x=self.x
        yn.y=self.y
        yn.size=self.size
        yn.draw()
        return yn

        
    def demo(self):
        D = shapes.Drawing(200, 100)
        yn = YesNo0()
        yn.x = 15
        yn.y = 25
        yn.size = 70
        yn.testValue = 0
        yn.draw()
        D.add(yn)
        yn2 = YesNo0()
        yn2.x = 120
        yn2.y = 25
        yn2.size = 70
        yn2.testValue = 1
        yn2.draw()
        D.add(yn2)
        labelFontSize = 8
        D.add(shapes.String(yn.x+(yn.size/2),(yn.y-(1.2*labelFontSize)),
                            'testValue=0', fillColor=colors.black, textAnchor='middle',
                            fontSize=labelFontSize))
        D.add(shapes.String(yn2.x+(yn2.size/2),(yn2.y-(1.2*labelFontSize)),
                            'testValue=1', fillColor=colors.black, textAnchor='middle',
                            fontSize=labelFontSize))
        labelFontSize = 10
        D.add(shapes.String(yn.x+85,(yn.y-20),
                            self.__class__.__name__, fillColor=colors.black, textAnchor='middle',
                            fontSize=labelFontSize))
        return D
     
class FloppyDisk0(Widget):
    """This widget draws an icon of a floppy disk.

        possible attributes:
        'x', 'y', 'size', 'diskcolor'

        """

    _attrMap = {
        'x': isNumber,
        'y': isNumber,
        'size': isNumber,
        'diskColor': isColor
        }

    def __init__(self):
        self.x = 0
        self.y = 0
        self.size = 100 
        self.diskColor = colors.black

    def demo(self):
        D = shapes.Drawing(200, 100)
        fd = FloppyDisk0()
        fd.x=50
        fd.y=0
        fd.draw()
        D.add(fd)
        labelFontSize = 10
        D.add(shapes.String(fd.x+(fd.size/2),(fd.y-(1.2*labelFontSize)),
                            self.__class__.__name__, fillColor=colors.black, textAnchor='middle',
                            fontSize=labelFontSize))
        return D
     
    def draw(self):
        # general widget bits
        s = self.size  # abbreviate as we will use this a lot 
        g = shapes.Group()
        

        # floppy disk specific bits
        diskBody = shapes.Rect(x=self.x, y=self.y+(s/100), width=s, height=s-(s/100),
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

        metalcover = shapes.Rect(x=self.x+(s*0.2), y=(self.y), width=s*0.5, height=s*0.35,
               fillColor = colors.silver,
               strokeColor = None,
               strokeWidth=0)
        g.add(metalcover)

        coverslot = shapes.Rect(x=self.x+(s*0.28), y=(self.y)+(s*0.035), width=s*0.12, height=s*0.28,
               fillColor = self.diskColor,
               strokeColor = None,
               strokeWidth=0)
        g.add(coverslot)

        return g

class ArrowOne0(Widget):
    """This widget draws an arrow (style one).

        possible attributes:
        'x', 'y', 'size', 'color'

        """

    _attrMap = {
        'x': isNumber,
        'y': isNumber,
        'size': isNumber,
        'color': isColor
        }

    def __init__(self):
        self.x = 0
        self.y = 0
        self.size = 100 
        self.color = colors.red

    def demo(self):
        D = shapes.Drawing(200, 100)
        a1 = ArrowOne0()
        a1.x=50
        a1.y=0
        a1.draw()
        D.add(a1)
        labelFontSize = 10
        D.add(shapes.String(a1.x+(a1.size/2),(a1.y-(1.2*labelFontSize)),
                            self.__class__.__name__, fillColor=colors.black, textAnchor='middle',
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

class ArrowTwo0(Widget):
    """This widget draws an arrow (style two).

        possible attributes:
        'x', 'y', 'size', 'color'

        """

    _attrMap = {
        'x': isNumber,
        'y': isNumber,
        'size': isNumber,
        'color': isColor
        }

    def __init__(self):
        self.x = 0
        self.y = 0
        self.size = 100 
        self.color = colors.blue

    def demo(self):
        D = shapes.Drawing(200, 100)
        a2 = ArrowTwo0()
        a2.x=50
        a2.y=0
        a2.draw()
        D.add(a2)
        labelFontSize = 10
        D.add(shapes.String(a2.x+(a2.size/2),(a2.y-(1.2*labelFontSize)),
                            self.__class__.__name__, fillColor=colors.black, textAnchor='middle',
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


def test():
    """This function produces a pdf with examples of all the signs and symbols from this file.
    """
    labelFontSize = 10
    D = shapes.Drawing(450,650)
    cb = Crossbox0()
    cb.x = 20
    cb.y = 530
    cb.demo()
    D.add(cb)
    D.add(shapes.String(cb.x+(cb.size/2),(cb.y-(1.2*labelFontSize)),
                           cb.__class__.__name__, fillColor=colors.black, textAnchor='middle',
                           fontSize=labelFontSize))

    tb = Tickbox0()
    tb.x = 170
    tb.y = 530
    tb.demo()
    D.add(tb)
    D.add(shapes.String(tb.x+(tb.size/2),(tb.y-(1.2*labelFontSize)),
                            tb.__class__.__name__, fillColor=colors.black, textAnchor='middle',
                            fontSize=labelFontSize))


    yn = YesNo0()
    yn.x = 320
    yn.y = 530
    yn.demo()
    D.add(yn)
    tempstring = yn.__class__.__name__ + '*'
    D.add(shapes.String(yn.x+(tb.size/2),(yn.y-(1.2*labelFontSize)),
                            tempstring, fillColor=colors.black, textAnchor='middle',
                            fontSize=labelFontSize))
    D.add(shapes.String(130,6,
                            "(The 'YesNo' widget returns a tickbox if testvalue=1, and a crossbox if testvalue=0)", fillColor=colors.black, textAnchor='middle',
                            fontSize=labelFontSize*0.75))


    ss = StopSign0()
    ss.x = 20
    ss.y = 400
    ss.demo()
    D.add(ss)
    D.add(shapes.String(ss.x+(ss.size/2), ss.y-(1.2*labelFontSize),
                            ss.__class__.__name__, fillColor=colors.black, textAnchor='middle',
                            fontSize=labelFontSize))

    ne = NoEntry0()
    ne.x = 170
    ne.y = 400
    ne.demo()
    D.add(ne)
    D.add(shapes.String(ne.x+(ne.size/2),(ne.y-(1.2*labelFontSize)),
                            ne.__class__.__name__, fillColor=colors.black, textAnchor='middle',
                            fontSize=labelFontSize))

    sf = SmileyFace0()
    sf.x = 320
    sf.y = 400
    sf.demo()
    D.add(sf)
    D.add(shapes.String(sf.x+(sf.size/2),(sf.y-(1.2*labelFontSize)),
                            sf.__class__.__name__, fillColor=colors.black, textAnchor='middle',
                            fontSize=labelFontSize))

    ds = DangerSign0()
    ds.x = 20
    ds.y = 270
    ds.demo()
    D.add(ds)
    D.add(shapes.String(ds.x+(ds.size/2),(ds.y-(1.2*labelFontSize)),
                            ds.__class__.__name__, fillColor=colors.black, textAnchor='middle',
                            fontSize=labelFontSize))    
    
    na = NotAllowed0()
    na.x = 170
    na.y = 270
    na.demo()
    D.add(na)
    D.add(shapes.String(na.x+(na.size/2),(na.y-(1.2*labelFontSize)),
                            na.__class__.__name__, fillColor=colors.black, textAnchor='middle',
                            fontSize=labelFontSize))    

    ns = NoSmoking0()
    ns.x = 320
    ns.y = 270
    ns.demo()
    D.add(ns)
    D.add(shapes.String(ns.x+(ns.size/2),(ns.y-(1.2*labelFontSize)),
                            ns.__class__.__name__, fillColor=colors.black, textAnchor='middle',
                            fontSize=labelFontSize))    

    a1 = ArrowOne0()
    a1.x = 20
    a1.y = 140
    a1.demo()
    D.add(a1)
    D.add(shapes.String(a1.x+(a1.size/2),(a1.y-(1.2*labelFontSize)),
                            a1.__class__.__name__, fillColor=colors.black, textAnchor='middle',
                            fontSize=labelFontSize)) 

    a2 = ArrowTwo0()
    a2.x = 170
    a2.y = 140
    a2.demo()
    D.add(a2)
    D.add(shapes.String(a2.x+(a2.size/2),(a2.y-(1.2*labelFontSize)),
                            a2.__class__.__name__, fillColor=colors.black, textAnchor='middle',
                           fontSize=labelFontSize)) 

    fd = FloppyDisk0()
    fd.x = 320
    fd.y = 140
    fd.demo()
    D.add(fd)
    D.add(shapes.String(fd.x+(fd.size/2),(fd.y-(1.2*labelFontSize)),
                            fd.__class__.__name__, fillColor=colors.black, textAnchor='middle',
                            fontSize=labelFontSize)) 

    renderPDF.drawToFile(D, 'signsandsymbols.pdf', 'signsandsymbols.py')
    print 'wrote file: signsandsymbols.pdf'
    
if __name__=='__main__':
    test()
