#copyright ReportLab Inc. 2000-2001
#see license.txt for license details
#history http://cvs.sourceforge.net/cgi-bin/cvsweb.cgi/reportlab/graphics/charts/linecharts.py?cvsroot=reportlab
#$Header: /tmp/reportlab/reportlab/graphics/charts/linecharts.py,v 1.14 2001/09/25 12:14:22 rgbecker Exp $
"""
This modules defines a very preliminary Line Chart example.
"""

import string
from types import FunctionType, ClassType, StringType

from reportlab.lib import colors 
from reportlab.lib.validators import isNumber, isColor, isColorOrNone, isListOfStrings, isListOfStringsOrNone, SequenceOf
from reportlab.lib.attrmap import *
from reportlab.graphics.widgetbase import Widget, TypedPropertyCollection, PropHolder
from reportlab.graphics.shapes import Line, Rect, Group, Drawing
from reportlab.graphics.widgets.signsandsymbols import NoEntry
from reportlab.graphics.charts.axes import XCategoryAxis, YValueAxis
from reportlab.graphics.charts.textlabels import Label
from reportlab.graphics.charts.markers import *


class LineChartProperties(PropHolder):
    _attrMap = AttrMap(
        strokeWidth = AttrMapValue(isNumber,
            desc='Width of a line.'),
        strokeColor = AttrMapValue(isColorOrNone,
            desc='Color of a line.'),
        symbol = AttrMapValue(None,
            desc='Widget placed at data points.'),
        )


class LineChart(Widget):
    pass


# This is conceptually similar to the VerticalBarChart.
# Still it is better named HorizontalLineChart... :-/

class HorizontalLineChart(LineChart):
    """Line chart with multiple lines.

    A line chart is assumed to have one category and one value axis. 
    Despite its generic name this particular line chart class has
    a vertical value axis and a horizontal category one. It may
    evolve into individual horizontal and vertical variants (like
    with the existing bar charts).

    Available attributes are:

        x: x-position of lower-left chart origin
        y: y-position of lower-left chart origin
        width: chart width
        height: chart height

        useAbsolute: disables auto-scaling of chart elements (?)
        lineLabelNudge: distance of data labels to data points
        lineLabels: labels associated with data values
        lineLabelFormat: format string or callback function
        groupSpacing: space between categories

        joinedLines: enables drawing of lines

        strokeColor: color of chart lines (?)
        fillColor: color for chart background (?)
        lines: style list, used cyclically for data series

        valueAxis: value axis object
        categoryAxis: category axis object
        categoryNames: category names

        data: chart data, a list of data series of equal length
    """

    _attrMap = AttrMap(
        x = AttrMapValue(isNumber,
            desc='X position of the lower-left corner of the chart.'),
        y = AttrMapValue(isNumber,
            desc='Y position of the lower-left corner of the chart.'),
        width = AttrMapValue(isNumber,
            desc='Width of the chart.'),
        height = AttrMapValue(isNumber,
            desc='Height of the chart.'),

        useAbsolute = AttrMapValue(isNumber,
            desc='Flag to use absolute spacing values.'),
        lineLabelNudge = AttrMapValue(isNumber,
            desc='Distance between a data point and its label.'),
        lineLabels = AttrMapValue(None,
            desc='Handle to the list of data point labels.'),
        lineLabelFormat = AttrMapValue(None,
            desc='Formatting string or function used for data point labels.'),
        groupSpacing = AttrMapValue(isNumber,
            desc='? - Likely to disappear.'),

        joinedLines = AttrMapValue(isNumber,
            desc='Display data points joined with lines if true.'),

        strokeColor = AttrMapValue(isColorOrNone,
            desc='Color used for background border of plot area.'),
        fillColor = AttrMapValue(isColorOrNone,
            desc='Color used for background interior of plot area.'),

        lines = AttrMapValue(None,
            desc='Handle of the lines.'),

        valueAxis = AttrMapValue(None,
            desc='Handle of the value axis.'),
        categoryAxis = AttrMapValue(None,
            desc='Handle of the category axis.'),
        categoryNames = AttrMapValue(isListOfStringsOrNone,
            desc='List of category names.'),
        data = AttrMapValue(None,
            desc='Data to be plotted, list of (lists of) numbers.'),
        )

    def __init__(self):
        self.x = 0
        self.y = 0
        self.width = 200
        self.height = 100

        # Allow for a bounding rectangle.
        self.strokeColor = None
        self.fillColor = None

        # Named so we have less recoding for the horizontal one :-)
        self.categoryAxis = XCategoryAxis()
        self.valueAxis = YValueAxis()

        # This defines two series of 3 points.  Just an example.
        self.data = [(100,110,120,130),
                     (70, 80, 80, 90)]        
        self.categoryNames = ('North','South','East','West')

        self.lines = TypedPropertyCollection(LineChartProperties)
        self.lines.strokeWidth = 1
        self.lines[0].strokeColor = colors.red
        self.lines[1].strokeColor = colors.green
        self.lines[2].strokeColor = colors.blue

        # control spacing. if useAbsolute = 1 then
        # the next parameters are in points; otherwise
        # they are 'proportions' and are normalized to
        # fit the available space.
        self.useAbsolute = 0   #- not done yet
        self.groupSpacing = 1 #5

        self.lineLabels = TypedPropertyCollection(Label)
        self.lineLabelFormat = None

        # This says whether the origin is above or below
        # the data point. +10 means put the origin ten points
        # above the data point if value > 0, or ten
        # points below if data value < 0.  This is different
        # to label dx/dy which are not dependent on the
        # sign of the data.
        self.lineLabelNudge = 10
        # If you have multiple series, by default they butt
        # together.

        # New line chart attributes.
        self.joinedLines = 1 # Connect items with straight lines.


    def demo(self):
        """Shows basic use of a line chart."""

        drawing = Drawing(200, 100)

        data = [
                (13, 5, 20, 22, 37, 45, 19, 4),
                (14, 10, 21, 28, 38, 46, 25, 5)
                ]
        
        lc = HorizontalLineChart()

        lc.x = 20
        lc.y = 10
        lc.height = 85
        lc.width = 170
        lc.data = data
        lc.lines.symbol = makeEmptyCircle

        drawing.add(lc)

        return drawing


    def calcPositions(self):
        """Works out where they go.

        Sets an attribute _positions which is a list of
        lists of (x, y) matching the data.
        """

        self._seriesCount = len(self.data)
        self._rowLength = len(self.data[0])
        
        if self.useAbsolute:
            # Dimensions are absolute.
            normFactor = 1.0
        else:
            # Dimensions are normalized to fit.
            normWidth = self.groupSpacing
            availWidth = self.categoryAxis.scale(0)[1]
            normFactor = availWidth / normWidth
        
        self._positions = []
        for rowNo in range(len(self.data)):
            lineRow = []
            for colNo in range(len(self.data[0])):
                datum = self.data[rowNo][colNo]
                (groupX, groupWidth) = self.categoryAxis.scale(colNo)
                x = groupX + (0.5 * self.groupSpacing * normFactor)
                y = self.valueAxis.scale(0)
                height = self.valueAxis.scale(datum) - y
                lineRow.append((x, y+height))
            self._positions.append(lineRow)
        

    def drawLabel(self, group, rowNo, colNo, x, y):
        "Draw a label for a given item in the list."

        labelFmt = self.lineLabelFormat
        labelValue = self.data[rowNo][colNo]
        
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
            # Make sure labels are some distance off the data point.
            if y > 0:
                label.setOrigin(x, y + self.lineLabelNudge)
            else:
                label.setOrigin(x, y - self.lineLabelNudge)
            label.setText(labelText)

            group.add(label)


    def makeBackground(self):
        g = Group()

        g.add(Rect(self.x, self.y,
                   self.width, self.height,
                   strokeColor = self.strokeColor,
                   fillColor= self.fillColor))
        
        return g


    def makeLines(self):
        g = Group()

        labelFmt = self.lineLabelFormat

        # Iterate over data rows.        
        for rowNo in range(len(self._positions)):
            row = self._positions[rowNo]
            styleCount = len(self.lines)
            styleIdx = rowNo % styleCount
            rowStyle = self.lines[styleIdx]

            if hasattr(self.lines[styleIdx], 'strokeWidth'):
                strokeWidth = self.lines[styleIdx].strokeWidth
            elif hasattr(self.lines, 'strokeWidth'):
                strokeWidth = self.lines.strokeWidth
            else:
                strokeWidth = None

            # Iterate over data columns.        
            for colNo in range(len(row)):
                x1, y1 = row[colNo]
                if self.joinedLines == 1:
                    if colNo > 0:
                        # Draw lines between adjacent items.
                        x2, y2 = row[colNo-1]
                        line = Line(x1, y1, x2, y2)
                        line.strokeColor = rowStyle.strokeColor
                        line.strokeWidth = rowStyle.strokeWidth
                        g.add(line)

            # Iterate once more over data columns
            # (to make sure symbols and labels are on top).
            if hasattr(self.lines[styleIdx], 'symbol'):
                uSymbol = self.lines[styleIdx].symbol
            elif hasattr(self.lines, 'symbol'):
                uSymbol = self.lines.symbol
            else:
                uSymbol = None                

            if uSymbol:            
                for colNo in range(len(row)):
                    x1, y1 = row[colNo]

                    # Draw a symbol for each data item. The usedSymbol
                    # attribute can be either a Widget class or a function
                    # returning a widget object.
                    if type(uSymbol) == FunctionType:
                        symbol = uSymbol(x1, y1, 5, rowStyle.strokeColor)
                    elif type(uSymbol) == ClassType:
                        size = 10.0
                        symbol = uSymbol()
                        if not isinstance(symbol, Widget):
                            break
                        symbol.x = x1 - (size/2)
                        symbol.y = y1 - (size/2)
                        try:
                            symbol.size = size
                            symbol.color = rowStyle.strokeColor
                        except:
                            pass

                    g.add(symbol)

            # Draw item labels.
            self.drawLabel(g, rowNo, colNo, x1, y1)
        
        return g


    def draw(self):
        "Draws itself."
        
        self.valueAxis.setPosition(self.x, self.y, self.height)
        self.valueAxis.configure(self.data)

        # If zero is in chart, put x axis there, otherwise
        # use bottom.
        xAxisCrossesAt = self.valueAxis.scale(0)
        if ((xAxisCrossesAt > self.y + self.height) or (xAxisCrossesAt < self.y)):
            y = self.y
        else:
            y = xAxisCrossesAt

        self.categoryAxis.setPosition(self.x, y, self.width)
        self.categoryAxis.configure(self.data)
        
        self.calcPositions()        
        
        g = Group()

        g.add(self.categoryAxis)
        g.add(self.valueAxis)
        g.add(self.makeBackground())
        g.add(self.makeLines())

        return g


class VerticalLineChart(LineChart):
    pass


def sample1():
    drawing = Drawing(400, 200)

    data = [
            (13, 5, 20, 22, 37, 45, 19, 4),
            (5, 20, 46, 38, 23, 21, 6, 14)
            ]
    
    lc = HorizontalLineChart()

    lc.x = 50
    lc.y = 50
    lc.height = 125
    lc.width = 300
    lc.data = data
    lc.joinedLines = 1
    lc.lines.symbol = makeFilledDiamond
    lc.lineLabelFormat = '%2.0f'

    catNames = string.split('Jan Feb Mar Apr May Jun Jul Aug', ' ')
    lc.categoryAxis.categoryNames = catNames
    lc.categoryAxis.labels.boxAnchor = 'n'

    lc.valueAxis.valueMin = 0
    lc.valueAxis.valueMax = 60
    lc.valueAxis.valueStep = 15
    
    drawing.add(lc)

    return drawing


class SampleHorizontalLineChart(HorizontalLineChart):
    "Sample class overwriting one method to draw additional horizontal lines."
    
    def demo(self):
        """Shows basic use of a line chart."""

        drawing = Drawing(200, 100)

        data = [
                (13, 5, 20, 22, 37, 45, 19, 4),
                (14, 10, 21, 28, 38, 46, 25, 5)
                ]
        
        lc = SampleHorizontalLineChart()

        lc.x = 20
        lc.y = 10
        lc.height = 85
        lc.width = 170
        lc.data = data
        lc.strokeColor = colors.white
        lc.fillColor = colors.HexColor(0xCCCCCC)

        drawing.add(lc)

        return drawing


    def makeBackground(self):
        g = Group()

        g.add(HorizontalLineChart.makeBackground(self))        

        valAxis = self.valueAxis
        valTickPositions = valAxis._tickValues

        for y in valTickPositions:
            y = valAxis.scale(y)
            g.add(Line(self.x, y, self.x+self.width, y,
                       strokeColor = self.strokeColor))
        
        return g



def sample1a():
    drawing = Drawing(400, 200)

    data = [
            (13, 5, 20, 22, 37, 45, 19, 4),
            (5, 20, 46, 38, 23, 21, 6, 14)
            ]

    lc = SampleHorizontalLineChart()

    lc.x = 50
    lc.y = 50
    lc.height = 125
    lc.width = 300
    lc.data = data
    lc.joinedLines = 1
    lc.strokeColor = colors.white
    lc.fillColor = colors.HexColor(0xCCCCCC)
    lc.lines.symbol = makeFilledDiamond
    lc.lineLabelFormat = '%2.0f'

    catNames = string.split('Jan Feb Mar Apr May Jun Jul Aug', ' ')
    lc.categoryAxis.categoryNames = catNames
    lc.categoryAxis.labels.boxAnchor = 'n'

    lc.valueAxis.valueMin = 0
    lc.valueAxis.valueMax = 60
    lc.valueAxis.valueStep = 15
    
    drawing.add(lc)

    return drawing


def sample2():
    drawing = Drawing(400, 200)

    data = [
            (13, 5, 20, 22, 37, 45, 19, 4),
            (5, 20, 46, 38, 23, 21, 6, 14)
            ]
    
    lc = HorizontalLineChart()

    lc.x = 50
    lc.y = 50
    lc.height = 125
    lc.width = 300
    lc.data = data
    lc.joinedLines = 1
    lc.lines.symbol = makeSmiley
    lc.lineLabelFormat = '%2.0f'
    lc.strokeColor = colors.black
    lc.fillColor = colors.lightblue

    catNames = string.split('Jan Feb Mar Apr May Jun Jul Aug', ' ')
    lc.categoryAxis.categoryNames = catNames
    lc.categoryAxis.labels.boxAnchor = 'n'

    lc.valueAxis.valueMin = 0
    lc.valueAxis.valueMax = 60
    lc.valueAxis.valueStep = 15
    
    drawing.add(lc)

    return drawing


def sample3():
    drawing = Drawing(400, 200)

    data = [
            (13, 5, 20, 22, 37, 45, 19, 4),
            (5, 20, 46, 38, 23, 21, 6, 14)
            ]
    
    lc = HorizontalLineChart()

    lc.x = 50
    lc.y = 50
    lc.height = 125
    lc.width = 300
    lc.data = data
    lc.joinedLines = 1
    lc.lineLabelFormat = '%2.0f'
    lc.strokeColor = colors.black

    lc.lines[0].symbol = makeSmiley
    lc.lines[1].symbol = NoEntry
    lc.lines[0].strokeWidth = 2
    lc.lines[1].strokeWidth = 4

    catNames = string.split('Jan Feb Mar Apr May Jun Jul Aug', ' ')
    lc.categoryAxis.categoryNames = catNames
    lc.categoryAxis.labels.boxAnchor = 'n'

    lc.valueAxis.valueMin = 0
    lc.valueAxis.valueMax = 60
    lc.valueAxis.valueStep = 15
    
    drawing.add(lc)

    return drawing
