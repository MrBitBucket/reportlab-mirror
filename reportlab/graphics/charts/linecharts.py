"""
This modules defines a very preliminary Line Chart example.
"""

import string
from types import FunctionType

from reportlab.lib import colors 
from reportlab.graphics.shapes import *
from reportlab.graphics.widgetbase import Widget, TypedPropertyCollection
from reportlab.graphics.widgets.signsandsymbols import SmileyFace0
from reportlab.graphics.charts.textlabels import Label
from reportlab.graphics.charts.axes import XCategoryAxis, YValueAxis
      

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

        
class LineChart(Widget):
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
        usedSymbol: function returning a widget placed at data points

        strokeColor: color of chart lines (?)
        fillColor: color for chart background (?)
        defaultColors: color list, used cyclically for data series

        valueAxis: value axis object
        categoryAxis: category axis object
        categoryNames: category names

        data: chart data, a list of data series of equal length
    """

    _attrMap = {
        'x':isNumber,
        'y':isNumber,
        'width':isNumber,
        'height':isNumber,

        'useAbsolute':isNumber,
        'lineLabelNudge':isNumber,
        'lineLabels':None,
        'lineLabelFormat':None,
        'groupSpacing':isNumber,

        'joinedLines':isNumber,
        'usedSymbol':None,

        'strokeColor':isColorOrNone,
        'fillColor':isColorOrNone,
        'defaultColors':SequenceOf(isColor),

        'valueAxis':None,
        'categoryAxis':None,
        'categoryNames':isListOfStrings,

        'data':None
        }

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
        # we really need some well-designed default lists of
        # colors e.g. from Tufte.  These will be used in a
        # cycle to set the fill color of each series.
        self.defaultColors = [colors.red, colors.green, colors.blue]

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
        self.usedSymbol = makeFilledSquare


    def demo(self):
        """Shows basic use of a line chart."""

        drawing = Drawing(200, 100)

        data = [
                (13, 5, 20, 22, 37, 45, 19, 4),
                (14, 10, 21, 28, 38, 46, 25, 5)
                ]
        
        lc = LineChart()

        lc.x = 20
        lc.y = 10
        lc.height = 85
        lc.width = 170
        lc.data = data

        drawing.add(lc)

        return drawing


    def calcPositions(self):
        """Works out where they go.

        Sets an attribute _positions which is a list of
        lists of (x, y) matching the data."""

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
        

    def draw(self):
        "Draws itself."
        
        self.valueAxis.configure(self.data)
        self.valueAxis.setPosition(self.x, self.y, self.height)

        # If zero is in chart, put x axis there, otherwise
        # use bottom.
        xAxisCrossesAt = self.valueAxis.scale(0)
        if ((xAxisCrossesAt > self.y + self.height) or (xAxisCrossesAt < self.y)):
            self.categoryAxis.setPosition(self.x, self.y, self.width)
        else:
            self.categoryAxis.setPosition(self.x, xAxisCrossesAt, self.width)

        self.categoryAxis.configure(self.data)
        
        self.calcPositions()        
        
        g = Group()

        # debug mode - show border
        g.add(Rect(self.x, self.y,
                   self.width, self.height,
                   strokeColor = self.strokeColor,
                   fillColor= self.fillColor))
        
        g.add(self.categoryAxis)
        g.add(self.valueAxis)

        labelFmt = self.lineLabelFormat

        # Iterate over data rows.        
        for rowNo in range(len(self._positions)):
            row = self._positions[rowNo]
            colorCount = len(self.defaultColors)
            colorIdx = rowNo % colorCount
            rowColor = self.defaultColors[colorIdx]

            # Iterate over data columns.        
            for colNo in range(len(row)):
                x1, y1 = row[colNo]
                if self.joinedLines == 1:
                    if colNo > 0:
                        # Draw lines between adjacent items.
                        x2, y2 = row[colNo-1]
                        line = Line(x1, y1, x2, y2)
                        line.strokeColor = rowColor
                        g.add(line)

            # Iterate once more over data columns
            # (to make sure symbols and labels are on top).
            for colNo in range(len(row)):
                x1, y1 = row[colNo]
                # Draw a symbol for each data item.
                symbol = self.usedSymbol(x1, y1, 5, rowColor)
                g.add(symbol)

                # Draw item labels.
                self.drawLabel(g, rowNo, colNo, x1, y1)

        return g


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


def sample1():
    drawing = Drawing(400, 200)

    data = [
            (13, 5, 20, 22, 37, 45, 19, 4),
            (5, 20, 46, 38, 23, 21, 6, 14)
            ]
    
    lc = LineChart()

    lc.x = 50
    lc.y = 50
    lc.height = 125
    lc.width = 300
    lc.data = data
    lc.joinedLines = 1
    lc.usedSymbol = makeFilledDiamond
    lc.lineLabelFormat = '%2.0f'
##    lc.strokeColor = colors.yellow

    catNames = string.split('Jan Feb Mar Apr May Jun Jul Aug', ' ')
    catNames = map(lambda n:n+'-99', catNames)
    lc.categoryAxis.categoryNames = catNames
    lc.categoryAxis.labels.boxAnchor = 'ne'
    lc.categoryAxis.labels.dx = 8
    lc.categoryAxis.labels.dy = -2
    lc.categoryAxis.labels.angle = 30

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
    
    lc = LineChart()

    lc.x = 50
    lc.y = 50
    lc.height = 125
    lc.width = 300
    lc.data = data
    lc.joinedLines = 1
    lc.usedSymbol = makeSmiley
    lc.lineLabelFormat = '%2.0f'
    lc.strokeColor = colors.black
    lc.fillColor = colors.lightblue

    catNames = string.split('Jan Feb Mar Apr May Jun Jul Aug', ' ')
    catNames = map(lambda n:n+'-99', catNames)
    lc.categoryAxis.categoryNames = catNames
    lc.categoryAxis.labels.boxAnchor = 'ne'
    lc.categoryAxis.labels.dx = 8
    lc.categoryAxis.labels.dy = -2
    lc.categoryAxis.labels.angle = 30

    lc.valueAxis.valueMin = 0
    lc.valueAxis.valueMax = 60
    lc.valueAxis.valueStep = 15
    
    drawing.add(lc)

    return drawing
