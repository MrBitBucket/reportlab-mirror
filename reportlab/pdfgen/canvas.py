#copyright ReportLab Inc. 2000
#see license.txt for license details
#history http://cvs.sourceforge.net/cgi-bin/cvsweb.cgi/reportlab/pdfgen/canvas.py?cvsroot=reportlab
#$Header: /tmp/reportlab/reportlab/pdfgen/canvas.py,v 1.68 2001/03/15 10:35:00 rgbecker Exp $
__version__=''' $Id: canvas.py,v 1.68 2001/03/15 10:35:00 rgbecker Exp $ '''
__doc__=""" 
The Canvas object is the primary interface for creating PDF files. See
doc/userguide.pdf for copious examples.
"""


import os
import sys
import string
import time
import tempfile
import cStringIO
from types import *
from math import sin, cos, tan, pi, ceil

from reportlab import config
from reportlab.pdfbase import pdfutils
from reportlab.pdfbase import pdfdoc
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfgen  import pdfgeom, pathobject, textobject
from reportlab.lib.colors import Color, CMYKColor, toColor
from reportlab.lib.utils import import_zlib, import_Image
from reportlab.lib.utils import fp_str

zlib = import_zlib()
_SeqTypes=(TupleType,ListType)

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
    """This class is the programmer's interface to the PDF file format.  Methods
    are (or will be) provided here to do just about everything PDF can do.
    
    The underlying model to the canvas concept is that of a graphics state machine
    that at any given point in time has a current font, fill color (for figure
    interiors), stroke color (for figure borders), line width and geometric transform, among
    many other characteristics.
    
    Canvas methods generally either draw something (like canvas.line) using the
    current state of the canvas or change some component of the canvas
    state (like canvas.setFont).  The current state can be saved and restored
    using the saveState/restoreState methods.
    
    Objects are "painted" in the order they are drawn so if, for example
    two rectangles overlap the last draw will appear "on top".  PDF form
    objects (supported here) are used to draw complex drawings only once,
    for possible repeated use.
    
    There are other features of canvas which are not visible when printed,
    such as outlines and bookmarks which are used for navigating a document
    in a viewer.
    
    Here is a very silly example usage which generates a Hello World pdf document.
    
    from reportlab.pdfgen import canvas
    c = canvas.Canvas("hello.pdf")
    from reportlab.lib.units import inch
    # move the origin up and to the left
    c.translate(inch,inch) 
    # define a large font
    c.setFont("Helvetica", 80)
    # choose some colors
    c.setStrokeColorRGB(0.2,0.5,0.3)
    c.setFillColorRGB(1,0,1)
    # draw a rectangle
    c.rect(inch,inch,6*inch,9*inch, fill=1)
    # make text go straight up
    c.rotate(90)
    # change color
    c.setFillColorRGB(0,0,0.77)
    # say hello (note after rotate the y coord needs to be negative!)
    c.drawString(3*inch, -3*inch, "Hello World")
    c.showPage()
    c.save()
    """
    
    def __init__(self,filename,
                 pagesize=(595.27,841.89),
                 bottomup = 1,
                 pageCompression=1,
                 encoding=config.defaultEncoding,
                 verbosity=0):
        """Create a canvas of a given size. etc.
        Most of the attributes are private - we will use set/get methods
        as the preferred interface.  Default page size is A4."""
        self._filename = filename
        self._encodingName = encoding
        self._doc = pdfdoc.PDFDocument(encoding)

        #this only controls whether it prints 'saved ...' - 0 disables
        self._verbosity = verbosity

        
        self._pagesize = pagesize
        #self._currentPageHasImages = 0
        self._pageTransition = None
        self._destinations = {} # dictionary of destinations for cross indexing.

        self.setPageCompression(pageCompression)
        self._pageNumber = 1   # keep a count
        #self3 = []    #where the current page's marking operators accumulate
        # when we create a form we need to save operations not in the form
        self._codeStack = []
        self._restartAccumulators()  # restart all accumulation state (generalized, arw)
        self._annotationCount = 0

        self._outlines = [] # list for a name tree
        
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

        self._addStandardFonts()
        
    def _make_preamble(self):
        if self.bottomup:
            #set initial font
            self._preamble = '1 0 0 1 0 0 cm BT /F9 12 Tf 14.4 TL ET'
        else:
            #switch coordinates, flip text and set font
            self._preamble = '1 0 0 -1 0 %s cm BT /F9 12 Tf 14.4 TL ET' % fp_str(self._pagesize[1])

    def _escape(self, s):
        """PDF escapes are like Python ones, but brackets need slashes before them too.
        Use Python's repr function and chop off the quotes first"""
        s = repr(s)[1:-1]
        s = string.replace(s, '(','\(')
        s = string.replace(s, ')','\)')
        return s

    #info functions - non-standard
    def setAuthor(self, author):
        """identify the author for invisible embedding inside the PDF document.
           the author annotation will appear in the the text of the file but will
           not automatically be seen when the document is viewed."""
        self._doc.setAuthor(author)

    def addOutlineEntry(self, title, key, level=0, closed=None):
        """Adds a new entry to the outline at given level.  If LEVEL not specified,
        entry goes at the top level.  If level specified, it must be
        no more than 1 greater than the outline level in the last call.
        
        The key must be the (unique) name of a bookmark.
        the title is the (non-unique) name to be displayed for the entry.
        
        If closed is set then the entry should show no subsections by default
        when displayed.
        
        Example
           c.addOutlineEntry("first section", "section1")
           c.addOutlineEntry("introduction", "s1s1", 1, closed=1)
           c.addOutlineEntry("body", "s1s2", 1)
           c.addOutlineEntry("detail1", "s1s2s1", 2)
           c.addOutlineEntry("detail2", "s1s2s2", 2)
           c.addOutlineEntry("conclusion", "s1s3", 1)
           c.addOutlineEntry("further reading", "s1s3s1", 2)
           c.addOutlineEntry("second section", "section1")
           c.addOutlineEntry("introduction", "s2s1", 1)
           c.addOutlineEntry("body", "s2s2", 1, closed=1)
           c.addOutlineEntry("detail1", "s2s2s1", 2)
           c.addOutlineEntry("detail2", "s2s2s2", 2)
           c.addOutlineEntry("conclusion", "s2s3", 1)
           c.addOutlineEntry("further reading", "s2s3s1", 2)
           
        generated outline looks like
            - first section
            |- introduction
            |- body
            |  |- detail1
            |  |- detail2
            |- conclusion
            |  |- further reading
            - second section
            |- introduction
            |+ body
            |- conclusion
            |  |- further reading
           
        Note that the second "body" is closed.
        
        Note that you can jump from level 5 to level 3 but not
        from 3 to 5: instead you need to provide all intervening
        levels going down (4 in this case).  Note that titles can
        collide but keys cannot.
        """
        #to be completed
        #self._outlines.append(title)
        self._doc.outline.addOutlineEntry(key, level, title, closed=closed)
        
    def setOutlineNames0(self, *nametree):   # keep this for now (?)
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
        #print nametree
        apply(self._doc.outline.setNames, (self,)+nametree)
        
    def setTitle(self, title):
        """write a title into the PDF file that won't automatically display
           in the document itself."""
        self._doc.setTitle(title)
        
    def setSubject(self, subject):
        """write a subject into the PDF file that won't automatically display
           in the document itself."""
        self._doc.setSubject(subject)
        
    def pageHasData(self):
        "Info function - app can call it after showPage to see if it needs a save"
        return len(self._code) == 0
        
    def showOutline(self):
        """Specify that Acrobat Reader should start with the outline tree visible.
        showFullScreen() and showOutline() conflict; the one called last
        wins."""
        self._doc._catalog.showOutline()
    
    def showFullScreen0(self):
        """Specify that Acrobat Reader should start in full screen mode.
        showFullScreen() and showOutline() conflict; the one called last
        wins."""
        self._doc._catalog.showFullScreen()

    def showPage(self):
        """Close the current page and possibly start on a new page."""
        page = pdfdoc.PDFPage()
        page.pagewidth = self._pagesize[0]
        page.pageheight = self._pagesize[1]
        page.hasImages = self._currentPageHasImages
        page.setPageTransition(self._pageTransition)
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
        
    def bookmarkPage(self, key):
        """bind a bookmark (destination) to the current page"""
        # XXXX there are a lot of other ways a bookmark destination can be bound: should be implemented.
        # XXXX the other ways require tracking of the graphics state....
        dest = self._bookmarkReference(key)
        self._doc.inPage() # try to enable page-only features
        pageref = self._doc.thisPageRef()
        dest.fit()
        dest.setPage(pageref) # formatter won't make a ref to a ref
        return dest
        
    def bookmarkHorizontalAbsolute(self, key, yhorizontal):
        """Bind a bookmark (destination) to the current page at a horizontal position.
           Note that the yhorizontal of the book mark is with respect to the default
           user space (where the origin is at the lower left corner of the page)
           and completely ignores any transform (translation, scale, skew, rotation,
           etcetera) in effect for the current graphics state.  The programmer is
           responsible for making sure the bookmark matches an appropriate item on
           the page."""
        dest = self._bookmarkReference(key)
        self._doc.inPage() # try to enable page-only features
        pageref = self._doc.thisPageRef()
        dest.fith(yhorizontal)
        dest.setPage(pageref)
        return dest
        
    #def _inPage0(self):  disallowed!
    #    """declare a page, enable page features"""
    #    self._doc.inPage()
        
    #def _inForm0(self):
    #    "deprecated in favore of beginForm...endForm"
    #    self._doc.inForm()
            
    def doForm(self, name):
        """use a form XObj in current operation stream.  The form
           should have been defined previously using beginForm ... endForm.
           The form will be drawn within the context of the current graphics
           state."""
        internalname = self._doc.hasForm(name)
        if not internalname:
            raise ValueError, "form is not defined %s" % name
        self._code.append("/%s Do" % internalname)
        self._formsinuse.append(name)
        
    def _restartAccumulators(self):
        if self._codeStack:
            # restore the saved code
            saved = self._codeStack[-1]
            del self._codeStack[-1]
            (self._code, self._formsinuse, self._annotationrefs, self._formData) = saved
        else:
            self._code = []    # ready for more...
            self._currentPageHasImages = 1 # for safety...
            self._formsinuse = []
            self._annotationrefs = []
            self._formData = None

    def _pushAccumulators(self):
        "when you enter a form, save accumulator info not related to the form for page (if any)"
        saved = (self._code, self._formsinuse, self._annotationrefs, self._formData)
        self._codeStack.append(saved)
        self._code = []    # ready for more...
        self._currentPageHasImages = 1 # for safety...
        self._formsinuse = []
        self._annotationrefs = []
        self._formData = None
        
    def beginForm(self, name, lowerx=0, lowery=0, upperx=None, uppery=None):
        """declare the current graphics stream to be a named form.
           A graphics stream can either be a page or a form, not both.
           Some operations (like bookmarking) are permitted for pages
           but not forms.  The form will not automatically be shown in the
           document but must be explicitly referenced using doForm in pages
           that require the form."""
        if self._code:
            # save the code that is not in the formf
            self._pushAccumulators()
            #self._codeStack.append(self._code)
            #self._code = []
        self._formData = (name, lowerx, lowery, upperx, uppery)
        self._doc.inForm()
        #self._inForm0()
        
    def endForm(self):
        """emit the current collection of graphics operations as a Form
           as declared previously in beginForm."""
        (name, lowerx, lowery, upperx, uppery) = self._formData
        #self.makeForm0(name, lowerx, lowery, upperx, uppery)
        # fall through!  makeForm0 disallowed
        #def makeForm0(self, name, lowerx=0, lowery=0, upperx=None, uppery=None):
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
        
    #def forceCodeInsert0(self, code):
    #    """I know a whole lot about PDF and I want to add a bunch of code I know will work..."""
    #    self._code.append(code)
        
    def textAnnotation0(self, contents, Rect=None, addtopage=1, name=None, **kw):
        """Experimental.
        """
        if not Rect:
            (w,h) = self._pagesize# default to whole page (?)
            Rect = (0,0,w,h)
        annotation = apply(pdfdoc.TextAnnotation, (Rect, contents), kw)
        self._addAnnotation(annotation, name, addtopage)
        
    def inkAnnotation0(self, contents, InkList=None, Rect=None, addtopage=1, name=None, **kw):
        "Experimental"
        (w,h) = self._pagesize
        if not Rect:
            Rect = (0,0,w,h)
        if not InkList:
            InkList = ( (100,100,100,h-100,w-100,h-100,w-100,100), )
        annotation = apply(pdfdoc.InkAnnotation, (Rect, contents, InkList), kw)
        self.addAnnotation(annotation, name, addtopage)
    
    def linkAbsolute(self, contents, destinationname, Rect=None, addtopage=1, name=None, **kw):
        """rectangular link annotation positioned wrt the default user space.
           The identified rectangle on the page becomes a "hot link" which
           when clicked will send the viewer to the page and position identified
           by the destination.
           
           Rect identifies (lowerx, lowery, upperx, uppery) for lower left
           and upperright points of the rectangle.  Translations and other transforms
           are IGNORED (the rectangular position is given with respect
           to the default user space.
           destinationname should be the name of a bookmark (which may be defined later
           but must be defined before the document is generated).
           
           You may want to use the keyword argument Border='[0 0 0]' to
           suppress the visible rectangle around the during viewing link."""
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
        "get the page number for the current page being generated."
        return self._pageNumber
        
    def save(self):
        """Saves and close the PDF document in the file.
           If there is current data a ShowPage is executed automatically.
           After this operation the canvas must not be used further."""
        if len(self._code):  
            self.showPage()

        self._doc.SaveToFile(self._filename, self)
        if self._verbosity > 0:
            if type(self._filename)==StringType:
                name = self._filename
            else:
                if hasattr(self._filename,'name'):
                    name = self._filename.name
                else:
                    name = str(filename)
            print 'saved', name

    def setPageSize(self, size):
        """accepts a 2-tuple in points for paper size for this
        and subsequent pages"""
        self._pagesize = size
        self._make_preamble()

    def addLiteral(self, s, escaped=1):
        """introduce the literal text of PDF operations s into the current stream.
           Only use this if you are an expert in the PDF file format."""
        s = str(s) # make sure its a string
        if escaped==0:
            s = self._escape(s) # convert to string for safety
        self._code.append(s)

        ######################################################################
        #
        #      coordinate transformations
        #
        ######################################################################

    def transform(self, a,b,c,d,e,f):
        """adjoin a mathematical transform to the current graphics state matrix.
           Not recommended for beginners."""
        #"""How can Python track this?"""
        #a0,b0,c0,d0,e0,f0 = self._currentMatrix
        #self._currentMatrix = (a0*a+c0*b,    b0*a+d0*b,
        #                       a0*c+c0*d,    b0*c+d0*d,
        #                       a0*e+c0*f+e0, b0*e+d0*f+f0)
        if self._code and self._code[-1][-3:]==' cm':
            L = string.split(self._code[-1])
            a0, b0, c0, d0, e0, f0 = map(float,L[-7:-1])
            s = len(L)>7 and string.join(L)+ ' %s cm' or '%s cm'
            self._code[-1] = s % fp_str(a0*a+c0*b,b0*a+d0*b,a0*c+c0*d,b0*c+d0*d,a0*e+c0*f+e0,b0*e+d0*f+f0)
        else:
            self._code.append('%s cm' % fp_str(a,b,c,d,e,f))

    def translate(self, dx, dy):
        """move the origin from the current (0,0) point to the (dx,dy) point
           (with respect to the current graphics state)."""
        self.transform(1,0,0,1,dx,dy)

    def scale(self, x, y):
        """Scale the horizontal dimension by x and the vertical by y
           (with respect to the current graphics state).
           For example canvas.scale(2.0, 0.5) will make everything short and fat."""
        self.transform(x,0,0,y,0,0)

    def rotate(self, theta):
        """Canvas.rotate(theta)

        Rotate the canvas by the angle theta (in degrees)."""
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
        """Save the current graphics state to be restored later by restoreState.
        
        For example:
            canvas.setFont("Helvetica", 20)
            canvas.saveState()
            ...
            canvas.setFont("Courier", 9)
            ...
            canvas.restoreState()
            # if the save/restore pairs match then font is Helvetica 20 again.
        """
        #"""These need expanding to save/restore Python's state tracking too"""
        self._code.append('q')
        
    def restoreState(self):
        """restore the graphics state to the matching saved state (see saveState)."""
        #"""These need expanding to save/restore Python's state tracking too"""
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
        """draw a line segment from (x1,y1) to (x2,y2) (with color, thickness and
        other attributes determined by the current graphics state)."""     
        self._code.append('n %s m %s l S' % (fp_str(x1, y1), fp_str(x2, y2)))

    def lines(self, linelist):
        """Like line(), permits many lines to be drawn in one call.
           for example for the figure
               |
             -- --
               |
        
             crosshairs = [(20,0,20,10), (20,30,20,40), (0,20,10,20), (30,20,40,20)]
             canvas.lines(crosshairs)
        """
        self._code.append('n')
        for (x1,y1,x2,y2) in linelist:
            self._code.append('%s m %s l' % (fp_str(x1, y1), fp_str(x2, y2)))
        self._code.append('S')

    def grid(self, xlist, ylist):
        """Lays out a grid in current line style.  Supply list of
        x an y positions."""
        assert len(xlist) > 1, "x coordinate list must have 2+ items"
        assert len(ylist) > 1, "y coordinate list must have 2+ items"
        lines = []
        y0, y1 = ylist[0], ylist[-1]
        x0, x1 = xlist[0], xlist[-1]
        for x in xlist:
            lines.append((x,y0,x,y1))
        for y in ylist:
            lines.append((x0,y,x1,y))
        self.lines(lines)

    def bezier(self, x1, y1, x2, y2, x3, y3, x4, y4):
        "Bezier curve with the four given control points"
        self._code.append('n %s m %s c S' %
                          (fp_str(x1, y1), fp_str(x2, y2, x3, y3, x4, y4))
                          )
    def arc(self, x1,y1, x2,y2, startAng=0, extent=90):
        """Draw a partial ellipse inscribed within the rectangle x1,y1,x2,y2,
        starting at startAng degrees and covering extent degrees.   Angles
        start with 0 to the right (+x) and increase counter-clockwise.
        These should have x1<x2 and y1<y2.
        
        Contributed to piddlePDF by Robert Kern, 28/7/99.
        Trimmed down by AR to remove color stuff for pdfgen.canvas and
        revert to positive coordinates.
        
        The algorithm is an elliptical generalization of the formulae in
        Jim Fitzsimmon's TeX tutorial <URL: http://www.tinaja.com/bezarc1.pdf>."""

        pointList = pdfgeom.bezierArc(x1,y1, x2,y2, startAng, extent)
        #move to first point
        self._code.append('n %s m' % fp_str(pointList[0][:2]))
        for curve in pointList:
            self._code.append('%s c' % fp_str(curve[2:]))
        # stroke
        self._code.append('S')

        #--------now the shape drawing methods-----------------------

    def rect(self, x, y, width, height, stroke=1, fill=0):
        "draws a rectangle with lower left corner at (x,y) and width and height as given."
        self._code.append('n %s re ' % fp_str(x, y, width, height)
                          + PATH_OPS[stroke, fill, self._fillMode])        
    
    def ellipse(self, x1, y1, x2, y2, stroke=1, fill=0):
        """Draw an ellipse with foci at (x1,y1) (x2,y2).
        
        Uses bezierArc, which conveniently handles 360 degrees.
        Special thanks to Robert Kern."""
        ### XXXX above documentation is WRONG. Exactly what are (x1,y1), (x2,y2)?
        
        pointList = pdfgeom.bezierArc(x1,y1, x2,y2, 0, 360)
        #move to first point
        self._code.append('n %s m' % fp_str(pointList[0][:2]))
        for curve in pointList:
            self._code.append('%s c' % fp_str(curve[2:]))
        #finish
        self._code.append(PATH_OPS[stroke, fill, self._fillMode])
        
    def wedge(self, x1,y1, x2,y2, startAng, extent, stroke=1, fill=0):
        """Like arc, but connects to the centre of the ellipse.
        Most useful for pie charts and PacMan!"""

        x_cen  = (x1+x2)/2.
        y_cen  = (y1+y2)/2.
        pointList = pdfgeom.bezierArc(x1,y1, x2,y2, startAng, extent)
  
        self._code.append('n %s m' % fp_str(x_cen, y_cen))
        # Move the pen to the center of the rectangle
        self._code.append('%s l' % fp_str(pointList[0][:2]))
        for curve in pointList:
            self._code.append('%s c' % fp_str(curve[2:]))
        # finish the wedge
        self._code.append('%s l ' % fp_str(x_cen, y_cen))
        # final operator
        self._code.append(PATH_OPS[stroke, fill, self._fillMode])

    def circle(self, x_cen, y_cen, r, stroke=1, fill=0):
        """draw a cirle centered at (x_cen,y_cen) with radius r (special case of ellipse)"""

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

        self._code.append('n %s m' % fp_str(x2, y0))
        self._code.append('%s l' % fp_str(x3, y0))  # bottom row
        self._code.append('%s c'
                         % fp_str(x4, y0, x5, y1, x5, y2)) # bottom right

        self._code.append('%s l' % fp_str(x5, y3))  # right edge
        self._code.append('%s c'
                         % fp_str(x5, y4, x4, y5, x3, y5)) # top right
        
        self._code.append('%s l' % fp_str(x2, y5))  # top row
        self._code.append('%s c'
                         % fp_str(x1, y5, x0, y4, x0, y3)) # top left
        
        self._code.append('%s l' % fp_str(x0, y2))  # left edge
        self._code.append('%s c'
                         % fp_str(x0, y1, x1, y0, x2, y0)) # bottom left

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
         """set the fill color useing negative color values
            (cyan, magenta, yellow and darkness value).
         Takes 4 arguments between 0.0 and 1.0"""
         self._fillColorCMYK = (c, m, y, k)
         self._code.append('%s k' % fp_str(c, m, y, k))
         
    def setStrokeColorCMYK(self, c, m, y, k):
         """set the stroke color useing negative color values
            (cyan, magenta, yellow and darkness value).
            Takes 4 arguments between 0.0 and 1.0"""
         self._strokeColorCMYK = (c, m, y, k)
         self._code.append('%s K' % fp_str(c, m, y, k))

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

    def addFont(self, fontObj):
        "add a new font for subsequent use."
        self._doc.addFont(fontObj)
 
    def _addStandardFonts(self):
        """Ensures the standard 14 fonts are available in the system encoding.
        Called by canvas on initialization"""
        pdfmetrics.addStandardFonts()
        for fontName in pdfmetrics.standardFonts:
            self.addFont(pdfmetrics.fontsByName[fontName])

    def listLoadedFonts0(self):
        "Convenience function to list all loaded fonts"
        names = pdfmetrics.widths.keys()
        names.sort()
        return names

    def setFont(self, psfontname, size, leading = None):
        """Sets the font.  If leading not specified, defaults to 1.2 x
        font size. Raises a readable exception if an illegal font
        is supplied.  Font names are case-sensitive! Keeps track
        of font name and size for metrics."""
        self._fontname = psfontname
        self._fontsize = size
        pdffontname = self._doc.getInternalFontName(psfontname)
        if leading is None:
            leading = size * 1.2
        self._leading = leading
        self._code.append('BT %s %s Tf %0.1f TL ET' % (pdffontname, fp_str(size), leading))

    def stringWidth(self, text, fontName, fontSize, encoding=None):
        "gets width of a string in the given font and size"
        if encoding is not None:
            import logger
            logger.warnOnce('encoding argument to Canvas.stringWidth is deprecated and has no effect!')
        #if encoding is None: encoding = self._doc.encoding
        return pdfmetrics.stringWidth(text, fontName, fontSize)
        
    # basic graphics modes

    def setLineWidth(self, width):
        self._lineWidth = width
        self._code.append('%s w' % fp_str(width))

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
        self._code.append('%s M' % fp_str(limit))

    def setDash(self, array=[], phase=0):
        """Two notations.  pass two numbers, or an array and phase"""
        if type(array) == IntType or type(array) == FloatType:
            self._code.append('[%s %s] 0 d' % (array, phase))
        elif type(array) == ListType or type(array) == TupleType:
            assert phase >= 0, "phase is a length in user space"
            textarray = string.join(map(str, array))
            self._code.append('[%s] %s d' % (textarray, phase))
        
    def setFillColorRGB(self, r, g, b):
        """Set the fill color using positive color description
           (Red,Green,Blue).  Takes 3 arguments between 0.0 and 1.0"""
        self._fillColorRGB = (r, g, b)
        self._code.append('%s rg' % fp_str(r,g,b))
        
    def setStrokeColorRGB(self, r, g, b):
        """Set the stroke color using positive color description
           (Red,Green,Blue).  Takes 3 arguments between 0.0 and 1.0"""
        self._strokeColorRGB = (r, g, b)
        self._code.append('%s RG' % fp_str(r,g,b))

    def setFillColor(self, aColor):
        """Takes a color object, allowing colors to be referred to by name"""
        if isinstance(aColor, CMYKColor):
            c,m,y,k = (aColor.cyan, aColor.magenta, aColor.yellow, aColor.black)
            self._fillColorCMYK = (c, m, y, k)
            self._code.append('%s k' % fp_str(c, m, y, k))
        elif isinstance(aColor, Color): 
        #if type(aColor) == ColorType:
            rgb = (aColor.red, aColor.green, aColor.blue)
            self._fillColorRGB = rgb
            self._code.append('%s rg' % fp_str(rgb) )
        elif type(aColor) in _SeqTypes:
            l = len(aColor)
            if l==3:
                self._fillColorRGB = aColor
                self._code.append('%s rg' % fp_str(aColor) )
            elif l==4:
                self.setFillColorCMYK(self, aColor[0], aColor[1], aColor[2], aColor[3])
            else:
                raise 'Unknown color', str(aColor)
        elif type(aColor) is StringType:
            self.setFillColor(toColor(aColor))
        else:
            raise 'Unknown color', str(aColor)

    def setStrokeColor(self, aColor):
        """Takes a color object, allowing colors to be referred to by name"""
        if isinstance(aColor, CMYKColor):
            c,m,y,k = (aColor.cyan, aColor.magenta, aColor.yellow, aColor.black)
            self._strokeColorCMYK = (c, m, y, k)
            self._code.append('%s K' % fp_str(c, m, y, k))
        elif isinstance(aColor, Color): 
        #if type(aColor) == ColorType:
            rgb = (aColor.red, aColor.green, aColor.blue)
            self._strokeColorRGB = rgb
            self._code.append('%s RG' % fp_str(rgb) )
        elif type(aColor) in _SeqTypes:
            l = len(aColor)
            if l==3:
                self._strokeColorRGB = aColor
                self._code.append('%s RG' % fp_str(aColor) )
            elif l==4:
                self.setStrokeColorCMYK(self, aColor[0], aColor[1], aColor[2], aColor[3])
            else:
                raise 'Unknown color', str(aColor)
        elif type(aColor) is StringType:
            self.setFillColor(toColor(aColor))
        else:
            raise 'Unknown color', str(aColor)

    def setFillGray(self, gray):
        """Sets the gray level; 0.0=black, 1.0=white"""
        self._fillColorRGB = (gray, gray, gray)
        self._code.append('%s g' % fp_str(gray))
        
    def setStrokeGray(self, gray):
        """Sets the gray level; 0.0=black, 1.0=white"""
        self._strokeColorRGB = (gray, gray, gray)
        self._code.append('%s G' % fp_str(gray))
        
    # path stuff - the separate path object builds it    

    def beginPath(self):
        """Returns a fresh path object.  Paths are used to draw
        complex figures.  The object returned follows the protocol
        for a pathobject.PDFPathObject instance"""
        return pathobject.PDFPathObject()
    
    def drawPath(self, aPath, stroke=1, fill=0):
        "Draw the path object in the mode indicated"
        gc = aPath.getCode(); pathops = PATH_OPS[stroke, fill, self._fillMode]
        item = "%s %s" % (gc, pathops) # ENSURE STRING CONVERSION
        self._code.append(item)
        #self._code.append(aPath.getCode() + ' ' + PATH_OPS[stroke, fill, self._fillMode])

    def clipPath(self, aPath, stroke=1, fill=0):
        "clip as well as drawing"
        gc = aPath.getCode(); pathops = PATH_OPS[stroke, fill, self._fillMode]
        clip = (self._fillMode == FILL_EVEN_ODD and ' W* ' or ' W ')
        item = "%s%s%s" % (gc, clip, pathops) # ensure string conversion
        self._code.append(item)
        #self._code.append(  aPath.getCode()
        #                   + (self._fillMode == FILL_EVEN_ODD and ' W* ' or ' W ')
        #                   + PATH_OPS[stroke,fill,self._fillMode])

    def beginText(self, x=0, y=0):
        """Returns a fresh text object.  Text objects are used
           to add large amounts of text.  See textobject.PDFTextObject"""
        return textobject.PDFTextObject(self, x, y)

    def drawText(self, aTextObject):
        """Draws a text object"""
        self._code.append(str(aTextObject.getCode()))
        
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
        # new here
        from pdfimages import PDFImage
        img_obj = PDFImage(image, x,y, width, height)
        img_obj.drawInlineImage(self)
        return
        # the rest is historical (to delete)

        if type(image) == StringType:
            if os.path.splitext(image)[1] in ['.jpg', '.JPG', '.jpeg', '.JPEG']:
                #directly process JPEG files
                #open file, needs some error handling!!
                imageFile = open(image, 'rb')
                info = pdfutils.readJPEGInfo(imageFile)
                imgwidth, imgheight = info[0], info[1]
                if info[2] == 1:
                    colorSpace = 'DeviceGray'
                elif info[2] == 3:
                    colorSpace = 'DeviceRGB'
                else: #maybe should generate an error, is this right for CMYK?
                    colorSpace = 'DeviceCMYK'
                imageFile.seek(0) #reset file pointer
                imagedata = []
                #imagedata.append('BI /Width %d /Height /BitsPerComponent 8 /ColorSpace /%s /Filter [/Filter [ /ASCII85Decode /DCTDecode] ID' % (info[0], info[1], colorSpace))
                imagedata.append('BI /W %d /H %d /BPC 8 /CS /%s /F [/A85 /DCT] ID' % (info[0], info[1], colorSpace))
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
                if hasattr(self,'noImageCaching') and self.noImageCaching:
                    imagedata = pdfutils.cacheImageFile(image,returnInMemory=1)
                else:
                    if not pdfutils.cachedImageExists(image):
                        if not zlib:
                            print 'zlib not available'
                            return
                        Image = import_Image()
                        if not Image: return
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
            if not zlib:
                print 'zlib not available'
                return
            myimage = image.convert('RGB')
            imgwidth, imgheight = myimage.size
            imagedata = []

            # this describes what is in the image itself
            # *NB* according to the spec you can only use the short form in inline images
            #imagedata.append('BI /Width %d /Height /BitsPerComponent 8 /ColorSpace /%s /Filter [/Filter [ /ASCII85Decode /FlateDecode] ID' % (imgwidth, imgheight,'RGB'))
            imagedata.append('BI /W %d /H %d /BPC 8 /CS /RGB /F [/A85 /Fl] ID' % (imgwidth, imgheight))

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
        if not self.bottomup: y = y+height
        self._code.append('q %s 0 0 %s cm' % (fp_str(width), fp_str(height, x, y)))

        # self._code.extend(imagedata) if >=python-1.5.2
        for line in imagedata:
            self._code.append(line)

        self._code.append('Q')
        #self._code.append('BT')

    def setPageCompression(self, onoff=1):
        """Possible values 1 or 0 (1 for 'on' is the default).
        If on, the page data will be compressed, leading to much
        smaller files, but takes a little longer to create the files.
        This applies to all subsequent pages, or until setPageCompression()
        is next called."""
        if onoff and not zlib:
            print 'zlib not available'
            return
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
        # This builds a Python dictionary with the right arguments
        # for the Trans dictionary in the PDFPage object,
        # and stores it in the variable _pageTransition.
        # showPage later passes this to the setPageTransition method
        # of the PDFPage object, which turns it to a PDFDictionary.
        self._pageTransition = {}
        if not effectname:
            return
            
        #first check each optional argument has an allowed value
        if direction in [0,90,180,270]:
            direction_arg = ('Di', '/%d' % direction)
        else:
            raise 'PDFError', ' directions allowed are 0,90,180,270'
        
        if dimension in ['H', 'V']:
            dimension_arg = ('Dm', '/' + dimension)
        else:
            raise'PDFError','dimension values allowed are H and V'
        
        if motion in ['I','O']:
            motion_arg = ('M', '/' + motion)
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
        
        # now build the dictionary
        transDict = {}
        transDict['Type'] = '/Trans'
        transDict['D'] = '/%d' % duration
        transDict['S'] = '/' + effectname
        for (key, value) in args:
            transDict[key] = value
        self._pageTransition = transDict


if __name__ == '__main__':
    print 'For test scripts, look in reportlab/test'
