###############################################################################
#   $Log $
#   
#   
"""
Superclass for renderers to factor out common functionality and default implementations.
"""


__version__=''' $Id $ '''

from reportlab.graphics.shapes import *

def inverse(A):
    "For A affine 2D represented as 6vec return 6vec version of A**(-1)"
    # I checked this RGB
    det = float(A[0]*A[3] - A[2]*A[1])
    R = [A[3]/det, -A[1]/det, -A[2]/det, A[0]/det]
    return tuple(R+[-R[0]*A[4]-R[2]*A[5],-R[1]*A[4]-R[3]*A[5]])

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


def getStateDelta(shape):
    """Used to compute when we need to change the graphics state.
    For example, if we have two adjacent red shapes we don't need
    to set the pen color to red in between. Returns the effect
    the given shape would have on the graphics state"""
    delta = {}
    for (prop, value) in shape.getProperties().items():
        if STATE_DEFAULTS.has_key(prop):
            delta[prop] = value
    return delta


class StateTracker:
    """Keeps a stack of transforms and state
    properties.  It can contain any properties you
    want, but the keys 'transform' and 'ctm' have
    special meanings.  The getCTM()
    method returns the current transformation
    matrix at any point, without needing to
    invert matrixes when you pop."""
    def __init__(self, defaults=None):
        # one stack to keep track of what changes...
        self.__deltas = []

        # and another to keep track of cumulative effects.  Last one in
        # list is the current graphics state.  We put one in to simplify
        # loops below.
        self.__combined = []
        if defaults is None:
            defaults = STATE_DEFAULTS.copy()
        #ensure  that if we have a transform, we have a CTM
        if defaults.has_key('transform'):
            defaults['ctm'] = defaults['transform']
        self.__combined.append(defaults)

    def push(self,delta):
        """Take a new state dictionary of changes and push it onto
        the stack.  After doing this, the combined state is accessible
        through getState()"""

        newstate = self.__combined[-1].copy()
        for (key, value) in delta.items():
            if key == 'transform':  #do cumulative matrix
                newstate['transform'] = delta['transform']
                newstate['ctm'] = mmult(self.__combined[-1]['ctm'], delta['transform'])
                #print 'statetracker transform = (%0.2f, %0.2f, %0.2f, %0.2f, %0.2f, %0.2f)' % tuple(newstate['transform'])
                #print 'statetracker ctm = (%0.2f, %0.2f, %0.2f, %0.2f, %0.2f, %0.2f)' % tuple(newstate['ctm'])
                
            else:  #just overwrite it
                newstate[key] = value

        self.__combined.append(newstate)
        self.__deltas.append(delta)

    def pop(self):
        """steps back one, and returns a state dictionary with the
        deltas to reverse out of wherever you are.  Depending
        on your back endm, you may not need the return value,
        since you can get the complete state afterwards with getState()"""
        del self.__combined[-1]
        newState = self.__combined[-1]
        lastDelta = self.__deltas[-1]
        del  self.__deltas[-1]
        #need to diff this against the last one in the state
        reverseDelta = {}
        for key, curValue in lastDelta.items():
            prevValue = newState[key]
            if prevValue <> curValue:
                if key == 'transform':
                    reverseDelta[key] = inverse(lastDelta['transform'])
                else:  #just return to previous state
                    reverseDelta[key] = prevValue
        return reverseDelta

    def getState(self):
        "returns the complete graphics state at this point"
        return self.__combined[-1]

    def getCTM(self):
        "returns the current transformation matrix at this point"""
        return self.__combined[-1]['ctm']


def testStateTracker():
    print 'Testing state tracker'
    defaults = {'fillColor':None, 'strokeColor':None,'fontName':None, 'transform':[1,0,0,1,0,0]}
    deltas = [
        {'fillColor':'red'},
        {'fillColor':'green', 'strokeColor':'blue','fontName':'Times-Roman'},
        {'transform':[0.5,0,0,0.5,0,0]},
        {'transform':[0.5,0,0,0.5,2,3]},
        {'strokeColor':'red'}
        ]

    st = StateTracker(defaults)
    print 'initial:', st.getState()
    print
    for delta in deltas:
        print 'pushing:', delta
        st.push(delta)
        print 'state:  ',st.getState(),'\n'

    for delta in deltas:
        print 'popping:',st.pop()
        print 'state:  ',st.getState(),'\n'


class Renderer:
    """Virtual superclass for graphics renderers."""

    def __init__(self):
        self._tracker = StateTracker()
        
    def undefined(self, operation):
        raise ValueError, "%s operation not defined at superclass class=%s" %(operation, self.__class__)

    def draw(self, drawing, canvas, x, y):
        """This is the top level function, which
        draws the drawing at the given location.
        The recursive part is handled by drawNode."""
        self.undefined("draw")

    def drawNode(self, node):
        """This is the recursive method called for each node
        in the tree"""
        # Undefined here, but with closer analysis probably can be handled in superclass
        self.undefined("drawNode")
        
    def drawNodeDispatcher(self, node):
        """dispatch on the node's (super) class: shared code"""
        #print "drawNodeDispatcher", self, node.__class__

        # replace UserNode with its contents
        if isinstance(node, UserNode):
            node = node.provideNode()

        #draw the object, or recurse

        if isinstance(node, Line):
            self.drawLine(node)
        elif isinstance(node, Rect):
            self.drawRect(node)
        elif isinstance(node, Circle):
            self.drawCircle(node)
        elif isinstance(node, Ellipse):
            self.drawEllipse(node)
        elif isinstance(node, PolyLine):
            self.drawPolyLine(node)
        elif isinstance(node, Polygon):
            self.drawPolygon(node)
        elif isinstance(node, Path):
            self.drawPath(node)
        elif isinstance(node, String):
            self.drawString(node)
        elif isinstance(node, Group):
            self.drawGroup(node)
        elif isinstance(node, Wedge):
            #print "drawWedge"
            self.drawWedge(node)
        else:
            print 'DrawingError','Unexpected element %s in drawing!' % str(node)
        #print "done dispatching"
            
    _restores = {'stroke':'_stroke','stroke_width': '_lineWidth','stroke_linecap':'_lineCap',
                'stroke_linejoin':'_lineJoin','fill':'_fill','font_family':'_font',
                'font_size':'_fontSize'}

    def drawGroup(self, group):
        # just do the contents.  Some renderers might need to override this
        # if they need a flipped transform
        for childNode in group.contents:
            self.drawNode(childNode)

    def drawWedge(self, wedge):
        # by default ask the wedge to make a polygon of itself and draw that!
        #print "drawWedge"
        polygon = wedge.asPolygon()
        self.drawPolygon(polygon)
        
    def drawPath(self, path):
        polygons = path.asPolygons()
        for polygon in polygons:
                self.drawPolygon(polygon)

    def drawRect(self, rect):
        # could be implemented in terms of polygon
        self.undefined("drawRect")
        
    def drawLine(self, line):
        self.undefined("drawLine")

    def drawCircle(self, circle):
        self.undefined("drawCircle")

    def drawPolyLine(self, p):
        self.undefined("drawPolyLine")

    def drawEllipse(self, ellipse):
        self.undefined("drawEllipse")

    def drawPolygon(self, p):
        self.undefined("drawPolygon")

    def drawString(self, stringObj):
        self.undefined("drawString")

    def applyStateChanges(self, delta, newState):
        """This takes a set of states, and outputs the operators
        needed to set those properties"""
        self.undefined("applyStateChanges")

if __name__=='__main__':
    print "this file has no script interpretation"
    print __doc__
