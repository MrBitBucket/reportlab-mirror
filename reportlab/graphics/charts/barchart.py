from reportlab.graphics.widgetbase import Widget, Face, TypedPropertyCollection
from reportlab.graphics.shapes import *
from reportlab.graphics import renderPDF
from reportlab.lib import colors
from reportlab.pdfgen.canvas import Canvas

import string

isOrientation = OneOf(("horizontal", "vertical"))
isColorSequence = SequenceOf(isColor)

class BarFormatter(Widget):
    "parameter container for bars"
    _attrMap = {
        'orientation': isOrientation,
        'width': isNumber,
        #'length': isNumber,
        'fillColor': isColorOrNone,
        'defaultFillColor': isColorOrNone, # fillColor overrides
        'strokeWidth':isNumber,
        'strokeColor':isColorOrNone,
        'strokeDashArray':isListOfNumbersOrNone,
        }
    def __init__(self):
        self.orientation = "vertical"
        self.defaultFillColor = STATE_DEFAULTS["fillColor"]
        self.fillColor = None
        self.width = 10 # pick a number, any number
        self.strokeColor = STATE_DEFAULTS["strokeColor"]
        self.strokeWidth = STATE_DEFAULTS["strokeWidth"]
        self.strokeDashArray = STATE_DEFAULTS["strokeDashArray"]
    def materialize(self, length, xyorigin=(0,0), lengthoffset=0, widthoffset=0):
        "generate a drawables based on this template, with help of 'derived' parameters"
        # for purposes of generality return a *sequence* of drawables
        (x,y) = xyorigin
        orientation = self.orientation
        if orientation == "vertical":
            lowerleftx = x+widthoffset
            lowerlefty = y+lengthoffset
            upperleftx = lowerleftx+self.width
            upperlefty = lowerlefty+length
        elif orientation == "horizontal":
            lowerleftx = x+lengthoffset
            lowerlefty = y+widthoffset
            upperleftx = lowerleftx+length
            upperlefty = lowerlefty+self.width
        else:
            raise ValueError, "bad orientation %s" % orientation
        R = Rect(lowerleftx, lowerlefty, upperleftx-lowerleftx, upperlefty-lowerlefty)
        if self.fillColor is not None:
            R.fillColor = self.fillColor
        elif self.defaultFillColor is not None:
            R.fillColor = self.defaultFillColor
        if self.strokeWidth is not None: R.strokeWidth = self.strokeWidth
        if self.strokeColor is not None: R.strokeColor = self.strokeColor
        if self.strokeDashArray is not None: R.strokeDashArray = self.strokeDashArray 
        return [R]

defaultColors = [colors.darkcyan,
                     colors.blueviolet, 
                     colors.blue,
                     colors.cyan]

class VerticalBarGroup(Widget):
    "I need this to make a bar group by itself, I need the formatter to make groups of groups..."
    _attrMap = {
        "data": isListOfNumbers,
        "format": None,
        }
    def __init__(self):
        self.data = [1]
        self.format = self.getformatter()
    def getformatter(self):
        return VerticalBarGroupFormatter()
    def normalizedata(self):
        return self.data # default: do nothing.
    def draw(self):
        g = Group()
        data = self.normalizedata()
        m = self.format.materialize(data)
        for e in m:
            g.add(e)
        return g

class HorizontalBarGroup(VerticalBarGroup):
    def getformatter(self):
        return HorizontalBarGroupFormatter()

class VerticalBarGroupFormatter(Widget):
    orientation = "vertical"
    _attrMap = {
        "colors": isColorSequence,
        "x": isNumber,
        "y": isNumber,
        "delta": isNumber,
        #"barWidth": isNumber,
        "bars": None, # fix this
        }
    def __init__(self):
        self.colors = defaultColors
        self.x = self.y = 0
        self.delta = 15
        #self.barWidth = 10
        self.bars = TypedPropertyCollection(BarFormatter)
        self.bars.orientation = self.orientation
        self.bars.width = 10
    def materialize(self, data):
        result = []
        bars = self.bars
        colors = self.colors
        ncolors = len(colors)
        x = self.x; y = self.y; delta = self.delta; #barWidth=self.barWidth
        xyorigin = (x,y)
        for i in range(len(data)):
            bar = bars[i]
            bar.defaultFillColor = colors[i%ncolors]
            d = data[i]
            lengthoffset = 0
            widthoffset = i*delta
            barmaterialize = bar.materialize(d, xyorigin, lengthoffset, widthoffset)
            result.extend(barmaterialize)
        return result

class HorizontalBarGroupFormatter(VerticalBarGroupFormatter):
    orientation = "horizontal"

class LabelledVerticalBarGroupFormatter(Widget):
    orientation = "vertical"
    _attrMap = {
        "colors": isColorSequence,
        "x": isNumber,
        "y": isNumber,
        "delta": isNumber,
        #"barWidth": isNumber,
        "bars": None, # fix this
        }
    def __init__(self):
        self.colors = defaultColors
        self.x = self.y = 0
        self.delta = 15
        #self.barWidth = 10
        self.bars = TypedPropertyCollection(BarFormatter)
        self.bars.orientation = self.orientation
        self.bars.width = 10

class VerticalBarStack(VerticalBarGroup):
    def getformatter(self):
        return VerticalBarStackFormatter()

class VerticalBarStackFormatter(Widget):
    orientation = "vertical"
    _attrMap = {
        "colors": isColorSequence,
        "x": isNumber,
        "y": isNumber,
        #"delta": isNumber,
        #"barWidth": isNumber,
        "bars": None, # fix this
        }
    def __init__(self):
        self.colors = defaultColors
        self.x = self.y = 0
        #self.delta = 15
        #self.barWidth = 10
        self.bars = TypedPropertyCollection(BarFormatter)
        self.bars.orientation = self.orientation
        self.bars.width = 10
    def materialize(self, data):
        result = []
        bars = self.bars
        colors = self.colors
        ncolors = len(colors)
        x = self.x; y = self.y; #delta = self.delta; #barWidth=self.barWidth
        xyorigin = (x,y)
        total = 0
        for i in range(len(data)):
            bar = bars[i]
            bar.defaultFillColor = colors[i%ncolors]
            d = data[i]
            lengthoffset = total
            widthoffset = 0
            barmaterialize = bar.materialize(d, xyorigin, lengthoffset, widthoffset)
            result.extend(barmaterialize)
            total = total+d
        return result

class HorizontalBarStack(VerticalBarStack):
    def getformatter(self):
        return HorizontalBarStackFormatter()

class HorizontalBarStackFormatter(VerticalBarStackFormatter):
    orientation = "horizontal"

class VerticalAxis(Widget):
    "parameter container for an axis"
    # no "data": no need for a formatter
    defaultOrientation = "vertical"
    _attrMap = {
        'x': isNumber, 'y': isNumber,
        'orientation': isOrientation,
        'length': isNumber,
        'firstTick': isNumber,
        'delta': isNumber,
        'tickStart': isNumber, 'tickEnd': isNumber,
        'strokeWidth':isNumber,
        'strokeColor':isColorOrNone,
        'strokeDashArray':isListOfNumbersOrNone,
        }
    def __init__(self):
        self.x = self.y = 0
        self.orientation = self.defaultOrientation
        self.length = 100
        self.firstTick = 8
        self.delta = 30
        self.tickStart = -3
        self.tickEnd = 10
        self.strokeColor = STATE_DEFAULTS["strokeColor"]
        self.strokeWidth = STATE_DEFAULTS["strokeWidth"]
        self.strokeDashArray = STATE_DEFAULTS["strokeDashArray"]
    def draw(self):
        "generate a drawables based on this template, with help of 'derived' parameters"
        # for purposes of generality return a *sequence* of drawables
        G = Group()
        x = self.x; y = self.y
        orientation = self.orientation
        length = self.length
        # XXXX this is BROKEN!
        #if self.strokeColor: G.strokeColor = self.strokeColor
        #if self.strokeWidth: G.strokeWidth = self.strokeWidth
        #if self.strokeDashArray: G.strokeDashArray = self.strokeDashArray
        if orientation == "vertical":
            G.add(Line(x, y, x, y+self.length))
            y0 = self.firstTick
            while y0<length:
                y1 = y+y0
                G.add(Line(x+self.tickStart, y1, x+self.tickEnd, y1))
                y0 = y0 + self.delta
        elif orientation == "horizontal":
            G.add(Line(x, y, x+self.length, y))
            x0 = self.firstTick
            while x0<length:
                x1 = x+x0
                G.add(Line(x1, y+self.tickStart, x1, y+self.tickEnd))
                x0 = x0 + self.delta
        else:
            raise ValueError, "bad orientation %s" % orientation
        if self.strokeDashArray is not None: R.strokeDashArray = self.strokeDashArray 
        return G
    
class HorizontalAxis(VerticalAxis):
    "parameter container for an axis"
    defaultOrientation = "horizontal"


class LabelFormatter(Widget):
    "parameter container for labels"
    _attrMap = {
        'orientation': isOrientation, # not the orientation of the labels, the orientatoin of offsets
        'color': isColorOrNone,
        'defaultColor': isColorOrNone,
        'extraOffset': isNumber, # distance adjustment off the data point (reversed on negative data)
        'font': isString,
        'size': isNumber,
        }
    def __init__(self):
        self.orientation = "vertical"
        self.defaultColor = STATE_DEFAULTS["fillColor"]
        self.color = None
        self.extraOffset = 10
        self.font = STATE_DEFAULTS["fontName"]
        self.size = STATE_DEFAULTS["fontSize"]
    def materialize(self, text, length, xyorigin=(0,0), lengthoffset=0, widthoffset=0):
        "generate a drawables based on this template, with help of 'derived' parameters"
        # for purposes of generality return a *sequence* of drawables
        (x,y) = xyorigin
        orientation = self.orientation
        # semantics is flipped compared to bar groups
        if orientation == "horizontal":
            lowerleftx = x+widthoffset
            lowerlefty = y+lengthoffset
            upperleftx = lowerleftx
            upperlefty = lowerlefty+length
            anchor = "middle"
            if length<0:
                upperlefty = upperlefty-self.extraOffset-self.size
            else:
                upperlefty = upperlefty+self.extraOffset
        elif orientation == "vertical":
            lowerleftx = x+lengthoffset
            lowerlefty = y+widthoffset
            upperleftx = lowerleftx+length
            upperlefty = lowerlefty
            if length<0:
                upperleftx = upperleftx-self.extraOffset
                anchor = "end"
            else:
                upperleftx = upperleftx+self.extraOffset
                anchor = "start"
        else:
            raise ValueError, "bad orientation %s" % orientation
        textlist = string.split(text, "\n")
        result = []
        for text1 in textlist:
            R = String(upperleftx, upperlefty, text1)
            upperlefty = upperlefty-self.size*1.1 # XXX this should be an adjustable parameter
            R.textAnchor = anchor
            if self.color is not None:
                R.fillColor = self.color
            elif self.defaultColor is not None:
                R.fillColor = self.defaultColor
            if self.size is not None:
                R.fontSize = self.size
            if self.font is not None:
                R.fontName = self.font
            result.append(R)
        return result


class VerticalLabelGroup(Widget):
    "I need this to make a bar group by itself, I need the formatter to make groups of groups..."
    _attrMap = {
        "offsets": isListOfNumbers,
        "texts": isListOfStrings,
        "format": None,
        }
    def __init__(self):
        self.offsets = [1, -1]
        self.texts = ["Fee", "Fi", "Fowe", "Fumm"]
        self.format = self.getformatter()
    def getformatter(self):
        return VerticalLabelGroupFormatter()
    def normalizeoffsets(self):
        return self.offsets # default: do nothing.
    def draw(self):
        g = Group()
        offsets = self.normalizeoffsets()
        m = self.format.materialize(self.texts, offsets)
        for e in m:
            g.add(e)
        return g

class HorizontalLabelGroup(VerticalLabelGroup):
    "I need this to make a bar group by itself, I need the formatter to make groups of groups..."
    def getformatter(self):
        return HorizontalLabelGroupFormatter()

class VerticalLabelGroupFormatter(Widget):
    orientation = "vertical"
    _attrMap = {
        "colors": isColorSequence,
        "x": isNumber,
        "y": isNumber,
        "delta": isNumber,
        #"barWidth": isNumber,
        "labels": None, # fix this
        }
    def __init__(self):
        self.colors = (colors.black,)
        self.x = self.y = 0
        self.delta = 15
        #self.barWidth = 10
        self.labels = TypedPropertyCollection(LabelFormatter)
        self.labels.orientation = self.orientation
    def materialize(self, texts, offsets=(0,)): # default to no offset
        result = []
        labels = self.labels
        colors = self.colors
        ncolors = len(colors)
        noffsets = len(offsets)
        x = self.x; y = self.y; delta = self.delta; #barWidth=self.barWidth
        xyorigin = (x,y)
        for i in range(len(texts)):
            label = labels[i]
            text = texts[i]
            label.defaultColor = colors[i%ncolors]
            d = offsets[i%noffsets]
            lengthoffset = 0
            widthoffset = i*delta
            labelmaterialize = label.materialize(text, d, xyorigin, lengthoffset, widthoffset)
            result.extend(labelmaterialize)
        return result
    
class HorizontalLabelGroupFormatter(VerticalLabelGroupFormatter):
    orientation = "horizontal"

class Swatches(Widget):
    _attrmap = {
        "x": isNumber, "y": isNumber,
        "deltax": isNumber, "deltay": isNumber,
        "dx": isNumber, "dy": isNumber,
        "columnMaximum": isNumber,
        "alignment": OneOf(("left", "right")), # align text on the left or right
        "fontName": isString,
        "fontSize": isNumber,
        "colorNamePairs": None, # fix this
        }
    def __init__(self):
        self.x = self.y = 0
        self.alignment = "left"
        self.deltax = 75; self.deltay = 20
        self.dx = self.dy = 10
        self.columnMaximum = 3
        self.fontName="Helvetica"; self.fonbtSize=10
        self.fontSize = 10
        from reportlab.lib.colors import red, blue, green, pink, yellow
        self.colorNamePairs = [ (red, "red"), (blue, "blue"), (green, "green"), (pink, "pink"), (yellow, "yellow") ]
    def draw(self):
        colornamepairs = self.colorNamePairs
        G = Group()
        thisx = upperleftx = self.x
        thisy = upperlefty = self.y + self.deltay*self.columnMaximum
        count = 0
        dx, dy = self.dx, self.dy
        for (c,n) in colornamepairs:
            count = count+1
            if self.alignment=="left":
                # align text to left
                T = String(thisx-self.dx, thisy, str(n))
                T.textAnchor = "end"
                C = Rect(thisx,thisy,dx,dy)
            elif self.alignment=="right":
                # align text to right
                T = String(thisx+self.dx, thisy, str(n))
                T.textAnchor = "start"
                C = Rect(thisx-dx,thisy,dx,dy)
            else: raise ValueError, "bad alignment"
            C.fillColor = c
            T.fontName = self.fontName
            T.fontSize = self.fontSize
            G.add(T); G.add(C)
            if count>=self.columnMaximum:
                count = 0
                thisx = thisx+self.deltax
                thisy = upperlefty
            else:
                thisy = thisy-self.deltay
        return G

class VScale(Widget):
    orientation = "vertical"
    _attrmap = {
        "x": isNumber, "y": isNumber,
        "minimum": isNumber, "maximum": isNumber,
        "length": isNumber, # the amount of space for the scale
        "width": isNumber, # the size of the lines to draw across the chart
        "nLabels": isNumber, # the maximum number of labels to use
        "labelFormat": isString,
        "extraOffset": isNumber,
        "font": isString,
        "fontSize": isNumber,
        # XXX add color, line style, font stuff... etc....
        }
    def __init__(self):
        self.x = self.y = 50
        self.minimum = 1.23987432; self.maximum = 1.33338962
        self.length = 150; self.width = 120
        self.nLabels = 4
        self.labelFormat = "%5.2f"
        self.extraOffset = 15
        self.font = "Helvetica"
        self.fontSize = 10
    def factor(self):
        "return the scaling factor for points from domain space to canvas space"
        return self.length*1.0/(self.maximum - self.minimum)
    def domainToCanvas(self, domainvalue):
        "convert from domain coordinate to canvas coordinate"
        orientation = self.orientation
        f = self.factor()
        if orientation=="vertical": base = self.y
        elif orientation=="horizontal": base = self.x
        else: raise ValueError, "bad orientation "+repr(orientation)
        return base + f*(domainvalue-self.minimum)
    def draw(self):
        orientation = self.orientation
        # this could be done cleverly using the other widgets, but what the ....
        x,y = self.x, self.y
        fmt = self.labelFormat
        (delta, startpoint) = scaleParameters(self.minimum, self.maximum, self.nLabels)
        G = Group()
        # orientation independent data (direct values for vertical case, convert for horizontal case
        linedata = []
        textdata = []
        # the main axis
        linedata.append( (0, 0, 0, self.length) )
        # the cross lines and labels
        lineposition = startpoint - self.minimum
        factor = self.factor()
        #print "factor is", factor
        while lineposition+self.minimum<self.maximum:
            text = string.strip(fmt % (lineposition+self.minimum))
            clineposition = factor * lineposition
            #print "lineposition, clineposition", lineposition, clineposition
            linedata.append( (0, clineposition, self.width, clineposition) )
            textdata.append( (0, clineposition, text) )
            lineposition = lineposition + delta
        #print "done with lines"
        if orientation=="vertical":
            for (x1, y1, x2, y2) in linedata:
                G.add(Line(x+x1, y+y1, x+x2, y+y2))
            for (x1, y1, t) in textdata:
                S = String(x+x1-self.extraOffset, y+y1, t)
                S.fontName = self.font
                S.fontSize = self.fontSize
                S.textAnchor = "end"
                G.add(S)
        elif orientation=="horizontal":
            for (y1, x1, y2, x2) in linedata:
                G.add(Line(x+x1, y+y1, x+x2, y+y2))
            for (y1, x1, t) in textdata:
                S = String(x+x1, y+y1-self.extraOffset, t)
                S.textAnchor = "middle"
                G.add(S)
        else:
            raise ValueError, "bad orientation " + repr(orientation)
        return G

class HScale(VScale):
    orientation = "horizontal"    
        
def scaleParameters(x,y,maxlabels):
    """on number line between x and y choose delta for label marks and first mark
       (should be reasonable like 1.2,1.4,... not 1.23423, 1.342334,... regardless of messy end points.
    """
    if maxlabels<2:
        raise ValueError, "two or more labels required" # 4 or more recommended
    difference = y-x
    if difference<=0: raise ValueError, "%s not less than %s" % (x,y)
    orderofmagnitude = 1.0
    # find order of magnitude
    while orderofmagnitude>difference:
        orderofmagnitude = orderofmagnitude/10.0
    while orderofmagnitude*10<difference:
        orderofmagnitude = orderofmagnitude*10.0
    #print "order of magnitude", orderofmagnitude
    portion = difference/orderofmagnitude
    #print "portion", portion
    # find appropriate delta
    for deltacandidate in (0.1, 0.2, 0.25, 0.5, 1.0, 2.0, 2.5, 5.0, 10.0):
        delta = deltacandidate
        if portion/delta < maxlabels:
            #print delta, "ok", portion/delta
            break
        #print delta, "too small:", portion/delta
    delta = delta*orderofmagnitude
    # find starting point (rounded appropriately)
    (below, remainder) = divmod(x, orderofmagnitude)
    (below2, remainder2) = divmod(remainder, delta)
    startpoint = below*orderofmagnitude + (below2+1)*delta
    return (delta, startpoint)

def dd(__parent_dictionary__=None, **kw):
    result = {}
    if __parent_dictionary__ is not None:
        result.update(__parent_dictionary__)
    result.update(kw)
    return result
    
class HScaledBarChart(Widget):
    orientation = "horizontal"
    _attrmap = dd(
        x=isNumber, y=isNumber,
        barVertical=isNumber, # vertical space allowed for all bars
        fontSize=isNumber,
        #barWidth=isNumber,
        delta=isNumber,
        #maxLabels=isNumber,
        titleText=isString,
        titlex=isNumber, titley=isNumber, 
        title=None, #TextWidget,
        ruler=None, #HRuler,
        bars=None, #VBarGroup,
        scale=None, #VScale,
        labels=None, #HLabelSequence,
        data=None
        ) 
    def __init__(self):
        self.titleText = "Fund"
        if self.orientation=="horizontal":
            self.title = LabelFormatter()
            self.ruler = HorizontalAxis()
            self.bars = VerticalBarGroup()
            self.scale = VScale()
            self.labels = HorizontalLabelGroup()
        else:
            self.title = LabelFormatter()
            self.ruler = VerticalAxis()
            self.bars = HorizontalBarGroup()
            self.scale = HScale()
            self.labels = VerticalLabelGroup()
        self.x = 50; self.y = 30
        self.scale.nLabels = 4
        self.scale.labelFormat = "%d"
        self.scale.extraOffset = 5
        self.bars.format.bars.width = 20; #self.bars.delta = 25
        self.title.size = 6
        self.title.extraOffset = 0
        self.title.orientation = "vertical" # ie, center it :)
        #self.barWidth = 20; self.barSpacing = 5;
        self.delta = 25
        self.barVertical = 40
        self.titlex = 100; self.titley = 100
        #self.labels.y = 65
        self.labels.format.labels.extraOffset = -10
        self.fontSize = 6
        self.ruler.tickStart = -3; self.ruler.tickEnd = 0
        self.data = [ ("Jan\n99", 23),
             ("Feb\n99", 31),
             ("Mar\n99", 69.2),
             ("Apr\n99", 58),
        ]

    def draw(self):
        (self.scale.x, self.scale.y) = (self.ruler.x, self.ruler.y) = (self.bars.format.x, self.bars.format.y) = \
                             (self.x, self.y)
        self.ruler.firstTick = 0
        self.ruler.delta = self.delta
        self.scale.minimum = 0
        if self.orientation=="horizontal":
            self.labels.format.y = self.y
            self.labels.format.x = self.x + self.bars.format.bars.width/2.0
        else:
            self.labels.format.y = self.y - self.bars.format.bars.width/2.0
            self.labels.format.x = self.x
        self.bars.format.delta = self.labels.format.delta = self.delta
        self.labels.format.labels.size = self.scale.fontSize = self.fontSize
        labeltexts = []
        values = []
        for (t, v) in self.data:
            labeltexts.append(t)
            values.append(v)
        mvalue = max(values)
        self.scale.maximum = mvalue
        self.ruler.length = self.scale.width = self.delta * len(self.data)
        self.scale.length = self.barVertical
        # XXXX this should probably be 
        converter = self.barVertical *1.0/mvalue
        cvalues = []
        for v in values:
            cvalues.append(converter*v)
        self.bars.data = cvalues
        self.labels.texts = labeltexts
        self.labels.offsets = [-1.5*self.fontSize] # 1.5 below the bars (should be parameter)
        G = Group()
        m = self.title.materialize(self.titleText, 0, (self.titlex, self.titley), 0, 0)
        for x in ([self.scale.draw(), self.ruler.draw(), self.bars.draw(), self.labels.draw()] + m):
            G.add(x)
        return G
    
class VScaledBarChart(HScaledBarChart):
    orientation = "vertical"
    
def test():
    fn = "barchart.pdf"
    c = Canvas(fn)
    d = Drawing(400,200)
    x = 25
    for B in (HScaledBarChart,VScaledBarChart,):
        print B
        pc = B()
        pc.x = x
        x = x+200
        d.add(pc, 'chart1')
    c.setFont('Times-Roman', 20)
    c.drawString(100, 720, "bar chart")
    c.setFont('Times-Roman', 12)
    #BUG - currently the drawing gets the most recently used font as its default.
    d.drawOn(c, 100, 500)
    c.showPage()
    d = Drawing(400,200)
    x = 25
    for B in (HorizontalBarGroup, VerticalBarGroup):
        print B
        pc = B()
        pc.format.x = x
        pc.format.y = 50
        pc.data = [10,20,x*0.2,40,50,60]
        x = x+200
        d.add(pc, 'chart1')
    c.setFont('Times-Roman', 20)
    c.drawString(100, 720, "bar chart")
    c.setFont('Times-Roman', 12)
    #BUG - currently the drawing gets the most recently used font as its default.
    d.drawOn(c, 100, 500)
    c.showPage()
    d = Drawing(400,200)
    x = 50
    for B in (VScale, HScale):
        print B
        pc = B()
        pc.x = x
        pc.y = 30
        x = x+150
        d.add(pc, 'chart1')
    c.setFont('Times-Roman', 20)
    c.drawString(100, 720, "bar chart")
    c.setFont('Times-Roman', 12)
    #BUG - currently the drawing gets the most recently used font as its default.
    d.drawOn(c, 100, 500)
    c.showPage()
    d = Drawing(400,200)
    x = 100
    for B in (Swatches,):
        print B
        pc = B()
        pc.x = x
        pc.y = 50
        x = x+200
        d.add(pc, 'chart1')
    c.setFont('Times-Roman', 20)
    c.drawString(100, 720, "bar chart")
    c.setFont('Times-Roman', 12)
    #BUG - currently the drawing gets the most recently used font as its default.
    d.drawOn(c, 100, 500)
    c.showPage()
    d = Drawing(400,200)
    x = 25
    for B in (HorizontalLabelGroup, VerticalLabelGroup):
        print B
        pc = B()
        pc.format.x = x
        pc.format.y = 50
        pc.offsets = [1,-20,20,-1]
        pc.texts = ["this", "that", "the other", "again"]
        x = x+200
        d.add(pc, 'chart1')
    c.setFont('Times-Roman', 20)
    c.drawString(100, 720, "bar chart")
    c.setFont('Times-Roman', 12)
    #BUG - currently the drawing gets the most recently used font as its default.
    d.drawOn(c, 100, 500)
    c.showPage()
    d = Drawing(400,200)
    x = 25
    for B in (HorizontalBarStack, VerticalBarStack):
        pc = B()
        print B
        pc.format.x = x
        pc.format.y = 50
        pc.data = [10,20,x*0.2,10,5,6]
        x = x+200
        d.add(pc, 'chart1')
    c.setFont('Times-Roman', 20)
    c.drawString(100, 720, "bar chart")
    c.setFont('Times-Roman', 12)
    #BUG - currently the drawing gets the most recently used font as its default.
    d.drawOn(c, 100, 500)
    c.showPage()
    d = Drawing(400,200)
    x = 25
    for B in (HorizontalAxis, VerticalAxis):
        pc = B()
        print B
        pc.x = x
        pc.y = 50
        x = x+200
        d.add(pc, 'chart1')
    c.setFont('Times-Roman', 20)
    c.drawString(100, 720, "bar chart")
    c.setFont('Times-Roman', 12)
    #BUG - currently the drawing gets the most recently used font as its default.
    d.drawOn(c, 100, 500)
    c.save()
    print 'saved', fn

if __name__=='__main__':
    test()        