"""
This modules defines a preliminary collection of markers
used in charts.
"""

import string
from types import FunctionType

from reportlab.lib import colors 
from reportlab.graphics.shapes import Rect, Line, Polygon
from reportlab.graphics.widgets.signsandsymbols import SmileyFace0
from reportlab.graphics.widgetbase import Widget


def makeFilledSquare(x, y, size, color):
    "Make a filled square data item representation."

    d = size/2.0
    rect = Rect(x-d, y-d, 2*d, 2*d)
    rect.fillColor = color
    rect.strokeColor = color

    return rect


def makeFilledDiamond(x, y, size, color):
    "Make a filled diamond data item representation."

    d = size/2.0
    poly = Polygon((x-d,y, x,y+d, x+d,y, x,y-d))
    poly.fillColor = color
    poly.strokeColor = color

    return poly


def makeSmiley(x, y, size, color):
    "Make a smiley data item representation."

    d = size
    s = SmileyFace0()
    s.color = color
    s.x = x-d
    s.y = y-d
    s.size = d*2

    return s
