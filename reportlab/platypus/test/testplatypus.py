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
#	$Log: testplatypus.py,v $
#	Revision 1.7  2000/03/08 13:06:39  andy_robinson
#	Moved inch and cm definitions to reportlab.lib.units and amended all demos
#
#	Revision 1.6  2000/02/17 02:09:05  rgbecker
#	Docstring & other fixes
#	
#	Revision 1.5  2000/02/16 14:13:00  rgbecker
#	Final Fixes for Linux
#	
#	Revision 1.4  2000/02/16 09:42:50  rgbecker
#	Conversion to reportlab package
#	
#	Revision 1.3  2000/02/15 17:55:59  rgbecker
#	License text fixes
#	
#	Revision 1.2  2000/02/15 15:47:10  rgbecker
#	Added license, __version__ and Logi comment
#	
__version__=''' $Id: testplatypus.py,v 1.7 2000/03/08 13:06:39 andy_robinson Exp $ '''

#tests and documents Page Layout API
__doc__="""This is not obvious so here's a brief explanation.  This module is both
the test script and user guide for layout.  Each page has two frames on it:
one for commentary, and one for demonstration objects which may be drawn in
various esoteric ways.  The two functions getCommentary() and getExamples()
return the 'story' for each.  The run() function gets the stories, then
builds a special "document model" in which the frames are added to each page
and drawn into.
"""
import string
from reportlab.pdfgen import canvas
from reportlab.platypus import layout, tables
from reportlab.lib.units import inch, cm

#################################################################
#
#  first some drawing utilities
#
#
################################################################

BASEFONT = ('Times-Roman', 10)

def framePage(canvas):
    #canvas.drawImage("snkanim.gif", 36, 36)
    canvas.saveState()
    canvas.setStrokeColorRGB(1,0,0)
    canvas.setLineWidth(5)
    canvas.line(66,72,66,layout.PAGE_HEIGHT-72)

    canvas.setFont('Times-Italic',12)
    canvas.drawRightString(523, layout.PAGE_HEIGHT - 56, "Platypus User Guide and Test Script")
    
    canvas.setFont('Times-Roman',12)
    canvas.drawString(4 * inch, 0.75 * inch,
                        "Page %d" % canvas.getPageNumber())
    canvas.restoreState()
    

def getParagraphs(textBlock):
    """Within the script, it is useful to whack out a page in triple
    quotes containign separate paragraphs. This breaks one into its
    constituent paragraphs, using blank lines as the delimiter."""
    lines = string.split(textBlock, '\n')
    paras = []
    currentPara = []
    for line in lines:
        if len(string.strip(line)) == 0:
            #blank, add it
            if currentPara <> []:
                paras.append(string.join(currentPara, '\n'))
                currentPara = []
        else:
            currentPara.append(line)
    #...and the last one
    if currentPara <> []:
        paras.append(string.join(currentPara, '\n'))

    return paras

def getCommentary():
    """Returns the story for the commentary - all the paragraphs."""

    styleSheet = layout.getSampleStyleSheet()
    
    story = []
    story.append(layout.Paragraph("""
        PLATYPUS User Guide and Test Script
        """, styleSheet['Heading1']))


    spam = """
    Welcome to PLATYPUS!

    Platypus stands for "Page Layout and Typography Using Scripts".  It is a high
    level page layout library which lets you programmatically create complex
    documents with a minimum of effort.

    This document is toth the user guide and the output of the test script.
    In other words, a script used platypus to create the document you are now
    reading, and the fact that you are reading it proves that it works.  Or
    rather, that it worked for this script anyway.  It is a first release!  

    Platypus is built 'on top of' PDFgen, the Python library for creating PDF
    documents.  To learn about PDFgen, read the document testpdfgen.pdf.

    """    

    for text in getParagraphs(spam):
        story.append(layout.Paragraph(text, styleSheet['BodyText']))

    story.append(layout.Paragraph("""
        What concepts does PLATYPUS deal with?
        """, styleSheet['Heading2']))
    story.append(layout.Paragraph("""
        The central concepts in PLATYPUS are Drawable Objects, Frames, Flow
        Management, Styles and Style Sheets, Paragraphs and Tables.  This is
        best explained in contrast to PDFgen, the layer underneath PLATYPUS.
        PDFgen is a graphics library, and has primitive commans to draw lines
        and strings.  There is nothing in it to manage the flow of text down
        the page.  PLATYPUS works at the conceptual level fo a desktop publishing
        package; you can write programs which deal intelligently with graphic
        objects and fit them onto the page.
        """, styleSheet['BodyText']))

    story.append(layout.Paragraph("""
        How is this document organized?
        """, styleSheet['Heading2']))

    story.append(layout.Paragraph("""
        Since this is a test script, we'll just note how it is organized.
        the top of each page contains commentary.  The bottom half contains
        example drawings and graphic elements to whicht he commentary will
        relate.  Down below, you can see the outline of a text frame, and
        various bits and pieces within it.  We'll explain how they work
        on the next page.
        """, styleSheet['BodyText']))

    story.append(layout.PageBreak())
    #######################################################################
    #     Commentary Page 2
    #######################################################################
    
    story.append(layout.Paragraph("""
        Drawable Objects
        """, styleSheet['Heading2']))
    spam = """
        The first and most fundamental concept is that of a 'Drawable Object'.
        In PDFgen, you draw stuff by calling methods of the canvas to set up
        the colors, fonts and line styles, and draw the graphics primitives.
        If you set the pen color to blue, everything you draw after will be
        blue until you change it again.  And you have to handle all of the X-Y
        coordinates yourself.

        A 'Drawable object' is exactly what it says.  It knows how to draw itself
        on the canvas, and the way it does so is totally independent of what
        you drew before or after.  Furthermore, it draws itself at the location
        on the page you specify.

        The most fundamental Drawable Objects in most documents are likely to be
        paragraphs, tables, diagrams/charts and images - but there is no
        restriction.  You can write your own easily, and I hope that people
        will start to contribute them.  (Note for PIDDLE users - we'll provide a "PIDDLE drawing" object to let
        you insert platform-independent graphics into the flow of a document
        in the next couple of weeks)

        When you write a drawable object, you inherit from Drawable and
        must implement two methods.  object.wrap(availWidth, availHeight) will be called by other parts of
        the system, and tells you how much space you have.  You should return
        how much space you are going to use.  For a fixed-size object, this
        is trivial, but it is critical - PLATYPUS needs to figure out if things
        will fit on the page before drawing them.  For other objects such as paragraphs,
        the height is obviously determined by the available width.


        The second method is object.draw().  Here, you do whatever you want.
        The Drawable base class sets things up so that you have an origin of
        (0,0) for your drawing, and everything will fit nicely if you got the
        height and width right.  It also saves and restores the graphics state
        around your calls, so you don;t have to reset all the properties you
        changed.

        Programs which actually draw a Drawable don't
        call draw() this directly - they call object.drawOn(canvas, x, y).
        So you can write code in your own coordinate system, and things
        can be drawn anywhere on the page (possibly even scaled or rotated).
        """    
    for text in getParagraphs(spam):
        story.append(layout.Paragraph(text, styleSheet['BodyText']))

    story.append(layout.PageBreak())
    #######################################################################
    #     Commentary Page 3
    #######################################################################

    story.append(layout.Paragraph("""
        Available Drawable Objects
        """, styleSheet['Heading2']))

##    spam = """
##
##        """    
##    for text in getParagraphs(spam):
##        story.append(layout.Paragraph(text, styleSheet['BodyText']))

    story.append(layout.Paragraph("""
        Platypus comes with a basic set of drawable objects.  Here we list their
        class names and tell you what they do:
        """, styleSheet['BodyText']))
    #we can use the bullet feature to do a definition list
    story.append(layout.Paragraph("""
        This is a contrived object to give an example of a Drawable -
        just a fixed-size box with an X through it and a centred string.""",
            styleSheet['Definition'],
            bulletText='XBox  '  #hack - spot the extra space after
            ))
        
    story.append(layout.Paragraph("""
        This is the basic unit of a document.  Paragraphs can be finely
        tuned and offer a host of properties through their associated
        ParagraphStyle.""",
            styleSheet['Definition'],
            bulletText='Paragraph  '  #hack - spot the extra space after
            ))
    
    story.append(layout.Paragraph("""
        This is used for printing code and other preformatted text.
        There is no wrapping, and line breaks are taken where they occur.
        Many paragraph style properties do not apply.  You may supply
        an optional 'dedent' parameter to trim a number of characters
        off the front of each line.""",
            styleSheet['Definition'],
            bulletText='Preformatted  '  #hack - spot the extra space after
            ))
    story.append(layout.Paragraph("""
        This is a straight wrapper around an external image file.  By default
        the image will be drawn at a scale of one pixel equals one point, and
        centred in the frame.  You may supply an optional width and height.""",
            styleSheet['Definition'],
            bulletText='Image  '  #hack - spot the extra space after
            ))
        
    story.append(layout.Paragraph("""
        This is a base class for making grids.  It is really just a base for
        TextGrid below.""",
            styleSheet['Definition'],
            bulletText='BaseGrid  '  #hack - spot the extra space after
            ))

    story.append(layout.Paragraph("""
        This is a table drawing class descended from BaseGrid.  It is intended to be simpler
        than a full HTML table model yet be able to draw attractive output,
        and behave intelligently when the numbers of rows and columns vary.
        Still need to add the cell properties (shading, alignment, font etc.)""",
            styleSheet['Definition'],
            bulletText='TextGrid  '  #hack - spot the extra space after
            ))

    story.append(layout.Paragraph("""
        This is a 'null object' which merely takes up space on the page.
        Use it when you want some extra padding betweene elements.""",
            styleSheet['Definition'],
            bulletText='Spacer  '  #hack - spot the extra space after
            ))

    story.append(layout.Paragraph("""
        A PageBreak consumes all the remaining space in a frame.""",
            styleSheet['Definition'],
            bulletText='PageBreak  '  #hack - spot the extra space after
            ))

    story.append(layout.Paragraph("""
        This is in progress, but a macro is basically a chunk of Python code to
        be evaluated when it is drawn.  It could do lots of neat things.""",
            styleSheet['Definition'],
            bulletText='Macro  '  #hack - spot the extra space after
            ))


    return story

def getExamples():
    """Returns all the example drawable objects"""
    styleSheet = layout.getSampleStyleSheet()
    
    story = []

    #make a style with indents and spacing
    sty = layout.ParagraphStyle('obvious', None)
    sty.leftIndent = 18
    sty.rightIndent = 18
    sty.firstLineIndent = 36
    sty.spaceBefore = 6
    sty.spaceAfter = 6
    story.append(layout.Paragraph("""Now for some demo stuff - we need some on this page,
        even before we explain the concepts fully""", styleSheet['BodyText']))
    p = layout.Paragraph("""
        Platypus is all about fitting objects into frames on the page.  You
        are looking at a fairly simple Platypus paragraph in Debug mode.
        It has some gridlines drawn around it to show the left and right indents,
        and the space before and after, all of which are attributes set in
        the style sheet.  To be specific, this paragraph has left and
        right indents of 18 points, a first line indent of 36 points,
        and 6 points of space before and after itself.  A paragraph
        object fills the width of the enclosing frame, as you would expect.""", sty)

    p.debug = 1   #show me the borders
    story.append(p)

    story.append(layout.XBox(4*inch, 1*inch,
            'This is a box with a fixed size'))

    story.append(layout.Paragraph("""
        All of this is being drawn within a text frame which was defined
        on the page.  This frame is in 'debug' mode so you can see the border,
        and also see the margins which it reserves.  A frame does not have
        to have margins, but they have been set to 6 points each to create
        a little space around the contents.
        """, styleSheet['BodyText']))

    story.append(layout.PageBreak())

    #######################################################################
    #     Examples Page 2
    #######################################################################
    
    story.append(layout.Paragraph("""
        Here's the base class for Drawable...
        """, styleSheet['Italic']))
    
    code = '''class Drawable:
        """Abstract base class for things to be drawn.  Key concepts:
    1. It knows its size
    2. It draws in its own coordinate system (this requires the
        base API to provide a translate() function.
        """
    def __init__(self):
        self.width = 0
        self.height = 0
        self.wrapped = 0
        
    def drawOn(self, canvas, x, y):
        "Tell it to draw itself on the canvas.  Do not override"
        self.canv = canvas
        self.canv.saveState()
        self.canv.translate(x, y)

        self.draw()   #this is the bit you overload

        self.canv.restoreState()
        del self.canv
        
    def wrap(self, availWidth, availHeight):
        """This will be called by the enclosing frame before objects
        are asked their size, drawn or whatever.  It returns the
        size actually used."""
        return (self.width, self.height)
    '''
    
    story.append(layout.Preformatted(code, styleSheet['Code'], dedent=4))
    story.append(layout.PageBreak())
    #######################################################################
    #     Examples Page 3
    #######################################################################

    story.append(layout.Paragraph(
                "Here are some examples of the remaining objects above.",
                styleSheet['Italic']))
    
    story.append(layout.Paragraph("This is a bullet point", styleSheet['Bullet'], bulletText='O'))
    story.append(layout.Paragraph("Another bullet point", styleSheet['Bullet'], bulletText='O'))
    
    story.append(layout.Paragraph(
                "Here is an Image.  For now, these are always centred in the frame.",
                styleSheet['Italic']))

    story.append(layout.Image('pythonpowered.gif'))

##    story.append(layout.Paragraph("""
##                Next comes a grid.  class BaseGrid is the ancestor of Grid classes,
##                and doesn't do much more than this.  It, too, is centred.""",
##                styleSheet['Italic']))
##
##    story.append(layout.BaseGrid((36,36,36,36),(8,8,8)))

    story.append(layout.Paragraph("""Here is a Table, which takes all kinds of formatting options...""",
                styleSheet['Italic']))
    story.append(layout.Spacer(0, 12))
    
    g = tables.Table(
            (72,36,36,36,36),
            (24, 16,16,18),
            (('','North','South','East','West'),
             ('Quarter 1',100,200,300,400),
             ('Quarter 2',100,200,300,400),
             ('Total',200,400,600,800))
            )

##    #add some lines
##    g.addLines(0, 0, -1, -1, 0.25)  #inner grid
##    g.addLines(0, 1, -1, 1, 2)  #fattish top line
##    g.addLines(0, -2, -1, -2, 2)  #fattish bottom 2 lines
##    g.addLines(0, -1, -1, -1, 2)  #fattish bottom 2 lines
    style = tables.TableStyle([('ALIGN', (1,1), (-1,-1), 'RIGHT'),
                               ('ALIGN', (0,0), (-1,0), 'CENTRE'),
                               ('GRID', (0,0), (-1,-1), 0.25, 'BLACK'),
                               ('LINEBELOW', (0,0), (-1,0), 2, 'BLACK'),
                               ('LINEBELOW',(1,-1), (-1, -1), 2, (0.5, 0.5, 0.5)),
                               ('TEXTCOLOR', (0,1), (0,-1), 'RED'),
                               ('BACKGROUND', (0,0), (-1,0), (0,0.7,0.7))
                               ])
    g.setStyle(style)
    story.append(g)
    
    return story
    

def run():
    #Rather than using a SimpleFlowDocument, this will manually construct
    #some frames, since we need fine control for the demo.
    #each page has a main frame for the commentary, and
    #another for the demo/test functionality.
    cnvs = canvas.Canvas('testlayout.pdf')

    commentary = getCommentary()
    examples = getExamples()

    #while either story has data left, keep creating pages
    #and drawing into them
    firstPage = 1
    while (len(examples) > 0 or len(commentary) > 0):
        framePage(cnvs)
        frame1 = layout.SimpleFrame(cnvs, inch, 5.8*inch, 6 * inch, 5 * inch)
        frame2 = layout.SimpleFrame(cnvs, inch, inch, 6 * inch, 4.5 * inch)
        frame2.showBoundary = 1
        frame1.addFromList(commentary)
        frame2.addFromList(examples)

        cnvs.showPage()
        
    cnvs.save()
    
    
if __name__ == "__main__":
    run()
