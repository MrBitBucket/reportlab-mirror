#copyright ReportLab Inc. 2000
#see license.txt for license details
#history http://cvs.sourceforge.net/cgi-bin/cvsweb.cgi/reportlab/pdfgen/pathobject.py?cvsroot=reportlab
#$Header: /tmp/reportlab/reportlab/pdfgen/pathobject.py,v 1.8 2001/01/12 21:36:57 dinu_gherman Exp $
__version__=''' $Id: pathobject.py,v 1.8 2001/01/12 21:36:57 dinu_gherman Exp $ '''
__doc__=""" 
PDFPathObject is an efficient way to draw paths on a Canvas. Do not
instantiate directly, obtain one from the Canvas instead.

Progress Reports:
8.83, 2000-01-13, gmcm:
    created from pdfgen.py
"""

import string
import reportlab.pdfgen.pdfgeom
from reportlab.pdfgen import pdfgeom


class PDFPathObject:
    """Represents a graphic path.  There are certain 'modes' to PDF
    drawing, and making a separate object to expose Path operations
    ensures they are completed with no run-time overhead.  Ask
    the Canvas for a PDFPath with getNewPathObject(); moveto/lineto/
    curveto wherever you want; add whole shapes; and then add it back
    into the canvas with one of the relevant operators.
    
    Path objects are probably not long, so we pack onto one line"""

    def __init__(self):
        self._code = []
        self._code.append('n')   #newpath
        
    def getCode(self):
        "pack onto one line; used internally"
        return string.join(self._code, ' ')

    def moveTo(self, x, y):
        self._code.append('%0.2f %0.2f m' % (x,y))

    def lineTo(self, x, y):
        self._code.append('%0.2f %0.2f l' % (x,y))

    def curveTo(self, x1, y1, x2, y2, x3, y3):
        self._code.append('%0.2f %0.2f %0.2f %0.2f %0.2f %0.2f c' % (x1, y1, x2, y2, x3, y3))
    
    def arc(self, x1,y1, x2,y2, startAng=0, extent=90):
        """Contributed to piddlePDF by Robert Kern, 28/7/99.
        Draw a partial ellipse inscribed within the rectangle x1,y1,x2,y2,
        starting at startAng degrees and covering extent degrees.   Angles
        start with 0 to the right (+x) and increase counter-clockwise.
        These should have x1<x2 and y1<y2.

        The algorithm is an elliptical generalization of the formulae in
        Jim Fitzsimmon's TeX tutorial <URL: http://www.tinaja.com/bezarc1.pdf>."""

        pointList = pdfgeom.bezierArc(x1,y1, x2,y2, startAng, extent)
        #move to first point
        self._code.append('%0.2f %0.2f m' % pointList[0][:2])
        for curve in pointList:
            self._code.append('%0.2f %0.2f %0.2f %0.2f %0.2f %0.2f c' % curve[2:])

    def arcTo(self, x1,y1, x2,y2, startAng=0, extent=90):
        """Like arc, but draws a line from the current point to
        the start if the start is not the current point."""
        pointList = pdfgeom.bezierArc(x1,y1, x2,y2, startAng, extent)
        self._code.append('%0.2f %0.2f l' % pointList[0][:2])
        for curve in pointList:
            self._code.append('%0.2f %0.2f %0.2f %0.2f %0.2f %0.2f c' % curve[2:])
    
    def rect(self, x, y, width, height):
        """Adds a rectangle to the path"""
        self._code.append('%0.2f %0.2f %0.2f %0.2f re' % (x, y, width, height))

    def ellipse(self, x, y, width, height):
        """adds an ellipse to the path"""
        pointList = pdfgeom.bezierArc(x, y, x + width,y + height, 0, 360)
        self._code.append('%0.2f %0.2f m' % pointList[0][:2])
        for curve in pointList:
            self._code.append('%0.2f %0.2f %0.2f %0.2f %0.2f %0.2f c' % curve[2:])
       
    def circle(self, x_cen, y_cen, r):
        """adds a circle to the path"""
        x1 = x_cen - r
        #x2 = x_cen + r
        y1 = y_cen - r
        #y2 = y_cen + r
        width = height = 2*r
        #self.ellipse(x_cen - r, y_cen - r, x_cen + r, y_cen + r)
        self.ellipse(x1, y1, width, height)
        
    def close(self):
        "draws a line back to where it started"
        self._code.append('h')

