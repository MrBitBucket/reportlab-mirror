"""
This modules defines a very preliminary Line Plot example.
"""

import string, time
from types import FunctionType

from reportlab.lib import colors 
from reportlab.graphics.widgetbase import Widget, TypedPropertyCollection
from reportlab.graphics.widgets.signsandsymbols import SmileyFace0
from reportlab.graphics.charts.textlabel0 import Label
from reportlab.graphics.shapes import *
from reportlab.graphics.charts.textlabel0 import Label
from reportlab.graphics.charts.axes0 import XValueAxis, YValueAxis, XTimeValueAxis
      

def mkTimeTuple(timeString):
    "Convert a string to a tuple for use in the time module."

    list = [0] * 9
    dd, mm, yyyy = map(int, string.split(timeString, '/'))
    list[:3] = [yyyy, mm, dd]
    
    return tuple(list)

    
def str2seconds(timeString):
    "Convert a number of seconds since the epoch into a date string."
    return time.mktime(mkTimeTuple(timeString))


def seconds2str(seconds):
    "Convert a date string into the number of seconds since the epoch."
    return time.strftime('%Y-%m-%d', time.gmtime(seconds))


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

        
class LinePlot(Widget):
    """Line plot with multiple lines.

    Both x- and y-axis are value axis.
    """

    _attrMap = {
        'debug':isNumber,
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

        'xValueAxis':None,
        'yValueAxis':None,
        'data':None
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
        self.xValueAxis = XTimeValueAxis()
        self.yValueAxis = YValueAxis()

        # this defines two series of 3 points.  Just an example.
        self.data = [(100,110,120,130),
                     (70, 80, 80, 90)]        
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
        self.usedSymbol = makeFilledSquare


    def demo(self):
        """Shows basic use of a line chart."""

        drawing = Drawing(200, 100)

        return drawing

##        data = [
##                (13, 5, 20, 22, 37, 45, 19, 4),
##                (5, 20, 46, 38, 23, 21, 6, 14)
##                ]
##        
##        lc = LinePlot()
##        lc.x = 10
##        lc.y = 10
##        lc.height = 85
##        lc.width = 90
##        lc.data = data
##
##        lc.xValueAxis.valueMin = 0
##        lc.xValueAxis.valueMax = len(lc.data[0])
##        lc.xValueAxis.valueStep = 1
##
##        drawing.add(lc)
##
##        return drawing


    def calcPositions(self):
        """Works out where they go.

        Sets an attribute _positions which is a list of
        lists of (x, y) matching the data."""

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
                    x = self.xValueAxis.scale(time.mktime(mkTimeTuple(datum[0])))
                else:
                    x = self.xValueAxis.scale(datum[0])
                y = self.yValueAxis.scale(datum[1])
                line.append((x, y))
            self._positions.append(line)


    def draw(self):
        self.yValueAxis.configure(self.data)
        self.yValueAxis.setPosition(self.x, self.y, self.height)

        # if zero is in chart, put x axis there, otherwise
        # use bottom.
        xAxisCrossesAt = self.yValueAxis.scale(0)
        if ((xAxisCrossesAt > self.y + self.height) or (xAxisCrossesAt < self.y)):
            self.xValueAxis.setPosition(self.x, self.y, self.width)
        else:
            self.xValueAxis.setPosition(self.x, xAxisCrossesAt, self.width)

        self.xValueAxis.configure(self.data)
        
        self.calcPositions()        
        
        g = Group()

        # debug mode - show border
        g.add(Rect(self.x, self.y,
                   self.width, self.height,
                   strokeColor = self.strokeColor,
                   fillColor= self.fillColor))
        
        g.add(self.xValueAxis)
        g.add(self.yValueAxis)

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

                # Draw item (bar) labels.
                self.drawLabel(g, rowNo, colNo, x1, y1)

        return g


    def drawLabel(self, group, rowNo, colNo, x, y):
        "Draw a label for a given item in the list."

        pass
##        labelFmt = self.lineLabelFormat
##        labelValue = self.data[rowNo][colNo]
##        
##        if labelFmt is None:
##            labelText = None
##        elif type(labelFmt) is StringType:
##            labelText = labelFmt % labelValue
##        elif type(labelFmt) is FunctionType:
##            labelText = labelFmt(labelValue)
##        else:
##            msg = "Unknown formatter type %s, expected string or function"  
##            raise Exception, msg % labelFmt
##
##        if labelText:
##            label = self.lineLabels[(rowNo, colNo)]
##            #hack to make sure labels are outside the bar
##            if y > 0:
##                label.setOrigin(x, y + self.lineLabelNudge)
##            else:
##                label.setOrigin(x, y - self.lineLabelNudge)
##            label.setText(labelText)
##            group.add(label)


def sample0():
    "A line plot with non-equidistant points in x-axis."
    
    drawing = Drawing(400, 200)

    data = [
        ((1,1), (2,2), (2.5,1), (3,3), (4,5)),
        ((1,2), (2,3), (2.5,2), (3,4), (4,6))
        ]
    
    lp = LinePlot()

    lp.x = 50
    lp.y = 50
    lp.height = 125
    lp.width = 300
    lp.data = data
    lp.joinedLines = 1
    lp.usedSymbol = makeFilledDiamond
    lp.lineLabelFormat = '%2.0f'
    lp.strokeColor = colors.black

    lp.xValueAxis.valueMin = 0
    lp.xValueAxis.valueMax = 7
    lp.xValueAxis.valueStep = 1

    lp.yValueAxis.valueMin = 0
    lp.yValueAxis.valueMax = 7
    lp.yValueAxis.valueStep = 1
    
    drawing.add(lp)

    return drawing


def sample1():
    "A line plot with non-equidistant points in x-axis."
    
    drawing = Drawing(400, 200)

    data = [
        ((1,1), (2,2), (2.5,1), (3,3), (4,5)),
        ((1,2), (2,3), (2.5,2), (3,4), (4,6))
        ]
    
    lp = LinePlot()

    lp.x = 50
    lp.y = 50
    lp.height = 125
    lp.width = 300
    lp.data = data
    lp.joinedLines = 1
    lp.usedSymbol = makeFilledDiamond
    lp.lineLabelFormat = '%2.0f'
    lp.strokeColor = colors.black

    lp.xValueAxis.valueMin = 0
    lp.xValueAxis.valueMax = 7
    lp.xValueAxis.valueSteps = [1, 2, 2.5, 3, 4, 5]
    lp.xValueAxis.labelTextFormat = '%2.1f'

    lp.yValueAxis.valueMin = 0
    lp.yValueAxis.valueMax = 7
    lp.yValueAxis.valueStep = 1
    
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
    lp.usedSymbol = makeFilledDiamond
    lp.lineLabelFormat = '%4.2f'
    lp.strokeColor = colors.black

    start = time.mktime(mkTimeTuple('25/11/1991'))
    t0 = time.mktime(mkTimeTuple('30/11/1991'))
    t1 = time.mktime(mkTimeTuple('31/12/1991'))
    t2 = time.mktime(mkTimeTuple('31/03/1992'))
    t3 = time.mktime(mkTimeTuple('30/06/1992'))
    t4 = time.mktime(mkTimeTuple('30/09/1992'))
    end = time.mktime(mkTimeTuple('31/12/1992'))
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

##ID_ICRS,PriceTypeID,Date,Fund ROR,IndexROR
##41,4,25/11/1991 00:00,1,1
##41,4,30/11/1991 00:00,1.000933333,1.000895188
##41,4,31/12/1991 00:00,1.0062,1.006259951
##41,4,31/01/1992 00:00,1.0112,1.01165347
##41,4,29/02/1992 00:00,1.0158,1.017224821
##41,4,31/03/1992 00:00,1.020733333,1.022776967
##41,4,30/04/1992 00:00,1.026133333,1.028108211
##41,4,31/05/1992 00:00,1.030266667,1.033061804
##41,4,30/06/1992 00:00,1.034466667,1.037424855
##41,4,31/07/1992 00:00,1.038733333,1.041857904
##41,4,31/08/1992 00:00,1.0422,1.045738637
##41,4,30/09/1992 00:00,1.045533333,1.052416182
##41,4,31/10/1992 00:00,1.049866667,1.058263606
##41,4,30/11/1992 00:00,1.054733333,1.065175179
##41,4,31/12/1992 00:00,1.061,1.07088448
