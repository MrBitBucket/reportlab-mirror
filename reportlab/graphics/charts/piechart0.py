# experimental pie chart script.  Two types of pie - one is a monolithic
#widget with all top-level properties, the other delegates most stuff to
#a wedges collection whic lets you customize the group or every individual
#wedge.

from reportlab.graphics.widgetbase import Widget, Face
from reportlab.graphics.shapes import *
from reportlab.graphics import renderPDF
from reportlab.lib import colors
from reportlab.pdfgen.canvas import Canvas
import math

class Pie(Widget):
    """This is the pie which appears in the middle of a pie chart.
    It does NOT include legends, titles and other furniture.
    The rectangle is the 'bounding box' for the circle of
    ellipse; if one uses exploded slices or labels, they
    will typically stick out from the defining rectangle."""
    
    #there is no design at all between this color choice;
    # we need a palette with some reasoning behind it.
    defaultColors = [colors.darkcyan,
                     colors.blueviolet,
                     colors.blue,
                     colors.cyan]
    _attrMap = {
        'x':isNumber,
        'y':isNumber,
        'width':isNumber,
        'height':isNumber,
        'data':isListOfNumbers,
        'labels':isListOfStringsOrNone,
        'labelRadius':isNumber,   # 0.5 = mid-slice, 1.25 = just outside
        'labelFontName':isString,
        'labelFontSize':isNumber,
        'labelColor':isColor,
        'startAngle':isNumber,
        'direction': lambda x: x in ['clockwise','anticlockwise'],
        'popouts': lambda x: type(x) == type({}) and isListOfNumbers(x.keys()) and isListOfNumbers(x.values()),
        'strokeColor':isColorOrNone,
        'strokeWidth':isNumber
        }
    def __init__(self):
        self.x = 0
        self.y = 0
        self.width = 100
        self.height = 100
        self.data = [1]
        self.labels = None  # or list of strings
        self.labelRadius = 1.25
        self.labelFontName = 'Times-Roman'
        self.labelFontSize = 12
        self.labelColor = colors.black
        self.startAngle = 90
        self.direction = "clockwise"
        self.popouts = {}
        self.strokeColor = colors.black
        self.strokeWidth = 0
        
    def demo(self):
        self.x = 50
        self.y = 10
        self.height = 80
        self.width = 80
        self.data = [10,20,30,40,50,60]
                     
    def draw(self):
        # normalize slice data
        sum = 0.0
        for number in self.data:
            sum = sum + number
        normData = []
        for number in self.data:
            normData.append(360.0 * number / sum)

        #labels
        if self.labels is None:
            labels = [''] * len(normData)
        else:
            labels = self.labels
        assert len(labels) == len(self.data), "Number of labels does not match number of data points!"
        
        xradius = self.width/2.0
        yradius = self.height/2.0
        centerx = self.x + xradius
        centery = self.y + yradius

        if self.direction == "anticlockwise":
            whichWay = 1
        else:
            whichWay = -1
        i = 0
        colorCount = len(self.defaultColors)
        
        g = Group()
        startAngle = self.startAngle #% 360
        for angle in normData:
            thisWedgeColor = self.defaultColors[i % colorCount]
            endAngle = (startAngle + (angle * whichWay)) #% 360
            if startAngle < endAngle:
                a1 = startAngle
                a2 = endAngle
            elif endAngle < startAngle:
                a1 = endAngle
                a2 = startAngle
            else:  #equal, do not draw
                continue

            # is it a popout?
            cx, cy = centerx, centery
            if self.popouts.has_key(i):
                # pop out the wedge
                averageAngle = (a1+a2)/2.0
                aveAngleRadians = averageAngle*math.pi/180.0
                popdistance = self.popouts[i]
                cx = centerx + popdistance * math.cos(aveAngleRadians)
                cy = centery + popdistance * math.sin(aveAngleRadians)

                
            theWedge = Wedge(cx,
                             cy,
                             xradius,
                             a1,
                             a2,
                             yradius=yradius)
            theWedge.fillColor = thisWedgeColor
            theWedge.strokeColor = self.strokeColor
            theWedge.strokeWidth = self.strokeWidth
            g.add(theWedge)
            # now draw a label
            if labels[i] <> "":
                averageAngle = (a1+a2)/2.0
                aveAngleRadians = averageAngle*math.pi/180.0
                labelX = centerx + (0.5 * self.width * math.cos(aveAngleRadians) * self.labelRadius)
                labelY = centery + (0.5 * self.height * math.sin(aveAngleRadians) * self.labelRadius)
                
                theLabel = String(labelX, labelY, labels[i])
                theLabel.textAnchor = "middle"
                theLabel.fontSize = self.labelFontSize
                theLabel.fontName = self.labelFontName
                theLabel.fillColor = self.labelColor

                g.add(theLabel)
                
            startAngle = endAngle
            i = i + 1

            
        return g

            
    #########################################################################
    #
    #   experiment on a PieChart exposing/modifying individual elements     #
    #
    #########################################################################

class WedgeFormatter(Widget):
    """This lets you customise some things about the wedges in a pie chart.
    It is not to be confused with the 'wedge itself'; this just holds
    a recipe for how to format one, and does not allow you to hack the
    angles.  It can format a genuine Wedge object for you with its
    format method. """
    _attrMap = {
        'strokeWidth':isNumber,
        'strokeColor':isColorOrNone,
        'strokeDashArray':isListOfNumbersOrNone,
        'popout':isNumber,
        'fontName':isString,
        'fontSize':isNumber,
        'fontColor':isColorOrNone,
        'labelRadius':isNumber
        }

    def __init__(self):
        self.strokeWidth = 0
        self.strokeColor = STATE_DEFAULTS["strokeColor"]
        self.strokeDashArray = STATE_DEFAULTS["strokeDashArray"]
        self.popout = 0
        self.fontName = STATE_DEFAULTS["fontName"]
        self.fontSize = STATE_DEFAULTS["fontSize"]
        self.fontColor = STATE_DEFAULTS["fillColor"]
        self.labelRadius = 1.2


class TypedPropertyCollection(Widget):
    """This makes it easy to create lists of objects.  You initialize
    it with a class of what it is to contain, and that is all you
    can add to it.  You can assign properties to the collection
    as a whole, or to a numeric index within it; if so it creates
    a new child object to hold that data.  So:
        wedges = TypesPropertyCollection0(WedgeFormatter)
        wedges.strokeWidth = 2                # applies to all
        wedges.strokeColor = colors.red       # applies to all
        wedges[3].strokeColor = colors.blue   # only to one
    The last line should be taken as a prescription of how to
    create wedge no. 3 if one is needed; no error is raised if
    there are only two data points."""
    def __init__(self, exampleClass):
        #give it same validation rules as what it holds
        self._prototype = exampleClass
        example = exampleClass()
        self._attrMap = example._attrMap.copy()
        #give it same default values as whhat it holds
        self.setProperties(example.getProperties())
        self._children = {}
        
        
        
    def __getitem__(self, index):
        try:
            return self._children[index]
        except KeyError:
            child = self._prototype()
            #should we copy down?  how to keep in synch?
            child.setProperties(Widget.getProperties(self))
            self._children[index] = child
            return child

    def __setitem__(self, key, value):
        assert isinstance(value, self._prototype), "This collection can only hold objects of type %s" % self._prototype.__name__
        
    def getProperties(self):
        # return any children which are defined and whatever
        # differs from the parent
        props = {}

        for (key, value) in Widget.getProperties(self).items():
            props['%s' % key] = value
                  
        for idx in self._children.keys():
            childProps = self._children[idx].getProperties()
            for (key, value) in childProps.items():
                parentValue = getattr(self, key)
                if parentValue <> value:
                    newKey = '[%s].%s' % (idx, key)
                    props[newKey] = value

        return props
    


class PieWithWedges(Widget):
    defaultColors = [colors.darkcyan,
                     colors.blueviolet,
                     colors.blue,
                     colors.cyan]
    _attrMap = {
        'x':isNumber,
        'y':isNumber,
        'width':isNumber,
        'height':isNumber,
        'data':isListOfNumbers,
        'labels':isListOfStringsOrNone,
        'startAngle':isNumber,
        'direction': lambda x: x in ['clockwise','anticlockwise'],
        'wedges':None   # could be improved
        }
    
    def __init__(self):
        self.x = 0
        self.y = 0
        self.width = 100
        self.height = 100
        self.data = [1]
        self.labels = None  # or list of strings
        self.startAngle = 90
        self.direction = "clockwise"

        
        self.wedges = TypedPropertyCollection(WedgeFormatter)
        # no need to change the defaults for a WedgeFormatter; if we did,
        ## we would do e.g.
        #self.wedges.strokeColor = colors.blueviolet
        
    def demo(self):
        self.x = 50
        self.y = 10
        self.height = 80
        self.width = 80
        self.data = [10,20,30,40,50,60]
                     
    def draw(self):
        # normalize slice data
        sum = 0.0
        for number in self.data:
            sum = sum + number
        normData = []
        for number in self.data:
            normData.append(360.0 * number / sum)

        #labels
        if self.labels is None:
            labels = [''] * len(normData)
        else:
            labels = self.labels
        assert len(labels) == len(self.data), "Number of labels does not match number of data points!"
        
        xradius = self.width/2.0
        yradius = self.height/2.0
        centerx = self.x + xradius
        centery = self.y + yradius

        if self.direction == "anticlockwise":
            whichWay = 1
        else:
            whichWay = -1
        i = 0
        colorCount = len(self.defaultColors)
        
        g = Group()
        startAngle = self.startAngle #% 360
        for angle in normData:
            thisWedgeColor = self.defaultColors[i % colorCount]
            endAngle = (startAngle + (angle * whichWay)) #% 360
            if startAngle < endAngle:
                a1 = startAngle
                a2 = endAngle
            elif endAngle < startAngle:
                a1 = endAngle
                a2 = startAngle
            else:  #equal, do not draw
                continue

            # is it a popout?
            cx, cy = centerx, centery
            if self.wedges[i].popout <> 0:
                # pop out the wedge
                averageAngle = (a1+a2)/2.0
                aveAngleRadians = averageAngle*math.pi/180.0
                popdistance = self.wedges[i].popout
                cx = centerx + popdistance * math.cos(aveAngleRadians)
                cy = centery + popdistance * math.sin(aveAngleRadians)

                
            theWedge = Wedge(cx,
                             cy,
                             xradius,
                             a1,
                             a2,
                             yradius=yradius)
            theWedge.fillColor = thisWedgeColor
            theWedge.strokeColor = self.wedges[i].strokeColor
            theWedge.strokeWidth = self.wedges[i].strokeWidth
            theWedge.strokeDashArray = self.wedges[i].strokeDashArray
            g.add(theWedge)
            # now draw a label
            if labels[i] <> "":
                averageAngle = (a1+a2)/2.0
                aveAngleRadians = averageAngle*math.pi/180.0
                labelX = centerx + (0.5 * self.width * math.cos(aveAngleRadians) * self.wedges[i].labelRadius)
                labelY = centery + (0.5 * self.height * math.sin(aveAngleRadians) * self.wedges[i].labelRadius)
                
                theLabel = String(labelX, labelY, labels[i])
                theLabel.textAnchor = "middle"
                theLabel.fontSize = self.wedges[i].fontSize
                theLabel.fontName = self.wedges[i].fontName
                theLabel.fillColor = self.wedges[i].fontColor

                g.add(theLabel)
                
            startAngle = endAngle
            i = i + 1

            
        return g

def test():
    d = Drawing(400,200)

    d.add(String(100,175,"Without labels", textAnchor="middle"))
    d.add(String(300,175,"With labels", textAnchor="middle"))
    

    pc = Pie()
    pc.x = 25
    pc.y = 50
    pc.data = [10,20,30,40,50,60]
    pc.popouts[0] = 5
    d.add(pc, 'pie1')
    
    pc2 = Pie()
    pc2.x = 150
    pc2.y = 50
    pc2.data = [10,20,30,40,50,60]
    pc2.labels = ['a','b','c','d','e','f']
    #pc2.labelRadius = 0.5
    d.add(pc2, 'pie2')

    pc3 = Pie()
    pc3.x = 275
    pc3.y = 50
    pc3.data = [10,20,30,40,50,60]
    pc3.labels = ['a','b','c','d','e','f']
    pc3.labelRadius = 0.65
    pc3.labelFontName = "Helvetica-Bold"
    pc3.labelFontSize = 16
    pc3.labelColor = colors.yellow
    d.add(pc3, 'pie3')

    c = Canvas('piechart0.pdf')
    c.setFont('Times-Roman', 20)
    c.drawString(100, 720, "Monolithic pie chart with no top level attributes")
    c.setFont('Times-Roman', 12)
    #BUG - currently the drawing gets the most recently used font as its default.
    d.drawOn(c, 100, 500)

    d = Drawing(400, 200)
    pc = PieWithWedges()
    pc.x = 150
    pc.y = 50
    pc.data = [10,20,30,40,50,60]
    pc.labels = ['a','b','c','d','e','f']
    pc.wedges.strokeWidth=0.5
    pc.wedges[3].popout = 20
    pc.wedges[3].strokeWidth = 2
    pc.wedges[3].strokeDashArray = [2,2]
    pc.wedges[3].labelRadius = 1.75
    pc.wedges[3].fontColor = colors.red
    

    pc.dumpProperties()
    d.add(pc)

    d.drawOn(c, 100, 200)

    c.setFont('Times-Roman', 20)
    c.drawString(100, 420, "Pie chart with wedges collection")
    c.setFont('Times-Roman', 12)
    c.drawString(100, 405, "Allows customisation of individual slices (but not their angles!)")
    
    
    c.save()
    print 'saved piechart0.pdf'

if __name__=='__main__':
    test()        