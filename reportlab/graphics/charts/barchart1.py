"""
This modules defines a variety of Bar Chart components.

The basic flavors are Side-by-side, stacked and 100% bar charts,
available in horizontal and vertical versions.
"""
#chartparts - candidate components for a chart library.

import string
from types import FunctionType

from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.lib import colors 
from reportlab.graphics.widgetbase import Widget, TypedPropertyCollection
from reportlab.graphics.shapes import *
from reportlab.graphics.charts.textlabel0 import Label
from reportlab.graphics.charts.axes0 import XCategoryAxis, YValueAxis
from reportlab.graphics.charts.axes0 import YCategoryAxis, XValueAxis
      

# Bar chart classes

class VerticalBarChart(Widget):
    """Bar chart with multiple side-by-side bars.

    Variants will be provided for stacked and 100% charts,
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
        self.barWidth = 10
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
        self.barLabelNudge = 0
        # if you have multiple series, by default they butt
        # together.


    def demo(self):
        """Shows basic use of a bar chart"""
        drawing = Drawing(200, 100)

        data = [
                (13, 5, 20, 22, 37, 45, 19, 4),
                (14, 6, 21, 23, 38, 46, 20, 5)
                ]
        
        bc = VerticalBarChart()
        bc.x = 10
        bc.y = 10
        bc.height = 85
        bc.width = 90
        bc.data = data
        drawing.add(bc)
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
        
        for rowNo in range(len(self._barPositions)):
            row = self._barPositions[rowNo]
            colorCount = len(self.defaultColors)
            colorIdx = rowNo % colorCount
            rowColor = self.defaultColors[colorIdx]
            for colNo in range(len(row)):
                barPos = row[colNo]
                (x, y, width, height) = barPos
                r = Rect(x, y, width, height)
                r.fillColor = rowColor
                r.strokeColor = colors.black
                g.add(r)

                if labelFmt is None:
                    labelText = None
                elif type(labelFmt) is StringType:
                    labelText = labelFmt % self.data[rowNo][colNo]
                elif type(labelFmt) is FunctionType:
                    labelText = labelFmt(self.data[rowNo][colNo])
                else:
                    raise Exception, "Unknown formatter type %s, expected string or function" % labelFmt

                # We currently overwrite the boxAnchor with 'c' and display
                # it at a constant offset to the bar's top/bottom determined
                # by the barLabelNudge attribute.
                if labelText:
                    label = self.barLabels[(rowNo, colNo)]
                    labelWidth = stringWidth(labelText, label.fontName, label.fontSize)                    

                    sign = lambda v:[-1, 1][v>=0] # Where the heck is this function??
                    y0 = y + height + sign(height) * self.barLabelNudge
                    x0 = x + 0.5*width
                    label.boxAnchor = 'c' # saves a lot of correcting code like this:...
##                    if label.boxAnchor in ('w', 'sw', 'nw'):
##                        x0 = x0 - 0.5*labelWidth
##                    elif label.boxAnchor in ('e', 'se', 'ne'):
##                        x0 = x0 + 0.5*labelWidth
##                    elif label.boxAnchor == 'c':
##                        pass
                    label.setOrigin(x0, y0)
                    label.setText(labelText)

                    g.add(label)

        return g
        

# Samples

def sample0a():
    "Make a slightly pathologic bar chart with only TWO data items."
    
    drawing = Drawing(400, 200)

    data = [(13, 20)]
    
    bc = VerticalBarChart()
    bc.x = 50
    bc.y = 50
    bc.height = 125
    bc.width = 300
    bc.data = data

    bc.strokeColor = colors.black

    bc.valueAxis.valueMin = 0
    bc.valueAxis.valueMax = 60
    bc.valueAxis.valueStep = 15
    
    bc.categoryAxis.labels.boxAnchor = 'ne'
    bc.categoryAxis.labels.dx = 8
    bc.categoryAxis.labels.dy = -2
    bc.categoryAxis.labels.angle = 30
    bc.categoryAxis.categoryNames = ['Ying', 'Yang']

    drawing.add(bc)

    return drawing    

    
def sample0b():
    "Make a pathologic bar chart with only ONE data item."
    
    drawing = Drawing(400, 200)

    data = [(42,)]
    
    bc = VerticalBarChart()
    bc.x = 50
    bc.y = 50
    bc.height = 125
    bc.width = 300
    bc.data = data
    bc.strokeColor = colors.black

    bc.valueAxis.valueMin = 0
    bc.valueAxis.valueMax = 50
    bc.valueAxis.valueStep = 15
    
    bc.categoryAxis.labels.boxAnchor = 'ne'
    bc.categoryAxis.labels.dx = 8
    bc.categoryAxis.labels.dy = -2
    bc.categoryAxis.labels.angle = 30
    bc.categoryAxis.categoryNames = ['Jan-99']

    drawing.add(bc)

    return drawing    

    
def sample0c():
    "Make a really pathologic bar chart with NO data items at all!"
    
    drawing = Drawing(400, 200)

    data = [()]
    
    bc = VerticalBarChart()
    bc.x = 50
    bc.y = 50
    bc.height = 125
    bc.width = 300
    bc.data = data
    bc.strokeColor = colors.black

    bc.valueAxis.valueMin = 0
    bc.valueAxis.valueMax = 60
    bc.valueAxis.valueStep = 15
    
    bc.categoryAxis.labels.boxAnchor = 'ne'
    bc.categoryAxis.labels.dx = 8
    bc.categoryAxis.labels.dy = -2
    bc.categoryAxis.categoryNames = []

    drawing.add(bc)

    return drawing    

    
def sample1():
    drawing = Drawing(400, 200)

    data = [
            (13, 5, 20, 22, 37, 45, 19, 4),
            (14, 6, 21, 23, 38, 46, 20, 5)
            ]
    
    bc = VerticalBarChart()
    bc.x = 50
    bc.y = 50
    bc.height = 125
    bc.width = 300
    bc.data = data
    bc.strokeColor = colors.black

    bc.valueAxis.valueMin = 0
    bc.valueAxis.valueMax = 60
    bc.valueAxis.valueStep = 15
    
    bc.categoryAxis.labels.boxAnchor = 'ne'
    bc.categoryAxis.labels.dx = 8
    bc.categoryAxis.labels.dy = -2
    bc.categoryAxis.labels.angle = 30

    catNames = string.split('Jan Feb Mar Apr May Jun Jul Aug', ' ')
    catNames = map(lambda n:n+'-99', catNames)
    bc.categoryAxis.categoryNames = catNames
    drawing.add(bc)

    return drawing    

    
def sample2a():
    "Sample of multi-series bar chart."
    
    data = [(2.4, -5.7, 2, 5, 9.2),
            (0.6, -4.9, -3, 4, 6.8)
            ]

    labels = ("Q3 2000", "Year to Date", "12 months", "Annualised\n3 years", "Since 07.10.99")

    drawing = Drawing(400, 200)

    bc = VerticalBarChart()
    bc.x = 50
    bc.y = 50
    bc.height = 120
    bc.width = 300
    bc.data = data

    bc.barSpacing = 0
    bc.groupSpacing = 10
    bc.barWidth = 10
    
    bc.valueAxis.valueMin = -15
    bc.valueAxis.valueMax = +15
    bc.valueAxis.valueStep = 5
    bc.valueAxis.labels.fontName = 'Helvetica'
    bc.valueAxis.labels.fontSize = 8    
    bc.valueAxis.labels.boxAnchor = 'n'   # irrelevant (becomes 'c')
    bc.valueAxis.labels.textAnchor = 'middle'

    bc.categoryAxis.categoryNames = labels
    bc.categoryAxis.labels.fontName = 'Helvetica'
    bc.categoryAxis.labels.fontSize = 8
    bc.categoryAxis.labels.dy = -60
    
    drawing.add(bc)    

    return drawing


def sample2b():
    "Sample of multi-series bar chart."

    data = [(2.4, -5.7, 2, 5, 9.2),
            (0.6, -4.9, -3, 4, 6.8)
            ]

    labels = ("Q3 2000", "Year to Date", "12 months", "Annualised\n3 years", "Since 07.10.99")

    drawing = Drawing(400, 200)

    bc = VerticalBarChart()
    bc.x = 50
    bc.y = 50
    bc.height = 120
    bc.width = 300
    bc.data = data

    bc.barSpacing = 5
    bc.groupSpacing = 10
    bc.barWidth = 10
    
    bc.valueAxis.valueMin = -15
    bc.valueAxis.valueMax = +15
    bc.valueAxis.valueStep = 5
    bc.valueAxis.labels.fontName = 'Helvetica'
    bc.valueAxis.labels.fontSize = 8    
    bc.valueAxis.labels.boxAnchor = 'n'   # irrelevant (becomes 'c')
    bc.valueAxis.labels.textAnchor = 'middle'

    bc.categoryAxis.categoryNames = labels
    bc.categoryAxis.labels.fontName = 'Helvetica'
    bc.categoryAxis.labels.fontSize = 8
    bc.categoryAxis.labels.dy = -60
    
    drawing.add(bc)    

    return drawing


def sample2c():

    data = [(2.4, -5.7, 2, 5, 9.99),
            (0.6, -4.9, -3, 4, 9.99)
            ]

    labels = ("Q3 2000", "Year to Date", "12 months", "Annualised\n3 years", "Since 07.10.99")

    drawing = Drawing(400, 200)

    bc = VerticalBarChart()
    bc.x = 50
    bc.y = 50
    bc.height = 120
    bc.width = 300
    bc.data = data

    bc.barSpacing = 2
    bc.groupSpacing = 10
    bc.barWidth = 10
    
    bc.valueAxis.valueMin = -15
    bc.valueAxis.valueMax = +15
    bc.valueAxis.valueStep = 5
    bc.valueAxis.labels.fontName = 'Helvetica'
    bc.valueAxis.labels.fontSize = 8    

    bc.categoryAxis.categoryNames = labels
    bc.categoryAxis.labels.fontName = 'Helvetica'
    bc.categoryAxis.labels.fontSize = 8
    bc.valueAxis.labels.boxAnchor = 'n'
    bc.valueAxis.labels.textAnchor = 'middle'
    bc.categoryAxis.labels.dy = -60

    bc.barLabelNudge = 10
    
    bc.barLabelFormat = '%0.2f'
    bc.barLabels.dx = 0
    bc.barLabels.dy = 0
    bc.barLabels.boxAnchor = 'n'  # irrelevant (becomes 'c')
    bc.barLabels.fontName = 'Helvetica'
    bc.barLabels.fontSize = 6

    drawing.add(bc)    

    return drawing


def sample3():
    """Two side-by-side vertical bar charts"""

    names = ("UK Equities", "US Equities", "European Equities", "Japanese Equities",
              "Pacific (ex Japan) Equities", "Emerging Markets Equities",
              "UK Bonds", "Overseas Bonds", "UK Index-Linked", "Cash")
    series1 = (-1.5, 0.3, 0.5, 1.0, 0.8, 0.7, 0.4, 0.1, 1.0, 0.3)
    
    series2 = (0.0, 0.33, 0.55, 1.1, 0.88, 0.77, 0.44, 0.11, 1.10, 0.33)

    assert len(names) == len(series1), "bad data"
    assert len(names) == len(series2), "bad data"
    
    drawing = Drawing(400, 200)

    leftChart = VerticalBarChart()
    leftChart.x = 0
    leftChart.y = 0
    leftChart.height = 100
    leftChart.width = 150
    leftChart.data = (series1,)
    leftChart.defaultColors = (colors.green,)

    leftChart.barLabelFormat = '%0.2f'
    leftChart.barLabels.dx = 0
    leftChart.barLabels.dy = 0
    leftChart.barLabels.boxAnchor = 'w' # irrelevant (becomes 'c')
    leftChart.barLabels.angle = 90
    leftChart.barLabels.fontName = 'Helvetica'
    leftChart.barLabels.fontSize = 6
    leftChart.barLabelNudge = 10
    
    leftChart.valueAxis.visible = 0
    leftChart.valueAxis.valueMin = -2
    leftChart.valueAxis.valueMax = +2
    leftChart.valueAxis.valueStep = 1

    leftChart.categoryAxis.tickUp = 0
    leftChart.categoryAxis.tickDown = 0
    leftChart.categoryAxis.categoryNames = names
    leftChart.categoryAxis.labels.angle = 90
    leftChart.categoryAxis.labels.boxAnchor = 'w'
    leftChart.categoryAxis.labels.dx = 0
    leftChart.categoryAxis.labels.dy = -125
    leftChart.categoryAxis.labels.fontName = 'Helvetica'
    leftChart.categoryAxis.labels.fontSize = 6
        
    g = Group(leftChart)
    g.translate(100, 175)
    g.rotate(-90)
    
    drawing.add(g)    

    return drawing
