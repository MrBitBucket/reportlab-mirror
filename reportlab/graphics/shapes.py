# core of the graphics library - defines Drawing and Shapes
"""
"""

import string
from math import pi, cos, sin, tan
from types import FloatType, IntType, ListType, TupleType, StringType
from pprint import pprint

from reportlab.platypus import Flowable
from reportlab.rl_config import shapeChecking
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


# Singleton value for automatic numerals.

class _Auto:
    "Class for a numeral whose value is determined when needed."

    def __repr__(self):
        return 'Auto'

    def __str__(self):
        return 'Auto'

Auto = _Auto()


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

def isNumberOrAuto(x):
    """Don't think we really want complex numbers for widths!"""
    if x == Auto:
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


class OneOf:
    """Make validator functions for list of choices. Usage:
    >>> f = shapes.OneOf(('happy','sad'))
    >>> f('happy')
    1
    >>> f('grumpy')
    0
    >>> 
    """
    def __init__(self, choices):
        self._choices = choices
    def __call__(self, arg):
        return arg in self._choices


class SequenceOf:
    """Make validator functions for sequence of things:
    >>> isListOfColors = shapes.SequenceOf(isColor)
    
    """
    def __init__(self, atomicFunc):
        self._atomicFunc = atomicFunc
    def __call__(self, seq):
        if type(seq) not in (ListType, TupleType):
            return 0
        else:
            for elem in seq:
                if not self._atomicFunc(elem):
                    return 0
            return 1

    
    ####################################################################
    # math utilities.  These could probably be moved into lib
    # somewhere.
    ####################################################################

# constructors for matrices:
def nullTransform():
    return (1, 0, 0, 1, 0, 0)

def translate(dx, dy):
    return (1, 0, 0, 1, dx, dy)

def scale(sx, sy):
    return (sx, 0, 0, sy, 0, 0)

def rotate(angle):
    a = angle * pi /180 
    return (cos(a), sin(a), -sin(a), cos(a), 0, 0)

def skewX(angle):
    a = angle * 180 / pi
    return (1, 0, tan(a), 1, 0, 0)

def skewY(angle):
    a = angle * 180 / pi
    return (1, tan(a), 0, 1, 0, 0)

def mmult(A, B):
    "A postmultiplied by B"
    # I checked this RGB
    # [a0 a2 a4]    [b0 b2 b4]
    # [a1 a3 a5] *  [b1 b3 b5]
    # [      1 ]    [      1 ]
    #
    return (A[0]*B[0] + A[2]*B[1],
            A[1]*B[0] + A[3]*B[1],
            A[0]*B[2] + A[2]*B[3],
            A[1]*B[2] + A[3]*B[3],
            A[0]*B[4] + A[2]*B[5] + A[4],
            A[1]*B[4] + A[3]*B[5] + A[5])

def inverse(A):
    "For A affine 2D represented as 6vec return 6vec version of A**(-1)"
    # I checked this RGB
    det = float(A[0]*A[3] - A[2]*A[1])
    R = [A[3]/det, -A[1]/det, -A[2]/det, A[0]/det]
    return tuple(R+[-R[0]*A[4]-R[2]*A[5],-R[1]*A[4]-R[3]*A[5]])

def zTransformPoint(A,v):
    "Apply the homogenous part of atransformation a to vector v --> A*v"
    return (A[0]*v[0]+A[2]*v[1],A[1]*v[0]+A[3]*v[1])

def transformPoint(A,v):
    "Apply transformation a to vector v --> A*v"
    return (A[0]*v[0]+A[2]*v[1]+A[4],A[1]*v[0]+A[3]*v[1]+A[5])

def transformPoints(matrix, V):
    return map(transformPoint, V)

def zTransformPoints(matrix, V):
    return map(lambda x,matrix=matrix: zTransformPoint(matrix,x), V)

def _textBoxLimits(text, font, fontSize, leading, textAnchor, boxAnchor):
	w = 0
	for t in text:
		w = max(w,stringWidth(t,font, fontSize))

	h = len(text)*leading
	yt = fontSize
	if boxAnchor[0]=='s':
		yb = -h
		yt = yt - h
	elif boxAnchor[0]=='n':
		yb = 0
	else:
		yb = -h/2.0
		yt = yt + yb

	if boxAnchor[-1]=='e':
		xb = -w
		if textAnchor=='end': xt = 0
		elif textAnchor=='start': xt = -w
		else: xt = -w/2.0
	elif boxAnchor[-1]=='w':
		xb = 0
		if textAnchor=='end': xt = w
		elif textAnchor=='start': xt = 0
		else: xt = w/2.0
	else:
		xb = -w/2.0
		if textAnchor=='end': xt = -xb
		elif textAnchor=='start': xt = xb
		else: xt = 0

	return xb, yb, w, h, xt, yt

def _rotatedBoxLimits( x, y, w, h, angle):
    '''
    Find the corner points of the rotated w x h sized box at x,y 
    return the corner points and the min max points in the original space
    '''
    C = zTransformPoints(rotate(angle),((x,y),(x+w,y),(x+w,y+h),(x,y+h)))
    X = map(lambda x: x[0], C)
    Y = map(lambda x: x[1], C)
    return min(X), max(X), min(Y), max(Y), C


    #################################################################
    #
    #    And now the shapes themselves....
    #
    #################################################################
   
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

    def copy0(self):
        """Return a clone of this shape."""

        # implement this in the descendants as they need the right init methods.
        raise NotImplementedError, "No copy method implemented for %s" % self.__class__.__name__
       
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
        """This adds the ability to check every attribute assignment as it is made.
        It slows down shapes but is a big help when developing. It does not
        get defined if rl_config.shapeChecking = 0"""

        #print 'shapeChecking = 1, defining setattr'
        def __setattr__(self, attr, value):
            """By default we verify.  This could be off
            in some parallel base classes."""
            if self._attrMap is not None:
                if attr[0] <> '_':
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
    #else:
    #    print 'shapeChecking = 0, not defining setattr'


class Drawing(Shape, Flowable):
    """Outermost container; the thing a renderer works on.
    This has no properties except a height, width and list
    of contents."""

    _attrMap = {
        'width':isNumber,
        'height':isNumber,
        'contents':isListOfShapes,
        'canv':None}
    
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

    def expandUserNodes0(self):
        """Return a new drawing which only contains primitive shapes."""

        # many limitations - shared nodes become multiple ones,
        newDrawing = Drawing(self.width, self.height)
        newDrawing._attrMap = self._attrMap.copy()

        for child in self.contents:
            if isinstance(child, UserNode):
                newChild = child.provideNode()
            elif isinstance(child, Group):
                newChild = child.expandUserNodes0()
            else:
                newChild = child.copy0()
            newDrawing.contents.append(newChild)
        # they may have names.  reproduce them

        for (oldKey, oldValue) in self.__dict__.items():
            if oldValue in self.contents:
                pos = mylist.index(oldValue)
                setattr(newDrawing, oldKey, newDrawing.contents[pos])

        return newDrawing

    def copy0(self):
        """Returns a deep copy of the drawing."""
        
        newDrawing = Drawing(self.width, self.height)
        newDrawing._attrMap = self._attrMap.copy0()
        for child in self.contents:
            newDrawing.contents.append(child)

        for (oldKey, oldValue) in self.__dict__.items():
            if oldValue in self.contents:
                pos = self.contents.index(oldValue)
                setattr(newDrawing, oldKey, newDrawing.contents[pos])

        return newDrawing
            
    def expandUserNodes0(self):
        """Return a new group which only contains primitive shapes."""

        # many limitations - shared nodes become multiple ones,
        newDrawing = Drawing(self.width, self.height)
        newDrawing._attrMap = self._attrMap.copy0()

        for child in self.contents:
            if isinstance(child, UserNode):
                newChild = child.provideNode()
            elif isinstance(child, Group):
                newChild = child.expandUserNodes0()
            else:
                newChild = child.copy0()
            newDrawing.contents.append(newChild)
        # they may have names.  reproduce them

        for (oldKey, oldValue) in self.__dict__.items():
            if oldValue in self.contents:
                pos = self.contents.index(oldValue)
                setattr(newDrawing, oldKey, newDrawing.contents[pos])

        return newDrawing
        

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

    def copy0(self):
        """Returns a new group with recursively copied contents.

        Expands all user nodes if they do not define a copy method."""

        newGroup = Group()
        newGroup.transform = self.transform[:]
        for child in self.contents:
            newGroup.append(child.copy())
        # they may have names.  reproduce them
        for (oldKey, oldValue) in self.__dict__.items():
            if oldValue in self.contents:
                pos = mylist.index(oldValue)
                setattr(newGroup, oldKey, newGroup.contents[pos])
        return newGroup

    def expandUserNodes0(self):
        """Return a new group which only contains primitive shapes."""

        # many limitations - shared nodes become multiple ones,
        newGroup = Group()
        newGroup.transform = self.transform[:]
        
        for child in self.contents:
            if isinstance(child, UserNode):
                newChild = child.provideNode()
            elif isinstance(child, Group):
                newChild = child.expandUserNodes0()
            else:
                newChild = child.copy()
            newGroup.contents.append(newChild)
        # they may have names.  reproduce them

        for (oldKey, oldValue) in self.__dict__.items():
            if oldValue in self.contents:
                pos = mylist.index(oldValue)
                setattr(newGroup, oldKey, newGroup.contents[pos])

        return newGroup
            

    def rotate(self, theta):
        """Convenience to help you set transforms"""
        self.transform = mmult(self.transform, rotate(theta))
    
    def translate(self, dx, dy):
        """Convenience to help you set transforms"""
        self.transform = mmult(self.transform, translate(dx, dy))
    
    def scale(self, sx, sy):
        """Convenience to help you set transforms"""
        self.transform = mmult(self.transform, scale(sx, sy))
    

    def skew(self, kx, ky):
        """Convenience to help you set transforms"""
        self.transform = mmult(mmult(self.transform, skewX(kx)),skewY(ky))
    

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

    def copy0(self):
        new = Rect(self.x, self.y, self.width, self.height)
        new.setProperties(self.getProperties())
        return new
    

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

    def copy0(self):
        new = Circle(self.cx, self.cy, self.r)
        new.setProperties(self.getProperties())
        return new


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

    def copy0(self):
        new = Ellipse(self.cx, self.cy, self.rx, self.ry)
        new.setProperties(self.getProperties())
        return new


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

    def copy0(self):
        new = Wedge(self.centerx,
                    self.centery,
                    self.radius,
                    self.startangledegrees,
                    self.endangledegrees)
        new.setProperties(self.getProperties())
        return new


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

    def copy0(self):
        new = Polygon(self.points)
        new.setProperties(self.getProperties())
        return new


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

    def copy0(self):
        new = PolyLine(self.points)
        new.setProperties(self.getProperties())
        return new


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

    def copy0(self):
        new = String(self.x, self.y, self.text)
        new.setProperties(self.getProperties())
        return new


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
