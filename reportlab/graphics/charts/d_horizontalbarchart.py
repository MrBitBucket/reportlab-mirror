from reportlab.graphics.charts.textlabels import Label
from reportlab.graphics.shapes import Drawing, Group, Line
from reportlab.graphics.widgetbase import TypedPropertyCollection
from reportlab.lib.colors import Color, _PCMYK_black
from reportlab.lib.attrmap import *
from reportlab.lib.units import cm
from reportlab.lib.validators import *
from reportlab.pdfbase.pdfmetrics import getFont
from reportlab.graphics.charts import barcharts
from reportlab.graphics.charts.lineplots import _maxWidth

def _highest(list, roundInterval=10):
    v=max(map(max, list))
    d,f=divmod(v,roundInterval)
    if f>0:
        f=1
    else:
        f=0.5
    return (d+f)*roundInterval

class HorizontalBarChart(barcharts.HorizontalBarChart):
    """Returns a widget - used by the class HorizontalBarChartDrawing (in file horizontalbarchart_db.py).
    Based on (and inherits from) barcharts.HorizontalBarChart.

    labelRow2 is an optional attribute - this can safely be set to
    None, in which case it will be ommited. If it does exist, it is
    used to produce a third column of labels for eg, 'previous quarter
    in brackets'."""

    _attrMap = AttrMap(BASE=barcharts.HorizontalBarChart,
        categoryNames = AttrMapValue(isNoneOrListOfNoneOrStrings,
            desc='List of category names'),
        background = AttrMapValue(isColorOrNone,
            desc='Background colour for chart area (if any)'),
        labelRow2 = AttrMapValue(isNoneOrListOfNoneOrNumbers,
            desc='List of numbers used for optional second set of labels (eg previous quarter)'),
        lineLength = AttrMapValue(isNumber,
            desc='Length of the horizontal line (behind the actual bars)'),
        lineStrokeWidth = AttrMapValue(None,
            desc='Stroke width of the horizontal line (behind the actual bars)'),
        lineColor = AttrMapValue(isColorOrNone,
            desc='Colour of the horizontal line (behind the actual bars)'),
        labelData = AttrMapValue(isAnything,
            desc="Data used for the labels"),
        labelFontName = AttrMapValue(isString,
            desc="Name of font used for the labels"),
        labelFontSize = AttrMapValue(isNumber,
            desc="Size of font used for the labels"),
        labelOffset = AttrMapValue(isNumber,
            desc="Space between label text and grid edge"),
        labelFillColor = AttrMapValue(isColor,
            desc="Ink color for the labels"),
        labelFormat = AttrMapValue(isAnything,
            desc="Formatting routine to be used on 2nd and 3rd columns of labels"),
        labelRightPadding = AttrMapValue(isAnything,
            desc="Space between 2nd and 3rd columns of labels"),
        leftPadding = AttrMapValue(isNumber,
            desc='Padding on left of drawing'),
        rightPadding = AttrMapValue(isNumber,
            desc='Padding on right of drawing'),
        topPadding = AttrMapValue(isNumber,
            desc='Padding at top of drawing'),
        bottomPadding = AttrMapValue(isNumber,
            desc='Padding at bottom of drawing'),
        valueMin = AttrMapValue(isNumber,
            desc='The lowest value to appear on the chart'),
        topOffset = AttrMapValue(isNumber, desc='the top of the enclosing drawing'),
        _labels = AttrMapValue(isListOfStrings,
            desc=''),
        _dxl = AttrMapValue(isNumber,
            desc=''),
        )

    def __init__(self):
        barcharts.HorizontalBarChart.__init__(self)
        self.barSpacing = 0.1*cm
        self.groupSpacing = 0.15*cm
        self.topOffset = 105

        self.labelFontName = "Helvetica-Oblique"
        self.labelFontSize = 6
        self.labelFillColor = _PCMYK_black
        self.labelOffset = 5
        self.labelRightPadding = 0.4*cm

        self.x = 0
        self.y = 0
        self.width = 1.5*cm # width of the BARS
        self.height = 3.5*cm # height of the BARS

        self.leftPadding=5
        self.topPadding=5

        # this defines a series of points - used for drawing bars and label1
        # self.data(0) is the data used to plot the bars
        # NB These go from bottom to top...
        self.data      = [(3.5, 15.5, 6.0, 7.5, 7.7,  7.7,  9.4, 10.9, 14.9, 16.9)]
        self.labelData = [(3.5, 15.5, 6.0, 7.5, 7.7,  7.7,  9.4, 10.9, 14.9, 16.9)]
        self.labelRow2 = [5.3,  3.3, 2.4, 4.5, 6.3, 10.1, 14.2, 12.5, 15.4, 26.2]
        self.categoryNames = ('Cash',
                              'Other',
                              'Italy',
                              'Switzerland',
                              'Sweden',
                              'Finland',
                              'Netherlands',
                              'Ireland',
                              'France',
                              'Germany')
        self.labelFormat = '%.1f%%'
        self.valueMin = 0

        # used for the horizontal line behind the bars
        self.lineLength = 1.5*cm
        self.lineStrokeWidth = 0.5
        self.lineColor = _PCMYK_black

        # control bar spacing. if useAbsolute = 1 then
        # the next parameters are in points; otherwise
        # they are 'proportions' and are normalized to
        # fit the available space.  Half a barSpacing
        # is allocated at the beginning and end of the
        # chart.
        self.useAbsolute = 1
        self.barWidth = 0.175*cm
        self.barSpacing = 0.185*cm
        self.valueAxis.visible = 0
        self.categoryAxis.visible = 0

        self.barLabelFormat = None

        self.bars = TypedPropertyCollection(barcharts.BarChartProperties)
        self.bars.strokeColor = _PCMYK_black
        self.background=colors.Color(254/255.0, 251/255.0, 242/255.0)
        self.background=None

        for f in range (0,len(self.data)):
            self.bars[f].fillColor = colors.Color(232/255.0,224/255.0,119/255.0)
            self.bars[f].strokeWidth = 0.5

        self._labels=[]
        if self.labelData != None and max(self.labelData)!=None:
            for f in range(0, len(self.labelData[0])):
                if self.labelFormat is None:
                    self._labels.append(self.labelData[0][f])
                elif type(self.labelFormat) is StringType:
                    self._labels.append(self.labelFormat % self.labelData[0][f])
                elif type(self.labelFormat) is FunctionType:
                    self._labels.append(self.labelFormat(self.labelData[0][f]))
                elif isinstance(self.labelFormat, Formatter):
                    self._labels.append(self.labelFormat(self.labelData[0][f]))
        else:
            templabelData = []
            for f in range(0, len(self.data[0])):
                templabelData.append(None)
            self.labelData.append(tuple(templabelData))

        for f in range(0, len(self.data[0])):
            ty = self.y+(self.barWidth/2.0)+((self.barWidth+self.barSpacing)*f)
            self._dxl = _maxWidth(self.categoryNames, self.labelFontName, self.labelFontSize)           
            

    def draw(self): 
        g = Group()
        if self.categoryNames == None:
            self.categoryNames =[]
            for f in range(0, 10):
                self.categoryNames.append(None)
            self.categoryNames=tuple(self.categoryNames)
        if self.labelData != None and max(self.labelData[0])!=None:
            self.labelData = self.data

        # is labelRow2 empty?
        allNull = 0
        if self.labelRow2:
            for f in range (0,len(self.labelRow2)):
                if self.labelRow2[f]==None:
                    allNull=allNull+1
            if allNull==len(self.labelRow2):
                self.labelRow2 = None

        # the actual bar chart
        self.valueAxis.valueMin = self.valueMin
        # so we can actually see some of the line even for the longest bar
        self.valueAxis.valueMax = _highest(self.data)
        self.height = self._desiredCategoryAxisLength()
        self.y = self.topOffset - self.topPadding - self.height
        _dxl = _maxWidth(self._labels, self.labelFontName, self.labelFontSize) # this is NOT self.dxl!
        g.add(barcharts.HorizontalBarChart.draw(self))

        # do the labels
        ascent=getFont(self.labelFontName).face.ascent
        if ascent==0:
            ascent=0.718 # default (from helvetica)
        ascent=ascent*self.labelFontSize # normalize

        self._labels=[]
        if self.labelData != None and max(self.labelData[0])!=None:
            for f in range(0, len(self.labelData[0])):
                if self.labelFormat is None:
                    self._labels.append(self.labelData[0][f])
                elif type(self.labelFormat) is StringType:
                    self._labels.append(self.labelFormat % self.labelData[0][f])
                elif type(self.labelFormat) is FunctionType:
                    self._labels.append(self.labelFormat(self.labelData[0][f]))
                elif isinstance(self.labelFormat, Formatter):
                    self._labels.append(self.labelFormat(self.labelData[0][f]))
        else:
            self.labelData=[]
            templabelData = []
            for f in range(0, 10):
                templabelData.append(None)
                self._labels.append(None)
            self.labelData.append(tuple(templabelData))

        R=range(0, len(self.data[0]))
        if self.categoryAxis.reverseDirection:
            R.reverse()

        ty = self.y+(self.barWidth+self.groupSpacing)/2.0
        tyInc = self.barWidth+self.groupSpacing
        for f in R:
            #left labels - column 1
            l = Label()
            l.setOrigin(self.x-self.labelOffset, ty)
            l.setText(self.categoryNames[f])
            l.fontName = self.labelFontName
            l.fontSize = self.labelFontSize
            l.fillColor = self.labelFillColor
            l.textAnchor= 'end'
            l.boxAnchor="e"
            g.add(l)

            #right labels - column 2
            l = Label()
            l.setOrigin(self.x+self.lineLength+self.labelOffset, ty)
            l.setText(self._labels[f])
            l.fontName = self.labelFontName
            l.fontSize = self.labelFontSize
            l.fillColor = self.labelFillColor
            l.boxAnchor="w"
            l.textAnchor= 'start'
            g.add(l)

            #right labels - column 3
            if self.labelRow2:
                l = Label()
                l.setOrigin(self.x+self.lineLength+self.labelOffset+_dxl+self.labelRightPadding, ty)
                if self.labelFormat is None:
                    labelText = self.labelRow2[f]
                elif type(self.labelFormat) is StringType:
                    labelText = self.labelFormat % self.labelRow2[f]
                elif type(self.labelFormat) is FunctionType:
                    labelText = self.labelFormat(self.labelRow2[f])
                elif isinstance(self.labelFormat, Formatter):
                    labelText = self.labelFormat(self.labelRow2[f])
                else:
                    msg = "Unknown formatter type %s, expected string or function" % labelFormat
                    raise Exception, msg
                labelText = "(%s)" % str(labelText)
                l.setText(labelText)
                l.fontName = self.labelFontName
                l.fontSize = self.labelFontSize
                l.fillColor = self.labelFillColor
                l.boxAnchor="w"
                l.textAnchor= 'start'
                g.add(l)

            # the background lines - now done as lines
            le=self.data[0][f]*float(self.lineLength/_highest(self.data))
            g.add(Line(self.x+le, ty, self.x+self.lineLength, ty,
                       strokeColor = self.lineColor,
                       strokeWidth = self.lineStrokeWidth))
            ty=ty+tyInc

        g.shift(self.leftPadding+self._dxl+self.labelOffset, 0)
        return g

    def demo(self, drawing=None):
        if not drawing:
            drawing = Drawing(140,105)
        drawing.add(self.draw())
        return drawing            


if __name__ == "__main__":
    d = HorizontalBarChart()
    d.demo().save(fnRoot="d_horizontalbarchart")
