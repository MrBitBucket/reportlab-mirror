#copyright ReportLab Inc. 2000-2001
#see license.txt for license details
#history http://cvs.sourceforge.net/cgi-bin/cvsweb.cgi/reportlab/graphics/charts/legends.py?cvsroot=reportlab
#$Header: /tmp/reportlab/reportlab/graphics/charts/legends.py,v 1.12 2001/07/02 16:50:53 rgbecker Exp $
"""This will be a collection of legends to be used with charts.
"""


import string, copy

from reportlab.lib import colors
from reportlab.lib.validators import isNumber, OneOf, isString, isColorOrNone
from reportlab.lib.attrmap import *
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.graphics.widgetbase import Widget
from reportlab.graphics.shapes import Drawing, Group, String, Rect, STATE_DEFAULTS


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
        x = AttrMapValue(isNumber,
            desc="x-coordinate of upper-left reference point"),
        y = AttrMapValue(isNumber,
            desc="y-coordinate of upper-left reference point"),
        deltax = AttrMapValue(isNumber,
            desc="x-distance between neighbouring swatches"),
        deltay = AttrMapValue(isNumber,
            desc="y-distance between neighbouring swatches"),
        dxTextSpace = AttrMapValue(isNumber,
            desc="Distance between swatch rectangle and text"),
        dx = AttrMapValue(isNumber,
            desc="Width of swatch rectangle"),
        dy = AttrMapValue(isNumber,
            desc="Height of swatch rectangle"),
        columnMaximum = AttrMapValue(isNumber,
            desc="Max. number of items per column"),
        alignment = AttrMapValue(OneOf("left", "right"),
            desc="Alginment of text with respect to swatches"),
        colorNamePairs = AttrMapValue(None,
            desc="List of color/name tuples (color can also be widget)"),

        fontName = AttrMapValue(isString,
            desc="Font name of the strings"),
        fontSize = AttrMapValue(isNumber,
            desc="Font size of the strings"),
        fillColor = AttrMapValue(isColorOrNone,
            desc=""),
        strokeColor = AttrMapValue(isColorOrNone,
            desc="Border color of the swatches")
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


    def _calculateMaxWidth(self, colorNamePairs):
        "Calculate the maximum width of some given strings."

        texts = map(lambda p:p[1], colorNamePairs[:3])
        widths = []
        for i in range(len(texts)):
            texts[i] = String(0,0, str(texts[i]))
            ti = texts[i]
            widths.append(stringWidth(ti.text, ti.fontName, ti.fontSize))
        maxWidth = max(widths)

        return maxWidth


    def draw(self):
        g = Group()
        colorNamePairs = self.colorNamePairs
        thisx = upperleftx = self.x
        thisy = upperlefty = self.y - self.dx
        dx, dy = self.dx, self.dy

        columnCount = 0
        count = 0
        for col, name in colorNamePairs:
            if self.alignment == "left":
                # align text to left
                t = String(thisx, thisy, str(name))
                j = columnCount*self.columnMaximum
                d = self._calculateMaxWidth(colorNamePairs[j:])
                t.x = t.x + d
                t.textAnchor = "end"
                x, y, width, height = thisx+d+self.dxTextSpace, thisy, dx, dy
            elif self.alignment == "right":
                # align text to right
                t = String(thisx+self.dx+self.dxTextSpace, thisy, str(name))
                t.textAnchor = "start"
                x, y, width, height = thisx, thisy, dx, dy
            else:
                raise ValueError, "bad alignment"

            t.fontName = self.fontName
            t.fontSize = self.fontSize
            t.fillColor = self.fillColor

            # Make a 'normal' color swatch...
            if isinstance(col, colors.Color):
                r = Rect(x, y, width, height)
                r.fillColor = col
                r.strokeColor = self.strokeColor
                g.add(r)
            # ... or try and see if we should do better.
            else:
                try:
                    c = copy.deepcopy(col)
                    c.x = x
                    c.y = y
                    c.width = width
                    c.height = height
                    g.add(c)
                except:
                    pass

            g.add(t)

            if count == self.columnMaximum-1:
                count = 0
                thisx = thisx+self.deltax
                thisy = upperlefty
                columnCount = columnCount + 1
            else:
                thisy = thisy-self.deltay
                count = count+1

        return g


    def demo(self):
        "Make sample legend."

        d = Drawing(200, 100)
        
        legend = Legend()
        legend.alignment = 'left'
        legend.x = 0
        legend.y = 100
        legend.dxTextSpace = 5
        items = string.split('red green blue yellow pink black white', ' ')
        items = map(lambda i:(getattr(colors, i), i), items)
        legend.colorNamePairs = items

        d.add(legend, 'legend')

        return d


def sample1c():
    "Make sample legend."
    
    d = Drawing(200, 100)
    
    legend = Legend()
    legend.alignment = 'right'
    legend.x = 0
    legend.y = 100
    legend.dxTextSpace = 5
    items = string.split('red green blue yellow pink black white', ' ')
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
    items = string.split('red green blue yellow pink black white', ' ')
    items = map(lambda i:(getattr(colors, i), i), items)
    legend.colorNamePairs = items

    d.add(legend, 'legend')

    return d
