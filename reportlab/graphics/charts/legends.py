#Copyright ReportLab Europe Ltd. 2000-2004
#see license.txt for license details
#history http://www.reportlab.co.uk/cgi-bin/viewcvs.cgi/public/reportlab/trunk/reportlab/graphics/charts/legends.py
"""This will be a collection of legends to be used with charts.
"""
__version__=''' $Id$ '''

import copy, operator

from reportlab.lib import colors
from reportlab.lib.validators import isNumber, OneOf, isString, isColorOrNone,\
        isNumberOrNone, isListOfNumbersOrNone, isStringOrNone, isBoolean,\
        NoneOr, AutoOr, isAuto, Auto, isBoxAnchor
from reportlab.lib.attrmap import *
from reportlab.pdfbase.pdfmetrics import stringWidth, getFont
from reportlab.graphics.widgetbase import Widget, TypedPropertyCollection, PropHolder
from reportlab.graphics.shapes import Drawing, Group, String, Rect, Line, STATE_DEFAULTS
from reportlab.graphics.charts.areas import PlotArea
from reportlab.graphics.widgets.markers import uSymbol2Symbol, isSymbol


class Legend(Widget):
    """A simple legend containing rectangular swatches and strings.

    The swatches are filled rectangles whenever the respective
    color object in 'colorNamePairs' is a subclass of Color in
    reportlab.lib.colors. Otherwise the object passed instead is
    assumed to have 'x', 'y', 'width' and 'height' attributes.
    A legend then tries to set them or catches any error. This
    lets you plug-in any widget you like as a replacement for
    the default rectangular swatches.

    Strings can be nicely aligned left or right to the swatches.
    """

    _attrMap = AttrMap(
        x = AttrMapValue(isNumber, desc="x-coordinate of upper-left reference point"),
        y = AttrMapValue(isNumber, desc="y-coordinate of upper-left reference point"),
        deltax = AttrMapValue(isNumberOrNone, desc="x-distance between neighbouring swatches"),
        deltay = AttrMapValue(isNumberOrNone, desc="y-distance between neighbouring swatches"),
        dxTextSpace = AttrMapValue(isNumber, desc="Distance between swatch rectangle and text"),
        autoXPadding = AttrMapValue(isNumber, desc="x Padding between columns if deltax=None"),
        autoYPadding = AttrMapValue(isNumber, desc="y Padding between rows if deltay=None"),
        yGap = AttrMapValue(isNumber, desc="Additional gap between rows"),
        dx = AttrMapValue(isNumber, desc="Width of swatch rectangle"),
        dy = AttrMapValue(isNumber, desc="Height of swatch rectangle"),
        columnMaximum = AttrMapValue(isNumber, desc="Max. number of items per column"),
        alignment = AttrMapValue(OneOf("left", "right"), desc="Alignment of text with respect to swatches"),
        colorNamePairs = AttrMapValue(None, desc="List of color/name tuples (color can also be widget)"),
        fontName = AttrMapValue(isString, desc="Font name of the strings"),
        fontSize = AttrMapValue(isNumber, desc="Font size of the strings"),
        fillColor = AttrMapValue(isColorOrNone, desc=""),
        strokeColor = AttrMapValue(isColorOrNone, desc="Border color of the swatches"),
        strokeWidth = AttrMapValue(isNumber, desc="Width of the border color of the swatches"),
        swatchMarker = AttrMapValue(NoneOr(AutoOr(isSymbol)), desc="None, Auto() or makeMarker('Diamond') ..."),
        callout = AttrMapValue(None, desc="a user callout(self,g,x,y,(color,text))"),
        boxAnchor = AttrMapValue(isBoxAnchor,'Anchor point for the legend area'),
        variColumn = AttrMapValue(isBoolean,'If true column widths may vary (default is false)'),
       )

    def __init__(self):
        # Upper-left reference point.
        self.x = 0
        self.y = 0

        # Alginment of text with respect to swatches.
        self.alignment = "left"

        # x- and y-distances between neighbouring swatches.
        self.deltax = 75
        self.deltay = 20
        self.autoXPadding = 5
        self.autoYPadding = 2

        # Size of swatch rectangle.
        self.dx = 10
        self.dy = 10

        # Distance between swatch rectangle and text.
        self.dxTextSpace = 10

        # Max. number of items per column.
        self.columnMaximum = 3

        # Color/name pairs.
        self.colorNamePairs = [ (colors.red, "red"),
                                (colors.blue, "blue"),
                                (colors.green, "green"),
                                (colors.pink, "pink"),
                                (colors.yellow, "yellow") ]

        # Font name and size of the labels.
        self.fontName = STATE_DEFAULTS['fontName']
        self.fontSize = STATE_DEFAULTS['fontSize']
        self.fillColor = STATE_DEFAULTS['fillColor']
        self.strokeColor = STATE_DEFAULTS['strokeColor']
        self.strokeWidth = STATE_DEFAULTS['strokeWidth']
        self.swatchMarker = None
        self.boxAnchor = 'nw'
        self.yGap = 0
        self.variColumn = 0

    def _getChartStyleName(self,chart):
        for a in 'lines', 'bars', 'slices', 'strands':
            if hasattr(chart,a): return a
        return None

    def _getChartStyle(self,chart):
        return getattr(chart,self._getChartStyleName(chart),None)

    def _getTexts(self,colorNamePairs):
        if not isAuto(colorNamePairs):
            texts = [str(p[1]) for p in colorNamePairs]
        else:
            chart = colorNamePairs.chart
            texts = [str(chart.getSeriesName(i,'series %d' % i)) for i in xrange(chart._seriesCount)]
        return texts

    def _calculateMaxWidth(self, colorNamePairs):
        "Calculate the maximum width of some given strings."
        M = []
        a = M.append
        for t in self._getTexts(colorNamePairs):
            m = [stringWidth(s, self.fontName, self.fontSize) for s in t.split('\n')]
            M.append(m and max(m) or 0)
        return self.variColumn and [max(M[r:r+3]) for r in range(0,len(M),self.columnMaximum)] or max(M)

    def _calcHeight(self):
        dy = self.dy
        yGap = self.yGap
        thisy = upperlefty = self.y - dy
        fontSize = self.fontSize
        ascent=getFont(self.fontName).face.ascent/1000.
        if ascent==0: ascent=0.718 # default (from helvetica)
        ascent *= fontSize
        leading = fontSize*1.2
        deltay = self.deltay
        if not deltay: deltay = max(dy,leading)+self.autoYPadding
        columnCount = 0
        count = 0
        lowy = upperlefty
        lim = self.columnMaximum - 1
        for name in self._getTexts(self.colorNamePairs):
            T = (name and str(name) or '').split('\n')
            S = []
            y = thisy+(dy-ascent)*0.5-leading
            newy = thisy-max(deltay,len(S)*leading)-yGap
            lowy = min(y,newy,lowy)
            if count==lim:
                count = 0
                thisy = upperlefty
                columnCount = columnCount + 1
            else:
                thisy = newy
                count = count+1
        return upperlefty - lowy

    def _defaultSwatch(self,x,thisy,dx,dy,fillColor,strokeWidth,strokeColor):
        return Rect(x, thisy, dx, dy,
                    fillColor = fillColor,
                    strokeColor = strokeColor,
                    strokeWidth = strokeWidth,
                    )

    def draw(self):
        colorNamePairs = self.colorNamePairs
        autoCP = isAuto(colorNamePairs)
        if autoCP:
            chart = getattr(colorNamePairs,'chart',getattr(colorNamePairs,'obj',None))
            swatchMarker = None
            autoCP = Auto(obj=chart)
            n = chart._seriesCount
            chartTexts = self._getTexts(colorNamePairs)
        else:
            swatchMarker = getattr(self,'swatchMarker',None)
            if isAuto(swatchMarker):
                chart = getattr(swatchMarker,'chart',getattr(swatchMarker,'obj',None))
                swatchMarker = Auto(obj=chart)
            n = len(colorNamePairs)
        dx = self.dx
        dy = self.dy
        alignment = self.alignment
        columnMaximum = self.columnMaximum
        deltax = self.deltax
        deltay = self.deltay
        dxTextSpace = self.dxTextSpace
        fontName = self.fontName
        fontSize = self.fontSize
        fillColor = self.fillColor
        strokeWidth = self.strokeWidth
        strokeColor = self.strokeColor
        leading = fontSize*1.2
        yGap = self.yGap
        if not deltay:
            deltay = max(dy,leading)+self.autoYPadding
        ba = self.boxAnchor
        baw = ba not in ('nw','w','sw','autox')
        maxWidth = self._calculateMaxWidth(colorNamePairs)
        nCols = int((n+columnMaximum-1)/columnMaximum)
        xW = dx+dxTextSpace+self.autoXPadding
        variColumn = self.variColumn
        if variColumn:
            width = reduce(operator.add,maxWidth,0)+xW*nCols
        else:
            deltax = max(maxWidth+xW,deltax)
            width = nCols*deltax
            maxWidth = nCols*[maxWidth]

        thisx = self.x
        thisy = self.y - self.dy
        if ba not in ('ne','n','nw','autoy'):
            height = self._calcHeight()
            if ba in ('e','c','w'):
                thisy += height/2.
            else:
                thisy += height
        if baw:
            if ba in ('n','c','s'):
                thisx -= width/2
            else:
                thisx -= width
        upperlefty = thisy

        g = Group()
        def gAdd(t,g=g,fontName=fontName,fontSize=fontSize,fillColor=fillColor):
            t.fontName = fontName
            t.fontSize = fontSize
            t.fillColor = fillColor
            return g.add(t)

        ascent=getFont(fontName).face.ascent/1000.
        if ascent==0: ascent=0.718 # default (from helvetica)
        ascent *= fontSize # normalize

        lim = columnMaximum - 1
        callout = getattr(self,'callout',None)
        for i in xrange(n):
            if autoCP:
                col = autoCP
                col.index = i
                name = chartTexts[i]
            else:
                col, name = colorNamePairs[i]
                if isAuto(swatchMarker):
                    col = swatchMarker
                    col.index = i
            T = (name and str(name) or '').split('\n')
            S = []
            j = int(i/columnMaximum)

            # thisy+dy/2 = y+leading/2
            y = thisy+(dy-ascent)*0.5
            if callout: callout(self,g,thisx,y,colorNamePairs[count])
            if alignment == "left":
                for t in T:
                    # align text to left
                    S.append(String(thisx+maxWidth[j],y,t,fontName=fontName,fontSize=fontSize,fillColor=fillColor,
                            textAnchor = "end"))
                    y -= leading
                x = thisx+maxWidth[j]+dxTextSpace
            elif alignment == "right":
                for t in T:
                    # align text to right
                    S.append(String(thisx+dx+dxTextSpace,y,t,fontName=fontName,fontSize=fontSize,fillColor=fillColor,
                            textAnchor = "start"))
                    y -= leading
                x = thisx
            else:
                raise ValueError, "bad alignment"

            # Make a 'normal' color swatch...
            if isAuto(col):
                chart = getattr(col,'chart',getattr(col,'obj',None))
                g.add(chart.makeSwatchSample(getattr(col,'index',i),x,thisy,dx,dy))
            elif isinstance(col, colors.Color):
                if isSymbol(swatchMarker):
                    g.add(uSymbol2Symbol(swatchMarker,x+dx/2.,thisy+dy/2.,col))
                else:
                    g.add(self._defaultSwatch(x,thisy,dx,dy,fillColor=col,strokeWidth=strokeWidth,strokeColor=strokeColor))
            else:
                try:
                    c = copy.deepcopy(col)
                    c.x = x
                    c.y = thisy
                    c.width = dx
                    c.height = dy
                    g.add(c)
                except:
                    pass

            map(gAdd,S)

            if i%columnMaximum==lim:
                if variColumn:
                    thisx += maxWidth[j]+xW
                else:
                    thisx = thisx+deltax
                thisy = upperlefty
            else:
                thisy = thisy-max(deltay,len(S)*leading)-yGap

        return g

    def demo(self):
        "Make sample legend."

        d = Drawing(200, 100)

        legend = Legend()
        legend.alignment = 'left'
        legend.x = 0
        legend.y = 100
        legend.dxTextSpace = 5
        items = 'red green blue yellow pink black white'.split()
        items = map(lambda i:(getattr(colors, i), i), items)
        legend.colorNamePairs = items

        d.add(legend, 'legend')

        return d

class LineSwatch(Widget):
    """basically a Line with properties added so it can be used in a LineLegend"""
    _attrMap = AttrMap(
        x = AttrMapValue(isNumber, desc="x-coordinate for swatch line start point"),
        y = AttrMapValue(isNumber, desc="y-coordinate for swatch line start point"),
        width = AttrMapValue(isNumber, desc="length of swatch line"),
        height = AttrMapValue(isNumber, desc="used for line strokeWidth"),
        strokeColor = AttrMapValue(isColorOrNone, desc="color of swatch line"),
        strokeDashArray = AttrMapValue(isListOfNumbersOrNone, desc="dash array for swatch line"),
    )

    def __init__(self):
        from reportlab.lib.colors import red
        from reportlab.graphics.shapes import Line
        self.x = 0
        self.y = 0
        self.width  = 20
        self.height = 1
        self.strokeColor = red
        self.strokeDashArray = None

    def draw(self):
        l = Line(self.x,self.y,self.x+self.width,self.y)
        l.strokeColor = self.strokeColor
        l.strokeDashArray  = self.strokeDashArray
        l.strokeWidth = self.height
        return l

class LineLegend(Legend):
    """A subclass of Legend for drawing legends with lines as the
    swatches rather than rectangles. Useful for lineCharts and
    linePlots. Should be similar in all other ways the the standard
    Legend class.
    """

    def __init__(self):
        Legend.__init__(self)

        # Size of swatch rectangle.
        self.dx = 10
        self.dy = 2

    def _defaultSwatch(self,x,thisy,dx,dy,fillColor,strokeWidth,strokeColor):
        l =  LineSwatch()
        l.x = x
        l.y = thisy
        l.width = dx
        l.height = dy
        l.strokeColor = fillColor
        return l

def sample1c():
    "Make sample legend."

    d = Drawing(200, 100)

    legend = Legend()
    legend.alignment = 'right'
    legend.x = 0
    legend.y = 100
    legend.dxTextSpace = 5
    items = 'red green blue yellow pink black white'.split()
    items = map(lambda i:(getattr(colors, i), i), items)
    legend.colorNamePairs = items

    d.add(legend, 'legend')

    return d


def sample2c():
    "Make sample legend."

    d = Drawing(200, 100)

    legend = Legend()
    legend.alignment = 'right'
    legend.x = 20
    legend.y = 90
    legend.deltax = 60
    legend.dxTextSpace = 10
    legend.columnMaximum = 4
    items = 'red green blue yellow pink black white'.split()
    items = map(lambda i:(getattr(colors, i), i), items)
    legend.colorNamePairs = items

    d.add(legend, 'legend')

    return d

def sample3():
    "Make sample legend with line swatches."

    d = Drawing(200, 100)

    legend = LineLegend()
    legend.alignment = 'right'
    legend.x = 20
    legend.y = 90
    legend.deltax = 60
    legend.dxTextSpace = 10
    legend.columnMaximum = 4
    items = 'red green blue yellow pink black white'.split()
    items = map(lambda i:(getattr(colors, i), i), items)
    legend.colorNamePairs = items
    d.add(legend, 'legend')

    return d


def sample3a():
    "Make sample legend with line swatches and dasharrays on the lines."

    d = Drawing(200, 100)

    legend = LineLegend()
    legend.alignment = 'right'
    legend.x = 20
    legend.y = 90
    legend.deltax = 60
    legend.dxTextSpace = 10
    legend.columnMaximum = 4
    items = 'red green blue yellow pink black white'.split()
    darrays = ([2,1], [2,5], [2,2,5,5], [1,2,3,4], [4,2,3,4], [1,2,3,4,5,6], [1])
    cnp = []
    for i in range(0, len(items)):
        l =  LineSwatch()
        l.strokeColor = getattr(colors, items[i])
        l.strokeDashArray = darrays[i]
        cnp.append((l, items[i]))
    legend.colorNamePairs = cnp
    d.add(legend, 'legend')

    return d
