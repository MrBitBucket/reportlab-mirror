#!/usr/bin/env python

"""Make the ReportLab vector logo from a Create XML file.

Right now the file containing the XML data for the logo is
loaded only once into a singleton XML tree, but for each
logo instance the relevant data is retrieved from the XML
tree again. Clearly, this could be further optimised, but
at the expense of losing some generality...
"""

import pprint, os, string
from types import StringType, ListType, TupleType

from reportlab.lib.units import cm
from reportlab.lib.colors import *
from reportlab.graphics.shapes import *
from reportlab.graphics.widgetbase import *
from reportlab.graphics import renderPDF

import pyRXP


_LOGODATA = None


######################################################################
# Math helpers
######################################################################

def sign(x):
    "Return sign of x."
    # Funny, but this is still not in the standard module 'math'...

    if x < 0:
        return -1
    elif x > 0:
        return 1
    else:
        return 0


def turn3(A, B, C):
    "Return 1|0|-1 if C is left|on|right of A->B"

    return (C[0]-A[0])*(B[1]-A[1]) - (C[1]-A[1])*(B[0]-A[0])


def turn(pts, debug=0):
    """Return signed cummulated sum of turn3 over a list of points.

    Note that for 'twisted' (but still 'uncurved') polygons you can
    get a perfectly valid orientation value of zero!

    Also note that for our purposes points connected with curved
    Bezier paths don't change the orientation, as we don't deal with
    the control points here! Strictly speaking, though, the order
    of the two control points associated to a polygon 'edge' do have
    an impact on that edge's contribution to the overall orientation!

    This function ignores that, but it is very straightforward to
    implement a function that correctly respects the control points.
    """

    # Sort of a hack we'll solve later...
    if len(pts) < 3:
        return 0

    # Add cumulated sums of shifted neighbouring triple points.
    sum = 0
    for i in xrange(len(pts)-2):
        A, B, C = pts[i:i+3]
        sum = sum + turn3(A, B, C)

    # Add contributions of triple points wrapped at the path's end.
    sum = sum + turn3(pts[-2], pts[-1], pts[0])
    sum = sum + turn3(pts[-1], pts[0], pts[1])

    return sign(sum)


def scaleBackAfterSkew(width, height, skewTransform, _debug=0):
    "Returns a scaling transform to re-fit a skewed rect into its original size rect."

    # Not excessively tested!! Handle with care!

    mm = mmult
    x0, y0 = width, height
    if _debug:
        print "before skewing: x1, y1", x0, y0
    trans0 = skewTransform
    x1, y1 = transformPoint(trans0, (width, height))
    if _debug:
        print "after skewing: x1, y1", x1, y1

    scx = scale(1, 1)
    scy = scale(1, 1)
    fx = x0/x1
    if fx < 1:
        scx = scale(fx, 1)
        if _debug:
            print 'fx', fx
            print 'scx', scx
    fy = y0/y1
    if fy < 1:
        scy = scale(1, fy)
        if _debug:
            print 'fy', fy
            print 'scy', scy
    sc = mm(scx, scy)
    if _debug:
        print 'sc', sc

    trans1 = mm(sc, trans0)
    x1, y1 = transformPoint(trans1, (width, height))
    if _debug:
        print "final: x1, y1", x1, y1

    return trans1


######################################################################
# Data helpers
######################################################################

def rmWhitespace(data):
    "Remove all whitespace strings from a sequence."

    if data == [] or data == None:
        return data

    L = []
    for i in xrange(len(data)):
        d = data[i]
        if type(d) == StringType:
            if string.strip(d) != '':
                L.append(d)
        else:
            L.append(d)

    assert len(L) <= len(data)

    return L


def makePairList(list):
    """Return a list with even length as list of pairs.

    E.g. [0, 1, 2, 3] -> [(0, 1), (2, 3)].
    """

    assert len(list) % 2 == 0

    L = []
    for i in range(0, len(list), 2):
        L.append((list[i], list[i+1]))

    return L


######################################################################
# Convenience XML displaying functions
#
# These functions are not strictly needed, but allow to display
# pretty nicely a tree parsed with pyRXP.
# (These were originaly written to operate on such XML "trees",
# but would be just as easy to write using their PropertyList
# dictionary equivalent.)
######################################################################

def printStructure(tree, lev=0):
    "Print tree as indented list of tag names (only)."

    if tree == None:
        return

    [tagName, attrs, content, unused] = tree

    print "%s%s" % (lev*'  ', tagName)

    if content != None:
        for c in content:
            if type(c) == TupleType:
                printStructure(c, lev+1)


def printExtendedStructure(tree, lev=0):
    """Print tree as indented list of tags, with 'some' content.

    We print only tags named 'key' and 'string' plus what
    they contain.
    """

    if tree == None:
        return

    [tagName, attrs, content, unused] = tree

    if tagName not in ('key', 'string'):
        print "%s%s" % (lev*'  ', tagName)

    if content != None:
        for c in content:
            if type(c) == TupleType:
                printExtendedStructure(c, lev+1)

    if tagName in ('key', 'string'):
        if content:
            cont = content[0]
        else:
            cont = ''
        print "%s%s: %s" % (lev*'  ', tagName, repr(cont))


def printExtendedStructure2(tree, lev=0):
    "Print tree as indented list of tags, with some summarized content."

    if tree == None:
        return

    [tagName, attrs, content, unused] = tree

    if content != None:
        for c in content:
            if type(c) == TupleType:
                printExtendedStructure2(c, lev+1)

    if tagName == 'dict':
        kvPairs = makePairList(content)
        kvPairs = filter(lambda p:p[0][2][0] in ('Bounds', 'Class', 'Rotation'), kvPairs)
        found = 0
        for k, v in kvPairs:
            if k[2][0] == 'Class':
                if v[2] == ['Rectangle']:
                    found = 1
        if found:
            keys = map(lambda p:p[0][2][0], kvPairs)
            print "%s%s: %s" % (lev*'  ', tagName, repr(string.join(keys, '|')))


######################################################################
# XML utility and conversion stuff
######################################################################

def cleanTree(tree):
    "Remove all intra-element whitespace data from the tree."
    # Could be an option for pyRXP, perhaps?

    if tree == None:
        return

    [tagName, attrs, content, unused] = tree

    if content != None:
        if type(content == TupleType):
            content = rmWhitespace(content)
            for i in xrange(len(content)):
                cont = content[i]
                if type(cont) != StringType and len(cont) == 4:
                    content[i] = tuple(cleanTree(cont))

    clone = [tagName, attrs, content, unused]

    return clone


def tree2dict(cleanTree):
    "Convert a clean XML tree to a PropertyList as Python dictionary."
    # This allows to access tree data MUCH EASIER!

    tree = cleanTree
    if tree == None:
        return

    [tagName, attrs, content, unused] = tree

    if tagName == 'plist':
        return tree2dict(content[0])

    elif tagName == 'string':
        try:
            return content[0]
        except IndexError:
            return ''

    elif tagName == 'data':
        s = content[0]
        for c in string.whitespace:
            s = string.replace(s, c, '')
        return s

    elif tagName == 'key':
        return content[0]

    elif tagName == 'array':
        try:
            return map(tree2dict, content)
        except TypeError:
            return []

    elif tagName == 'dict':
        res = {}
        kvPairs = makePairList(content)
        for k, v in kvPairs:
            res[tree2dict(k)] = tree2dict(v)
        return res

    return None


def dict2tree(cleanDict):
    return


######################################################################
# Data handling
######################################################################

def bounds2rect(bounds):
    "Convert a Bounds value to a RL rectangle tuple."

    bounds = string.replace(bounds, '{', '(')
    bounds = string.replace(bounds, '}', ')')
    (x, y), (width, height) = eval(bounds)
    bounds = x, y, width, height

    return bounds


def bezierDict2data(dict):
    "Fetch Bezier path data from a dict."

    bounds = bounds2rect(dict['Bounds'])
    ops = dict['BezierDict']['Operations']
    ops = map(lambda x:int(x), ops)
    pts = dict['BezierDict']['Points']
    pts = map(lambda x:eval(x[1:-1]), pts)

    return ops, pts, bounds


def rectDict2data(dict):
    "Fetch rectangle data from a dict."

    bounds = bounds2rect(dict['Bounds'])
    rot = dict.get('Rotation', 0)

    return bounds, rot


def displacePoints(pts, dx, dy):
    "Return a list of points displaced by (dx, dy)."

    for i in xrange(len(pts)):
        p = pts[i]
        pts[i] = (p[0]+dx, p[1]+dy)

    return pts


######################################################################


class RLVectorLogo(Widget):
    """Vectorised ReportLab logo, based on a Create XML file.

    For further information about Create see www.stone.com.
    """

    _attrMap = AttrMap(
        x = AttrMapValue(isNumber),
        y = AttrMapValue(isNumber),
        height = AttrMapValue(isNumberOrNone),
        width = AttrMapValue(isNumberOrNone),
        strokeColor = AttrMapValue(isColorOrNone),
        fillColor = AttrMapValue(isColorOrNone),
        skewValues = AttrMapValue(isListOfNumbers),
        strokeWidth = AttrMapValue(isNumber),
        borderWidth = AttrMapValue(isNumber),
        )

    import reportlab
    _rlDir = os.path.dirname(reportlab.__file__)
    _filename = os.path.join(_rlDir, 'lib', 'rllogo.cre8') # actually a directory!
    _dtdPath = 'file://localhost/System/Library/DTDs/PropertyList.dtd'

    def __init__(self):
        self.x = 0
        self.y = 0
        self.width = 136.5
        self.height = 90.5

        self.strokeColor = black # Or ReportLabBlue, mostly...
        self.fillColor = white

        self.skewValues = (10, 0)
        self.strokeWidth = 0
        self.borderWidth = 0

        self._showPoints = 0
        self._debug = 0

        global _LOGODATA
        if not _LOGODATA:
            _LOGODATA = self.buildTreeFromXmlFile()

        self._tree = _LOGODATA
        self._tree = cleanTree(self._tree)

        # Find outer bounds of the graphic.
        dict = tree2dict(self._tree)
        bounds = dict['PageList'][0]['GraphicsList'][0]['Bounds']        
        bounds = bounds2rect(bounds)
        bounds = map(float, bounds)
        self._width, self._height = bounds[2:4]


    def _printDict(self):
        import pprint        
        dict = tree2dict(self._tree)
        pprint.pprint(dict)


    def _printTree(self):
        import pprint        
        pprint.pprint(self._tree)


    def buildTreeFromXmlFile(self):
        "Parse an XML file and return the tree."

        path = self._filename
        if os.path.splitext(path)[1] == '.cre8':
            path = os.path.join(path, 'Document.cre8')
        xmlCode = open(path).read()
        dtd = os.path.basename(self._dtdPath)
        dtd = os.path.join(self._rlDir, 'lib', dtd)
        dtd = os.path.splitdrive(dtd)[1]
        dtd = string.replace(dtd, '\\', '/')
        dtd = "file://%s" % dtd
        xmlCode = string.replace(xmlCode, self._dtdPath, dtd)
        tree = pyRXP.parse(xmlCode,
                           srcName=path,
                           warnCB=lambda x: sys.stdout.write(x))

        from reportlab.rl_config import _verbose
        if _verbose:
            print "loaded %s" % self._filename

        return tree


    def demo(self):
        d = shapes.Drawing(self.width, self.height)
        d.add(self)

        return d


    def _addDisks(self, drawing, pts):
        "Add a list of disks with changing colors from blue to red."
        
        startCol = blue
        endCol = red
        for i in range(len(pts)):
            pt = pts[i]
            c = linearlyInterpolatedColor(startCol, endCol, 0, len(pts), i)
            disk = Circle(pt[0], pt[1], 2)
            disk.strokeColor = c
            disk.fillColor = c
            drawing.add(disk)


    def _addPaths(self, group, ops, pts):
        # This could, perhaps also use Path(points, operators) syntax...
        # (if it gets the winding right).

        g = group

        moveTo, lineTo, curveTo, close = range(4)
        left, right = 1, -1

        filledPaths = []
        emptyPaths = []
        circleLists = []
        lines = []

        strokeColor = self.strokeColor
        fillColor = self.fillColor

        j = 0
        for i in xrange(len(ops)):
            op = ops[i]
            pt = pts[j]

            if op == moveTo:
                path = Path()
                path.strokeWidth = self.strokeWidth
                points = []
                path.moveTo(pt[0], pt[1])
                points.append(pt)
            elif op == 1:
                path.lineTo(pt[0], pt[1])
                points.append(pt)
            elif op == 2:
                cpt1, cpt2 = pts[j+1], pts[j+2] # control points
                j = j + 2
                path.curveTo(pt[0], pt[1],
                             cpt1[0], cpt1[1],
                             cpt2[0], cpt2[1])
                points.append(pt)
                lines.append((cpt1, cpt2))
            elif op == 3:
                path.closePath()
                orientation = turn(points)
                if orientation == left:
                    path.strokeColor = strokeColor
                    path.fillColor = strokeColor
                    filledPaths.append(path)
                elif orientation == right:
                    path.strokeColor = fillColor
                    path.fillColor = fillColor
                    emptyPaths.append(path)
                j = j - 1
                circleLists.append(points)
                points = []
                
            j = j + 1

        if points:
            path.closePath()
            orientation = turn(points)
            if orientation == left:
                path.strokeColor = strokeColor
                path.fillColor = strokeColor
                filledPaths.append(path)
            elif orientation == right:
                path.strokeColor = fillColor
                path.fillColor = fillColor
                emptyPaths.append(path)
            circleLists.append(points)

        for p in filledPaths:
            g.add(p)

        for p in emptyPaths:
            g.add(p)

        if self._showPoints:
            for points in circleLists:
                self._addDisks(g, points)


    def _addBorder(self):
        "Make the logo's filled background rectangle."

        g = Group()

        rect = Rect(0, 0, self._width, self._height)
        rect.strokeColor = None
        rect.fillColor = self.fillColor
        g.add(rect)

        return g


    def _addRect(self, group, bounds, rot):
        "Add a rectangle."
        
        x, y, width, height = bounds

        rect = Rect(x, y, width, height)
        rect.strokeWidth = self.strokeWidth
        rect.strokeColor = self.strokeColor
        rect.fillColor = self.strokeColor

        if rot != 0:
            rect.strokeColor = red
            rect.fillColor = red

        g = Group()
        g.add(rect)
        if rot != 0:
            # doesn't work yet!
            cx = x+width/2.0
            cy = y+height/2.0
##            g.shift(-cx, -cy)
##            g.rotate(rot)
##            g.shift(cx, cy)   

        group.add(g)


    def _addDebuggingAids(self):
        "Add red frames and circles for visual debugging purposes."

        m = self.borderWidth
        mm = mmult

        stuff = []
        
        tr = translate(self.x, self.y)
        skx = skewX(self.skewValues[0])
        sky = skewY(self.skewValues[1])
        trans0 = mm(skx, sky)
        x0, y0 = transformPoint(tr, (m, m))
        scaleBack = scaleBackAfterSkew(self.width, self.height, trans0)
        trans1 = mm(tr, scaleBack)
        x1, y1 = transformPoint(trans1, (self.width-m, self.height-m))
        
        f = Group()
        c0 = Circle(x0, y0, 5)
        c1 = Circle(x1, y1, 5)
        c0.fillColor = red
        c1.fillColor = red
        f.add(c0)
        f.add(c1)
        stuff.append(f)

        rect = Rect(self.x, self.y, self.width, self.height)
        rect.strokeColor = red
        rect.fillColor = None
        stuff.append(rect)

        if self.borderWidth:
            m = self.borderWidth
            rect = Rect(self.x+m, self.y+m, self.width-2*m, self.height-2*m)
            rect.strokeColor = red
            rect.fillColor = None
            stuff.append(rect)

        return stuff
    

    def draw(self):
        dict = tree2dict(self._tree)
        groupGraph = dict['PageList'][0]['GraphicsList'][0]['GroupGraphics']

        total = Group() # will contain everything
        g = Group() # will contain glyphs and paper border

        # This is the only hard-coded part paying tribute to
        # the structure of the generated logo file.
        # (Clearly, this can be more generalised, though.)
        for el in groupGraph:
            klass = el['Class']
            bounds = bounds2rect(el['Bounds'])
            if klass == 'Spline':
                ops, pts, bounds = bezierDict2data(el)
                pts = map(lambda p:(p[0],-p[1]), pts)
                dx, dy = bounds[0:2]
                dpts = displacePoints(pts, 0, self._height)
                dpts = displacePoints(dpts, dx, -dy)
                self._addPaths(g, ops, dpts)
            elif klass == 'Group':
                for sel in el['GroupGraphics']:
                    klass1 = sel['Class']
                    if klass1 == 'Rectangle':
                        rbounds, rot = rectDict2data(sel)
                        x, y, width, height = rbounds
                        x = x + bounds[0]
                        y = self._height - y - height
                        rbounds = x, y, width, height
                        self._addRect(g, rbounds, rot)
                    elif klass1 == 'MultiLine':
                        ops, pts, sbounds = bezierDict2data(sel)
                        pts = map(lambda p:(p[0],-p[1]), pts)
                        dx, dy = sbounds[0:2]
                        dx, dy = dx + bounds[0], dy + bounds[1]
                        dpts = displacePoints(pts, 0, self._height)
                        dpts = displacePoints(dpts, dx, -dy)
                        self._addPaths(g, ops, dpts)

        # add background
        m = self.borderWidth
        if self.borderWidth:
            h = Group()
            h.add(self._addBorder())
            h.scale((self.width)/self._width, (self.height)/self._height)
            h.shift(self.x, self.y)
            total.add(h)

        # add real logo
        g.scale((self.width-2*m)/self._width, (self.height-2*m)/self._height)
        apply(g.skew, self.skewValues)

        # rescale logo if needed
        skx = skewX(self.skewValues[0])
        sky = skewY(self.skewValues[1])
        mm = mmult
        sk = mm(skx, sky)
        scaleBack = scaleBackAfterSkew(self.width, self.height, sk)
        g.scale(scaleBack[0], scaleBack[3])
        g.shift(self.x+m, self.y+m)

        total.add(g)

        # add visual debugging aids
        if self._debug:
            for stuff in self._addDebuggingAids():
                total.add(stuff)
            
        return total


def main():
    from reportlab.rl_config import _verbose

    # make first PDF page with reasonable logos
    top = 27.7*cm
    left = 2*cm
    
    l1 = RLVectorLogo()
    l1.x = left
    l1.y = top - 100
    l1.width = 150
    l1.height = 100
    # l1.skewValues = (10, 20)
    # l1.borderWidth = 5   ###

    l2 = RLVectorLogo()
    l2.x = left + 200
    l2.y = top - 100
    l2.width = 150
    l2.height = 100
    l2.strokeColor = ReportLabBlue
    l2.skewValues = (0, 0)

    l3 = RLVectorLogo()
    l3.x = left
    l3.y = top - 100 - 150
    l3.width = 150
    l3.height = 100

    l4 = RLVectorLogo()
    l4.x = left + 200
    l4.y = top - 100 - 150
    l4.width = 150
    l4.height = 100
    l4.strokeColor = ReportLabBlue

    l5 = RLVectorLogo()
    l5.x = left
    l5.y = top - 100 - 2*150
    l5.width = 150
    l5.height = 100
    l5.skewValues = (20, 10)

    l6 = RLVectorLogo()
    l6.x = left + 200
    l6.y = top - 100 - 2*150
    l6.width = 150
    l6.height = 100
    l6.strokeColor = ReportLabBlue
    l6.skewValues = (20, 10)

    l7 = RLVectorLogo()
    l7.x = left
    l7.y = top - 100 - 3*150
    l7.width = 150
    l7.height = 100
    l7.skewValues = (0, 0)
    l7.borderWidth = 5
    l7.strokeColor = white
    l7.fillColor = black

    l8 = RLVectorLogo()
    l8.x = left + 200
    l8.y = top - 100 - 3*150
    l8.width = 150
    l8.height = 100
    l8.skewValues = (0, 0)
    l8.borderWidth = 5
    l8.strokeColor = white
    l8.fillColor = ReportLabBlue

    l9 = RLVectorLogo()
    l9.x = left
    l9.y = top - 100 - 4*150
    l9.width = 150
    l9.height = 100
    l9.borderWidth = 5
    l9.strokeColor = white
    l9.fillColor = black

    l10 = RLVectorLogo()
    l10.x = left + 200
    l10.y = top - 100 - 4*150
    l10.width = 150
    l10.height = 100
    l10.borderWidth = 5
    l10.strokeColor = white
    l10.fillColor = ReportLabBlue

    d = Drawing(21*cm, 29.7*cm)
    for logo in (l1, l2, l3, l4, l5, l6, l7, l8, l9, l10):
        d.add(logo)
    filename = 'rllogos.pdf'
    renderPDF.drawToFile(d, filename, '')
    if _verbose:
        print "saved %s" % filename

    # make second PDF page with less reasonable logos
    L1a = RLVectorLogo()
    L1a.x = left
    L1a.y = top - 100
    L1a.width = 150
    L1a.height = 100
    L1a.strokeColor = black
    L1a.strokeWidth = 12

    L1b = RLVectorLogo()
    L1b.x = left
    L1b.y = top - 100
    L1b.width = 150
    L1b.height = 100
    L1b.strokeColor = ReportLabBlue

    L2a = RLVectorLogo()
    L2a.x = left + 200
    L2a.y = top - 100
    L2a.width = 150
    L2a.height = 100
    L2a.strokeColor = grey

    L2b = RLVectorLogo()
    L2b.x = left + 200 - 3
    L2b.y = top - 100 - 3
    L2b.width = 150
    L2b.height = 100
    L2b.strokeColor = black

    d = Drawing(21*cm, 29.7*cm)
    for logo in (L1a, L1b, L2a, L2b):
        d.add(logo)
    filename = 'rllogos_q.pdf'
    renderPDF.drawToFile(d, filename, '')
    if _verbose:
        print "saved %s" % filename


if __name__ == '__main__':
    main()
