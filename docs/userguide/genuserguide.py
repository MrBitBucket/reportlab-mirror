#!/bin/env python
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
#	$Log: genuserguide.py,v $
#	Revision 1.2  2000/06/19 21:13:02  aaron_watters
#	2nd try. more text
#
#	Revision 1.1  2000/06/17 02:57:56  aaron_watters
#	initial checkin. user guide generation framework.
#	
__version__=''' $Id: genuserguide.py,v 1.2 2000/06/19 21:13:02 aaron_watters Exp $ '''


__doc__ = """
This module contains the script for building the user guide.
"""

from reportlab.platypus.doctemplate import SimpleDocTemplate
from reportlab.platypus.flowables import Flowable
from reportlab.lib.units import inch
from reportlab.lib.pagesizes import letter
from reportlab.platypus import Paragraph, Spacer, Preformatted, PageBreak
from reportlab.lib.styles import PropertySet, getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
import examples

styleSheet = getSampleStyleSheet()
from reportlab.lib.corp import ReportLabLogo
LOGO = ReportLabLogo(0.25*inch, 0.25*inch, inch, 0.75*inch)

class PageAnnotations:
    """ "closure" containing onfirstpage, onnextpage actions
        and any data they might want to use.
    """
    pagesize = letter
    pagenumber = 1
    def onFirstPage(self, canvas, doc):
        (xsize, ysize) = self.pagesize
        LOGO.draw(canvas)
        #  width=6.25*inch,height=0.62*inch)
        canvas.setFont("Helvetica", 12)
        canvas.drawRightString(xsize-inch, ysize-0.8*inch, "ReportLab User Guide")
        self.pagenumber = self.pagenumber+1
    def onNextPage(self, canvas, doc):
        canvas.saveState()
        (xsize, ysize) = self.pagesize
        canvas.setFont("Helvetica", 12)
        canvas.drawString(inch, ysize-0.8*inch, "Page %s" % self.pagenumber)
        self.onFirstPage(canvas, doc)
        canvas.restoreState()
        
class Guide:
    def __init__(self):
        self.myannotations = PageAnnotations()
        self.story = story()
    def go(self, filename="userguide.pdf"):
        # generate the doc...
	doc = SimpleDocTemplate(filename,pagesize = letter ,showBoundary=0,
	  leftMargin=inch, rightMargin=inch, topMargin=1.7*inch, bottomMargin=inch+90)
	story = self.story
	doc.build(story, self.myannotations.onFirstPage, self.myannotations.onNextPage)

H = styleSheet['Heading2']
lessonnamestyle = ParagraphStyle("lessonname", parent=H)
lessonnamestyle.fontName = 'Helvetica-Bold'
B = styleSheet['BodyText']
discussiontextstyle = ParagraphStyle("discussiontext", parent=B)
discussiontextstyle.fontName= 'Helvetica'
exampletextstyle = styleSheet['Code']
# size for every example
examplefunctionxinches = 5.5
examplefunctionyinches = 3
examplefunctiondisplaysizes = (examplefunctionxinches*inch, examplefunctionyinches*inch)

# for testing
def NOP(*x,**y):
    return None

BODY = []
def story():
    return BODY

def disc(text, klass=Paragraph, style=discussiontextstyle):
    P = klass(text, style)
    BODY.append(P)
    
def eg(text):
    BODY.append(Spacer(0.1*inch, 0.1*inch))
    disc(text, klass=Preformatted, style=exampletextstyle)
    
#eg("""
#this
#  is 
#    an 
#     example""")
    
def head(text):
    disc(text, style=lessonnamestyle)
    
#head("this is a header")
    
def lesson(text):
    BODY.append(PageBreak())
    head(text)
    
def canvasdemo(function):
    BODY.append(Spacer(0.1*inch, 0.1*inch))
    BODY.append(OperationWrapper(function))
    
class OperationWrapper(Flowable):
    """wrap a drawing operation as a flowable.
       the operation should respect the examplefunctiondisplaysizes
       limitations.
       This example wraps a drawing operator f(pdfgen.canvas).
       Always enclosed in a rectangle.
    """
    def __init__(self, operation):
        self.operation = operation
        
    def wrap(self, aw, ah):
        return examplefunctiondisplaysizes # always the same
        
    def draw(self):
        canvas = self.canv
        canvas.saveState()
        (x,y) = examplefunctiondisplaysizes
        self.operation(canvas)
        canvas.restoreState()
        canvas.rect(0,0,x,y)
        
###### testing...
#canvasdemo(NOP)

#lesson("this is a new lesson")

#disc("this explains the example")

#eg("""
#this
#  is the
#    example
#      code""")
      
#disc("the execution of the example follows")
      
#canvasdemo(NOP) # execute some code

head("ReportLab User Guide")

disc("""
This document is intended to be a conversational introduction
to the use of the ReportLab packages.  Some previous programming experience
is presumed and familiarity with the Python Programming language is
recommended.
""")

disc("""
This document is in a <em>very</em> preliminary form.
""")

lesson("Introduction to pdfgen")

disc("""
The pdfgen package is the lowest level interface for
generating PDF documents.  A pdfgen program is essentially
a sequence of instructions for "painting" a document onto
a sequence of pages.  The interface object which provides the
painting operations is the pdfgen canvas.  
""")

disc("""
The canvas should be thought of as a sheet of white paper
with points on the sheet identified using Cartesian (X,Y) coordinates
which by default have the (0,0) origin point at the lower
left corner of the page.  Furthermore the first coordinate (x)
goes to the right and the second coordinate (y) goes up, by
default.""")

disc("""
A simple example
program that uses a canvas follows.
""")

eg("""
    from reportlab.pdfgen import canvas
    c = canvas.Canvas("hello.pdf")
    hello(c)
    c.showPage()
    c.save()
""")

disc("""
The above code creates a canvas object which will generate
a PDF file named hello.pdf in the current working directory.
It then calls the hello function passing the canvas as an argument.
Finally the showPage method saves the current page of the canvas
and the save method stores the file and closes the canvas.""")

disc("""
The showPage method causes the canvas to stop drawing on the
current page and any further operations will draw on a subsequent
page (if there are any further operations -- if not there no
new page is created).  The save method must be called after the
construction of the document is complete -- it generates the PDF
document, which is the whole purpose of the canvas object.
""")

disc("""
Suppose the hello function referenced above is implemented as
follows (we will not explain each of the operations in detail
yet).
""")

eg(examples.testhello)

disc("""
Examining this code notice that there are essentially two types
of operations performed using a canvas.  The first type draws something
on the page such as a text string or a rectangle or a line.  The second
type changes the state of the canvas such as
changing the current fill or stroke color or changing the current font
type and size.  
""")

disc("""
If we imagine the program as a painter working on
the canvas the "draw" operations apply paint to the canvas using
the current set of tools (colors, line styles, fonts, etcetera)
and the "state change" operations change one of the current tools
(changing the fill color from whatever it was to blue, or changing
the current font to Times-Roman in 15 points, for example).
""")

disc("""
The document generated by the "hello world" program listed above would contain
the following graphics.
""")

canvasdemo(examples.hello)

head("About the demos in this document")

disc("""
This document contains demonstrations of the code discussed like the one shown
in the rectangle above.  These demos are drawn on a "tiny page" embedded
within the real pages of the guide.  The tiny pages are %s inches wide
and %s inches tall.  The demos displays show the actual output of the demo
code.
""" % (examplefunctionxinches, examplefunctionyinches))

lesson('The tools: the "draw" operations')

disc("""
This section briefly lists the tools available to the program
for painting information onto a page using the canvas interface.
These will be discussed in detail in later sections.  They are listed
here for easy reference and for summary purposes.
""")

head("Line methods")

eg("""canvas.line(x1,y1,x2,y2)""")
eg("""canvas.lines(linelist)""")

disc("""
The line methods draw straight line segments on the canvas.
""")

head("Shape methods")

eg("""canvas.grid(xlist, ylist) """)
eg("""canvas.bezier(x1, y1, x2, y2, x3, y3, x4, y4)""")
eg("""canvas.arc(x1,y1,x2,y2) """)
eg("""canvas.rect(x, y, width, height, stroke=1, fill=0) """)
eg("""canvas.ellipse(x, y, width, height, stroke=1, fill=0)""")
eg("""canvas.wedge(x1,y1, x2,y2, startAng, extent, stroke=1, fill=0) """)
eg("""canvas.circle(x_cen, y_cen, r, stroke=1, fill=0)""")
eg("""canvas.roundRect(x, y, width, height, radius, stroke=1, fill=0) """)

disc("""
The shape methods draw common complex shapes on the canvas.
""")

head("The draw string methods")

eg("""canvas.drawString(x, y, text):""")
eg("""canvas.drawRightString(x, y, text) """)
eg("""canvas.drawCentredString(x, y, text)""")

disc("""
The draw string methods draw single lines of text on the canvas.
""")

head("The text object methods")
eg("""textobject = canvas.beginText(x, y) """)
eg("""canvas.drawText(textobject) """)

disc("""
Text objects are used to format text in ways that
are not supported directly by the canvas interface.
A program creates a text object from the canvas using beginText
and then formats text by invoking textobject methods.
Finally the textobject is drawn onto the canvas using
drawText.
""")

head("The path object methods")

eg("""path = canvas.beginPath() """)
eg("""canvas.drawPath(path, stroke=1, fill=0 """)
eg("""canvas.clipPath(path, stroke=1, fill=0 """)

head("Image methods")

eg("""canvas.drawInlineImage(self, image, x,y, width=None,height=None) """)

head("Ending a page")

eg("""canvas.showPage()""")

lesson('The toolbox: the "state change" operations')

disc("""
This section briefly lists the ways to switch the tools used by the
program
for painting information onto a page using the canvas interface.
These too will be discussed in detail in later sections.
""")

head("Changing Colors")
eg("""canvas.setFillColorCMYK(c, m, y, k) """)
eg("""canvas.setStrikeColorCMYK(c, m, y, k) """)
eg("""canvas.setFillColorRGB(r, g, b) """)
eg("""canvas.setStrokeColorRGB(r, g, b) """)
eg("""canvas.setFillColor(acolor) """)
eg("""canvas.setStrokeColor(acolor) """)
eg("""canvas.setFillGray(gray) """)
eg("""canvas.setStrokeGray(gray) """)

head("Changing Fonts")
eg("""canvas.setFont(psfontname, size, leading = None) """)

head("Changing Graphical Styles")

eg("""canvas.setLineWidth(width) """)
eg("""canvas.setLineCap(mode) """)
eg("""canvas.setLineJoin(mode) """)
eg("""canvas.setMiterLimit(limit) """)
eg("""canvas.setDash(self, array=[], phase=0) """)

head("Changing Geometry")

eg("""canvas.setPageSize(pair) """)
eg("""canvas.transform(a,b,c,d,e,f): """)
eg("""canvas.translate(dx, dy) """)
eg("""canvas.scale(x, y) """)
eg("""canvas.rotate(theta) """)
eg("""canvas.skew(alpha, beta) """)

head("State control")

eg("""canvas.saveState() """)
eg("""canvas.restoreState() """)


lesson("Other canvas methods.")

disc("""
Not all methods of the canvas object fit into the "tool" or "toolbox"
categories.  Below are some of the misfits, included here for completeness.
""")

eg("""
 canvas.setAuthor()
 canvas.addOutlineEntry(title, key, level=0, closed=None)
 canvas.setTitle(title)
 canvas.setSubject(subj)
 canvas.pageHasData()
 canvas.showOutline()
 canvas.bookmarkPage(name)
 canvas.bookmarkHorizontalAbsolute(name, yhorizontal)
 canvas.doForm()
 canvas.beginForm(name, lowerx=0, lowery=0, upperx=None, uppery=None)
 canvas.endForm()
 canvas.linkAbsolute(contents, destinationname, Rect=None, addtopage=1, name=None, **kw)
 canvas.getPageNumber()
 canvas.addLiteral()
 canvas.getAvailableFonts()
 canvas.stringWidth(self, text, fontName, fontSize)
 canvas.setPageCompression(onoff=1)
 canvas.setPageTransition(self, effectname=None, duration=1, 
                        direction=0,dimension='H',motion='I')
""")


lesson('Coordinates (default user space)')

disc("""
By default locations on a page are identified by a pair of numbers.
For example the pair (4.5*inch, 1*inch) identifies the location
found on the page by starting at the lower left corner and moving to
the right 4.5 inches and up one inch.
""")

disc("""For example, the following function draws
a number of elements on a canvas.""")

eg(examples.testcoords)

disc("""In the default user space the (0,0) point is at the lower
left corner.  Executing the coords function in the default user space
(for the "demo minipage") we obtain the following.""")

canvasdemo(examples.coords)

head("Moving the origin: the translate method")

disc("""Often it is useful to "move the origin" to a new point off
the lower left corner.  The canvas.translate(x,y) method moves the origin
for the current page to the point currently identified by (x,y).""")

disc("""For example the following translate function first moves
the origin before drawing the same objects as shown above.""")

eg(examples.testtranslate)

disc("""This produces the following.""")

canvasdemo(examples.translate)

disc("""
<em>Note:</em> As illustrated in the example it is perfectly possible to draw objects 
or parts of objects "off the page".
In particular a common confusing bug is a translation operation that translates the
entire drawing off the visible area of the page.  If a program produces a blank page
it is possible that all the drawn objects are off the page.
""")

head("Shrinking and growing: the scale operation")

disc("""Another important operation is scaling.  The scaling operation canvas.scale(dx,dy)
stretches or shrinks the x and y dimensions by the dx, dy factors respectively.  Often
dx and dy are the same -- for example to reduce a drawing by half in all dimensions use
dx = dy = 0.5.  However for the purposes of illustration we show an example where
dx and dy are different.
""")

eg(examples.testscale)

disc("""This produces a "short and fat" reduced version of the previously displayed operations.""")

canvasdemo(examples.scale)

disc("""<em>Note:</em> scaling may also move objects or parts of objects off the page,
or may cause objects to "shrink to nothing." """)

disc("""Scaling and translation can be combined, but the order of the
operations are important.""")

eg(examples.testscaletranslate)

disc("""This example function first saves the current canvas state
and then does a scaling followed by a translate.  Afterward the function
restores the state (effectively removing the effects of the scaling and
translation) and then does the <em>same</em> operations in a different order.
Observe the effect below.""")

canvasdemo(examples.scaletranslate)

disc("""<em>Note:</em> scaling shrinks or grows everything including line widths
so using the canvas.scale method to render a microscopic drawing in 
scaled microscopic units
may produce a blob (because all line widths will get expanded a huge amount).  
Also rendering an aircraft wing in meters scaled to centimeters may cause the lines
to shrink to the point where they disappear.  For engineering or scientific purposes
such as these scale and translate
the units externally before rendering them using the canvas.""")

head("Saving and restoring the canvas state: saveState and restoreState")

disc("""
The scaletranslate function used an important feature of the canvas object:
the ability to save and restore the current parameters of the canvas.
By enclosing a sequence of operations in a matching pair of canvas.saveState()
an canvas.restoreState() operations all changes of font, color, line style,
scaling, translation, or other aspects of the canvas graphics state can be
restored to the state at the point of the saveState().  Remember that the save/restore
calls must match: a stray save or restore operation may cause unexpected
and undesirable behavior.
""")

lesson('Painting back to front')

eg(examples.testspumoni)

canvasdemo(examples.spumoni)

eg(examples.testspumoni2)

canvasdemo(examples.spumoni2)


lesson('Fonts and text objects')

lesson('Paths and polygons')

lesson('Rectangles, circles, ellipses')

lesson('Bezier curves')

lesson("...more lessons...")
    
if __name__=="__main__":
    g = Guide()
    g.go()
    