# core of the graphics library - defines Drawing and Shapes
"""
"""

from types import FloatType, IntType, ListType, TupleType, StringType
from pprint import pprint
from reportlab.platypus import Flowable
import string

from reportlab.config import shapeChecking

from reportlab.lib import colors

class NotImplementedError(Exception):
    pass
# two constants for filling rules
NON_ZERO_WINDING = 'Non-Zero Winding'
EVEN_ODD = 'Even-Odd'

## these can be overridden at module level before you start
#creating shapes.  So, if using a special color model,
#this provides support for the rendering mechanism.
#you can change defaults globally before you start
#making shapes; one use is to substitute another
#color model cleanly throughout the drawing.

STATE_DEFAULTS = {   # sensible defaults for all
    'transform': (1,0,0,1,0,0),

    # styles follow SVG naming
    'strokeColor': colors.black,
    'strokeWidth': 1,
    'strokeLineCap': 0,
    'strokeLineJoin': 0,
    'strokeMiterLimit' : 'TBA',  # don't know yet so let bomb here
    'strokeDashArray': None,
    'strokeOpacity': 1.0,  #100%

    'fillColor': colors.black,   #...or text will be invisible
    #'fillRule': NON_ZERO_WINDING, - these can be done later
    #'fillOpacity': 1.0,  #100% - can be done later

    'fontSize': 10,
    'fontName': 'Times-Roman',
    'textAnchor':  'start' # can be start, middle, end, inherited
    }

    ################################################################
    #
    #   Here are some standard verifying functions which can be
    #   used in an attrMap
    #
    ################################################################
    
def isBoolean(x):
    return (x in (0, 1))

def isString(x):
    return (type(x) == StringType)
            
def isNumber(x):
    """Don't think we really want complex numbers for widths!"""
    return (type(x) in (FloatType, IntType))

def isNumberOrNone(x):
    """Don't think we really want complex numbers for widths!"""
    if x is None:
        return 1
    else:
        return (type(x) in (FloatType, IntType))

def isTextAnchor(x):
    return (x in ('start','middle','end'))

def isListOfNumbers(x):
    """Don't think we really want complex numbers for widths!"""
    if type(x) in (ListType, TupleType):
        for element in x:
            if not isNumber(element):
                return 0
        return 1
    else:
        return 0

def isListOfNumbersOrNone(x):
    if x is None:
        return 1
    else:
        return isListOfNumbers(x)
    
def isListOfShapes(x):
    if type(x) in (ListType, TupleType):
        answer = 1
        for element in x:
            if not isinstance(x, Shape):
                answer = 0
        return answer
    else:
        return 0

def isListOfStrings(x):
    if type(x) in (ListType, TupleType):
        answer = 1
        for element in x:
            if type(element) <> type(""):
                answer = 0
        return answer
    else:
        return 0

def isListOfStringsOrNone(x):
    if x is None:
        return 1
    else:
        return isListOfStrings(x)

def isTransform(x):
    if type(x) in (ListType, TupleType):
        if len(x) == 6:
            for element in x:
                if not isNumber(element):
                    return 0
            return 1
        else:
            return 0
    else:
        return 0
    

def isColor(x):
    return isinstance(x, colors.Color)

def isColorOrNone(x):
    if x is None:
        return 1
    else:
        return isinstance(x, colors.Color)

def isValidChild(x):
    """Is it allowed in a drawing or group?  i.e.
    descends from Shape or UserNode"""
    return isinstance(x, UserNode) or isinstance(x, Shape)


   
class Shape:
    """Base class for all nodes in the tree. Nodes are simply
    packets of data to be created, stored, and ultimately
    rendered - they don't do anything active.  They provide
    convenience methods for verification but do not
    check attribiute assignments or use any clever setattr
    tricks this time."""
    _attrMap = None
    def __init__(self, keywords={}):
        """In general properties may be supplied to the
        constructor."""
        for key, value in keywords.items():
            #print 'setting keyword %s.%s = %s' % (self, key, value)
            setattr(self, key, value)

       
    def getProperties(self):
        """Interface to make it easy to extract automatic
        documentation"""
        #basic nodes have no children so this is easy.
        #for more complex objects like widgets you
        #may need to override this.
        props = {}
        for key, value in self.__dict__.items():
            if key[0:1] <> '_':
                props[key] = value
        return props
        
    def setProperties(self, props):
        """Supports the bulk setting if properties from,
        for example, a GUI application or a config file."""
        self.__dict__.update(props)
        #self.verify()

    def dumpProperties(self, prefix=""):
        """Convenience. Lists them on standard output.  You
        may provide a prefix - mostly helps to generate code
        samples for documentation."""
        propList = self.getProperties().items()
        propList.sort()
        if prefix:
            prefix = prefix + '.'
        for (name, value) in propList:
            print '%s%s = %s' % (prefix, name, value)
            
    def verify(self):
        """If the programmer has provided the optional
        _attrMap attribute, this checks all expected
        attributes are present; no unwanted attributes
        are present; and (if a checking function is found)
        checks each attribute.  Either succeeds or raises
        an informative exception."""
        if self._attrMap is not None:
            for key in self.__dict__.keys():
                if key[0] <> '_':
                    assert self._attrMap.has_key(key), "Unexpected attribute %s found in %s" % (key, self)
            for (attr, checkerFunc) in self._attrMap.items():
                assert hasattr(self, attr), "Missing attribute %s from %s" % (attr, self)
                if checkerFunc:
                    value = getattr(self, attr)
                    assert checkerFunc(value), "Invalid value %s for attribute %s in class %s" % (value, attr, self.__class__.__name__)
    if shapeChecking:
        """This adds the ability to check every attribite assignment as it is made.
        It slows down shapes but is a big help when developing. It does not
        get defined if config.shapeChecking = 0"""
        def __setattr__(self, attr, value):
            """By default we verify.  This could be off
            in some parallel base classes."""
            if self._attrMap is not None:
                if attr[0:1] <> '_':
                    try:
                        checker = self._attrMap[attr]
                        if checker:
                            if not checker(value):
                                raise AttributeError, "Illegal assignment of '%s' to '%s' in class %s" % (value, attr, self.__class__.__name__)
                    except KeyError:
                        raise AttributeError, "Illegal attribute '%s' in class %s" % (attr, self.__class__.__name__)
            #if we are still here, set it.
            self.__dict__[attr] = value
            #print 'set %s.%s = %s' % (self.__class__.__name__, attr, value)

class Drawing(Shape, Flowable):
    """Outermost container; the thing a renderer works on.
    This has no properties except a height, width and list
    of contents."""
    _attrMap = {'width':isNumber, 'height':isNumber, 'contents':isListOfShapes, 'canv':None}
    
    def __init__(self, width, height, *nodes):
        # Drawings need _attrMap to be an instance rather than
        # a class attribute, as it may be extended at run time.
        self._attrMap = self._attrMap.copy()
            
        self.width = width
        self.height = height
        self.contents = list(nodes)
        

    def add(self, node, name=None):
        """Adds a shape to a drawing.  If a name is provided, it may
        subsequently be accessed by name and becomes a regular
        attribute of the drawing."""
        assert isValidChild(node), "Can only add Shape or UserNode objects to a drawing"
        self.contents.append(node)
        if name:
            #it better be valid or the checker will scream; and we need
            #to make _attrMap an instance rather than a class attribite
            #at this point too
            self._attrMap[name] = isValidChild
            setattr(self, name, node)
            
    def draw(self):
        """This is used by the Platypus framework to let the document
        draw itself in a story.  It is specific to PDF and should not
        be used directly."""
        import renderPDF
        R = renderPDF._PDFRenderer()
        R.draw(self, self.canv, 0, 0)
    

class Group(Shape):
    """Groups elements together.  May apply a transform
    to its contents.  Has a publicly accessible property
    'contents' which may be used to iterate over contents.
    In addition, child nodes may be given a name in which
    case they are subsequently accessible as properties."""

    _attrMap = {'transform':isTransform, 'contents':isListOfShapes}
    
    def __init__(self, *elements, **keywords):
        """Initial lists of elements may be provided to allow
        compact definitions in literal Python code.  May or
        may not be useful."""

        # Groups need _attrMap to be an instance rather than
        # a class attribute, as it may be extended at run time.
        self._attrMap = self._attrMap.copy()
        self.contents = []
        self.transform = (1,0,0,1,0,0)
        for elt in elements:
            self.add(elt)
        # this just applies keywords; do it at the end so they
        #don;t get overwritten
        Shape.__init__(self, keywords)
        

    def add(self, node, name=None):
        """Appends child node to the 'contents' attribute.  In addition,
        if a name is provided, it is subsequently accessible by name"""
        # propagates properties down
        assert isValidChild(node), "Can only add Shape or UserNode objects to a Group"
        self.contents.append(node)
        if name:
            #it better be valid or the checker will scream; and we need
            #to make _attrMap an instance rather than a class attribite
            #at this point too
            self._attrMap[name] = isValidChild
            setattr(self, name, node)
        

    def rotate(self, theta):
        """Convenience to help you set transforms"""
        raise NotImplementedError, "Finish me off please!"

    def translate(self, dx, dy):
        """Convenience to help you set transforms"""
        raise NotImplementedError, "Finish me off please!"
    
    def scale(self, sx, sy):
        """Convenience to help you set transforms"""
        raise NotImplementedError, "Finish me off please!"


    def skew(self, kx, ky):
        """Convenience to help you set transforms"""
        raise NotImplementedError, "Finish me off please!"



class LineShape(Shape):
    # base for types of lines
    _attrMap = {
        'strokeColor':isColorOrNone,
        'strokeWidth':isNumber,
        'strokeLineCap':None,
        'strokeLineJoin':None,
        'strokeMiterLimit':isNumber,
        'strokeDashArray':None,
        }
    def __init__(self, kw):
        self.strokeColor = STATE_DEFAULTS['strokeColor']
        self.strokeWidth = 1
        self.strokeLineCap = 0
        self.strokeLineJoin = 0
        self.strokeMiterLimit = 0
        self.strokeDashArray = None
        self.setProperties(kw)

class Line(LineShape):
    _attrMap = {
        'strokeColor':isColorOrNone,
        'strokeWidth':isNumber,
        'strokeLineCap':None,
        'strokeLineJoin':None,
        'strokeMiterLimit':isNumber,
        'strokeDashArray':None,
        'x1':isNumber,
        'y1':isNumber,
        'x2':isNumber,
        'y2':isNumber
        }

    def __init__(self, x1, y1, x2, y2, **kw):
        LineShape.__init__(self, kw)
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2

    
class SolidShape(Shape):
    # base for anything with outline and content
    _attrMap = {
        'strokeColor':isColorOrNone,
        'strokeWidth':isNumber,
        'strokeLineCap':None,
        'strokeLineJoin':None,
        'strokeMiterLimit':isNumber,
        'strokeDashArray':None,
        'fillColor':isColorOrNone
        }
    def __init__(self, kw):
        self.strokeColor = STATE_DEFAULTS['strokeColor']
        self.strokeWidth = 1
        self.strokeLineCap = 0
        self.strokeLineJoin = 0
        self.strokeMiterLimit = 0
        self.strokeDashArray = None
        self.fillColor = STATE_DEFAULTS['fillColor']
        # do this at the end so keywords overwrite
        #the above settings
        Shape.__init__(self, kw)
        
class Path(SolidShape):
    # same as current implementation; to do
    pass
  
class Rect(SolidShape):
    """Rectangle, possibly with rounded corners."""    
    _attrMap = {
        'strokeColor': isColorOrNone,
        'strokeWidth': isNumber,
        'strokeLineCap': None,   #TODO - define the types expected and add a checker function
        'strokeLineJoin': None,  #TODO - define the types expected and add a checker function
        'strokeMiterLimit': None, #TODO - define the types expected and add a checker function
        'strokeDashArray': None, #TODO - define the types expected and add a checker function
        'fillColor': isColorOrNone,
        'x': isNumber,
        'y': isNumber,
        'width': isNumber,
        'height': isNumber,
        'rx': isNumber,
        'ry': isNumber
        }
        
    def __init__(self, x, y, width, height, rx=0, ry=0, **kw):
        SolidShape.__init__(self, kw)
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.rx = rx
        self.ry = ry    

class Circle(SolidShape):
    _attrMap = {
        'strokeColor': None,
        'strokeWidth': isNumber,
        'strokeLineCap': None,
        'strokeLineJoin': None,
        'strokeMiterLimit': None,
        'strokeDashArray': None,
        'fillColor': None,
        'cx': isNumber,
        'cy': isNumber,
        'r': isNumber
        }
    
    def __init__(self, cx, cy, r, **kw):
        SolidShape.__init__(self, kw)
        self.cx = cx
        self.cy = cy
        self.r = r

class Ellipse(SolidShape):
    _attrMap = {
        'strokeColor': None,
        'strokeWidth': isNumber,
        'strokeLineCap': None,
        'strokeLineJoin': None,
        'strokeMiterLimit': None,
        'strokeDashArray': None,
        'fillColor': None,
        'cx': isNumber,
        'cy': isNumber,
        'rx': isNumber,
        'ry': isNumber
        }
    def __init__(self, cx, cy, rx, ry, **kw):
        SolidShape.__init__(self, kw)
        self.cx = cx
        self.cy = cy
        self.rx = rx
        self.ry = ry

class Wedge(SolidShape):
    """A "slice of a pie" by default translates to a polygon moves anticlockwise
       from start angle to end angle"""
    _attrMap = {
        'strokeColor': None,
        'strokeWidth': isNumber,
        'strokeLineCap': None,
        'strokeLineJoin': None,
        'strokeMiterLimit': None,
        'strokeDashArray': None,
        'fillColor': None,
        'centerx': isNumber,
        'centery': isNumber,
        'radius': isNumber,
        'startangledegrees': isNumber,
        'endangledegrees': isNumber,
        'yradius':isNumberOrNone
        }
    degreedelta = 1 # jump every 1 degrees
    def __init__(self, centerx, centery, radius, startangledegrees, endangledegrees, yradius=None, **kw):
        if yradius is None: yradius = radius
        SolidShape.__init__(self, kw)
        while endangledegrees<startangledegrees:
            endangledegrees = endangledegrees+360
        #print "__init__"
        self.centerx, self.centery, self.radius, self.startangledegrees, self.endangledegrees = \
           centerx, centery, radius, startangledegrees, endangledegrees
        self.yradius = yradius
    #def __repr__(self):
    #        return "Wedge"+repr((self.centerx, self.centery, self.radius, self.startangledegrees, self.endangledegrees ))
    #__str__ = __repr__
    def asPolygon(self):
        #print "asPolygon"
        centerx, centery, radius, startangledegrees, endangledegrees = \
           self.centerx, self.centery, self.radius, self.startangledegrees, self.endangledegrees
        yradius = self.yradius
        degreedelta = self.degreedelta
        points = []
        a = points.append
        a(centerx); a(centery)
        from math import sin, cos, pi
        degreestoradians = pi/180.0
        radiansdelta = degreedelta*degreestoradians
        startangle = startangledegrees*degreestoradians
        endangle = endangledegrees*degreestoradians
        while endangle<startangle:
              #print "endangle", endangle
              endangle = endangle+2*pi
        angle = startangle
        #print "start", startangle, "end", endangle
        while angle<endangle:
            #print angle
            x = centerx + cos(angle)*radius
            y = centery + sin(angle)*yradius
            a(x); a(y)
            angle = angle+radiansdelta
        #print "done"
        x = centerx + cos(endangle)*radius
        y = centery + sin(endangle)*yradius
        a(x); a(y)
        return Polygon(points)

class Polygon(SolidShape):
    """Defines a closed shape; Is implicitly
    joined back to the start for you."""
    _attrMap = {
        'strokeColor': None,
        'strokeWidth': isNumber,
        'strokeLineCap': None,
        'strokeLineJoin': None,
        'strokeMiterLimit': None,
        'strokeDashArray': None,
        'fillColor': None,
        'points': isListOfNumbers,
        }
    def __init__(self, points=[], **kw):
        SolidShape.__init__(self, kw)
        assert len(points) % 2 == 0, 'Point list must have even number of elements!'
        self.points = points

class PolyLine(LineShape):
    """Series of line segments.  Does not define a
    closed shape; never filled even if apparently joined.
    Put the numbers in the list, not two-tuples."""
    _attrMap = {
        'strokeColor':isColorOrNone,
        'strokeWidth':isNumber,
        'strokeLineCap':None,
        'strokeLineJoin':None,
        'strokeMiterLimit':isNumber,
        'strokeDashArray':None,
        'points':isListOfNumbers
        }
    def __init__(self, points=[], **kw):
        LineShape.__init__(self, kw)
        lenPoints = len(points)
        if lenPoints:
            if type(points[0]) in (ListType,TupleType):
                L = []
                for (x,y) in points:
                    L.append(x)
                    L.append(y)
                points = L
            else:
                assert len(points) % 2 == 0, 'Point list must have even number of elements!'
        self.points = points

class String(Shape):
    """Not checked against the spec, just a way to make something work.
    Can be anchored left, middle or end."""
    # to do.
    _attrMap = {
        'x': isNumber,
        'y': isNumber,
        'text': isString,
        'fontName':None,  #TODO - checker
        'fontSize':isNumber,
        'fillColor':isColorOrNone,
        'textAnchor':isTextAnchor
        }
    def __init__(self, x, y, text, **kw):
        self.x = x
        self.y = y
        self.text = text
        self.textAnchor = 'start'
        self.fontName = STATE_DEFAULTS['fontName']
        self.fontSize = STATE_DEFAULTS['fontSize']
        self.fillColor = STATE_DEFAULTS['fillColor']
        self.setProperties(kw)

class UserNode:
        """A simple template for creating a new node.  The user (Python
        programmer) may subclasses this.  provideNode() must be defined to
        provide a Shape primitive when called by a renderer.  It does
        NOT inherit from Shape, as the renderer always replaces it, and
        your own classes can safely inherit from it without getting
        lots of unintended behaviour."""

        def provideNode(self):
                """Override this to create your own node. This lets widgets be
                added to drawings; they must create a shape (typically a group)
                so that the renderer can draw the custom node."""
                raise NotImplementedError, "this method must be redefined by the user/programmer"




def test():
    r = Rect(10,10,200,50)
    import pprint
    pp = pprint.pprint
    print 'a Rectangle:'
    pp(r.getProperties())
    print
    print 'verifying...',
    r.verify()
    print 'OK'
    #print 'setting rect.z = "spam"'
    #r.z = 'spam'
    print 'deleting rect.width'
    del r.width
    print 'verifying...',
    r.verify()
    

if __name__=='__main__':
    test()
    