#copyright ReportLab Inc. 2000-2001
#see license.txt for license details

from reportlab.lib import colors
from reportlab.lib.validators import *
from reportlab.lib.attrmap import *
from reportlab.graphics.shapes import Drawing, Group, Line, Rect
from reportlab.graphics.widgetbase import Widget
from reportlab.graphics import renderPDF


def frange(start, end=None, inc=None):
    "A range function, that does accept float increments..."

    if end == None:
        end = start + 0.0
        start = 0.0

    if inc == None:
        inc = 1.0

    L = []
    while 1:
        next = start + len(L) * inc
        if inc > 0 and next >= end:
            break
        elif inc < 0 and next <= end:
            break
        L.append(next)
        
    return L


def makeDistancesList(list):
    """Returns a list of distances between adjacent numbers in some input list.

    E.g. [1, 1, 2, 3, 5, 7] -> [0, 1, 1, 2, 2]
    """

    d = []
    for i in range(len(list[:-1])):
        d.append(list[i+1] - list[i])

    return d


class Grid(Widget):
    """This makes a rectangular grid of equidistant stripes.

    The grid contains an outer border rectangle, and stripes
    inside which can be drawn with lines and/or as solid tiles.
    The drawing order is: outer rectangle, then lines and tiles.

    The stripes' width is indicated as 'delta'. The sequence of
    stripes can have an offset named 'delta0'. Both values need
    to be positive!
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
        deltaSteps = AttrMapValue(isListOfNumbers,
            desc='List of deltas to be used cyclically.'),
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
        self.deltaSteps = []
        self.fillColor = colors.white
        self.stripeColors = [colors.red, colors.green, colors.blue]
        self.strokeColor = colors.black
        self.strokeWidth = 2


    def demo(self):
        D = Drawing(100, 100)

        g = Grid()
        D.add(g)

        return D


    def makeOuterRect(self):
        # outer grid rectangle
        group = Group()
        #print 'Grid.makeOuterRect(%d, %d, %d, %d)' % (self.x, self.y, self.width, self.height)
        rect = Rect(self.x, self.y, self.width, self.height)
        rect.fillColor = self.fillColor
        rect.strokeColor = self.strokeColor
        rect.strokeWidth = self.strokeWidth

        return group


    def makeLinePosList(self, start, isX=0):
        "Returns a list of positions where to place lines."

        w, h = self.width, self.height
        if isX:
            length = w
        else:
            length = h
        if self.deltaSteps:
            r = [start + self.delta0]
            i = 0
            while 1:
                if r[-1] > start + length:
                    del r[-1]
                    break
                r.append(r[-1] + self.deltaSteps[i % len(self.deltaSteps)])
                i = i + 1
        else:
            r = frange(start + self.delta0, start + length, self.delta)

        r.append(start + length)
        if self.delta0 != 0:
            r.insert(0, start)
        #print 'Grid.makeLinePosList() -> %s' % r
        return r
    

    def makeInnerLines(self):
        # inner grid lines
        group = Group()
        
        w, h = self.width, self.height

        if self.useLines == 1:
            if self.orientation == 'vertical':
                r = self.makeLinePosList(self.x, isX=1)
                for x in r:
                    line = Line(x, self.y, x, self.y + h)
                    line.strokeColor = self.strokeColor
                    line.strokeWidth = self.strokeWidth
                    group.add(line)
            elif self.orientation == 'horizontal':
                r = self.makeLinePosList(self.y, isX=0)
                for y in r:
                    line = Line(self.x, y, self.x + w, y)
                    line.strokeColor = self.strokeColor
                    line.strokeWidth = self.strokeWidth
                    group.add(line)

        return group

    
    def makeInnerTiles(self):
        # inner grid lines
        group = Group()

        w, h = self.width, self.height

        # inner grid stripes (solid rectangles)
        if self.useRects == 1:
            cols = self.stripeColors

            if self.orientation == 'vertical':
                r = self.makeLinePosList(self.x, isX=1)
            elif self.orientation == 'horizontal':
                r = self.makeLinePosList(self.y, isX=0)

            dist = makeDistancesList(r)
            
            i = 0
            for j in range(len(dist)):
                if self.orientation == 'vertical':
                    x = r[j]
                    stripe = Rect(x, self.y, dist[j], h)
                elif self.orientation == 'horizontal':
                    y = r[j]
                    stripe = Rect(self.x, y, w, dist[j])
                stripe.fillColor = cols[i % len(cols)] 
                stripe.strokeColor = None
                group.add(stripe)
                i = i + 1

        return group

    
    def draw(self):
        # general widget bits
        group = Group()
        
        group.add(self.makeOuterRect())
        group.add(self.makeInnerTiles())
        group.add(self.makeInnerLines())

        return group


class DoubleGrid(Widget):
    """This combines two ordinary Grid objects orthogonal to each other.
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

        grid0 = AttrMapValue(None,
            desc="The first grid component."),
        grid1 = AttrMapValue(None,
            desc="The second grid component."),
        )

    def __init__(self):
        self.x = 0
        self.y = 0
        self.width = 100 
        self.height = 100 

        g0 = Grid()        
        g0.x = self.x
        g0.y = self.y
        g0.width = self.width 
        g0.height = self.height 
        g0.orientation = 'vertical' 
        g0.useLines = 1
        g0.useRects = 0
        g0.delta = 20
        g0.delta0 = 0
        g0.deltaSteps = []
        g0.fillColor = colors.white
        g0.stripeColors = [colors.red, colors.green, colors.blue]
        g0.strokeColor = colors.black
        g0.strokeWidth = 1

        g1 = Grid()        
        g1.x = self.x
        g1.y = self.y
        g1.width = self.width 
        g1.height = self.height 
        g1.orientation = 'horizontal' 
        g1.useLines = 1
        g1.useRects = 0
        g1.delta = 20
        g1.delta0 = 0
        g1.deltaSteps = []
        g1.fillColor = colors.white
        g1.stripeColors = [colors.red, colors.green, colors.blue]
        g1.strokeColor = colors.black
        g1.strokeWidth = 1

        self.grid0 = g0
        self.grid1 = g1


##    # This gives an AttributeError:
##    #   DoubleGrid instance has no attribute 'grid0'
##    def __setattr__(self, name, value):
##        if name in ('x', 'y', 'width', 'height'):
##            setattr(self.grid0, name, value)
##            setattr(self.grid1, name, value)


    def demo(self):
        D = Drawing(100, 100)
        g = DoubleGrid()
        D.add(g)
        return D


    def draw(self):
        group = Group()

        g0, g1 = self.grid0, self.grid1

        # Order groups to make sure both v and h lines
        # are visible (works only when there is only
        # one kind of stripes, v or h).
        if g0.useRects == 1 and g1.useRects == 0:       
            group.add(g0.draw())
            group.add(g1.draw())
        else:
            group.add(g1.draw())
            group.add(g0.draw())

        return group


class ShadedRect(Widget):
    """This makes a rectangle with shaded colors between two colors.

    Colors are interpolated linearly between 'fillColorStart'
    and 'fillColorEnd', both of which appear at the margins.
    If 'numShades' is set to one, though, only 'fillColorStart'
    is used.    
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
        self.numShades = 20
        self.fillColorStart = colors.pink
        self.fillColorEnd = colors.black
        self.strokeColor = colors.black
        self.strokeWidth = 2


    def demo(self):
        D = Drawing(100, 100)

        g = ShadedRect()
        D.add(g)

        return D


    def _flipRectCorners(self):
        "Flip rectangle's corners if width or height is negative."

        if self.width < 0 and self.height > 0:
            self.x = self.x + self.width 
            self.width = -self.width 
            if self.orientation == 'vertical':
                self.fillColorStart, self.fillColorEnd = self.fillColorEnd, self.fillColorStart
        elif self.height < 0 and self.width > 0:
            self.y = self.y + self.height 
            self.height = -self.height 
            if self.orientation == 'horizontal':
                self.fillColorStart, self.fillColorEnd = self.fillColorEnd, self.fillColorStart
        elif self.height < 0 and self.height < 0:
            self.x = self.x + self.width 
            self.width = -self.width 
            self.y = self.y + self.height 
            self.height = -self.height 


    def draw(self):
        # general widget bits
        group = Group()

        self._flipRectCorners()
        
        w, h = self.width, self.height

        rect = Rect(self.x, self.y, w, h)
        rect.strokeColor = self.strokeColor
        rect.strokeWidth = self.strokeWidth
        rect.fillColor = None
        group.add(rect)

        c0, c1 = self.fillColorStart, self.fillColorEnd
        r, g, b = c0.red, c0.green, c0.blue
        num = float(self.numShades) # must make it float!

        if self.orientation == 'vertical':
            if num == 1:
                xVals = [self.x]
            else:
                xVals = frange(self.x, self.x + w, w/num)

            for x in xVals:
                stripe = Rect(x, self.y, w/num, h)
                col = colors.Color(r, g, b)
                stripe.fillColor = col
                stripe.strokeColor = None
                stripe.strokeWidth = 0
                group.add(stripe)
                if num > 1:
                    r = r + (c1.red - c0.red) / (num-1)
                    g = g + (c1.green - c0.green) / (num-1)
                    b = b + (c1.blue - c0.blue) / (num-1)
 
        elif self.orientation == 'horizontal':
            if num == 1:
                yVals = [self.y]
            else:
                yVals = frange(self.y, self.y + h, h/num)

            for y in yVals:
                stripe = Rect(self.x, y, w, h/num)
                col = colors.Color(r, g, b)
                stripe.fillColor = col
                stripe.strokeColor = None
                stripe.strokeWidth = 0
                group.add(stripe)
                if num > 1:
                    r = r + (c1.red - c0.red) / (num-1)
                    g = g + (c1.green - c0.green) / (num-1)
                    b = b + (c1.blue - c0.blue) / (num-1)

        return group


def colorRange(startCol, endCol, numOfShades):
    "Return a range of intermediate colors between startCol and endCol."

    msg = 'Start/end colors must be of same class.'
    assert startCol.__class__ == endCol.__class__, msg

    colClass = startCol.__class__
    
    num = float(numOfShades)
    colorList = []
    
    if num == 1.0:
        colorList = [startCol]
    elif num > 1.0:
        col = startCol
        colorList.append(col)
        c0, c1 = startCol, endCol
        for i in range(1, int(num)):
            if colClass == colors.Color:
                r, g, b = colorList[-1].red, colorList[-1].green, colorList[-1].blue
                r = r + (c1.red - c0.red) / (num-1)
                g = g + (c1.green - c0.green) / (num-1)
                b = b + (c1.blue - c0.blue) / (num-1)
                col = colClass(r, g, b)
                colorList.append(col)
            elif colClass == colors.CMYKColor:
                c, m, y, k = colorList[-1].cyan, colorList[-1].magenta, colorList[-1].yellow, colorList[-1].black
                c = c + (c1.cyan - c0.cyan) / (num-1)
                m = m + (c1.magenta - c0.magenta) / (num-1)
                y = y + (c1.yellow - c0.yellow) / (num-1)
                k = k + (c1.black - c0.black) / (num-1)
                col = colClass(c, m, y, k)
                colorList.append(col)
            elif colClass == colors.PCMYKColor:
                c, m, y, k = colorList[-1].cyan, colorList[-1].magenta, colorList[-1].yellow, colorList[-1].black
                c = c + (c1.cyan - c0.cyan) / (num-1)
                m = m + (c1.magenta - c0.magenta) / (num-1)
                y = y + (c1.yellow - c0.yellow) / (num-1)
                k = k + (c1.black - c0.black) / (num-1)
                [c, m, y, k] = map(lambda x:100*x, [c, m, y, k])
                col = colClass(c, m, y, k)
                colorList.append(col)
            
    return colorList


def test0():
    "Create color ranges."

    c0, c1 = colors.Color(0, 0, 0), colors.Color(1, 1, 1)
    for c in colorRange(c0, c1, 4):
        print c
    print

    c0, c1 = colors.CMYKColor(0, 0, 0, 0), colors.CMYKColor(0, 0, 0, 1)
    for c in colorRange(c0, c1, 4):
        print c
    print

    c0, c1 = colors.PCMYKColor(0, 0, 0, 0), colors.PCMYKColor(0, 0, 0, 100)
    for c in colorRange(c0, c1, 4):
        print c
    print
    

def test1():
    "Generate a PDF document full of uncommented samples."
    
    D = Drawing(450, 650)

    d = 80
    s = 50
    
    for row in range(10):
        y = 530 - row*d
        if row == 0:
            for col in range(4):
                x = 20 + col*d
                g = Grid()
                g.x = x
                g.y = y
                g.width = s
                g.height = s
                g.useRects = 0
                g.useLines = 1
                if col == 0:
                    pass
                elif col == 1:
                    g.delta0 = 10
                elif col == 2:
                    g.orientation = 'horizontal'
                elif col == 3:
                    g.deltaSteps = [5, 10, 20, 30]
                g.demo()
                D.add(g)
        elif row == 1:
            for col in range(4):
                x = 20 + col*d 
                g = Grid()
                g.y = y
                g.x = x
                g.width = s
                g.height = s
                if col == 0:
                    pass
                elif col == 1:
                    g.delta0 = 10
                elif col == 2:
                    g.orientation = 'horizontal'
                elif col == 3:
                    g.deltaSteps = [5, 10, 20, 30]
                    g.useRects = 1
                    g.useLines = 0
                g.demo()
                D.add(g)
        elif row == 2:
            for col in range(3):
                x = 20 + col*d
                g = Grid()
                g.x = x
                g.y = y
                g.width = s
                g.height = s
                g.useLines = 1
                g.useRects = 1
                if col == 0:
                    pass
                elif col == 1:
                    g.delta0 = 10
                elif col == 2:
                    g.orientation = 'horizontal'
                g.demo()
                D.add(g)
        elif row == 3:
            for col in range(3):
                x = 20 + col*d
                sr = ShadedRect()
                sr.x = x
                sr.y = y
                sr.width = s
                sr.height = s
                sr.fillColorStart = colors.Color(0, 0, 0)
                sr.fillColorEnd = colors.Color(1, 1, 1)
                if col == 0:
                    sr.numShades = 5
                elif col == 1:
                    sr.numShades = 2
                elif col == 2:
                    sr.numShades = 1
                sr.demo()
                D.add(sr)
        elif row == 4:
            for col in range(3):
                x = 20 + col*d
                sr = ShadedRect()
                sr.x = x
                sr.y = y
                sr.width = s
                sr.height = s
                sr.fillColorStart = colors.red
                sr.fillColorEnd = colors.blue
                sr.orientation = 'horizontal'
                if col == 0:
                    sr.numShades = 10
                elif col == 1:
                    sr.numShades = 20
                elif col == 2:
                    sr.numShades = 50
                sr.demo()
                D.add(sr)
        elif row == 5:
            for col in range(3):
                x = 20 + col*d
                sr = ShadedRect()
                sr.x = x
                sr.y = y
                sr.width = s
                sr.height = s
                sr.fillColorStart = colors.white
                sr.fillColorEnd = colors.green
                sr.orientation = 'horizontal'
                if col == 0:
                    sr.numShades = 10
                elif col == 1:
                    sr.numShades = 20
                    sr.orientation = 'vertical'
                elif col == 2:
                    sr.numShades = 50
                sr.demo()
                D.add(sr)
        elif row == 6:
            for col in range(3):
                x = 20 + col*d
                sr = ShadedRect()
                sr.x = x
                sr.y = y+s
                sr.width = s
                sr.height = -s
                sr.fillColorStart = colors.white
                sr.fillColorEnd = colors.green
                sr.orientation = 'horizontal'
                if col == 0:
                    sr.numShades = 10
                elif col == 1:
                    sr.numShades = 20
                    sr.orientation = 'vertical'
                elif col == 2:
                    sr.numShades = 50
                sr.demo()
                D.add(sr)

    renderPDF.drawToFile(D, 'grids1.pdf', 'grids1.py')
    print 'wrote file: grids1.pdf'


def test2():
    "Generate a PDF document with some uncommented samples."

    D = Drawing(450, 650)

    d = 80
    s = 50
    
    for row in range(2):
        y = 530 - row*d
        if row == 0:
            for col in range(4):
                x = 20 + col*d
                g = DoubleGrid()
                g.x = x
                g.y = y
                g.width = s
                g.height = s

                # This should be done implicitely...
                g.grid0.x = x
                g.grid0.y = y
                g.grid1.x = x
                g.grid1.y = y
                g.grid0.width = s
                g.grid0.height = s
                g.grid1.width = s
                g.grid1.height = s

                if col == 0:
                    pass
                elif col == 1:
                    g.grid0.delta0 = 10
                elif col == 2:
                    g.grid0.delta0 = 5
                elif col == 3:
                    g.grid0.deltaSteps = [5, 10, 20, 30]
                g.demo()
                D.add(g)
        elif row == 1:
            for col in range(4):
                x = 20 + col*d 
                g = DoubleGrid()
                g.x = x
                g.y = y
                g.width = s
                g.height = s

                # This should be done implicitely...
                g.grid0.x = x
                g.grid0.y = y
                g.grid1.x = x
                g.grid1.y = y
                g.grid0.width = s
                g.grid0.height = s
                g.grid1.width = s
                g.grid1.height = s

                if col == 0:
                    g.grid0.useRects = 0
                    g.grid0.useLines = 1
                    g.grid1.useRects = 0
                    g.grid1.useLines = 1
                elif col == 1:
                    g.grid0.useRects = 1
                    g.grid0.useLines = 1
                    g.grid1.useRects = 0
                    g.grid1.useLines = 1
                elif col == 2:
                    g.grid0.useRects = 1
                    g.grid0.useLines = 0
                    g.grid1.useRects = 0
                    g.grid1.useLines = 1
                elif col == 3:
                    g.grid0.useRects = 1
                    g.grid0.useLines = 0
                    g.grid1.useRects = 1
                    g.grid1.useLines = 0
                g.demo()
                D.add(g)

    renderPDF.drawToFile(D, 'grids2.pdf', 'grids2.py')
    print 'wrote file: grids2.pdf'
    

def test3():
    "Generate a PDF document full of uncommented samples."
    
    D = Drawing(450, 650)

    d = 80
    s = 50
    
    for row in range(10):
        y = 530 - row*d
        if row == 0:
            for col in range(4):
                x = 20 + col*d
                g = Grid()
                g.x = x
                g.y = y
                g.width = s
                g.height = s
                g.useRects = 0
                g.useLines = 1
                if col == 0:
                    pass
                elif col == 1:
                    g.delta0 = 10
                elif col == 2:
                    g.orientation = 'horizontal'
                elif col == 3:
                    g.deltaSteps = [5, 10, 20, 30]
                g.demo()
                D.add(g)
        elif row == 1:
            for col in range(4):
                x = 20 + col*d 
                g = Grid()
                g.y = y
                g.x = x
                g.width = s
                g.height = s
                if col == 0:
                    pass
                elif col == 1:
                    g.delta0 = 10
                elif col == 2:
                    g.orientation = 'horizontal'
                elif col == 3:
                    g.deltaSteps = [5, 10, 20, 30]
                    g.useRects = 1
                    g.useLines = 0
                g.demo()
                D.add(g)
        elif row == 2:
            for col in range(3):
                x = 20 + col*d
                g = Grid()
                g.x = x
                g.y = y
                g.width = s
                g.height = s
                g.useLines = 1
                g.useRects = 1
                if col == 0:
                    pass
                elif col == 1:
                    g.delta0 = 10
                elif col == 2:
                    g.orientation = 'horizontal'
                g.demo()
                D.add(g)
        elif row == 3:
            for col in range(3):
                x = 20 + col*d
                sr = ShadedRect()
                sr.x = x
                sr.y = y
                sr.width = s
                sr.height = s
##                sr.fillColorStart = colors.Color(0, 0, 0)
##                sr.fillColorEnd = colors.Color(1, 1, 1)
                sr.fillColorStart = colors.CMYKColor(0, 0, 0, 0)
                sr.fillColorEnd = colors.CMYKColor(1, 1, 1, 1)
                if col == 0:
                    sr.numShades = 5
                elif col == 1:
                    sr.numShades = 2
                elif col == 2:
                    sr.numShades = 1
                sr.demo()
                D.add(sr)
        elif row == 4:
            for col in range(3):
                x = 20 + col*d
                sr = ShadedRect()
                sr.x = x
                sr.y = y
                sr.width = s
                sr.height = s
##                sr.fillColorStart = colors.red
##                sr.fillColorEnd = colors.blue
                sr.fillColorStart = colors.CMYKColor(1, 0, 0, 0)
                sr.fillColorEnd = colors.CMYKColor(0, 0, 1, 0)
                sr.orientation = 'horizontal'
                if col == 0:
                    sr.numShades = 10
                elif col == 1:
                    sr.numShades = 20
                elif col == 2:
                    sr.numShades = 50
                sr.demo()
                D.add(sr)
        elif row == 5:
            for col in range(3):
                x = 20 + col*d
                sr = ShadedRect()
                sr.x = x
                sr.y = y
                sr.width = s
                sr.height = s
##                sr.fillColorStart = colors.white
##                sr.fillColorEnd = colors.green
                sr.fillColorStart = colors.PCMYKColor(11.0,11.0,72.0,0.0,	spotName='PANTONE 458 CV',density=1.00)
                sr.fillColorEnd = colors.PCMYKColor(100.0,65.0,0.0,30.0,	spotName='PANTONE 288 CV',density=1.00) 
                sr.orientation = 'horizontal'
                if col == 0:
                    sr.numShades = 10
                elif col == 1:
                    sr.numShades = 20
                    sr.orientation = 'vertical'
                elif col == 2:
                    sr.numShades = 50
                sr.demo()
                D.add(sr)
        elif row == 6:
            for col in range(3):
                x = 20 + col*d
                sr = ShadedRect()
                sr.x = x
                sr.y = y+s
                sr.width = s
                sr.height = -s
                sr.fillColorStart = colors.white
                sr.fillColorEnd = colors.green
                sr.orientation = 'horizontal'
                if col == 0:
                    sr.numShades = 10
                elif col == 1:
                    sr.numShades = 20
                    sr.orientation = 'vertical'
                elif col == 2:
                    sr.numShades = 50
                sr.demo()
                D.add(sr)

    renderPDF.drawToFile(D, 'grids3.pdf', 'grids3.py')
    print 'wrote file: grids3.pdf'


if __name__=='__main__':
    test0()
##    test1()
##    test2()
##    test3()
