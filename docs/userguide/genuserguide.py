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
#	Revision 1.12  2000/06/28 16:10:00  rgbecker
#	Fix unwanted 'i'
#
#	Revision 1.11  2000/06/28 14:52:43  rgbecker
#	Documentation changes
#	
#	Revision 1.10  2000/06/27 10:09:48  rgbecker
#	Minor cosmetic changes
#	
#	Revision 1.9  2000/06/23 21:09:03  aaron_watters
#	text text and more text
#	
#	Revision 1.8  2000/06/22 19:05:24  aaron_watters
#	added quickhack for font changes in paragraphs and lots of new text
#	
#	Revision 1.7  2000/06/22 13:55:59  aaron_watters
#	showPage resets all state parameters warning.
#	
#	Revision 1.6  2000/06/22 13:35:28  aaron_watters
#	textobject and pathobject methods, among other things
#	
#	Revision 1.5  2000/06/21 21:19:29  aaron_watters
#	colors, line styles, more examples
#	
#	Revision 1.4  2000/06/21 15:16:05  aaron_watters
#	Lots of graphical examples added
#	
#	Revision 1.3  2000/06/20 20:31:42  aaron_watters
#	typos and more examples
#	
#	Revision 1.2  2000/06/19 21:13:02  aaron_watters
#	2nd try. more text
#	
#	Revision 1.1  2000/06/17 02:57:56  aaron_watters
#	initial checkin. user guide generation framework.
#	
__version__=''' $Id: genuserguide.py,v 1.12 2000/06/28 16:10:00 rgbecker Exp $ '''


__doc__ = """
This module contains the script for building the user guide.
"""

_oldStyle=0		#change to 1 to get Aaron's original
if _oldStyle:
	from reportlab.lib.styles import getSampleStyleSheet
	styleSheet = getSampleStyleSheet()
else:
	import os, sys
	sys.path.insert(0,os.path.abspath(os.path.join('..','tools')))
	from rltemplate import RLDocTemplate
	from stylesheet import getStyleSheet
	styleSheet = getStyleSheet()

from reportlab.platypus.doctemplate import SimpleDocTemplate
from reportlab.platypus.flowables import Flowable
from reportlab.lib.units import inch
from reportlab.lib.pagesizes import letter
from reportlab.platypus import Paragraph, Spacer, Preformatted, PageBreak, CondPageBreak
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib import colors
import examples

from reportlab.lib.corp import ReportLabLogo
LOGO = ReportLabLogo(0.25*inch, 0.25*inch, inch, 0.75*inch)

from t_parse import Template
QFcodetemplate = Template("X$X$", "X")
QFreptemplate = Template("X^X^", "X")
if _oldStyle:
	codesubst = "%s<font name=courier color=green>%s</font>"
	QFsubst = "%s<font name=Helvetica color=blue><i>%s</i></font>"
else:
	codesubst = "%s<b><font name=courier></b>%s</font>"
	QFsubst = "%s<font name=Helvetica><i>%s</i></font>"
	

def quickfix(text):
    """inside text find any subsequence of form $subsequence$.
       Format the subsequence as code.  If similarly if text contains ^arg^
       format the arg as replaceable.  The escape sequence for literal
       $ is $\\$ (^ is ^\\^.
    """
    from string import join
    for (template,subst) in [(QFcodetemplate, codesubst), (QFreptemplate, QFsubst)]:
        fragment = text
        parts = []
        try:
            while fragment:
                try:
                    (matches, index) = template.PARSE(fragment)
                except: raise ValueError
                else:
                    [prefix, code] = matches
                    if code == "\\":
                        part = fragment[:index]
                    else:
                        part = subst % (prefix, code)
                    parts.append(part)
                    fragment = fragment[index:]
        except ValueError:
            parts.append(fragment)
        text = join(parts, "")
    return text
#print quickfix("$testing$ testing $one$ ^two^ $three(^four^)$")

if _oldStyle:
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
        if _oldStyle:
            self.myannotations = PageAnnotations()
        self.story = story()
    def go(self, filename="userguide.pdf"):
        # generate the doc...
        doc = RLDocTemplate(filename,pagesize = letter)
        story = self.story
        if _oldStyle:
            doc.build(story, self.myannotations.onFirstPage, self.myannotations.onNextPage)
        else:
            doc.build(story)

H1 = styleSheet['Heading1']
H2 = styleSheet['Heading2']
B = styleSheet['BodyText']
if _oldStyle:
	lessonnamestyle = ParagraphStyle("lessonname", parent=H2)
	lessonnamestyle.fontName = 'Helvetica-Bold'
	discussiontextstyle = ParagraphStyle("discussiontext", parent=B)
	discussiontextstyle.fontName= 'Helvetica'
else:
	lessonnamestyle = H2
	discussiontextstyle = B
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
    text = quickfix(text)
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
    
def head(text,style=lessonnamestyle):
    BODY.append(CondPageBreak(inch))
    disc(text, style=style)

def title(text):
	disc(text,style=styleSheet['Title'])
    
#head("this is a header")
    
def lesson(text):
    BODY.append(PageBreak())
    head(text,style=H1)
    
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
        

def pencilnote():
    BODY.append(examples.NoteAnnotation())
        
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

#pencilnote()

title("ReportLab User Guide")
head("Introduction",style=H1)

disc("""
This document is intended to be a conversational introduction
to the use of the ReportLab packages.  Some previous programming experience
is presumed and familiarity with the Python Programming language is
recommended.
""")

#canvasdemo(NOP) # execute some code

pencilnote()

disc("""
This document is in a <em>very</em> preliminary form.
""")

lesson("Introduction to $pdfgen$")

disc("""
The $pdfgen$ package is the lowest level interface for
generating PDF documents.  A $pdfgen$ program is essentially
a sequence of instructions for "painting" a document onto
a sequence of pages.  The interface object which provides the
painting operations is the $pdfgen$ canvas.  
""")

disc("""
The canvas should be thought of as a sheet of white paper
with points on the sheet identified using Cartesian ^(X,Y)^ coordinates
which by default have the ^(0,0)^ origin point at the lower
left corner of the page.  Furthermore the first coordinate ^x^
goes to the right and the second coordinate ^y^ goes up, by
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
The above code creates a $canvas$ object which will generate
a PDF file named $hello.pdf$ in the current working directory.
It then calls the $hello$ function passing the $canvas$ as an argument.
Finally the $showPage$ method saves the current page of the canvas
and the $save$ method stores the file and closes the canvas.""")

disc("""
The $showPage$ method causes the $canvas$ to stop drawing on the
current page and any further operations will draw on a subsequent
page (if there are any further operations -- if not no
new page is created).  The $save$ method must be called after the
construction of the document is complete -- it generates the PDF
document, which is the whole purpose of the $canvas$ object.
""")

disc("""
Suppose the $hello$ function referenced above is implemented as
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
the current font to $Times-Roman$ in 15 points, for example).
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
and %s inches tall.  The demo displays show the actual output of the demo
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

head("String drawing methods")

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
eg("""canvas.drawPath(path, stroke=1, fill=0) """)
eg("""canvas.clipPath(path, stroke=1, fill=0) """)

head("Image methods")

eg("""canvas.drawInlineImage(self, image, x,y, width=None,height=None) """)

head("Ending a page")

eg("""canvas.showPage()""")

disc("""The showPage method finishes the current page.  All additional drawing will
be done on another page.""")

pencilnote()

disc("""Warning!  All state changes (font changes, color settings, geometry transforms, etcetera)
are FORGOTTEN when you advance to a new page in $pdfgen$.  Any state settings you wish to preserve
must be set up again before the program proceeds with drawing!""")

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
 canvas.stringWidth(self, text, fontName, fontSize, encoding=None)
 canvas.setPageCompression(onoff=1)
 canvas.setPageTransition(self, effectname=None, duration=1, 
                        direction=0,dimension='H',motion='I')
""")


lesson('Coordinates (default user space)')

disc("""
By default locations on a page are identified by a pair of numbers.
For example the pair $(4.5*inch, 1*inch)$ identifies the location
found on the page by starting at the lower left corner and moving to
the right 4.5 inches and up one inch.
""")

disc("""For example, the following function draws
a number of elements on a canvas.""")

eg(examples.testcoords)

disc("""In the default user space the "origin" ^(0,0)^ point is at the lower
left corner.  Executing the $coords$ function in the default user space
(for the "demo minipage") we obtain the following.""")

canvasdemo(examples.coords)

head("Moving the origin: the $translate$ method")

disc("""Often it is useful to "move the origin" to a new point off
the lower left corner.  The $canvas.translate(^x,y^)$ method moves the origin
for the current page to the point currently identified by ^(x,y)^.""")

disc("""For example the following translate function first moves
the origin before drawing the same objects as shown above.""")

eg(examples.testtranslate)

disc("""This produces the following.""")

canvasdemo(examples.translate)


#canvasdemo(NOP) # execute some code

pencilnote()


disc("""
<i>Note:</i> As illustrated in the example it is perfectly possible to draw objects 
or parts of objects "off the page".
In particular a common confusing bug is a translation operation that translates the
entire drawing off the visible area of the page.  If a program produces a blank page
it is possible that all the drawn objects are off the page.
""")

head("Shrinking and growing: the scale operation")

disc("""Another important operation is scaling.  The scaling operation $canvas.scale(^dx,dy^)$
stretches or shrinks the ^x^ and ^y^ dimensions by the ^dx^, ^dy^ factors respectively.  Often
^dx^ and ^dy^ are the same -- for example to reduce a drawing by half in all dimensions use
$dx = dy = 0.5$.  However for the purposes of illustration we show an example where
$dx$ and $dy$ are different.
""")

eg(examples.testscale)

disc("""This produces a "short and fat" reduced version of the previously displayed operations.""")

canvasdemo(examples.scale)


#canvasdemo(NOP) # execute some code

pencilnote()


disc("""<i>Note:</i> scaling may also move objects or parts of objects off the page,
or may cause objects to "shrink to nothing." """)

disc("""Scaling and translation can be combined, but the order of the
operations are important.""")

eg(examples.testscaletranslate)

disc("""This example function first saves the current canvas state
and then does a $scale$ followed by a $translate$.  Afterward the function
restores the state (effectively removing the effects of the scaling and
translation) and then does the <i>same</i> operations in a different order.
Observe the effect below.""")

canvasdemo(examples.scaletranslate)


#canvasdemo(NOP) # execute some code

pencilnote()


disc("""<em>Note:</em> scaling shrinks or grows everything including line widths
so using the canvas.scale method to render a microscopic drawing in 
scaled microscopic units
may produce a blob (because all line widths will get expanded a huge amount).  
Also rendering an aircraft wing in meters scaled to centimeters may cause the lines
to shrink to the point where they disappear.  For engineering or scientific purposes
such as these scale and translate
the units externally before rendering them using the canvas.""")

head("Saving and restoring the canvas state: $saveState$ and $restoreState$")

disc("""
The $scaletranslate$ function used an important feature of the canvas object:
the ability to save and restore the current parameters of the canvas.
By enclosing a sequence of operations in a matching pair of $canvas.saveState()$
an $canvas.restoreState()$ operations all changes of font, color, line style,
scaling, translation, or other aspects of the canvas graphics state can be
restored to the state at the point of the $saveState()$.  Remember that the save/restore
calls must match: a stray save or restore operation may cause unexpected
and undesirable behavior.  Also, remember that <i>no</i> canvas state is
preserved across page breaks, and the save/restore mechanism does not work
across page breaks.
""")

head("Mirror image")

disc("""
It is interesting although perhaps not terribly useful to note that
scale factors can be negative.  For example the following function
""")

eg(examples.testmirror)

disc("""
creates a mirror image of the elements drawn by the $coord$ function.
""")

canvasdemo(examples.mirror)

disc("""
Notice that the text strings are painted backwards.
""")

lesson("Colors")

disc("""
There are four way to specify colors in $pdfgen$: by name (using the $color$
module, by red/green/blue (additive, $RGB$) value,
by cyan/magenta/yellow/darkness (subtractive, $CMYK$), or by gray level.
The $colors$ function below exercises each of the four methods.
""")

eg(examples.testcolors)

disc("""
The $RGB$ or additive color specification follows the way a computer
screen adds different levels of the red, green, or blue light to make
any color, where white is formed by turning all three lights on full
$(1,1,1)$.""")

disc("""The $CMYK$ or subtractive method follows the way a printer
mixes three pigments (cyan, magenta, and yellow) to form colors.
Because mixing chemicals is more difficult than combining light there
is a fourth parameter for darkness.  For example a chemical
combination of the $CMY$ pigments generally never makes a perfect
black -- instead producing a muddy color -- so, to get black printers
don't use the $CMY$ pigments but use a direct black ink.  Because
$CMYK$ maps more directly to the way printer hardware works it may
be the case that colors specified in $CMYK$ will provide better fidelity
and better control when printed.
""")

canvasdemo(examples.colors)

lesson('Painting back to front')

disc("""
Objects may be painted over other objects to good effect in $pdfgen$.  As
in painting with oils the object painted last will show up on top.  For
example, the $spumoni$ function below paints up a base of colors and then
paints a white text over the base.
""")

eg(examples.testspumoni)

disc("""
The word "SPUMONI" is painted in white over the colored rectangles,
with the apparent effect of "removing" the color inside the body of
the word.
""")

canvasdemo(examples.spumoni)

disc("""
The last letters of the word are not visible because the default canvas
background is white and painting white letters over a white background
leaves no visible effect.
""")

disc("""
This method of building up complex paintings in layers can be done
in very many layers in $pdfgen$ -- there are fewer physical limitations
than there are when dealing with physical paints.
""")

eg(examples.testspumoni2)

disc("""
The $spumoni2$ function layers an ice cream cone over the
$spumoni$ drawing.  Note that different parts of the cone
and scoops layer over eachother as well.
""")
canvasdemo(examples.spumoni2)


lesson('Fonts and text objects')

disc("""
Text may be drawn in many different colors, fonts, and sizes in $pdfgen$.
The $textsize$ function demonstrates how to change the color and font and
size of text and how to place text on the page.
""")

eg(examples.testtextsize)

disc("""
The $textsize$ function generates the following page.
""")

canvasdemo(examples.textsize)

disc("""
A number of different fonts are always available in $pdfgen$.
""")

eg(examples.testfonts)

disc("""
The $fonts$ function lists the fonts that are always available.
""")

canvasdemo(examples.fonts)

disc("""
Other fonts can be added to a PDF document as well.
""")

lesson("Text object methods")

disc("""
For the dedicated presentation of text in a PDF document, use a text object.
The text object interface provides detailed control of text layout parameters
not available directly at the canvas level.
""")

eg("""textobject.setTextOrigin(x,y)""")

eg("""textobject.setTextTransform(a,b,c,d,e,f)""")

eg("""textobject.moveCursor(dx, dy) # from start of current LINE""")

eg("""(x,y) = textobject.getCursor()""")

eg("""x = textobject.getX(); y = textobject.getY()""")

eg("""textobject.setFont(psfontname, size, leading = None)""")

eg("""textobject.textOut(text)""")

eg("""textobject.textLine(text='')""")

eg("""textobject.textLines(stuff, trim=1)""")

disc("""
The text object methods shown above relate to basic text geometry.
""")

disc("""
A text object maintains a text cursor which moves about the page when 
text is drawn.  For example the $setTextOrigin$ places the cursor
in a known position and the $textLine$ and $textLines$ methods move
the text cursor down past the lines that have been missing.
""")

eg(examples.testcursormoves1)

disc("""
The $cursormoves$ function relies on the automatic
movement of the text cursor for placing text after the origin
has been set.
""")

canvasdemo(examples.cursormoves1)

disc("""
It is also possible to control the movement of the cursor
more explicitly by using the $moveCursor$ method (which moves
the cursor as an offset from the start of the current <i>line</i>
NOT the current cursor, and which also has positive ^y^ offsets
move <i>down</i> (in contrast to the normal geometry where
positive ^y^ usually moves up.
""")

eg(examples.testcursormoves2)

disc("""
Here the $textOut$ does not move the down a line in contrast
to the $textLine$ function which does move down.
""")

canvasdemo(examples.cursormoves2)

head("Character Spacing")

eg("""textobject.setCharSpace(charSpace)""")

disc("""The $setCharSpace$ method adjusts one of the parameters of text -- the inter-character
spacing.""")

eg(examples.testcharspace)

disc("""The 
$charspace$ function exercises various spacing settings.
It produces the following page.""")

canvasdemo(examples.charspace)

head("Word Spacing")

eg("""textobject.setWordSpace(wordSpace)""")

disc("The $setWordSpace$ method adjusts the space between word.")

eg(examples.testwordspace)

disc("""The $wordspace$ function shows what various word space settings
look like below.""")

canvasdemo(examples.wordspace)

head("Horizontal Scaling")

eg("""textobject.setHorizScale(horizScale)""")

disc("""Lines of text can be stretched or shrunken horizontally by the 
$setHorizScale$ method.""")

eg(examples.testhorizontalscale)

disc("""The horizontal scaling parameter ^horizScale^
is given in percentages (with 100 as the default), so the 80 setting
shown below looks skinny.
""")
canvasdemo(examples.horizontalscale)

head("Interline spacing (Leading)")

eg("""textobject.setLeading(leading)""")

disc("""The vertical offset between the point at which one
line starts and where the next starts is called the leading
offset.  The $setLeading$ method adjusts the leading offset.
""")

eg(examples.testleading)

disc("""As shown below if the leading offset is set too small
characters of one line my write over the bottom parts of characters
in the previous line.""")

canvasdemo(examples.leading)

head("Other text object methods")

eg("""textobject.setTextRenderMode(mode)""")

disc("""The $setTextRenderMode$ method allows text to be used
as a forground for clipping background drawings, for example.""")

eg("""textobject.setRise(rise)""")

disc("""
The $setRise$ method <super>raises</super> or <sub>lowers</sub> text on the line
(for creating superscripts or subscripts, for example).
""")

eg("""textobject.setFillColor(aColor); 
textobject.setStrokeColor(self, aColor) 
# and similar""")

disc("""
These color change operations change the <font color=darkviolet>color</font> of the text and are otherwise
similar to the color methods for the canvas object.""")

lesson('Paths and Lines')

disc("""Just as textobjects are designed for the dedicated presentation
of text, path objects are designed for the dedicated construction of
graphical figures.  When path objects are drawn onto a canvas they are
are drawn as one figure (like a rectangle) and the mode of drawing
for the entire figure can be adjusted: the lines of the figure can
be drawn (stroked) or not; the interior of the figure can be filled or
not; and so forth.""")

disc("""
For example the $star$ function uses a path object
to draw a star
""")

eg(examples.teststar)

disc("""
The $star$ function has been designed to be useful in illustrating
various line style parameters supported by $pdfgen$.
""")

canvasdemo(examples.star)

head("Line join settings")

disc("""
The $setLineJoin$ method can adjust whether line segments meet in a point
a square or a rounded vertex.
""")

eg(examples.testjoins)

disc("""
The line join setting is only really of interest for thick lines because
it cannot be seen clearly for thin lines.
""")

canvasdemo(examples.joins)

head("Line cap settings")

disc("""The line cap setting, adjusted using the $setLineCap$ method,
determines whether a terminating line
ends in a square exactly at the vertex, a square over the vertex
or a half circle over the vertex.
""")

eg(examples.testcaps)

disc("""The line cap setting, like the line join setting, is only
visible when the lines are thick.""")

canvasdemo(examples.caps)

head("Dashes and broken lines")

disc("""
The $setDash$ method allows lines to be broken into dots or dashes.
""")

eg(examples.testdashes)

disc("""
The patterns for the dashes or dots can be in a simple on/off repeating pattern
or they can be specified in a complex repeating pattern.
""")

canvasdemo(examples.dashes)

head("Creating complex figures with path objects")

disc("""
Combinations of lines, curves, arcs and other figures
can be combined into a single figure using path objects.
For example the function shown below constructs two path
objects using lines and curves.  
This function will be used later on as part of a
pencil icon construction.
""")

eg(examples.testpenciltip)

disc("""
Note that the interior of the pencil tip is filled
as one object even though it is constructed from
several lines and curves.  The pencil lead is then
drawn over it using a new path object.
""")

canvasdemo(examples.penciltip)

lesson('Rectangles, circles, ellipses')

disc("""
The $pdfgen$ module supports a number of generally useful shapes
such as rectangles, rounded rectangles, ellipses, and circles.
Each of these figures can be used in path objects or can be drawn
directly on a canvas.  For example the $pencil$ function below
draws a pencil icon using rectangles and rounded rectangles with
various fill colors and a few other annotations.
""")

eg(examples.testpencil)

pencilnote()

disc("""
Note that this function is used to create the "margin pencil" to the left.
Also note that the order in which the elements are drawn are important
because, for example, the white rectangles "erase" parts of a black rectangle
and the "tip" paints over part of the yellow rectangle.
""")

canvasdemo(examples.pencil)

lesson('Bezier curves')

disc("""
Programs that wish to construct figures with curving borders
generally use Bezier curves to form the borders.
""")

eg(examples.testbezier)

disc("""
A Bezier curve is specified by four control points 
$(x1,y1)$, $(x2,y2)$, $(x3,y3)$, $(x4,y4)$.
The curve starts at $(x1,y1)$ and ends at $(x4,y4)$
and the line segment from $(x1,y1)$ to $(x2,y2)$
and the line segment from $(x3,y3)$ to $(x4,y4)$
both form tangents to the curve.  Furthermore the
curve is entirely contained in the convex figure with vertices
at the control points.
""")

canvasdemo(examples.bezier)

disc("""
The drawing above (the output of $testbezier$) shows
a bezier curves, the tangent lines defined by the control points
and the convex figure with vertices at the control points.
""")

head("Smoothly joining bezier curve sequences")

disc("""
It is often useful to join several bezier curves to form a
single smooth curve.  To construct a larger smooth curve from
several bezier curves make sure that the tangent lines to adjacent
bezier curves that join at a control point lie on the same line.
""")

eg(examples.testbezier2)

disc("""
The figure created by $testbezier2$ describes a smooth
complex curve because adjacent tangent lines "line up" as
illustrated below.
""")

canvasdemo(examples.bezier2)

lesson("Path object methods")

eg("""pathobject.moveTo(x,y)""")

eg("""pathobject.lineTo(x,y)""")

eg("""pathobject.curveTo(x1, y1, x2, y2, x3, y3) """)

eg("""pathobject.arc(x1,y1, x2,y2, startAng=0, extent=90) """)

eg("""pathobject.arcTo(x1,y1, x2,y2, startAng=0, extent=90) """)

eg("""pathobject.rect(x, y, width, height) """)

eg("""pathobject.ellipse(x, y, width, height)""")

eg("""pathobject.circle(x_cen, y_cen, r) """)

eg("""pathobject.close() """)

eg(examples.testhand)

canvasdemo(examples.hand)


eg(examples.testhand2)

canvasdemo(examples.hand2)


##### FILL THEM IN

lesson("...more lessons...")

#####################################################################################################3

lesson("Introduction to Platypus")

lesson("A very simple Flowable")

eg(examples.testnoteannotation)
    
if __name__=="__main__":
    g = Guide()
    g.go()
    
