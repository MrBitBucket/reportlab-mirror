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
#	$Log: monterey.py,v $
#	Revision 1.2  2000/02/15 17:55:59  rgbecker
#	License text fixes
#
#	Revision 1.1.1.1  2000/02/15 15:07:38  rgbecker
#	Initial setup of demos directory and contents.
#	
__version__=''' $Id: monterey.py,v 1.2 2000/02/15 17:55:59 rgbecker Exp $ '''
"""This builds the document for my talk at Monterey."""

from piddle import *
import platypus
import textcanvas
import pagesizes
import pythonpoint_old
    
def myPageBorder(canvas, doc):
    "Draws the standard border for this talk"
    canvas.drawImage('vertpython.gif',0, pagesizes.A4[0], 144, -1)

    canvas.drawString('copyright Robinson Analytics 1999',
        pagesizes.A4[1] - 3.5 * inch,
        pagesizes.A4[0] - 0.75*inch,
        font=Font(italic=1)
        )
        
    canvas.drawString('Printing with Python and PDFgen',
        pagesizes.A4[1] - 4.5 * inch,
        0.5*inch,
        font=Font(size=18)
        )
    

page1data = """/H1 Printing with Python
!image lj8100.jpg
/Center Andy Robinson, Robinson Analytics Ltd.
/Center O'Reilly Python Conference, Monterey, 24 Aug 1999
!page
/H2 Background to this project

o   London-based consultant and corporate developer
o   want to do neat Python stuff in the daytime
o   working for many years on financial modelling
o   this is one of 6 modules in that system
o   quickest to deliver, offers very wide benefits
o   25% of architecture done, but already very useful
o   don't worry, be crappy!

!page
/H2 Goal:  

A reporting package on the Next Curve...
o   Report on objects, not databases
o   Scalable to million page runs
o   Light enough to embed in any application
o   Allow reuse of graphical objects across reports
o   Open and Extensible
o   Publication Quality
o   Support all the world's languages

!page

/H2 Portable Document Format

"The New PostScript"
o   Free readers on all platforms
o   Better than paper - view it, email it, print it
o   'Final Form' for documents
o   High end solution - no limits to quality

...but you can't learn it in Notepad!

!page
/H1 PDFgen and PIDDLE

!page
/H2 Layer One: PDFgen
o   makes PDF documents from pure Python
o   wraps up PDF document structure
o   exposes nice effects - page transitions, outline trees
o   low level graphics primitives (PostScript model!)
o   Fine control of text placement
o   Supports Asian text
o   Supports coordinate transforms
... a foundation for other apps to build on
Status: In use now, fairly stable, internal cleanup due

!page
/H2 PDF Image Support

Python Imaging Library and zlib do the work - many formats.
Images cached (like .pyc files) - very fast builds possible.
!image python.gif

!page

/H2 Layer Two: PIDDLE

Plug In Drawing, Does Little Else
o   Easy Graphics Library
o   Abstract Canvas interface
o   Pluggable Back Ends
o   Same code can do viewing and printing
o   Standard set of test patterns
o   Uses Python Imaging Library

Back ends include Tkinter, wxPython, Mac, Pythonwin, 
PDF, Postscript, OpenGL, Adobe Illustrator, and Python
Imaging Library.  Really easy to add a new one!
!page

/H2 Layer Three: PLATYPUS 
"Page Layout and Typography Using Scripts"
Trying to work out the API now.
Key concepts:
o   Drawable Objects - can 'wrap to fit'
o   Frames on page
o   Frame consumes from a list of drawables until full
o   Document Models e.g. SimpleFlowDocument

XSL Flow Object model may be a good target.
!page
/H2 Drawable Objects

Next layer of PIDDLE extensibility.  
Each draws in its own coordinate system.
o   paragraph, image, table
o   chart libraries
o   diagrams
Open Source - let people contribute new ones. Anything you
could have in a view can be a new drawable type.

!page
/H2 Style Sheet Driven

Styles should use acquisition
o   Paragraph Styles - Style Sheet Compulsory!
o   Text Styles
o   Table and Table Cell Styles


!page

/H1 Vision:
o   XML to PDF in one step
o   Publish to web and print from same source
o   Publish books and Open Source documentation
o   Financial and Scientific reporting tool
o   Embedded reporting engine
o   Volume reporting tool for business

!page

/H2 PythonPoint


How I made this presentation...
"""


def run():
    a4width, a4height = pagesizes.A4
    mysize = (a4height, a4width)   # flip it to landscape
    
    doc = platypus.SimpleFlowDocument('monterey.pdf',mysize)
    #doc.showBoundary = 1
    doc.leftmargin =  2 * inch  # all default to one inch if not given
    doc.onFirstPage = myPageBorder
    doc.onNewPage = myPageBorder
    
    things_to_draw = pythonpoint_old.parsePPFtext(page1data)
    
    doc.build(things_to_draw)

if __name__ == '__main__':
    run()
    
