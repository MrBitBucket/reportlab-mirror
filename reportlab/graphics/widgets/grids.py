#copyright ReportLab Inc. 2000-2001
#see license.txt for license details

from reportlab.lib import colors
from reportlab.lib.validators import *
from reportlab.lib.attrmap import *
from reportlab.graphics.shapes import Drawing, Group, Line, Rect
from reportlab.graphics.widgetbase import Widget
from reportlab.graphics import renderPDF


class Grid0(Widget):
    """This makes a rectangular grid of equidistant stripes.

    The grid contains an outer border rectangle, and stripes
    inside which can be drawn with lines and/or as solid tiles.
    The darwing order is outer rectangle, then lines and tiles.

    The stripes' width is indicated as 'delta'. The sequence of
    stripes can have an offset named 'delta0'. Both values need
    to be positive.
    """

    _attrMap = AttrMap(
        x = AttrMapValue(isNumber,
            desc="The grid's lower-left x position."),
        y = AttrMapValue(isNumber,
            desc="The grid's lower-left y position."),
        width = AttrMapValue(isNumber,
            desc="The grid's width."),
        height = AttrMapValue(isNumber,
            desc="The grid's height."),
        orientation = AttrMapValue(OneOf(('vertical', 'horizontal')),
            desc='Determines if stripes are vertical or horizontal.'),
        useLines = AttrMapValue(OneOf((0, 1)),
            desc='Determines if stripes are drawn with lines.'),
        useRects = AttrMapValue(OneOf((0, 1)),
            desc='Determines if stripes are drawn with solid rectangles.'),
        delta = AttrMapValue(isNumber,
            desc='Determines the width/height of the stripes.'),
        delta0 = AttrMapValue(isNumber,
            desc='Determines the stripes initial width/height offset.'),
        stripeColors = AttrMapValue(isListOfColors,
            desc='Colors applied cyclically in the right or upper direction.'),
        fillColor = AttrMapValue(isColorOrNone,
            desc='Background color for entire rectangle.'),
        strokeColor = AttrMapValue(isColorOrNone,
            desc='Color used for lines.'),
        strokeWidth = AttrMapValue(isNumber,
            desc='Width used for lines.'),
        )

    def __init__(self):
        self.x = 0
        self.y = 0
        self.width = 100 
        self.height = 100 
        self.orientation = 'vertical' 
        self.useLines = 0
        self.useRects = 1
        self.delta = 20
        self.delta0 = 0
        self.fillColor = colors.white
        self.stripeColors = [colors.red, colors.green, colors.blue]
        self.strokeColor = colors.black
        self.strokeWidth = 2


    def demo(self):
        D = Drawing(100, 100)

        g = Grid0()
        g.draw()
        D.add(g)

        return D


    def makeOuterRect(self):
        # outer grid rectangle
        group = Group()

        rect = Rect(self.x, self.y, self.width, self.height)
        rect.fillColor = self.fillColor
        rect.strokeColor = self.strokeColor
        rect.strokeWidth = self.strokeWidth

        return group


    def makeInnerLines(self):
        # inner grid lines
        group = Group()
        
        if self.useLines == 1:
            if self.orientation == 'vertical':
                for x in xrange(self.x + self.delta0, self.x + self.width, self.delta):
                    line = Line(x, self.y, x, self.y + self.height)
                    line.strokeColor = self.strokeColor
                    line.strokeWidth = self.strokeWidth
                    group.add(line)
            elif self.orientation == 'horizontal':
                for y in xrange(self.y + self.delta0, self.y + self.height, self.delta):
                    line = Line(self.x, y, self.x + self.width, y)
                    line.strokeColor = self.strokeColor
                    line.strokeWidth = self.strokeWidth
                    group.add(line)

        return group

    
    def makeInnerTiles(self):
        # inner grid lines
        group = Group()

        # inner grid stripes (solid rectangles)
        if self.useRects == 1:
            cols = self.stripeColors
            if self.orientation == 'vertical':
                i = 0
                r = range(self.x + self.delta0, self.x + self.width, self.delta)
                for j in xrange(len(r)):
                    x = r[j]
                    try:
                        stripe = Rect(x, self.y, r[j+1]-x, self.height)
                        stripe.fillColor = cols[i % len(cols)] 
                        stripe.strokeColor = None
                        group.add(stripe)
                        i = i + 1
                    except IndexError:
                        if self.delta0 == 0:
                            stripe = Rect(x, self.y, self.delta, self.height)
                            stripe.fillColor = cols[i % len(cols)] 
                            stripe.strokeColor = None
                            group.add(stripe)
                            i = i + 1
                # if offset != 0 we need to draw left- and rightmost
                # stripe seperately
                if self.delta0 != 0:
                    lmStripe = Rect(self.x, self.y, self.delta0, self.height)
                    lmStripe.fillColor = cols[-1] 
                    lmStripe.strokeColor = None
                    group.add(lmStripe)

                    rmStripe = Rect(self.x + self.width - self.delta0, self.y, self.delta0, self.height)
                    rmStripe.fillColor = cols[i % len(cols)] 
                    rmStripe.strokeColor = None
                    group.add(rmStripe)

            elif self.orientation == 'horizontal':
                i = 0
                r = range(self.y + self.delta0, self.y + self.height, self.delta)
                for j in xrange(len(r)):
                    y = r[j]
                    try:
                        stripe = Rect(self.x, y, self.width, r[j+1]-y)
                        stripe.fillColor = cols[i % len(cols)] 
                        stripe.strokeColor = None
                        group.add(stripe)
                        i = i + 1
                    except IndexError:
                        if self.delta0 == 0:
                            stripe = Rect(self.x, y, self.width, self.delta)
                            stripe.fillColor = cols[i % len(cols)] 
                            stripe.strokeColor = None
                            group.add(stripe)
                            i = i + 1
                # if offset != 0 we need to draw upper- and lowermost
                # stripe seperately
                if self.delta0 != 0:
                    lmStripe = Rect(self.x, self.y, self.width, self.delta0)
                    lmStripe.fillColor = cols[-1] 
                    lmStripe.strokeColor = None
                    group.add(lmStripe)

                    umStripe = Rect(self.x, self.y + self.width - self.delta0, self.width, self.delta0)
                    umStripe.fillColor = cols[i % len(cols)] 
                    umStripe.strokeColor = None
                    group.add(umStripe)

        return group

    
    def draw(self):
        # general widget bits
        group = Group()
        
        group.add(self.makeOuterRect())
        group.add(self.makeInnerTiles())
        group.add(self.makeInnerLines())

        return group


class ShadedRect0(Widget):
    """This makes a rectangle with shaded colors between two colors.
    """

    _attrMap = AttrMap(
        x = AttrMapValue(isNumber,
            desc="The grid's lower-left x position."),
        y = AttrMapValue(isNumber,
            desc="The grid's lower-left y position."),
        width = AttrMapValue(isNumber,
            desc="The grid's width."),
        height = AttrMapValue(isNumber,
            desc="The grid's height."),
        orientation = AttrMapValue(OneOf(('vertical', 'horizontal')),
            desc='Determines if stripes are vertical or horizontal.'),
        numShades = AttrMapValue(isNumber,
            desc='The number of interpolating colors.'),
        fillColorStart = AttrMapValue(isColorOrNone,
            desc='Start value of the color shade.'),
        fillColorEnd = AttrMapValue(isColorOrNone,
            desc='End value of the color shade.'),
        strokeColor = AttrMapValue(isColorOrNone,
            desc='Color used for border line.'),
        strokeWidth = AttrMapValue(isNumber,
            desc='Width used for lines.'),
        )

    def __init__(self):
        self.x = 0
        self.y = 0
        self.width = 100 
        self.height = 100 
        self.orientation = 'vertical' 
        self.numShades = 20.0
        self.fillColorStart = colors.pink
        self.fillColorEnd = colors.black
        self.strokeColor = colors.black
        self.strokeWidth = 2


    def demo(self):
        D = Drawing(100, 100)

        g = ShadedRect0()
        g.draw()
        D.add(g)

        return D


    def draw(self):
        # general widget bits
        group = Group()
        
        rect = Rect(self.x, self.y, self.width, self.height)
        rect.strokeColor = self.strokeColor
        rect.strokeWidth = self.strokeWidth
        rect.fillColor = None
        group.add(rect)

        c0, c1 = self.fillColorStart, self.fillColorEnd
        r, g, b = c0.red, c0.green, c0.green
        num = self.numShades

        if self.orientation == 'vertical':
            for x in xrange(self.x, self.x + self.width, self.width/num):
                line = Rect(x, self.y, self.width/num, self.height)
                col = colors.Color(r, g, b)
                line.fillColor = col
                line.strokeColor = None
                line.strokeWidth = 0
                group.add(line)
                r = r + (c1.red - c0.red)/num
                g = g + (c1.green - c0.green)/num
                b = b + (c1.blue - c0.blue)/num
 
        elif self.orientation == 'horizontal':
            for y in xrange(self.y, self.y + self.height, self.height/num):
                line = Rect(self.x, y, self.width, self.height/num)
                col = colors.Color(r, g, b)
                line.fillColor = col
                line.strokeColor = None
                line.strokeWidth = 0
                group.add(line)            
                r = r + (c1.red - c0.red)/num
                g = g + (c1.green - c0.green)/num
                b = b + (c1.blue - c0.blue)/num

        return group


def test():
    D = Drawing(450,650)

    g = Grid0()
    g.x = 20
    g.y = 530
    g.demo()
    D.add(g)

    g = Grid0()
    g.x = 140
    g.y = 530
    g.delta0 = 10
    g.demo()
    D.add(g)

    g = Grid0()
    g.x = 260
    g.y = 530
    g.orientation = 'horizontal'
    g.demo()
    D.add(g)

    sr = ShadedRect0()
    sr.x = 20
    sr.y = 390
    sr.fillColorStart = colors.Color(0, 0, 0)
    sr.fillColorEnd = colors.Color(1, 1, 1)
    sr.demo()
    D.add(sr)

    sr = ShadedRect0()
    sr.x = 140
    sr.y = 390
    sr.fillColorStart = colors.Color(1, 1, 1)
    sr.fillColorEnd = colors.Color(0, 0, 0)
    sr.demo()
    D.add(sr)

    sr = ShadedRect0()
    sr.x = 20
    sr.y = 250
    sr.numShades = 10
    sr.fillColorStart = colors.red
    sr.fillColorEnd = colors.blue
    sr.orientation = 'horizontal'
    sr.demo()
    D.add(sr)

    sr = ShadedRect0()
    sr.x = 140
    sr.y = 250
    sr.numShades = 20
    sr.fillColorStart = colors.red
    sr.fillColorEnd = colors.blue
    sr.orientation = 'horizontal'
    sr.demo()
    D.add(sr)

    sr = ShadedRect0()
    sr.x = 260
    sr.y = 250
    sr.numShades = 50
    sr.fillColorStart = colors.red
    sr.fillColorEnd = colors.blue
    sr.orientation = 'horizontal'
    sr.demo()
    D.add(sr)

    renderPDF.drawToFile(D, 'grids.pdf', 'grids.py')
    print 'wrote file: grids.pdf'
    

if __name__=='__main__':
    test()
