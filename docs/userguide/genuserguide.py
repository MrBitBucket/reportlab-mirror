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
#	Revision 1.1  2000/06/17 02:57:56  aaron_watters
#	initial checkin. user guide generation framework.
#
__version__=''' $Id: genuserguide.py,v 1.1 2000/06/17 02:57:56 aaron_watters Exp $ '''


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
examplefunctiondisplaysizes = (5.5*inch, 3*inch)

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
type changes the state of the canvas (like switching a tool) such as
changing the current fill or stroke color or changing the current font
type and size.
""")

disc("""
The document generated by this "hello world" program would contain
the following graphics.
""")

canvasdemo(examples.hello)

lesson("Canvas Text Operations")

lesson("...more lessons...")
    
if __name__=="__main__":
    g = Guide()
    g.go()
    