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
# documentation, and that the name of Robinson Analytics not be used
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
#	$Log: testpdfgen.py,v $
#	Revision 1.2  2000/02/15 15:47:09  rgbecker
#	Added license, __version__ and Logi comment
#
__version__=''' $Id: testpdfgen.py,v 1.2 2000/02/15 15:47:09 rgbecker Exp $ '''
#tests and documents new low-level canvas
import string
from pdfgen import canvas   # gmcm 2000/10/13, pdfgen now a package

inch = INCH = 72
cm = CM = inch / 2.54

#################################################################
#
#  first some drawing utilities
#
#
################################################################

BASEFONT = ('Times-Roman', 10)
def framePage(canvas, title):
    canvas.setFont('Times-BoldItalic',20)
    canvas.drawString(inch, 10.5 * inch, title)
                            
    canvas.setFont('Times-Roman',10)
    canvas.drawCentredString(4.135 * inch, 0.75 * inch,
                            'Page %d' % canvas.getPageNumber())
    
    #draw a border
    canvas.setStrokeColorRGB(1,0,0)
    canvas.setLineWidth(5)
    canvas.line(0.8 * inch, inch, 0.8 * inch, 10.75 * inch)
    #reset carefully afterwards
    canvas.setLineWidth(1)
    canvas.setStrokeColorRGB(0,0,0)

class DocBlock:
    """A DocBlock has a chunk of commentary and a chunk of code.
    It prints the code and commentary, then executes the code,
    which is presumed to draw in a region reserved for it.
    """
    def __init__(self):
        self.comment1 = "A doc block"
        self.code = "canvas.setTextOrigin(CM, CM)\ncanvas.textOut('Hello World')"
        self.comment2 = "That was a doc block"
        self.drawHeight = 0
        
    def _getHeight(self):
        "splits into lines"
        self.comment1lines = string.split(self.comment1, '\n')
        self.codelines = string.split(self.code, '\n')
        self.comment2lines = string.split(self.comment2, '\n')
        textheight = (len(self.comment1lines) +
                len(self.code) +
                len(self.comment2lines) +
                18)
        return max(textheight, self.drawHeight)

    def draw(self, canvas, x, y):
        #specifies top left corner
        canvas.saveState()
        height = self._getHeight()
        canvas.rect(x, y-height, 6*inch, height)
        #first draw the text
        canvas.setTextOrigin(x + 3 * inch, y - 12)
        canvas.setFont('Times-Roman',10)
        canvas.textLines(self.comment1)
        drawCode(canvas, self.code)
        canvas.textLines(self.comment2)

        #now a box for the drawing, slightly witin rect        
        canvas.rect(x + 9, y - height + 9, 198, height - 18)
        #boundary:
        self.namespace = {'canvas':canvas,'cm': cm,'inch':inch}
        canvas.translate(x+9, y - height + 9)
        codeObj = compile(self.code, '<sample>','exec')
        exec codeObj in self.namespace

        canvas.restoreState()
        

        
def drawAxes(canvas, label):
    """draws a couple of little rulers showing the coords -
    uses points as units so you get an imperial ruler
    one inch on each side"""
    #y axis
    canvas.line(0,0,0,72)
    for y in range(9):
        tenths = (y+1) * 7.2
        canvas.line(-6,tenths,0,tenths)
    canvas.line(-6, 66, 0, 72)  #arrow...
    canvas.line(6, 66, 0, 72)  #arrow...
    
    canvas.line(0,0,72,0)
    for x in range(9):
        tenths = (x+1) * 7.2
        canvas.line(tenths,-6,tenths, 0)
    canvas.line(66, -6, 72, 0)  #arrow...
    canvas.line(66, +6, 72, 0)  #arrow...

    canvas.drawString(18, 30, label)

def drawCrossHairs(canvas, x, y):
    """just a marker for checking text metrics - blue for fun"""

    canvas.saveState()
    canvas.setStrokeColorRGB(0,1,0)    
    canvas.line(x-6,y,x+6,y)
    canvas.line(x,y-6,x,y+6)
    canvas.restoreState()
    
def drawCode(canvas, code):
    """Draws a block of text at current point, indented and in Courier"""
    canvas.addLiteral('36 0 Td')
    canvas.setFillColorRGB(0,0,1)
    canvas.setFont('Courier',10)

    t = canvas.beginText()
    t.textLines(code)
    c.drawText(t)
    
    canvas.setFillColorRGB(0,0,0)
    canvas.addLiteral('-36 0 Td')
    canvas.setFont('Times-Roman',10)
    

def run():
##    print 'warning - hard-coded location'
##    c = pdfgen.Canvas('d:\\distiller\\testing\\testpdfgen.pdf')
##    c.setPageCompression(0)
    c = canvas.Canvas('testpdfgen.pdf')
    
    
    framePage(c, 'PDFgen graphics API test script')
    
    
    t = c.beginText(inch, 10*inch)
    drawCrossHairs(c, t.getX(),t.getY())
    t.textLine('Hello World')
    t.textLines("""
This tests a low-level API to the PDF file formac.  It is intended to sit
underneath PIDDLE, and to closely mirror the PDF / Postscript imaging
model.  There is an almost one to one correspondence between commands
and PDF operators.  However, where PDF provides several ways to do a job,
we have generally only picked one.

The test script attempts to use all of the methods exposed by pdfgen.PDFEngine.

First, let's look at test output.  Here are the basic commands:

canvas.enterTextMode()  must be called before text operations
canvas.exitTextMode()  must be called after text operations
You can do graphics in between calls, but no coordinate transforms
or clipping.

canvas.setTextOrigin(x, y)  sets the text origin
canvas.getCursor()  returns the current text cursor

canvas.textOut(text) writes text, and moves the cursor to the righc.
canvas.textLine(text) writes text, and moves the cursor down 'leading'.
This means textLine() is faster - no need to do a stringWidth!

canvas.textLines(stuff) accepts a multi-line string or a list/tuple
of strings, and moves the cursor down the page.
    
""")
    t.textLine('')
    t.textLine('The green crosshairs test whether the text cursor is tracking correctly.')
    drawCrossHairs(c, t.getX(),t.getY())
    t.textOut('textOut moves across:')
    drawCrossHairs(c, t.getX(),t.getY())
    t.textOut('textOut moves across:')
    drawCrossHairs(c, t.getX(),t.getY())
    t.textOut('textOut moves across:')
    drawCrossHairs(c, t.getX(),t.getY())
    t.textLine('')
    drawCrossHairs(c, t.getX(),t.getY())
    t.textLine('textLine moves down')
    drawCrossHairs(c, t.getX(),t.getY())
    t.textLine('textLine moves down')
    drawCrossHairs(c, t.getX(),t.getY())
    t.textLine('textLine moves down')
    drawCrossHairs(c, t.getX(),t.getY())

    t.setTextOrigin(4*inch,4*inch)
    drawCrossHairs(c, t.getX(),t.getY())
    t.textLines('This is a multi-line\nstring with embedded newlines\ndrawn with textLines().\n')
    t.textLines(['This is a list of strings',
                'drawn with textLines().',''])
    drawCrossHairs(c, t.getX(),t.getY())
    c.drawText(t)

    t = c.beginText(2*inch,2*inch)
    t.setFont('Times-Roman',10)
    drawCrossHairs(c, t.getX(),t.getY())
    t.textOut('Small text.')
    drawCrossHairs(c, t.getX(),t.getY())
    t.setFont('Courier',14)
    t.textOut('Bigger fixed width text.')
    drawCrossHairs(c, t.getX(),t.getY())
    t.setFont('Times-Roman',10)
    t.textOut('Small text again.')
    drawCrossHairs(c, t.getX(),t.getY())
    c.drawText(t)

    #mark the cursor where it stopped
    c.showPage()


    
    ##############################################################
    #
    # page 2 - line styles
    #
    ###############################################################

    #page 2 - lines and styles
    framePage(c, 'Line Drawing Styles')
    

    
    # three line ends, lines drawn the hard way
    #firt make some vertical end markers
    c.setDash(4,4)
    c.setLineWidth(0)
    c.line(inch,9.2*inch,inch, 7.8*inch)
    c.line(3*inch,9.2*inch,3*inch, 7.8*inch)
    c.setDash() #clears it
    
    c.setLineWidth(5)
    c.setLineCap(0)
    p = c.beginPath()
    p.moveTo(inch, 9*inch)
    p.lineTo(3*inch, 9*inch)
    c.drawPath(p)
    c.drawString(4*inch, 9*inch, 'the default - butt caps project half a width')
    
    c.setLineCap(1)
    p = c.beginPath()
    p.moveTo(inch, 8.5*inch)
    p.lineTo(3*inch, 8.5*inch)
    c.drawPath(p)
    c.drawString(4*inch, 8.5*inch, 'round caps')
        
    c.setLineCap(2)
    p = c.beginPath()
    p.moveTo(inch, 8*inch)
    p.lineTo(3*inch, 8*inch)
    c.drawPath(p)
    c.drawString(4*inch, 8*inch, 'square caps')
    
    c.setLineCap(0)

    # three line joins
    c.setLineJoin(0)
    p = c.beginPath()
    p.moveTo(inch, 7*inch)
    p.lineTo(2*inch, 7*inch)
    p.lineTo(inch, 6.7*inch)
    c.drawPath(p)
    c.drawString(4*inch, 6.8*inch, 'Default - mitered join')

    c.setLineJoin(1)
    p = c.beginPath()
    p.moveTo(inch, 6.5*inch)
    p.lineTo(2*inch, 6.5*inch)
    p.lineTo(inch, 6.2*inch)
    c.drawPath(p)
    c.drawString(4*inch, 6.3*inch, 'round join')

    c.setLineJoin(2)
    p = c.beginPath()
    p.moveTo(inch, 6*inch)
    p.lineTo(2*inch, 6*inch)
    p.lineTo(inch, 5.7*inch)
    c.drawPath(p)
    c.drawString(4*inch, 5.8*inch, 'bevel join')

    c.setDash(6,6)
    p = c.beginPath()
    p.moveTo(inch, 5*inch)
    p.lineTo(3*inch, 5*inch)
    c.drawPath(p)
    c.drawString(4*inch, 5*inch, 'dash pattern 6 points on, 3 off- setDash(6,3)')

    c.setDash([1,2,3,4,5,6],0)
    p = c.beginPath()
    p.moveTo(inch, 4.5*inch)
    p.lineTo(3*inch, 4.5*inch)
    c.drawPath(p)
    c.drawString(4*inch, 4.5*inch, 'dash pattern lengths growing - setDash([1,2,3,4,5,6],0)')

    c.setDash()

    
    c.showPage()

##############################################################
#
# higher level shapes
#
###############################################################
    framePage(c, 'Shape Drawing Routines')
    

    t = c.beginText(inch, 10*inch)
    t.textLines("""
Rather than making your own paths, you have access to a range of shape routines.
These are built in pdfgen out of lines and bezier curves, but use the most compact
set of operators possible.  We can add any new ones that are of general use at no
cost to performance.""")
    t.textLine()

    #line demo    
    c.line(inch, 8*inch, 3*inch, 8*inch)
    t.setTextOrigin(4*inch, 8*inch)
    t.textLine('canvas.line(x1, y1, x2, y2)')
    
    #bezier demo - show control points
    (x1, y1, x2, y2, x3, y3, x4, y4) = (
                        inch, 6.5*inch,
                        1.2*inch, 7.5 * inch,
                        3*inch, 7.5 * inch,
                        3.5*inch, 6.75 * inch
                        )
    c.bezier(x1, y1, x2, y2, x3, y3, x4, y4)
    c.setDash(3,3)
    c.line(x1,y1,x2,y2)
    c.line(x3,y3,x4,y4)
    c.setDash()
    t.setTextOrigin(4*inch, 7 * inch)
    t.textLine('canvas.bezier(x1, y1, x2, y2, x3, y3, x4, y4)')
    

    #rectangle
    c.rect(inch, 5.25 * inch, 2 * inch, 0.75 * inch)
    t.setTextOrigin(4*inch, 5.5 * inch)
    t.textLine('canvas.rect(x, y, width, height) - x,y is lower left')

    #wedge
    c.wedge(inch, 5*inch, 3*inch, 4*inch, 0, 315)
    t.setTextOrigin(4*inch, 4.5 * inch)
    t.textLine('canvas.wedge(x1, y1, x2, y2, startDeg, extentDeg)')
    t.textLine('Note that this is an elliptical arc, not just circular!')
    
    #wedge the other way
    c.wedge(inch, 4*inch, 3*inch, 3*inch, 0, -45)
    t.setTextOrigin(4*inch, 3.5 * inch)
    t.textLine('Use a negative extent to go clockwise')
    
    #circle
    c.circle(1.5*inch, 2*inch, 0.5 * inch)
    c.circle(3*inch, 2*inch, 0.5 * inch)
    t.setTextOrigin(4*inch, 2 * inch)
    t.textLine('canvas.circle(x, y, radius)')
    c.drawText(t)
##############################################################
#
# Page 4 - fonts
#
###############################################################

    
    c.showPage()
    framePage(c, "Font Control")

    c.drawString(inch, 10*inch, 'Listing available fonts...')

    y = 9.5*inch
    for fontname in c.getAvailableFonts():
        c.setFont(fontname,24)
        c.drawString(inch, y, 'This should be %s' % fontname)
        y = y - 28

    c.setFont('Times-Roman', 12)
    t = c.beginText(inch, 4*inch)
    t.textLines("""Now we'll look at the color functions and how they interact
    with the text.  In theory, a word is just a shape; so setFillColorRGB()
    determines most of what you see.  If you specify other text rendering
    modes, an outline color could be defined by setStrokeColorRGB() too""")
    c.drawText(t)
    
    
    t = c.beginText(inch, 2.75 * inch)
    t.setFont('Times-Bold',36)
    t.setFillColorRGB(0,1,0)  #green
    t.textLine('Green fill, no stroke')
    
    t.setStrokeColorRGB(1,0,0)  #ou can do this in a text object, or the canvas.
    t.setTextRenderMode(2)   # fill and stroke
    t.textLine('Green fill, red stroke - yuk!')

    t.setTextRenderMode(0)   # back to default - fill only
    t.setFillColorRGB(0,0,0)   #back to default
    t.setStrokeColorRGB(0,0,0) #ditto
    c.drawText(t)


    
#########################################################################
#
#  Page 5 - coord transforms
#
#########################################################################
    c.showPage()
    framePage(c, "Coordinate Transforms")
    c.setFont('Times-Roman', 12)
    t = c.beginText(inch, 10 * inch)
    t.textLines("""This shows coordinate transformations.  We draw a set of axes,
    moving down the page and transforming space before each one.
    You can use saveState() and restoreState() to unroll transformations.
    Note that functions which track the text cursor give the cursor position
    in the current coordinate system; so if you set up a 6 inch high frame
    2 inches down the page to draw text in, and move the origin to its top
    left, you should stop writing text after six inches and not eight.""")
    c.drawText(t)

    drawAxes(c, "0.  at origin")
    c.addLiteral('%about to translate space')
    c.translate(2*inch, 7 * inch)
    drawAxes(c, '1. translate near top of page')

    c.saveState()
    c.translate(1*inch, -2 * inch)
    drawAxes(c, '2. down 2 inches, across 1')
    c.restoreState()

    c.saveState()
    c.translate(0, -3 * inch)
    c.scale(2, -1)
    drawAxes(c, '3. down 3 from top, scale (2, -1)')
    c.restoreState()

    c.saveState()
    c.translate(0, -5 * inch)
    c.rotate(-30)
    drawAxes(c, "4. down 5, rotate 30' anticlockwise")
    c.restoreState()
    
    c.saveState()
    c.translate(3 * inch, -5 * inch)
    c.skew(0,30)
    drawAxes(c, "5. down 5, 3 across, skew beta 30")
    c.restoreState()

    
#########################################################################
#
#  Page 6 - clipping
#
#########################################################################
    c.showPage()
    framePage(c, "Clipping")
    c.setFont('Times-Roman', 12)
    t = c.beginText(inch, 10 * inch)
    t.textLines("""This shows clipping at work. We draw a chequerboard of rectangles
    into a path object, and clip it.  This then forms a mask which limits the region of
    the page on which one can draw.  This paragraph was drawn after setting the clipping
    path, and so you should only see part of the text.""")
    c.drawText(t)
    
    c.saveState()
    #c.setFillColorRGB(0,0,1)
    p = c.beginPath()
    #make a chesboard effect, 1 cm squares
    for i in range(14):
        x0 = (3 + i) * CM
        for j in range(7):
            y0 = (16 + j) * CM
            p.rect(x0, y0, 0.85*CM, 0.85*CM)
    c.addLiteral('%Begin clip path')
    c.clipPath(p)
    c.addLiteral('%End clip path')
    t = c.beginText(3 * CM, 22.5 * CM)
    t.textLines("""This shows clipping at work.  We draw a chequerboard of rectangles
    into a path object, and clip it.  This then forms a mask which limits the region of
    the page on which one can draw.  This paragraph was drawn after setting the clipping
    path, and so you should only see part of the text.
        This shows clipping at work.  We draw a chequerboard of rectangles
    into a path object, and clip it.  This then forms a mask which limits the region of
    the page on which one can draw.  This paragraph was drawn after setting the clipping
    path, and so you should only see part of the text.
        This shows clipping at work.  We draw a chequerboard of rectangles
    into a path object, and clip it.  This then forms a mask which limits the region of
    the page on which one can draw.  This paragraph was drawn after setting the clipping
    path, and so you should only see part of the text.""")
    c.drawText(t)
    
    c.restoreState()


    t = c.beginText(inch, 5 * inch)
    t.textLines("""You can also use text as an outline for clipping with the text render mode.
        The API is not particularly clean on this and one has to follow the right sequence;
        this can be optimized shortly.""")
    c.drawText(t)
    
    #first the outline
    c.saveState()
    t = c.beginText(inch, 3.0 * inch)
    t.setFont('Helvetica-BoldOblique',108)
    t.setTextRenderMode(5)  #stroke and add to path
    t.textLine('Python!')
    t.setTextRenderMode(0)
    c.drawText(t)    #this will make a clipping mask
    
    #now some small stuff which wil be drawn into the current clip mask
    t = c.beginText(inch, 4 * inch)
    t.setFont('Times-Roman',6)
    t.textLines((('spam ' * 40) + '\n') * 15)
    c.drawText(t)

    #now reset canvas to get rid of the clipping mask    
    c.restoreState()
    
    

#########################################################################
#
#  Page 7 - images
#
#########################################################################
    c.showPage()
    framePage(c, "Images")
    c.setFont('Times-Roman', 12)
    t = c.beginText(inch, 10 * inch)
    try:
        import Image
    except:
        t.textOut("Python Imaging Library not found!  You need it to see images.")
        c.save()
        return

        
    t.textLines("""This shows image capabilities.  If I've done things
        right, the bitmap should have its bottom left corner aligned
        with the crosshairs.""")
    t.textLines("""PDFgen uses the Python Imaging Library to process
        a very wide variety of image formats.  Although some processing
        is required, cached versions of the image are prepared and
        stored in the project directory, so that subsequent builds of
        an image-rich document are very fast indeed.""")
    
    c.drawText(t)

    c.drawInlineImage('PythonPowered.gif',2*inch, 7*inch)
    c.line(1.5*inch, 7*inch, 4*inch, 7*inch)
    c.line(2*inch, 6.5*inch, 2*inch, 8*inch)
    c.drawString(4.5 * inch, 7.25*inch, 'image drawn at natural size')

    c.drawInlineImage('PythonPowered.gif',2*inch, 4*inch, inch, inch)
    c.line(1.5*inch, 4*inch, 4*inch, 4*inch)
    c.line(2*inch, 3.5*inch, 2*inch, 5*inch)
    c.drawString(4.5 * inch, 4.25*inch, 'image distorted to fit box')
        
    c.save()



def pageShapes(c):
    """Demonstrates the basic lines and shapes"""
    c.showPage()
    framePage(c, "Basic line and shape routines""")
    c.setTextOrigin(inch, 10 * inch)
    c.setFont('Times-Roman', 12)
    c.textLines("""pdfgen provides some basic routines for drawing straight and curved lines,
    and also for solid shapes.""")

    y = 9 * inch
    d = DocBlock()
    d.comment1 = 'Lesson one'
    d.code = "canvas.textOut('hello, world')" 
    print d.code
    
    d.comment2 = 'Lesson two'
    
    d.draw(c, inch, 9 * inch)
    
if __name__ == "__main__":
    run()
