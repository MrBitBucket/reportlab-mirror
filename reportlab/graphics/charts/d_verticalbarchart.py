from reportlab.graphics.charts.textlabels import Label
from reportlab.graphics.shapes import Drawing, Group, Line
from reportlab.graphics.charts.legends import Legend
from reportlab.graphics.widgetbase import TypedPropertyCollection
from reportlab.lib.colors import PCMYKColor, _PCMYK_black
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

class VerticalBarChart(barcharts.VerticalBarChart):
    """Returns a widget - used by the class VerticalBarChartDrawing.
    Based on (and inherits from) barcharts.VerticalBarChart. Each bar has a vertical
    line from the (x)centre to the its label. The properties to do with
    this line are self.lineLength, self.lineStrokeWidth and self.lineColor.
    All the labels are at the same height, (ie in a horizontal line _outside_
    their bars).
    It's used for Chartbook 2001 - plot for eg Performance Year by Year."""

    _attrMap = AttrMap(BASE=barcharts.VerticalBarChart,
        labelOffset = AttrMapValue(isNumber,
            desc="Space between label text and grid edge"),

        background = AttrMapValue(isColorOrNone,
            desc="Color for the plot area background (if any)"),
        categoryNames = AttrMapValue(isListOfStrings,
            desc="Group names (eg years)"),

        lineLength = AttrMapValue(isNumber,
            desc='Length of the horizontal line (behind the actual bars)'),
        lineStrokeWidth = AttrMapValue(None,
            desc='Stroke width of the horizontal line (behind the actual bars)'),
        lineColor = AttrMapValue(isColorOrNone,
            desc='Colour of the horizontal line (behind the actual bars)'),
                       
        barLabelFormat = AttrMapValue(isAnything,
            desc="Formatting routine to be used on the bar labels"),
        barFillColors = AttrMapValue(isListOfColors,
            desc="List of colours to be used filling in the bars"),
        legend = AttrMapValue(None,
            desc="Handle to the chart legend"),

        leftPadding = AttrMapValue(isNumber,
            desc='Padding on left of drawing'),
        rightPadding = AttrMapValue(isNumber,
            desc='Padding on right of drawing'),
        topPadding = AttrMapValue(isNumber,
            desc='Padding at top of drawing'),
        bottomPadding = AttrMapValue(isNumber,
            desc='Padding at bottom of drawing'),
        )
    
    def __init__(self):
        barcharts.VerticalBarChart.__init__(self)
        self.height = 2.8*cm # height of BARS/LINES - NOT the whole chart
        self.width = 4.8*cm # width of BARS/LINES - NOT the whole chart
        self.background = None
        self.data      = [(24.7, 18.2, 23.9, 16.1, 13.8),
                          (23.8, 15.6, 23.8, 14.9, 25.1)]
        self.barLabelFormat = '%.1f%%'

        # used for the vertical line behind the bars
        self.lineLength = 2.8*cm
        self.lineStrokeWidth = 0.5
        self.lineColor = _PCMYK_black
 
        self.bars.strokeColor = _PCMYK_black
        self.bars.strokeWidth = 0.5
        self.groupSpacing = 0.9*cm
        self.barSpacing = 0.06*cm
        self.barWidth = 0.19*cm
        
        #Allows us up to six bars (per group) to be coloured
        c0 = PCMYKColor(100.0,65.0,0.0,30.0,density=100)
        c1 = PCMYKColor(11.0,11.0,72.0,0.0,density=100)
        self.bars[0].fillColor=c0
        self.bars[1].fillColor=c1
        self.bars[2].fillColor=PCMYKColor(100.0,65.0,0.0,30.0,density=75)
        self.bars[3].fillColor=PCMYKColor(11.0,11.0,72.0,0.0,density=75)
        self.bars[4].fillColor=PCMYKColor(100.0,65.0,0.0,30.0,density=50)
        self.bars[5].fillColor=PCMYKColor(11.0,11.0,72.0,0.0,density=50)

        self.valueAxis.valueMin = 0.0
        tl=[]
        for f in range (0, len(self.data)):
            for i in range (0,len(self.data[f])):
                tl.append(self.data[f][i])
        self.valueAxis.valueMax = _highest([tl])
        
        self.categoryAxis.visibleAxis = 0
        self.categoryAxis.visibleTicks = 1
        self.categoryAxis.tickDown = 0

        self.barLabels.fontName = "Helvetica-Oblique"
        self.barLabels.fontSize = 6
        self.barLabels.fillColor = _PCMYK_black
        self.barLabels.angle = 90

        self.labelOffset = 5

        self.bars.strokeWidth = 0.5
        self.categoryAxis.categoryNames = ('1996', '1997', '1998', '1999', '2000')

        self.valueAxis.visible = 0
        self.categoryAxis.visible = 1
        self.categoryAxis.labels.fontName = "Helvetica-Oblique"
        self.categoryAxis.labels.fontSize = 6
        self.categoryAxis.labels.fillColor = _PCMYK_black
        self.categoryAxis.labels.dy = -self.labelOffset

        self.legend=Legend()
        self.legend.columnMaximum = 3
        self.legend.colorNamePairs = [(c0, "Fund"), (c1, "Index")]
        self.legend.x = self.width
        self.legend.y = self.lineLength
        self.legend.fontName = "Helvetica"
        self.legend.fontSize = 6
        self.legend.deltax = 0.1*cm
        self.legend.deltay = 0.4*cm
        self.legend.dxTextSpace = 5
        self.legend.dx = 5
        self.legend.dy = 5
        self.legend.alignment = 'right'
        self.legend.strokeColor = _PCMYK_black
        self.legend.strokeWidth = 0.5
        tx=0
        for f in range (0, len(self.legend.colorNamePairs)):
            tx=tx+_maxWidth(self.legend.colorNamePairs[f][1], self.legend.fontName, self.legend.fontSize)
            tx=tx+self.legend.deltax+self.legend.dxTextSpace+self.legend.dx

        self.leftPadding   = 5
        self.rightPadding  = 5
        self.topPadding    = 5
        self.bottomPadding = 5

    def _labelXY(self,label,x,y,width,height):
        'Compute x, y for a label'
        self._collectedData.append((x + 0.5*width, y*(height>=0 and 1 or -1), height))
        return x+0.5*width, y+self.lineLength+(self.labelOffset*2)+self.barLabels.nudge

    def draw(self):
        g = Group()
        if self.barLabelFormat == None:
            self.barLabelFormat = _nullFormatter
        self._collectedData=[]

        tl=[]
        for f in range (0, len(self.data)):
            for i in range (0,len(self.data[f])):
                tl.append(self.data[f][i])
        self.valueAxis.valueMax = _highest([tl])

        #if we have a background colour,do a background
        if self.background:
            x,y = self._getDrawingDimensions()
            g.add(Rect(-self.leftPadding,-(self.bottomPadding+self.labelFontSize+self.labelOffset),
                       x,y,
                       strokeColor=None,
                       strokeWidth=0,
                       fillColor=self.background))
        
        #the actual barcharts        
        g.add(barcharts.VerticalBarChart.draw(self))

        # the vertical lines
        for i in range(0, len(self._collectedData)):
            x,y, h=self._collectedData[i]
            g.add(Line(x, y+h, x, y+self.lineLength,
                       strokeColor = self.lineColor,
                       strokeWidth = self.lineStrokeWidth))
    
        g.add(self.legend)

        g.shift(self.leftPadding,self.bottomPadding+self.categoryAxis.labels.fontSize+self.labelOffset)
        return g

    def _getDrawingDimensions(self):
        #find width of grid
        tx=self.x+self.width
        #add padding (and offset)
        tx=tx+self.leftPadding+self.rightPadding+self.labelOffset
        #add in maximum width of text in legend
        tt=[]
        for f in range (0, len(self.legend.colorNamePairs)):
            tt.append(self.legend.colorNamePairs[f][1])
        tx=tx+_maxWidth(tt, self.legend.fontName, self.legend.fontSize)
        tx=tx+self.legend.deltax+self.legend.dxTextSpace+self.legend.dx
        #up to baseline...
        ty=self.bottomPadding+self.categoryAxis.labels.fontSize+self.labelOffset
        #add length of longest label (including percent signs, yadda, yadda, yadda)
        tl=[]
        for f in range (0, len(self.data)):
            for i in range (0,len(self.data[f])):
                if self.barLabelFormat is None:
                    tl.append(self.data[0][f])
                elif type(self.barLabelFormat) is StringType:
                    tl.append(self.barLabelFormat % self.data[0][f])
                elif type(self.barLabelFormat) is FunctionType:
                    tl.append(self.barLabelFormat(self.data[0][f]))
                elif isinstance(self.barLabelFormat, Formatter):
                    tl.append(self.barLabelFormat(self.data[0][f]))
        ty=ty+self.lineLength+_maxWidth(tl, self.barLabels.fontName, self.barLabels.fontSize)
        ty=ty+self.topPadding
        #print (tx, ty)
        return (tx,ty)

    def demo(self, drawing=None):
        if not drawing:
            tx,ty=self._getDrawingDimensions()
            drawing = Drawing(tx, ty)
        drawing.add(self.draw())
        return drawing       


if __name__ == "__main__":
    d = VerticalBarChart()
    d.demo().save(fnRoot="d_verticalbarchart")