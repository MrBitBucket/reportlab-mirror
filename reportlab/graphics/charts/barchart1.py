#chartparts - candidate components for a chart library.
from reportlab.graphics.widgetbase import Widget
from reportlab.graphics.charts.piechart0 import TypedPropertyCollection
from reportlab.graphics.shapes import *
from reportlab.lib.colors import *


from reportlab.graphics.charts.textlabel0 import Label

    
      
class XCategoryAxis(Widget):
    """Comes in 'X' and 'Y' flavours.  A 'category axis' has an ordering
    but no metric.  It is divided into a number of equal-sized buckets.
    There may be tick marks or labels BETWEEN the buckets, and a label
    below it. The chart tells it where to go"""

    def __init__(self):
        # private properties set by methods.  The initial values
        # here are to make demos easy; they would always be
        # overridden in real life.
        self._x = 50
        self._y = 50
        self._width = 100
        self._catCount = 0
        # public properties


        self.strokeWidth = 1
        self.strokeColor = STATE_DEFAULTS['strokeColor']
        self.strokeDashArray = STATE_DEFAULTS['strokeColor']
        self.labels = TypedPropertyCollection(Label)
        self.labels.boxAnchor = 'n' #north - top edge
        self.labels.dy = -5 

        # ultra-simple tick marks for now go between categories
        # and have same line style as axis - need more
        self.tickUp = 0  # how far into chart does tick go?
        self.tickDown = 5  # how far below axis does tick go?

        # idea - can we represent a gridline as just a great
        # big tickmark which sticks in rather than out?  Would
        # one ever want both of them?
        #self.tickMarks = TypedPropertyCollection(TickMark)
        
        # if None, they don't get labels.  If provided,
        # you need one name per data point and they are
        # used for label text.
        self.categoryNames = None

    def demo(self):
        self.setPosition(30, 70, 140)
        self.setData([(10,20,30,40,50)])
        self.categoryNames = ['One','Two','Three','Four','Five']
        # all labels top-centre aligned apart from the last
        self.labels.boxAnchor = 'n'
        self.labels[4].boxAnchor = 'e'
        self.labels[4].angle = 90
        
        d = Drawing(200, 100)
        d.add(self)
        return d

    def setPosition(self, x, y, length):
        # ensure floating point
        self._x = x * 1.0
        self._y = y * 1.0
        self._length = length * 1.0

    def setData(self, multiSeries):
        self._catCount = len(multiSeries[0])
        
    def draw(self):
        g = Group()

        # is this the code style Aaron objects to?  why?        
        axis = Line(self._x, self._y, self._x + self._length, self._y)
        axis.strokeColor = self.strokeColor
        axis.strokeWidth = self.strokeWidth
        axis.strokeDashArray = self.strokeDashArray
        g.add(axis)

        if (self.tickUp <> self.tickDown):
            for i in range(self._catCount + 1):
                x = self._x + (1.0 * i * self._length / self._catCount)
                # draw tick marks
                tick = Line(x, self._y + self.tickUp,
                            x, self._y - self.tickDown)

                tick.strokeColor = self.strokeColor
                tick.strokeWidth = self.strokeWidth
                tick.strokeDashArray = self.strokeDashArray
                g.add(tick)

        if not (self.categoryNames is None):
            # need to add tick labels
            assert len(self.categoryNames) == self._catCount, \
                   "expected %d category names but found %d in axis" % (
                       len(self.CategoryNames), self_catCount
                       )
            catWidth = self._length / self._catCount
            for i in range(self._catCount):
                x = self._x + (i+0.5) * catWidth
                y = self._y
                label = self.labels[i]
                label.setOrigin(x, y)
                label.setText(self.categoryNames[i])
                g.add(label.draw())
                        

        return g

class YValueAxis(Widget):
    """Axis corresponding to a numeric quantity.
    
    Comes in 'X' and 'Y' flavours.  A 'value axis' has a real number
    quantity associated with it.  The chart tells it where to go.
    The default one divides the number line into equal spaces
    and has tickmarks and labels associated with each."""

    def __init__(self):
        # private properties set by methods.  The initial values
        # here are to make demos easy; they would always be
        # overridden in real life.
        self._x = 50
        self._y = 50
        self._height = 100
        # public properties


        self.strokeWidth = 1
        self.strokeColor = STATE_DEFAULTS['strokeColor']
        self.strokeDashArray = STATE_DEFAULTS['strokeColor']
        self.labels = TypedPropertyCollection(Label)

        self.tickUp = 0  # how far into chart does tick go?
        self.tickDown = 5  # how far below axis does tick go?

        # idea - can we represent a gridline as just a great
        # big tickmark which sticks in rather than out?  Would
        # one ever want both of them?
        # self.tickMarks = TypedPropertyCollection(TickMark)

        # this may be either of (a) a format string like '%0.2f'
        # or (b) a function which takes the value as an argument
        # and returns a chunk of text.  So you can write a
        # 'formatMonthEndDate' function and use that on irregular
        # data points.
        
        self.labelTextFormat = '%s'
        # if set to auto, these will be worked out for you.
        # if you override any or all of them, your values
        # will be used.
        self.valueMin = Auto
        self.valueMax = Auto
        self.valueStep = Auto
        
        # alternative which is more flexible - provide a list
        # of values to use, allowing equal spacing.  So you
        # can give month end timestamps, which are not equally
        # spaced mathematically.
        #
        # This overrides the above three if present.
        # self.valueList = None
        # or should it be in a subclass for TimeAxis?


    def setPosition(self, x, y, length):
        self._x = x
        self._y = y
        self._length = length

        

    def configure(self, dataSeries):
        """not worked out yet.  Let it look at the data and
        determine the tick mark intervals.  If valueMin,
        valueMax and valueStep are configured then it
        will use them; if any of them are set to Auto it
        will look at the data and make some sensible decision.
        You may override this to build custom axes with
        irregular intervals.  It creates an internal
        variable self._values, which is a list of numbers
        to use in plotting."""
        raise NotImplementedError

    def scale(self, value):
        """Converts a numeric value to a Y position.

        The chart first configures the axis, then asks it to
        work out the x value for each point when plotting
        lines or bars.  You could override this to do
        logarithmic axes."""
        raise NotImplementedError
        return y

class BarFormatter(Widget):
    """Represents the attributes of a bar which you can customize.

    """
    def __init__(self):
        pass


               
class VerticalBarGroup(Widget):
    """Represents the attributes of a series which you can customize"""
    
    
    def __init__(self):
        self.bars = TypedPropertyCollection(VerticalBar)
        self.labels = TypedPropertyCollection(Label)
        self.labelFormat = '%s'

        
    
class StandardBarChart(Widget):
    """Bar chart with multiple side-by-side bars.

    Variants will be provided for stacked and 100% charts,
    probably by running all three off a common base class."""
    
    def __init__(self):
        self.x = 0
        self.y = 0
        self.width = 200
        self.height = 100

        # each chart has an inner 'plot rectangle' which
        # is explicitly specified.  It is your problem
        # to make the margins big enough to hold the
        # text labels, and it is possible to overrun.
        self.leftMargin = 30  # leave room for left labels
        self.rightMargin = 0
        self.topMargin = 0
        self.bottomMargin = 20  # leave room for bottom labels

        # this defines two series of 3 points.  Just an example.
        self.data = [(100,110,120),
                     (70, 80, 80)]        

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
        self.useAbsolute = 0
        self.barWidth = 10
        self.barSpacing = 5

        # if you have multiple series, by default they butt
        # together.
        self.seriesSpacing = 0

        # can I do this?  Can't wait to try!
        self.series = TypedPropertyCollection(
                        TypedPropertyCollection(
                            BarFormatter
                            )
                        )
                        
        self.categoryAxis = XCategoryAxis()
        self.valueAxis = YValueAxis()
        
        
    def draw(self):
        # just to clarify the logic, not running yet
        self._seriesCount = len(self.data)
        # check all data is square
        self._rowLength = len(self.data[0])
        for row in self.data[1:]:
            assert len(row) == self._rowLength, "data series have unequal " \
                   "numbers of points. Please pad others out with zeros.            "


        self.calcBarPositions()

        g = Group()
        g.add(self.categoryAxis.draw())
        g.add(self.valueAxis.draw())

        for s in range(self._seriesCount):
            fmt = self.series[s].labelFormat
            for b in range(self._rowLength):
                barPos = self._barPositions[s][b]
                bar = Rect(barPos[0],
                           barPos[1],
                           barPos[2] - barPos[0],
                           barPos[3] - barPos[1])

                barFormatter = self.series[s].bars[b]
                barFormatter.format(bar)
                
                g.add(bar)

                # this instantiates them if they have not
                # yet been created
                label = self.series[s].labels[b]
                label.setOrigin(0.5 * (barPos[0] + barPos[2]), #middle
                                barPos[3]) #top

                dataValue = self.data[s][b]
                if type(fmt) is StringType:
                    label.setText(fmt % self.data[s][b])
                else:
                    label.setText(fmt(self.data[s][b]))

                g.add(label)

if __name__=='__main__':
    axis = XCategoryAxis()
    drawing = axis.demo()
    from reportlab.graphics.renderPDF import drawToFile
    drawToFile(drawing, 'barchart1_XCategoryAxis.pdf', 'X Category Axis')
    
    