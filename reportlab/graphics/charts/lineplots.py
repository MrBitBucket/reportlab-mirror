#copyright ReportLab Inc. 2000-2001
#see license.txt for license details
#history http://cvs.sourceforge.net/cgi-bin/cvsweb.cgi/reportlab/graphics/charts/lineplots.py?cvsroot=reportlab
#$Header: /tmp/reportlab/reportlab/graphics/charts/lineplots.py,v 1.15 2001/05/17 16:21:33 rgbecker Exp $
"""
This modules defines a very preliminary Line Plot example.
"""

import string, time
from types import FunctionType

from reportlab.lib import colors 
from reportlab.lib.validators import * 
from reportlab.lib.attrmap import *
from reportlab.graphics.shapes import Drawing, Group, Rect, Line, PolyLine
from reportlab.graphics.widgetbase import Widget, TypedPropertyCollection, PropHolder
from reportlab.graphics.widgets.signsandsymbols import SmileyFace0
from reportlab.graphics.charts.textlabels import Label
from reportlab.graphics.charts.axes import XValueAxis, YValueAxis
from reportlab.graphics.charts.utils import *
from reportlab.graphics.charts.markers import *


# This might be moved again from here...

class LinePlotProperties(PropHolder):
    _attrMap = AttrMap(
        strokeWidth = AttrMapValue(isNumber),
        strokeColor = AttrMapValue(isColorOrNone),
        strokeDashArray = AttrMapValue(isListOfNumbersOrNone),
        symbol = AttrMapValue(None),
        )


class LinePlot(Widget):
    """Line plot with multiple lines.

    Both x- and y-axis are value axis (so there are no seperate
    X and Y versions of this class).
    """

    _attrMap = AttrMap(
        debug = AttrMapValue(isNumber),
        x = AttrMapValue(isNumber),
        y = AttrMapValue(isNumber),
        width = AttrMapValue(isNumber),
        height = AttrMapValue(isNumber),

        useAbsolute = AttrMapValue(isNumber),
        lineLabelNudge = AttrMapValue(isNumber),
        lineLabels = AttrMapValue(None),
        lineLabelFormat = AttrMapValue(None),
        groupSpacing = AttrMapValue(isNumber),

        joinedLines = AttrMapValue(isNumber),

        strokeColor = AttrMapValue(isColorOrNone),
        fillColor = AttrMapValue(isColorOrNone),

        defaultStyles = AttrMapValue(None),

        xValueAxis = AttrMapValue(None),
        yValueAxis = AttrMapValue(None),
        data = AttrMapValue(None),
        )

    def __init__(self):
        self.debug = 0

        self.x = 0
        self.y = 0
        self.width = 200
        self.height = 100

        # allow for a bounding rectangle
        self.strokeColor = None
        self.fillColor = None

        self.xValueAxis = XValueAxis()
        self.yValueAxis = YValueAxis()

        # this defines two series of 3 points.  Just an example.
        self.data = [
            ((1,1), (2,2), (2.5,1), (3,3), (4,5)),
            ((1,2), (2,3), (2.5,2), (3,4), (4,6))
            ]

        self.defaultStyles = TypedPropertyCollection(LinePlotProperties)
        self.defaultStyles.strokeWidth = 1
        self.defaultStyles[0].strokeColor = colors.red
        self.defaultStyles[1].strokeColor = colors.blue
        
        # control bar spacing. is useAbsolute = 1 then
        # the next parameters are in points; otherwise
        # they are 'proportions' and are normalized to
        # fit the available space.  Half a barSpacing
        # is allocated at the beginning and end of the
        # chart.
        self.useAbsolute = 0   #- not done yet
        self.groupSpacing = 1 #5

        self.lineLabels = TypedPropertyCollection(Label)
        self.lineLabelFormat = None

        # this says whether the origin is inside or outside
        # the bar - +10 means put the origin ten points
        # above the tip of the bar if value > 0, or ten
        # points inside if bar value < 0.  This is different
        # to label dx/dy which are not dependent on the
        # sign of the data.
        self.lineLabelNudge = 10
        # if you have multiple series, by default they butt
        # together.

        # New line chart attributes.
        self.joinedLines = 1 # Connect items with straight lines.


    def demo(self):
        """Shows basic use of a line chart."""

        drawing = Drawing(400, 200)

        data = [
            ((1,1), (2,2), (2.5,1), (3,3), (4,5)),
            ((1,2), (2,3), (2.5,2), (3.5,5), (4,6))
            ]
        
        lp = LinePlot()

        lp.x = 50
        lp.y = 50
        lp.height = 125
        lp.width = 300
        lp.data = data
        lp.joinedLines = 1
        lp.lineLabelFormat = '%2.0f'
        lp.strokeColor = colors.black

        lp.defaultStyles[0].strokeColor = colors.red
        lp.defaultStyles[0].symbol = makeFilledCircle
        lp.defaultStyles[1].strokeColor = colors.blue
        lp.defaultStyles[1].symbol = makeFilledDiamond

        lp.xValueAxis.valueMin = 0
        lp.xValueAxis.valueMax = 5
        lp.xValueAxis.valueStep = 1

        lp.yValueAxis.valueMin = 0
        lp.yValueAxis.valueMax = 7
        lp.yValueAxis.valueStep = 1
        
        drawing.add(lp)

        return drawing


    def calcPositions(self):
        """Works out where they go.

        Sets an attribute _positions which is a list of
        lists of (x, y) matching the data.
        """

        self._seriesCount = len(self.data)
        self._rowLength = len(self.data[0])
        
        if self.useAbsolute:
            # bar dimensions are absolute
            normFactor = 1.0
        else:
            # bar dimensions are normalized to fit.  How wide
            # notionally is one group of bars?
            normWidth = self.groupSpacing
            availWidth = self.xValueAxis.scale(0)#[1]
            normFactor = availWidth / normWidth
        
        self._positions = []
        for rowNo in range(len(self.data)):
            line = []
            for colNo in range(len(self.data[0])):
                datum = self.data[rowNo][colNo] # x,y value
                if type(datum[0]) == type(''):
                    x = self.xValueAxis.scale(mktime(mkTimeTuple(datum[0])))
                else:
                    x = self.xValueAxis.scale(datum[0])
                y = self.yValueAxis.scale(datum[1])
                line.append((x, y))
            self._positions.append(line)


    def makeBackground(self):
        g = Group()

        g.add(Rect(self.x, self.y,
                   self.width, self.height,
                   strokeColor = self.strokeColor,
                   fillColor= self.fillColor))
                
        return g


    def drawLabel(self, group, rowNo, colNo, x, y):
        "Draw a label for a given item in the list."

        labelFmt = self.lineLabelFormat
        labelValue = self.data[rowNo][colNo][1] ###

        if labelFmt is None:
            labelText = None
        elif type(labelFmt) is StringType:
            labelText = labelFmt % labelValue
        elif type(labelFmt) is FunctionType:
            labelText = labelFmt(labelValue)
        else:
            msg = "Unknown formatter type %s, expected string or function"  
            raise Exception, msg % labelFmt

        if labelText:
            label = self.lineLabels[(rowNo, colNo)]
            #hack to make sure labels are outside the bar
            if y > 0:
                label.setOrigin(x, y + self.lineLabelNudge)
            else:
                label.setOrigin(x, y - self.lineLabelNudge)
            label.setText(labelText)
            group.add(label)


    def makeLines(self):
        g = Group()

        labelFmt = self.lineLabelFormat

        # Iterate over data rows.        
        for rowNo in range(len(self._positions)):
            row = self._positions[rowNo]

            styleCount = len(self.defaultStyles)
            styleIdx = rowNo % styleCount
            rowColor = self.defaultStyles[styleIdx].strokeColor
            dash = getattr(self.defaultStyles[styleIdx], 'strokeDashArray', None)

            # width = getattr(self.defaultStyles[styleIdx], 'strokeWidth', None)
            if hasattr(self.defaultStyles[styleIdx], 'strokeWidth'):
                width = self.defaultStyles[styleIdx].strokeWidth
            elif hasattr(self.defaultStyles, 'strokeWidth'):
                width = self.defaultStyles.strokeWidth
            else:
                width = None

            # Iterate over data columns.
            if self.joinedLines:
                points = []
                for xy in row:
                    points = points + [xy[0], xy[1]]
                line = PolyLine(points,strokeColor=rowColor,strokeLineCap=0,strokeLineJoin=1)
                if width:
                    line.strokeWidth = width
                if dash:
                    line.strokeDashArray = dash
                g.add(line)
            else:
                for colNo in range(len(row)):
                    x1, y1 = row[colNo]
                    if self.joinedLines == 1:
                        if colNo > 0:
                            # Draw lines between adjacent items.
                            x2, y2 = row[colNo-1]
                            line = Line(x1, y1, x2, y2,
                                        strokeColor=rowColor,
                                        strokeLineCap=1)
                            if width:
                                line.strokeWidth = width
                            if dash:
                                line.strokeDashArray = dash
                            g.add(line)

            # Iterate once more over data columns
            # (to make sure symbols and labels are on top).
            for colNo in range(len(row)):
                x1, y1 = row[colNo]

                # Draw a symbol for each data item.
                # This if should be done implicitely by the collection,
                # but it didn't want to...
                if hasattr(self.defaultStyles[styleIdx], 'symbol'):
                    symbol = self.defaultStyles[styleIdx].symbol(x1, y1, 5, rowColor)
                    g.add(symbol)
                elif hasattr(self.defaultStyles, 'symbol'):
                    symbol = self.defaultStyles.symbol(x1, y1, 5, rowColor)
                    g.add(symbol)
                
                # Draw item (bar) labels.
                self.drawLabel(g, rowNo, colNo, x1, y1)

        return g


    def draw(self):
        self.yValueAxis.setPosition(self.x, self.y, self.height)
        self.yValueAxis.configure(self.data)

        # if zero is in chart, put x axis there, otherwise
        # use bottom.
        xAxisCrossesAt = self.yValueAxis.scale(0)
        if ((xAxisCrossesAt > self.y + self.height) or (xAxisCrossesAt < self.y)):
            y = self.y
        else:
            y = xAxisCrossesAt

        self.xValueAxis.setPosition(self.x, y, self.width)
        self.xValueAxis.configure(self.data)
        
        self.calcPositions()        
        
        g = Group()

        g.add(self.makeBackground())
        g.add(self.xValueAxis)
        g.add(self.yValueAxis)
        g.add(self.makeLines())

        return g


def sample1a():
    "A line plot with non-equidistant points in x-axis."
    
    drawing = Drawing(400, 200)

    data = [
            ((1,1), (2,2), (2.5,1), (3,3), (4,5)),
            ((1,2), (2,3), (2.5,2), (3.5,5), (4,6))
        ]
    
    lp = LinePlot()

    lp.x = 50
    lp.y = 50
    lp.height = 125
    lp.width = 300
    lp.data = data
    lp.joinedLines = 1
    lp.strokeColor = colors.black

    lp.defaultStyles.symbol = makeEmptyCircle
    lp.defaultStyles[0].strokeWidth = 2
    lp.defaultStyles[1].strokeWidth = 4

    lp.xValueAxis.valueMin = 0
    lp.xValueAxis.valueMax = 5
    lp.xValueAxis.valueStep = 1

    lp.yValueAxis.valueMin = 0
    lp.yValueAxis.valueMax = 7
    lp.yValueAxis.valueStep = 1
    
    drawing.add(lp)

    return drawing


def sample1b():
    "A line plot with non-equidistant points in x-axis."
    
    drawing = Drawing(400, 200)

    data = [
            ((1,1), (2,2), (2.5,1), (3,3), (4,5)),
            ((1,2), (2,3), (2.5,2), (3.5,5), (4,6))
        ]
    
    lp = LinePlot()

    lp.x = 50
    lp.y = 50
    lp.height = 125
    lp.width = 300
    lp.data = data
    lp.joinedLines = 1
    lp.defaultStyles.symbol = makeEmptyCircle
    lp.lineLabelFormat = '%2.0f'
    lp.strokeColor = colors.black

    lp.xValueAxis.valueMin = 0
    lp.xValueAxis.valueMax = 5
    lp.xValueAxis.valueSteps = [1, 2, 2.5, 3, 4, 5]
    lp.xValueAxis.labelTextFormat = '%2.1f'

    lp.yValueAxis.valueMin = 0
    lp.yValueAxis.valueMax = 7
    lp.yValueAxis.valueStep = 1
    
    drawing.add(lp)

    return drawing


def sample1c():
    "A line plot with non-equidistant points in x-axis."
    
    drawing = Drawing(400, 200)

    data = [
            ((1,1), (2,2), (2.5,1), (3,3), (4,5)),
            ((1,2), (2,3), (2.5,2), (3.5,5), (4,6))
        ]
    
    lp = LinePlot()

    lp.x = 50
    lp.y = 50
    lp.height = 125
    lp.width = 300
    lp.data = data
    lp.joinedLines = 1
    lp.defaultStyles[0].symbol = makeFilledCircle
    lp.defaultStyles[1].symbol = makeEmptyCircle
    lp.lineLabelFormat = '%2.0f'
    lp.strokeColor = colors.black

    lp.xValueAxis.valueMin = 0
    lp.xValueAxis.valueMax = 5
    lp.xValueAxis.valueSteps = [1, 2, 2.5, 3, 4, 5]
    lp.xValueAxis.labelTextFormat = '%2.1f'

    lp.yValueAxis.valueMin = 0
    lp.yValueAxis.valueMax = 7
    lp.yValueAxis.valueSteps = [1, 2, 3, 5, 6]
    
    drawing.add(lp)

    return drawing


def preprocessData(series):
    "Convert date strings into seconds and multiply values by 100."

    return map(lambda x: (str2seconds(x[0]), x[1]*100), series)


def sample2():
    "A line plot with non-equidistant points in x-axis."
    
    drawing = Drawing(400, 200)

    data = [
        (('25/11/1991',1),
         ('30/11/1991',1.000933333),
         ('31/12/1991',1.0062),
         ('31/01/1992',1.0112),
         ('29/02/1992',1.0158),
         ('31/03/1992',1.020733333),
         ('30/04/1992',1.026133333),
         ('31/05/1992',1.030266667),
         ('30/06/1992',1.034466667),
         ('31/07/1992',1.038733333),
         ('31/08/1992',1.0422),
         ('30/09/1992',1.045533333),
         ('31/10/1992',1.049866667),
         ('30/11/1992',1.054733333),
         ('31/12/1992',1.061),
         ),
        ]

    data[0] = preprocessData(data[0])
    
    lp = LinePlot()

    lp.x = 50
    lp.y = 50
    lp.height = 125
    lp.width = 300
    lp.data = data
    lp.joinedLines = 1
    lp.defaultStyles.symbol = makeFilledDiamond
    lp.strokeColor = colors.black

    start = mktime(mkTimeTuple('25/11/1991'))
    t0 = mktime(mkTimeTuple('30/11/1991'))
    t1 = mktime(mkTimeTuple('31/12/1991'))
    t2 = mktime(mkTimeTuple('31/03/1992'))
    t3 = mktime(mkTimeTuple('30/06/1992'))
    t4 = mktime(mkTimeTuple('30/09/1992'))
    end = mktime(mkTimeTuple('31/12/1992'))
    lp.xValueAxis.valueMin = start
    lp.xValueAxis.valueMax = end
    lp.xValueAxis.valueSteps = [start, t0, t1, t2, t3, t4, end]
    lp.xValueAxis.labelTextFormat = seconds2str
    lp.xValueAxis.labels[1].dy = -20
    lp.xValueAxis.labels[2].dy = -35

    lp.yValueAxis.labelTextFormat = '%4.2f'
    lp.yValueAxis.valueMin = 100
    lp.yValueAxis.valueMax = 110
    lp.yValueAxis.valueStep = 2
    
    drawing.add(lp)

    return drawing
