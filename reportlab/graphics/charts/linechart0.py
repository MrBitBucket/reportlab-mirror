"""
This modules defines a very preliminary Line Chart example.
"""

import string
from types import FunctionType

from reportlab.lib import colors 
from reportlab.graphics.widgetbase import Widget, TypedPropertyCollection
from reportlab.graphics.charts.textlabel0 import Label
from reportlab.graphics.shapes import *
from reportlab.graphics.charts.textlabel0 import Label
from reportlab.graphics.charts.axes0 import XCategoryAxis, YValueAxis
      

class LineChart(Widget):
    """Line chart with multiple lines.

    Variants will be provided for ...,
    probably by running all three off a common base class."""

    _attrMap = {
        'debug':isNumber,
        'x':isNumber,
        'y':isNumber,
        'width':isNumber,
        'height':isNumber,

        'useAbsolute':isNumber,
        'barWidth':isNumber,
        'barLabelNudge':isNumber,
        'groupSpacing':isNumber,
        'barSpacing':isNumber,

        'joinedLines':isNumber,
        'blobLength':isNumber,

        'strokeColor':isColorOrNone,
        'fillColor':isColorOrNone,

        'defaultColors':SequenceOf(isColor),

        'categoryAxis':None,
        'categoryNames':isListOfStrings,
        'valueAxis':None,
        'data':None,
        'barLabels':None,
        'barLabelFormat':None
        }

    def __init__(self):
        self.debug = 0

        self.x = 0
        self.y = 0
        self.width = 200
        self.height = 100

        # allow for a bounding rectangle
        self.strokeColor = None
        self.fillColor = None

        # named so we have less recoding for the horizontal one :-)
        self.categoryAxis = XCategoryAxis()
        self.valueAxis = YValueAxis()

        # this defines two series of 3 points.  Just an example.
        self.data = [(100,110,120,130),
                     (70, 80, 80, 90)]        
        self.categoryNames = ('North','South','East','West')
        # we really need some well-designed default lists of
        # colors e.g. from Tufte.  These will be used in a
        # cycle to set the fill color of each series.
        self.defaultColors = [colors.red, colors.green, colors.blue]

        # control bar spacing. is useAbsolute = 1 then
        # the next parameters are in points; otherwise
        # they are 'proportions' and are normalized to
        # fit the available space.  Half a barSpacing
        # is allocated at the beginning and end of the
        # chart.
        self.useAbsolute = 0   #- not done yet
        self.barWidth = 0 # 10
        self.groupSpacing = 5
        self.barSpacing = 0

        self.barLabels = TypedPropertyCollection(Label)
        self.barLabelFormat = None

        # this says whether the origin is inside or outside
        # the bar - +10 means put the origin ten points
        # above the tip of the bar if value > 0, or ten
        # points inside if bar value < 0.  This is different
        # to label dx/dy which are not dependent on the
        # sign of the data.
        self.barLabelNudge = 10
        # if you have multiple series, by default they butt
        # together.

        # New line chart attributes.
        self.joinedLines = 1 # Connect items with straight lines.
        self.blobLength = 5  # Lenght of sqaure blobs (when unconnected).


    def demo(self):
        """Shows basic use of a line chart."""

        drawing = Drawing(200, 100)

        data = [
                (13, 5, 20, 22, 37, 45, 19, 4),
                (14, 10, 21, 28, 38, 46, 25, 5)
                ]
        
        lc = LineChart()
        lc.x = 10
        lc.y = 10
        lc.height = 85
        lc.width = 90
        lc.data = data
        drawing.add(lc)

        return drawing


    def calcBarPositions(self):
        """Works out where they go.

        Sets an attribute _barPositions which is a list of
        lists of (x, y, width, height) matching the data."""

        self._seriesCount = len(self.data)
        self._rowLength = len(self.data[0])
        
        if self.useAbsolute:
            # bar dimensions are absolute
            normFactor = 1.0
        else:
            # bar dimensions are normalized to fit.  How wide
            # notionally is one group of bars?
            normWidth = (self.groupSpacing 
                        + (self._seriesCount * self.barWidth) 
                        + ((self._seriesCount - 1) * self.barSpacing)
                        )
            availWidth = self.categoryAxis.scale(0)[1]
            normFactor = availWidth / normWidth
            if self.debug:
                print '%d series, %d points per series' % (self._seriesCount, self._rowLength)
                print 'width = %d group + (%d bars * %d barWidth) + (%d gaps * %d interBar) = %d total' % (
                    self.groupSpacing, self._seriesCount, self.barWidth,
                    self._seriesCount - 1, self.barSpacing, normWidth)
        
        self._barPositions = []
        for rowNo in range(len(self.data)):
            barRow = []
            for colNo in range(len(self.data[0])):
                datum = self.data[rowNo][colNo]

                (groupX, groupWidth) = self.categoryAxis.scale(colNo)
                x = (groupX +
                     (0.5 * self.groupSpacing * normFactor) +
                     (rowNo * self.barWidth * normFactor) +
                     (rowNo * self.barSpacing * normFactor)
                     )
                width = self.barWidth * normFactor
                     
                y = self.valueAxis.scale(0)
                height = self.valueAxis.scale(datum) - y
                barRow.append((x, y, width, height))
            self._barPositions.append(barRow)
        

    def draw(self):
        self.valueAxis.configure(self.data)
        self.valueAxis.setPosition(self.x, self.y, self.height)

        # if zero is in chart, put x axis there, otherwise
        # use bottom.
        xAxisCrossesAt = self.valueAxis.scale(0)
        if ((xAxisCrossesAt > self.y + self.height) or (xAxisCrossesAt < self.y)):
            self.categoryAxis.setPosition(self.x, self.y, self.width)
        else:
            self.categoryAxis.setPosition(self.x, xAxisCrossesAt, self.width)

        self.categoryAxis.configure(self.data)
        
        self.calcBarPositions()        
        
        g = Group()

        # debug mode - show border
        g.add(Rect(self.x, self.y,
                   self.width, self.height,
                   strokeColor = self.strokeColor,
                   fillColor= self.fillColor))
        
        g.add(self.categoryAxis)
        g.add(self.valueAxis)

        labelFmt = self.barLabelFormat

        # Iterate over data rows.        
        for rowNo in range(len(self._barPositions)):
            row = self._barPositions[rowNo]
            colorCount = len(self.defaultColors)
            colorIdx = rowNo % colorCount
            rowColor = self.defaultColors[colorIdx]

            # Iterate over data columns.        
            if self.joinedLines == 1:
                startIndex = 1
            else:
                startIndex = 0
            for colNo in range(startIndex, len(row)):
                barPos1 = row[colNo]
                (x1, y1, width1, height1) = barPos1
                if self.joinedLines == 1:
                    barPos0 = row[colNo-1]
                    (x0, y0, width0, height0) = barPos0
                    line = Line(x0, y0+height0, x1, y1+height1)
                    line.strokeColor = rowColor
                    g.add(line)
                else:
                    d = self.blobLength/2.0
                    rect = Rect(x1-d, y1+height1-d, 2*d, 2*d)
                    rect.fillColor = rowColor
                    rect.strokeColor = rowColor
                    g.add(rect)

                # Draw item (bar) labels.
                if self.joinedLines == 1:
                    self.drawLabel(g, rowNo, colNo-1, x0, y0, width0, height0)
                self.drawLabel(g, rowNo, colNo, x1, y1, width1, height1)

        return g


    def drawLabel(self, group, rowNo, colNo, x1, y1, width1, height1):
        "Draw a label for a given item in the list."

        labelFmt = self.barLabelFormat

        if labelFmt is None:
            labelText = None
        elif type(labelFmt) is StringType:
            labelText = labelFmt % self.data[rowNo][colNo]
        elif type(labelFmt) is FunctionType:
            labelText = labelFmt(self.data[rowNo][colNo])
        else:
            msg = "Unknown formatter type %s, expected string or function"  
            raise Exception, msg % labelFmt

        if labelText:
            label = self.barLabels[(rowNo, colNo)]
            #hack to make sure labels are outside the bar
            if height1 > 0:
                label.setOrigin(x1 + 0.5*width1, y1 + height1 + self.barLabelNudge)
            else:
                label.setOrigin(x1 + 0.5*width1, y1 + height1 - self.barLabelNudge)
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
    lc.barLabelFormat = '%2.0f'

    lc.strokeColor = colors.yellow  # visible border

    lc.valueAxis.valueMin = 0
    lc.valueAxis.valueMax = 60
    lc.valueAxis.valueStep = 15
    
    lc.categoryAxis.labels.boxAnchor = 'ne'
    lc.categoryAxis.labels.dx = 8
    lc.categoryAxis.labels.dy = -2
    lc.categoryAxis.labels.angle = 30

    catNames = string.split('Jan Feb Mar Apr May Jun Jul Aug', ' ')
    catNames = map(lambda n:n+'-99', catNames)
    lc.categoryAxis.categoryNames = catNames
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
    lc.joinedLines = 0
    lc.barLabelFormat = '%2.0f'

    lc.strokeColor = colors.yellow  # visible border

    lc.valueAxis.valueMin = 0
    lc.valueAxis.valueMax = 60
    lc.valueAxis.valueStep = 15
    
    lc.categoryAxis.labels.boxAnchor = 'ne'
    lc.categoryAxis.labels.dx = 8
    lc.categoryAxis.labels.dy = -2
    lc.categoryAxis.labels.angle = 30

    catNames = string.split('Jan Feb Mar Apr May Jun Jul Aug', ' ')
    catNames = map(lambda n:n+'-99', catNames)
    lc.categoryAxis.categoryNames = catNames
    drawing.add(lc)

    return drawing
