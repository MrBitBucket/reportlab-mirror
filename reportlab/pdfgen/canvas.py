###############################################################################
#
#	ReportLab Public License Version 1.0
#
#   Except for the change of names the spirit and intention of this
#   license is the same as that of Python
#
#	(C) Copyright ReportLab Inc. 1998-2000.
#
#
# All Rights Reserved
#
# Permission to use, copy, modify, and distribute this software and its
# documentation for any purpose and without fee is hereby granted, provided
# that the above copyright notice appear in all copies and that both that
# copyright notice and this permission notice appear in supporting
# documentation, and that the name of ReportLab not be used
# in advertising or publicity pertaining to distribution of the software
# without specific, written prior permission. 
# 
#
# Disclaimer
#
# ReportLab Inc. DISCLAIMS ALL WARRANTIES WITH REGARD TO THIS
# SOFTWARE, INCLUDING ALL IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS,
# IN NO EVENT SHALL ReportLab BE LIABLE FOR ANY SPECIAL, INDIRECT
# OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES WHATSOEVER RESULTING FROM LOSS
# OF USE, DATA OR PROFITS, WHETHER IN AN ACTION OF CONTRACT, NEGLIGENCE OR
# OTHER TORTIOUS ACTION, ARISING OUT OF OR IN CONNECTION WITH THE USE OR
# PERFORMANCE OF THIS SOFTWARE. 
#
###############################################################################
#	$Log: canvas.py,v $
#	Revision 1.20  2000/04/03 09:36:15  andy_robinson
#	Using trailing zero convention for new form and link API
#
#	Revision 1.19  2000/04/02 02:53:49  aaron_watters
#	added support for outline trees
#	
#	Revision 1.18  2000/03/26 20:45:01  aaron_watters
#	added beginForm..endForm and fixed some naming convention issues.
#	
#	Revision 1.17  2000/03/24 21:02:21  aaron_watters
#	added support for destinations, forms, linkages
#	
#	Revision 1.15  2000/03/10 21:46:04  andy_robinson
#	fixed typo in setDash
#	
#	Revision 1.14  2000/03/08 13:40:03  andy_robinson
#	Canvas has two methods setFillColor(aColor) and setStrokeColor(aColor)
#	which accepts color objects directly.
#	
#	Revision 1.13  2000/03/06 20:06:36  rgbecker
#	Typo self._currentPageHasImages = 1
#	
#	Revision 1.12  2000/03/02 12:58:58  rgbecker
#	Remove over officious import checks Imag/zlib
#	
#	Revision 1.11  2000/03/02 10:28:54  rgbecker
#	[].extend illegal in 1.5.1
#	
#	Revision 1.10  2000/02/24 17:28:13  andy_robinson
#	Added methods setFillGray(g), setStrokeGray(g) where 0 <= g <= 1
#	
#	Revision 1.9  2000/02/24 09:12:55  andy_robinson
#	
#	Removed some constants which are no longer used.
#	
#	Revision 1.8  2000/02/20 14:43:27  rgbecker
#	_currentPageHasImages = 0 in init
#	
#	Revision 1.7  2000/02/20 11:08:56  rgbecker
#	Canvas.setPageSize fix
#	
#	Revision 1.6  2000/02/17 15:26:28  rgbecker
#	Change page compression default
#	
#	Revision 1.5  2000/02/17 02:08:04  rgbecker
#	Docstring & other fixes
#	
#	Revision 1.4  2000/02/16 09:42:50  rgbecker
#	Conversion to reportlab package
#	
#	Revision 1.3  2000/02/15 17:55:59  rgbecker
#	License text fixes
#	
#	Revision 1.2  2000/02/15 15:47:09  rgbecker
#	Added license, __version__ and Logi comment
#	
__version__=''' $Id: canvas.py,v 1.20 2000/04/03 09:36:15 andy_robinson Exp $ '''
__doc__=""" 
PDFgen is a library to generate PDF files containing text and graphics.  It is the 
foundation for a complete reporting solution in Python.  It is also the
foundation for piddlePDF, the PDF back end for PIDDLE.

Documentation is a little slim right now; run then look at testpdfgen.py
to get a clue.

Progress Reports:
8.83, 2000-01-13, gmcm:
    Packagizing:
        renamed from pdfgen.py to canvas.py
        broke out PDFTextObject to textobject.py
        broke out PDFPathObject to pathobject.py
        placed all three in a package directory named pdfgen
0.82, 1999-10-27, AR:
        Fixed some bugs on printing to Postscript.  Added 'Text Object'
        analogous to Path Object to control entry and exit from text mode.
        Much simpler clipping API.  All verified to export Postscript and
        redistill.
        One limitation still - clipping to text paths is fine in Acrobat
        but not in Postscript (any level)
        
0.81,1999-10-13, AR:
        Adding RoundRect; changed all format strings to use %0.2f instead of %s,
        so we don't get exponentials in the output.
0.8,1999-10-07, AR:  all changed!
"""
##  0.81    1999-10-13:
##                
##
##
import os
import sys
import string
import time
import tempfile
import cStringIO
from types import *
from math import sin, cos, tan, pi, ceil

from reportlab.pdfbase import pdfutils
from reportlab.pdfbase import pdfdoc
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfgen  import pdfgeom, pathobject, textobject
from reportlab.lib import colors

# Robert Kern
# Constants for closing paths.
# May be useful if one changes 'arc' and 'rect' to take a
# default argument that tells how to close the path.
# That way we can draw filled shapes.

FILL_EVEN_ODD = 0
FILL_NON_ZERO = 1
    #this is used by path-closing routines.
    #map stroke, fill, fillmode -> operator
    # fillmode: 1 = non-Zero (obviously), 0 = evenOdd
PATH_OPS = {(0, 0, FILL_EVEN_ODD) : 'n',  #no op
            (0, 0, FILL_NON_ZERO) : 'n',  #no op
            (1, 0, FILL_EVEN_ODD) : 'S',  #stroke only
            (1, 0, FILL_NON_ZERO) : 'S',  #stroke only
            (0, 1, FILL_EVEN_ODD) : 'f*',  #Fill only
            (0, 1, FILL_NON_ZERO) : 'f',  #Fill only
            (1, 1, FILL_EVEN_ODD) : 'B*',  #Stroke and Fill
            (1, 1, FILL_NON_ZERO) : 'B',  #Stroke and Fill
            }

class Canvas:
    """This is a low-level interface to the PDF file format.  The plan is to
    expose the whole pdfgen API through this.  Its drawing functions should have a
    one-to-one correspondence with PDF functionality.  Unlike PIDDLE, it thinks
    in terms of RGB values, Postscript font names, paths, and a 'current graphics
    state'.  Just started development at 5/9/99, not in use yet.

    """
    def __init__(self,filename,pagesize=(595.27,841.89), bottomup = 1, pageCompression=0 ):
        """Most of the attributes are private - we will use set/get methods
        as the preferred interface.  Default page size is A4."""
        self._filename = filename
        self._doc = pdfdoc.PDFDocument()
        self._pagesize = pagesize
        #self._currentPageHasImages = 0
        self._pageTransitionString = ''
        self._destinations = {} # dictionary of destinations for cross indexing.

        self._pageCompression = pageCompression  #off by default - turn on when we're happy!
        self._pageNumber = 1   # keep a count
        #self._code = []    #where the current page's marking operators accumulate
        self._restartAccumulators()  # restart all accumulation state (generalized, arw)
        self._annotationCount = 0
        
        #PostScript has the origin at bottom left. It is easy to achieve a top-
        #down coord system by translating to the top of the page and setting y
        #scale to -1, but then text is inverted.  So self.bottomup is used
        #to also set the text matrix accordingly.  You can now choose your
        #drawing coordinates.
        self.bottomup = bottomup
        self._make_preamble()

        #initial graphics state
        self._x = 0
        self._y = 0
        self._fontname = 'Times-Roman'
        self._fontsize = 12
        self._textMode = 0  #track if between BT/ET
        self._leading = 14.4
        self._currentMatrix = (1., 0., 0., 1., 0., 0.)
        self._fillMode = 0   #even-odd
        
        #text state        
        self._charSpace = 0
        self._wordSpace = 0
        self._horizScale = 100
        self._textRenderMode = 0
        self._rise = 0
        self._textLineMatrix = (1., 0., 0., 1., 0., 0.)
        self._textMatrix = (1., 0., 0., 1., 0., 0.)

        # line drawing        
        self._lineCap = 0
        self._lineJoin = 0
        self._lineDash = None  #not done
        self._lineWidth = 0
        self._mitreLimit = 0

        self._fillColorRGB = (0,0,0)
        self._strokeColorRGB = (0,0,0)

    def _make_preamble(self):
        if self.bottomup:
            #set initial font
            #self._preamble = 'BT /F9 12 Tf 14.4 TL ET'
            self._preamble = '1 0 0 1 0 0 cm BT /F9 12 Tf 14.4 TL ET'
        else:
            #switch coordinates, flip text and set font
            #self._preamble = '1 0 0 -1 0 %0.2f cm BT /F9 12 Tf 14.4 TL ET' % self._pagesize[1]
            self._preamble = '1 0 0 -1 0 %0.2f cm BT /F9 12 Tf 14.4 TL ET' % self._pagesize[1]

    def _escape(self, s):
        """PDF escapes are like Python ones, but brackets need slashes before them too.
        Use Python's repr function and chop off the quotes first"""
        s = repr(s)[1:-1]
        s = string.replace(s, '(','\(')
        s = string.replace(s, ')','\)')
        return s

    #info functions - non-standard
    def setAuthor(self, author):
        self._doc.setAuthor(author)
        
    def setOutlineNames0(self, *nametree):
        """nametree should can be a recursive tree like so
           c.setOutlineNames(
             "chapter1dest",
             ("chapter2dest",
              ["chapter2section1dest",
               "chapter2section2dest",
               "chapter2conclusiondest"]
             ), # end of chapter2 description
             "chapter3dest",
             ("chapter4dest", ["c4s1", "c4s2"])
             )
          each of the string names inside must be bound to a bookmark
          before the document is generated.
        """
        apply(self._doc.outline.setNames, (self,)+nametree)
        
    def setTitle(self, title):
        self._doc.setTitle(title)
        
    def setSubject(self, subject):
        self._doc.setSubject(subject)
        
    def pageHasData(self):
        "Info function - app can call it after showPage to see if it needs a save"
        return len(self._code) == 0
        
    def showOutline0(self):
        "Specify that Acrobat Reader should start with the outline tree visible"
        self._doc._catalog.showOutline()
    
    def showPage(self):
        """This is where the fun happens"""
        page = pdfdoc.PDFPage()
        page.pagewidth = self._pagesize[0]
        page.pageheight = self._pagesize[1]
        page.hasImages = self._currentPageHasImages
        page.pageTransitionString = self._pageTransitionString
        page.setCompression(self._pageCompression)
        #print stream
        page.setStream([self._preamble] + self._code)
        self._setXObjects(page)
        self._setAnnotations(page)
        self._doc.addPage(page)
        
        #now get ready for the next one
        self._pageNumber = self._pageNumber + 1
        self._restartAccumulators()
        
    def _setAnnotations(self,page):
        page.Annots = self._annotationrefs
        
    def _setXObjects(self, thing):
        """for pages and forms, define the XObject dictionary for resources, if needed"""
        forms = self._formsinuse
        if forms:
            xobjectsdict = self._doc.xobjDict(forms)
            thing.XObjects = xobjectsdict
        else:
            thing.XObjects = None
            
    def _bookmarkReference(self, name):
        """get a reference to a (possibly undefined, possibly unbound) bookmark"""
        d = self._destinations
        try:
            return d[name]
        except:
            result = d[name] = pdfdoc.Destination(name) # newly defined, unbound
        return result
        
    def bookmarkPage0(self, name):
        """bind a bookmark (destination) to the current page"""
        # XXXX there are a lot of other ways a bookmark destination can be bound: should be implemented.
        # XXXX the other ways require tracking of the graphics state....
        dest = self._bookmarkReference(name)
        pageref = self._doc.thisPageRef()
        dest.fit()
        dest.setPageRef(pageref)
        return dest
        
    def bookmarkHorizontalAbsolute0(self, name, yhorizontal):
        """bind a bookmark (destination to the current page at a horizontal position"""
        dest = self._bookmarkReference(name)
        pageref = self._doc.thisPageRef()
        dest.fith(yhorizontal)
        dest.setPageRef(pageref)
        return dest
        
    def _inPage0(self):
        """declare a page, enable page features"""
        self._doc.inPage()
        
    def _inForm0(self):
        "deprecated in favore of beginForm...endForm"
        self._doc.inForm()
            
    def doForm0(self, name):
        """use a form XObj in current operation stream"""
        internalname = self._doc.hasForm(name)
        if not internalname:
            raise ValueError, "form is not defined %s" % name
        self._code.append("/%s Do" % internalname)
        self._formsinuse.append(name)
        
    def _restartAccumulators(self):
        self._code = []    # ready for more...
        self._currentPageHasImages = 1 # for safety...
        self._formsinuse = []
        self._annotationrefs = []
        self._formData = None
        
    def beginForm0(self, name, lowerx=0, lowery=0, upperx=None, uppery=None):
        "declare the current graphics stream to be a form"
        self._formData = (name, lowerx, lowery, upperx, uppery)
        self._inForm0()
        
    def endForm0(self):
        (name, lowerx, lowery, upperx, uppery) = self._formData
        self.makeForm0(name, lowerx, lowery, upperx, uppery)
        
    def makeForm0(self, name, lowerx=0, lowery=0, upperx=None, uppery=None):
        """Like showpage, but make a form using accumulated operations instead"""
        # deprecated in favor or beginForm(...)... endForm()
        (w,h) = self._pagesize
        if upperx is None: upperx=w
        if uppery is None: uppery=h
        form = pdfdoc.PDFFormXObject(lowerx=lowerx, lowery=lowery, upperx=upperx, uppery=uppery)
        form.compression = self._pageCompression
        form.setStreamList([self._preamble] + self._code) # ??? minus preamble (seems to be needed!)
        self._setXObjects(form)
        self._setAnnotations(form)
        self._doc.addForm(name, form)
        self._restartAccumulators()
        
    def textAnnotation0(self, contents, Rect=None, addtopage=1, name=None, **kw):
        if not Rect:
            (w,h) = self._pagesize# default to whole page (?)
            Rect = (0,0,w,h)
        annotation = apply(pdfdoc.TextAnnotation, (Rect, contents), kw)
        self._addAnnotation(annotation, name, addtopage)
        
    def inkAnnotation0(self, contents, InkList=None, Rect=None, addtopage=1, name=None, **kw):
        "not working?"
        (w,h) = self._pagesize
        if not Rect:
            Rect = (0,0,w,h)
        if not InkList:
            InkList = ( (100,100,100,h-100,w-100,h-100,w-100,100), )
        annotation = apply(pdfdoc.InkAnnotation, (Rect, contents, InkList), kw)
        self.addAnnotation(annotation, name, addtopage)
    
    def linkAbsolute0(self, contents, destinationname, Rect=None, addtopage=1, name=None, **kw):
        """link annotation positioned wrt the default user space"""
        destination = self._bookmarkReference(destinationname) # permitted to be undefined... must bind later...
        (w,h) = self._pagesize
        if not Rect:
            Rect = (0,0,w,h)
        kw["Rect"] = Rect
        kw["Contents"] = contents
        kw["Destination"] = destination
        annotation = apply(pdfdoc.LinkAnnotation, (), kw)
        self._addAnnotation(annotation, name, addtopage)
    
    def _addAnnotation(self, annotation, name=None, addtopage=1):
        count = self._annotationCount = self._annotationCount+1
        if not name: name="NUMBER"+repr(count)
        self._doc.addAnnotation(name, annotation)
        if addtopage:
            self._annotatePage(name)
            
    def _annotatePage(self, name):
        ref = self._doc.refAnnotation(name)
        self._annotationrefs.append(ref)

    def getPageNumber(self):
        return self._pageNumber
        
    def save(self):
        """Saves the file.  If holding data, do
        a showPage() to save them having to."""
        if len(self._code):  
            self.showPage()
        self._doc.SaveToFile(self._filename)
        print 'saved', self._filename

    def setPageSize(self, size):
        """accepts a 2-tuple in points for paper size for this
        and subsequent pages"""
        self._pagesize = size
        self._make_preamble()

    def addLiteral(self, s, escaped=1):
        if escaped==0:
            s = self._escape(s)
        self._code.append(s)


        ######################################################################
        #
        #      coordinate transformations
        #
        ######################################################################


    def transform(self, a,b,c,d,e,f):
        """How can Python track this?"""
        a0,b0,c0,d0,e0,f0 = self._currentMatrix
        self._currentMatrix = (a0*a+c0*b,    b0*a+d0*b,
                               a0*c+c0*d,    b0*c+d0*d,
                               a0*e+c0*f+e0, b0*e+d0*f+f0)
        self._code.append('%0.2f %0.2f %0.2f %0.2f %0.2f %0.2f cm' % (a,b,c,d,e,f))

    def translate(self, dx, dy):
        self.transform(1,0,0,1,dx,dy)

    def scale(self, x, y):
        self.transform(x,0,0,y,0,0)

    def rotate(self, theta):
        """Canvas.rotate(theta)

        theta is in degrees."""
        c = cos(theta * pi / 180)
        s = sin(theta * pi / 180)
        self.transform(c, s, -s, c, 0, 0)

    def skew(self, alpha, beta):
        tanAlpha = tan(alpha * pi / 180)
        tanBeta  = tan(beta  * pi / 180)
        self.transform(1, tanAlpha, tanBeta, 1, 0, 0)

        ######################################################################
        #
        #      graphics state management
        #
        ######################################################################



    def saveState(self):
        """These need expanding to save/restore Python's state tracking too"""
        self._code.append('q')
        
    def restoreState(self):
        """These need expanding to save/restore Python's state tracking too"""
        self._code.append('Q')

        ###############################################################
        #
        #   Drawing methods.  These draw things directly without
        #   fiddling around with Path objects.  We can add any geometry
        #   methods we wish as long as their meaning is precise and
        #   they are of general use.
        #
        #   In general there are two patterns.  Closed shapes
        #   have the pattern shape(self, args, stroke=1, fill=0);
        #   by default they draw an outline only. Line segments come
        #   in three flavours: line, bezier, arc (which is a segment
        #   of an elliptical arc, approximated by up to four bezier
        #   curves, one for each quadrant.
        #
        #   In the case of lines, we provide a 'plural' to unroll
        #   the inner loop; it is useful for drawing big grids
        ################################################################


        #--------first the line drawing methods-----------------------
    def line(self, x1,y1, x2,y2):
        "As it says"       
        self._code.append('n %0.2f %0.2f m %0.2f %0.2f l S' % (x1, y1, x2, y2))

    def lines(self, linelist):
        """As line(), but slightly more efficient for lots of them -
        one stroke operation and one less function call"""
        self._code.append('n')
        for (x1,y1,x2,y2) in linelist:
            self._code.append('%0.2f %0.2f m %0.2f %0.2f l' % (x1, y1, x2, y2))
        self._code.append('S')

    def grid(self, xlist, ylist):
        """Lays out a grid in current line style.  Suuply list of
        x an y positions."""
        assert len(xlist) > 1, "x coordinate list must have 2+ items"
        assert len(ylist) > 1, "y coordinate list must have 2+ items"
        lines = []
        y0, y1 = ylist[0], ylist[-1]
        x0, x1 = xlist[0], xlist[-1]
        for x in xlist:
            lines.append(x,y0,x,y1)
        for y in ylist:
            lines.append(x0,y,x1,y)
        self.lines(lines)

    def bezier(self, x1, y1, x2, y2, x3, y3, x4, y4):
        "Bezier curve with the four given control points"
        self._code.append('n %0.2f %0.2f m %0.2f %0.2f %0.2f %0.2f %0.2f %0.2f c S' %
                          (x1, y1, x2, y2, x3, y3, x4, y4)
                          )
    def arc(self, x1,y1, x2,y2, startAng=0, extent=90):
        """Contributed to piddlePDF by Robert Kern, 28/7/99.
        Trimmed down by AR to remove color stuff for pdfgen.canvas and
        revert to positive coordinates.
        
        Draw a partial ellipse inscribed within the rectangle x1,y1,x2,y2,
        starting at startAng degrees and covering extent degrees.   Angles
        start with 0 to the right (+x) and increase counter-clockwise.
        These should have x1<x2 and y1<y2.

        The algorithm is an elliptical generalization of the formulae in
        Jim Fitzsimmon's TeX tutorial <URL: http://www.tinaja.com/bezarc1.pdf>."""

        pointList = pdfgeom.bezierArc(x1,y1, x2,y2, startAng, extent)
        #move to first point
        self._code.append('n %0.2f %0.2f m' % pointList[0][:2])
        for curve in pointList:
            self._code.append('%0.2f %0.2f %0.2f %0.2f %0.2f %0.2f c' % curve[2:])
        # stroke
        self._code.append('S')

        #--------now the shape drawing methods-----------------------
    def rect(self, x, y, width, height, stroke=1, fill=0):
        "draws a rectangle"
        self._code.append('n %0.2f %0.2f %0.2f %0.2f re ' % (x, y, width, height)
                          + PATH_OPS[stroke, fill, self._fillMode])
        
    
    def ellipse(self, x1, y1, x2, y2, stroke=1, fill=0):
        """Uses bezierArc, which conveniently handles 360 degrees -
        nice touch Robert"""
        pointList = pdfgeom.bezierArc(x1,y1, x2,y2, 0, 360)
        #move to first point
        self._code.append('n %0.2f %0.2f m' % pointList[0][:2])
        for curve in pointList:
            self._code.append('%0.2f %0.2f %0.2f %0.2f %0.2f %0.2f c' % curve[2:])
        #finish
        self._code.append(PATH_OPS[stroke, fill, self._fillMode])

        
    def wedge(self, x1,y1, x2,y2, startAng, extent, stroke=1, fill=0):
        """Like arc, but connects to the centre of the ellipse.
        Most useful for pie charts and PacMan!"""

        x_cen  = (x1+x2)/2.
        y_cen  = (y1+y2)/2.
        pointList = pdfgeom.bezierArc(x1,y1, x2,y2, startAng, extent)
  
        self._code.append('n %0.2f %0.2f m' % (x_cen, y_cen))
        # Move the pen to the center of the rectangle
        self._code.append('%0.2f %0.2f l' % pointList[0][:2])
        for curve in pointList:
            self._code.append('%0.2f %0.2f %0.2f %0.2f %0.2f %0.2f c' % curve[2:])
        # finish the wedge
        self._code.append('%0.2f %0.2f l ' % (x_cen, y_cen))
        # final operator
        self._code.append(PATH_OPS[stroke, fill, self._fillMode])

    def circle(self, x_cen, y_cen, r, stroke=1, fill=0):
        """special case of ellipse"""

        x1 = x_cen - r
        x2 = x_cen + r
        y1 = y_cen - r
        y2 = y_cen + r
        self.ellipse(x1, y1, x2, y2, stroke, fill)

    def roundRect(self, x, y, width, height, radius, stroke=1, fill=0):
        """Draws a rectangle with rounded corners.  The corners are
        approximately quadrants of a circle, with the given radius."""
        #use a precomputed set of factors for the bezier approximation
        #to a circle. There are six relevant points on the x axis and y axis.
        #sketch them and it should all make sense!
        t = 0.4472 * radius
        
        x0 = x
        x1 = x0 + t
        x2 = x0 + radius
        x3 = x0 + width - radius
        x4 = x0 + width - t
        x5 = x0 + width

        y0 = y
        y1 = y0 + t
        y2 = y0 + radius
        y3 = y0 + height - radius
        y4 = y0 + height - t
        y5 = y0 + height

        self._code.append('n %0.2f %0.2f m' % (x2, y0))
        self._code.append('%0.2f %0.2f l' % (x3, y0))  # bottom row
        self._code.append('%0.2f %0.2f %0.2f %0.2f %0.2f %0.2f c'
                         % (x4, y0, x5, y1, x5, y2)) # bottom right

        self._code.append('%0.2f %0.2f l' % (x5, y3))  # right edge
        self._code.append('%0.2f %0.2f %0.2f %0.2f %0.2f %0.2f c'
                         % (x5, y4, x4, y5, x3, y5)) # top right
        
        self._code.append('%0.2f %0.2f l' % (x2, y5))  # top row
        self._code.append('%0.2f %0.2f %0.2f %0.2f %0.2f %0.2f c'
                         % (x1, y5, x0, y4, x0, y3)) # top left
        
        self._code.append('%0.2f %0.2f l' % (x0, y2))  # left edge
        self._code.append('%0.2f %0.2f %0.2f %0.2f %0.2f %0.2f c'
                         % (x0, y1, x1, y0, x2, y0)) # bottom left

        self._code.append('h')  #close off, although it should be where it started anyway
        
    
        self._code.append(PATH_OPS[stroke, fill, self._fillMode])
        ##################################################
        #
        #  Text methods
        #
        # As with graphics, a separate object ensures that
        # everything is bracketed between  text operators.
        # The methods below are a high-level convenience.
        # use PDFTextObject for multi-line text.
        ##################################################

 
    def setFillColorCMYK(self, c, m, y, k):
         """Takes 4 arguments between 0.0 and 1.0"""
         self._fillColorCMYK = (c, m, y, k)
         self._code.append('%0.2f %0.2f %0.2f %0.2f k' % (c, m, y, k))
         
    def setStrokeColorCMYK(self, c, m, y, k):
         """Takes 4 arguments between 0.0 and 1.0"""
         self._strokeColorCMYK = (c, m, y, k)
         self._code.append('%0.2f %0.2f %0.2f %0.2f K' % (c, m, y, k))

    def drawString(self, x, y, text):
        """Draws a string in the current text styles."""
        #we could inline this for speed if needed
        t = self.beginText(x, y)
        t.textLine(text)
        self.drawText(t)

    def drawRightString(self, x, y, text):
        """Draws a string right-aligned with the y coordinate"""
        width = self.stringWidth(text, self._fontname, self._fontsize)
        t = self.beginText(x - width, y)
        t.textLine(text)
        self.drawText(t)

    def drawCentredString(self, x, y, text):
        """Draws a string right-aligned with the y coordinate.  I
        am British so the spelling is correct, OK?"""
        width = self.stringWidth(text, self._fontname, self._fontsize)
        t = self.beginText(x - 0.5*width, y)
        t.textLine(text)
        self.drawText(t)
  
    def getAvailableFonts(self):
        """Returns the list of PostScript font names available.
        Standard set now, but may grow in future with font embedding."""
        fontnames = self._doc.getAvailableFonts()
        fontnames.sort()
        return fontnames

    def setFont(self, psfontname, size, leading = None):
        """Sets the font.  If leading not specified, defaults to 1.2 x
        font size. Raises a readable exception if an illegal font
        is supplied.  Font names are case-sensitive! Keeps track
        of font anme and size for metrics."""
        self._fontname = psfontname
        self._fontsize = size
        pdffontname = self._doc.getInternalFontName(psfontname)
        if leading is None:
            leading = size * 1.2
        self._leading = leading
        self._code.append('BT %s %0.1f Tf %0.1f TL ET' % (pdffontname, size, leading))

    def stringWidth(self, text, fontname, fontsize):
        "gets width of a string in the given font and size"
        return pdfmetrics.stringwidth(text, fontname) * 0.001 * fontsize
        
    # basic graphics modes
    def setLineWidth(self, width):
        self._lineWidth = width
        self._code.append('%0.2f w' % width)

    def setLineCap(self, mode):
        """0=butt,1=round,2=square"""
        assert mode in (0,1,2), "Line caps allowed: 0=butt,1=round,2=square"
        self._lineCap = mode
        self._code.append('%d J' % mode)
        
    def setLineJoin(self, mode):
        """0=mitre, 1=round, 2=bevel"""
        assert mode in (0,1,2), "Line Joins allowed: 0=mitre, 1=round, 2=bevel"
        self._lineJoin = mode
        self._code.append('%d j' % mode)
        
    def setMiterLimit(self, limit):
        self._miterLimit = limit
        self._code.append('%0.2f M' % limit)

    def setDash(self, array=[], phase=0):
        """Two notations.  pass two numbers, or an array and phase"""
        if type(array) == IntType or type(array) == FloatType:
            self._code.append('[%s %s] 0 d' % (array, phase))
        elif type(array) == ListType or type(array) == TupleType:
            assert phase <= len(array), "setDash phase must be l.t.e. length of array"
            textarray = string.join(map(str, array))
            self._code.append('[%s] %s d' % (textarray, phase))
        
    def setFillColorRGB(self, r, g, b):
        """Takes 3 arguments between 0.0 and 1.0"""
        self._fillColorRGB = (r, g, b)
        self._code.append('%0.2f %0.2f %0.2f rg' % (r,g,b))
        
    def setStrokeColorRGB(self, r, g, b):
        """Takes 3 arguments between 0.0 and 1.0"""
        self._strokeColorRGB = (r, g, b)
        self._code.append('%0.2f %0.2f %0.2f RG' % (r,g,b))

    def setFillColor(self, aColor):
        """Takes a color object, allowing colors to be referred to by name"""
        r, g, b = aColor.red, aColor.green, aColor.blue
        self._strokeColorRGB = (r, g, b)
        self._code.append('%0.2f %0.2f %0.2f rg' % (r,g,b))
        
    def setStrokeColor(self, aColor):
        """Takes a color object, allowing colors to be referred to by name"""
        r, g, b = aColor.red, aColor.green, aColor.blue
        self._strokeColorRGB = (r, g, b)
        self._code.append('%0.2f %0.2f %0.2f RG' % (r,g,b))

    def setFillGray(self, gray):
        """Sets the gray level; 0.0=black, 1.0=white"""
        self._fillColorRGB = (gray, gray, gray)
        self._code.append('%0.2f g' % gray)
        
    def setStrokeGray(self, gray):
        """Sets the gray level; 0.0=black, 1.0=white"""
        self._strokeColorRGB = (gray, gray, gray)
        self._code.append('%0.2f G' % gray)

        
    # path stuff - the separate path object builds it    
    def beginPath(self):
        """Returns a fresh path object"""
        return pathobject.PDFPathObject()
    
    def drawPath(self, aPath, stroke=1, fill=0):
        "Draw in the mode indicated"
        op = PATH_OPS[stroke, fill, self._fillMode]
        self._code.append(aPath.getCode() + ' ' + op)

    def clipPath(self, aPath, stroke=1, fill=0):
        "clip as well as drawing"
        op = PATH_OPS[stroke, fill, self._fillMode]
        self._code.append(aPath.getCode() + ' W ' + op)

    def beginText(self, x=0, y=0):
        """Returns a fresh text object"""
        return textobject.PDFTextObject(self, x, y)

    def drawText(self, aTextObject):
        """Draws a text object"""
        self._code.append(aTextObject.getCode())
        
        ######################################################
        #
        #   Image routines
        #
        ######################################################
    def drawInlineImage(self, image, x,y, width=None,height=None):
        """Draw an Image into the specified rectangle.  If width and
        height are omitted, they are calculated from the image size.
        Also allow file names as well as images.  This allows a
        caching mechanism"""
            
        self._currentPageHasImages = 1

        if type(image) == StringType:
            if os.path.splitext(image)[1] in ['.jpg', '.JPG']:
                #directly process JPEG files
                #open file, needs some error handling!!
                imageFile = open(image, 'rb')
                info = self.readJPEGInfo(imageFile)
                imgwidth, imgheight = info[0], info[1]
                if info[2] == 1:
                    colorSpace = 'DeviceGray'
                elif info[2] == 3:
                    colorSpace = 'DeviceRGB'
                else: #maybe should generate an error, is this right for CMYK?
                    colorSpace = 'DeviceCMYK'
                imageFile.seek(0)		#reset file pointer
                imagedata = []
                imagedata.append('BI')   # begin image
                # this describes what is in the image itself
                imagedata.append('/Width %0.2f /Height %0.2f' %(info[0], info[1]))
                imagedata.append('/BitsPerComponent 8')
                imagedata.append('/ColorSpace /%s' % colorSpace)
                imagedata.append('/Filter [ /ASCII85Decode /DCTDecode]')
                imagedata.append('ID')   
                #write in blocks of (??) 60 characters per line to a list
                compressed = imageFile.read()
                encoded = pdfutils._AsciiBase85Encode(compressed)
                outstream = cStringIO.StringIO(encoded)
                dataline = outstream.read(60)
                while dataline <> "":
                    imagedata.append(dataline)
                    dataline = outstream.read(60)
                imagedata.append('EI')
            else:
                if not pdfutils.cachedImageExists(image):
                    try:
                        import Image
                    except ImportError:
                        print 'Python Imaging Library not available'
                        return
                    try:
                        import zlib
                    except ImportError:
                        print 'zlib not available'
                        return
                    pdfutils.cacheImageFile(image)

                #now we have one cached, slurp it in
                cachedname = os.path.splitext(image)[0] + '.a85'
                imagedata = open(cachedname,'rb').readlines()
                #trim off newlines...
                imagedata = map(string.strip, imagedata)
                
                #parse line two for width, height
                words = string.split(imagedata[1])
                imgwidth = string.atoi(words[1])
                imgheight = string.atoi(words[3])
        else:
            #PIL Image
            #work out all dimensions
            try:
                import zlib
            except ImportError:
                print 'zlib not available'
                return
            myimage = image.convert('RGB')
            imgwidth, imgheight = myimage.size
            imagedata = []
            imagedata.append('BI')   # begin image

            # this describes what is in the image itself
            imagedata.append('/W %0.2f /H %0.2f /BPC 8 /CS /RGB /F [/A85 /Fl]' % (imgwidth, imgheight))
            imagedata.append('ID')   

            #use a flate filter and Ascii Base 85 to compress
            raw = myimage.tostring()
            assert(len(raw) == imgwidth * imgheight, "Wrong amount of data for image")
            compressed = zlib.compress(raw)   #this bit is very fast...
            encoded = pdfutils._AsciiBase85Encode(compressed) #...sadly this isn't

            #write in blocks of (??) 60 characters per line to a list
            outstream = cStringIO.StringIO(encoded)
            dataline = outstream.read(60)
            while dataline <> "":
                imagedata.append(dataline)
                dataline = outstream.read(60)
            imagedata.append('EI')

        #now build the PDF for the image.
        if not width:
            width = imgwidth
        if not height:
            height = imgheight
        
        # this says where and how big to draw it
        #self._code.append('ET')
        #self._code.append('q %0.2f 0 0 %0.2f %0.2f %0.2f cm' % (width, height, x, y+height))
        if self.bottomup:
            self._code.append('q %0.2f 0 0 %0.2f %0.2f %0.2f cm' % (width, height, x, y))
        else:
            self._code.append('q %0.2f 0 0 %0.2f %0.2f %0.2f cm' % (width, height, x, y+height))

		# self._code.extend(imagedata) if >=python-1.5.2
        for line in imagedata:
       	    self._code.append(line)
			
        self._code.append('Q')
        #self._code.append('BT')

#########################################################################
#
#  JPEG processing code - contributed by Eric Johnson
#
#########################################################################

    # Read data from the JPEG file. We should probably be using PIL to
    # get this information for us -- but this way is more fun!
    # Returns (width, height, color components) as a triple
    # This is based on Thomas Merz's code from GhostScript (viewjpeg.ps)
    def readJPEGInfo(self, image):
        "Read width, height and number of components from JPEG file"
    	import struct

	#Acceptable JPEG Markers:
	#  SROF0=baseline, SOF1=extended sequential or SOF2=progressive
	validMarkers = [0xC0, 0xC1, 0xC2]

	#JPEG markers without additional parameters
	noParamMarkers = \
	    [ 0xD0, 0xD1, 0xD2, 0xD3, 0xD4, 0xD5, 0xD6, 0xD7, 0xD8, 0x01 ]

	#Unsupported JPEG Markers
	unsupportedMarkers = \
	    [ 0xC3, 0xC5, 0xC6, 0xC7, 0xC8, 0xC9, 0xCA, 0xCB, 0xCD, 0xCE, 0xCF ]

	#read JPEG marker segments until we find SOFn marker or EOF
	done = 0
	while not done:
	    x = struct.unpack('B', image.read(1))
	    if x[0] == 0xFF:			#found marker
	    	x = struct.unpack('B', image.read(1))
		#print "Marker: ", '%0.2x' % x[0]
		#check marker type is acceptable and process it
		if x[0] in validMarkers:
		    image.seek(2, 1)		#skip segment length
		    x = struct.unpack('B', image.read(1)) #data precision
		    if x[0] != 8:
			raise 'PDFError', ' JPEG must have 8 bits per component'
		    y = struct.unpack('BB', image.read(2))
		    height = (y[0] << 8) + y[1] 
		    y = struct.unpack('BB', image.read(2))
		    width =  (y[0] << 8) + y[1]
		    y = struct.unpack('B', image.read(1))
		    color =  y[0]
		    return width, height, color
		    done = 1
		elif x[0] in unsupportedMarkers:
		    raise 'PDFError', ' Unsupported JPEG marker: %0.2x' % x[0]
		elif x[0] not in noParamMarkers:
		    #skip segments with parameters
		    #read length and skip the data
		    x = struct.unpack('BB', image.read(2))
		    image.seek( (x[0] << 8) + x[1] - 2, 1)	

    def setPageCompression(self, onoff=1):
        """Possible values 1 or 0 (1 for 'on' is the default).
        If on, the page data will be compressed, leading to much
        smaller files, but takes a little longer to create the files.
        This applies to all subsequent pages, or until setPageCompression()
        is next called."""
        self._pageCompression = onoff
        

    def setPageTransition(self, effectname=None, duration=1, 
                        direction=0,dimension='H',motion='I'):
        """PDF allows page transition effects for use when giving
        presentations.  There are six possible effects.  You can
        just guive the effect name, or supply more advanced options
        to refine the way it works.  There are three types of extra
        argument permitted, and here are the allowed values:
            direction_arg = [0,90,180,270]
            dimension_arg = ['H', 'V']
            motion_arg = ['I','O'] (start at inside or outside)
            
        This table says which ones take which arguments:

        PageTransitionEffects = {
            'Split': [direction_arg, motion_arg],
            'Blinds': [dimension_arg],
            'Box': [motion_arg],
            'Wipe' : [direction_arg],
            'Dissolve' : [],
            'Glitter':[direction_arg]
            }
        Have fun!
"""
        if not effectname:
            self._pageTransitionString = ''
            return
            
        #first check each optional argument has an allowed value
        if direction in [0,90,180,270]:
            direction_arg = '/Di /%d' % direction
        else:
            raise 'PDFError', ' directions allowed are 0,90,180,270'
        
        if dimension in ['H', 'V']:
            dimension_arg = '/Dm /%s' % dimension
        else:
            raise'PDFError','dimension values allowed are H and V'
        
        if motion in ['I','O']:
            motion_arg = '/M /%s' % motion
        else:
            raise'PDFError','motion values allowed are I and O'


        # this says which effects require which argument types from above
        PageTransitionEffects = {
            'Split': [direction_arg, motion_arg],
            'Blinds': [dimension_arg],
            'Box': [motion_arg],
            'Wipe' : [direction_arg],
            'Dissolve' : [],
            'Glitter':[direction_arg]
            }

        try:
            args = PageTransitionEffects[effectname]
        except KeyError:
            raise 'PDFError', 'Unknown Effect Name "%s"' % effectname
            self._pageTransitionString = ''
            return
        

        self._pageTransitionString = (('/Trans <</D %d /S /%s ' % (duration, effectname)) + 
            string.join(args, ' ') + ' >>')

if __name__ == '__main__':
    print 'For test scripts, run testpdfgen.py'
