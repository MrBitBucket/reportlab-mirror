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
#	$Log: pythonpoint.py,v $
#	Revision 1.8  2000/04/06 12:15:38  andy_robinson
#	Updated example XML to include full tag reference
#
#	Revision 1.7  2000/04/06 09:47:20  andy_robinson
#	Added several new shape tags.
#	Broke out parser into separate module, to
#	allow for alternative parsers in future.
#	Broke out 'user guide' into pythonpoint.xml
#	
#	Revision 1.6  2000/03/21 19:36:37  rgbecker
#	8bit character fixes
#	
#	Revision 1.5  2000/02/23 15:09:23  rgbecker
#	Memory leak fixes
#	
#	Revision 1.4  2000/02/17 02:06:28  rgbecker
#	Docstring & other fixes
#	
#	Revision 1.3  2000/02/16 09:42:50  rgbecker
#	Conversion to reportlab package
#	
#	Revision 1.2  2000/02/15 17:55:59  rgbecker
#	License text fixes
#	
#	Revision 1.1.1.1  2000/02/15 15:08:55  rgbecker
#	Initial setup of demos directory and contents.
#	
__version__=''' $Id: pythonpoint.py,v 1.8 2000/04/06 12:15:38 andy_robinson Exp $ '''
# xml parser stuff for PythonPoint
# PythonPoint Markup Language!
__doc__="""
This is PythonPoint!

The idea is a simple markup languages for describing
presentation slides, and other documents which run
page by page.  I expect most of it will be reusable
in other page layout stuff.

Look at the sample near the top, which shows how the presentation
should be coded up.

The parser, which is in a separate module to allow for multiple
parsers, turns the XML sample into an object tree.  There is a
simple class hierarchy of items, the inner levels of which create
drawable objects to go in the frames.  These know how to draw
themselves.

The currently available 'Presentation Objects' are:

    The main hierarchy...
        PPPresentation
        PPSection
        PPSlide
        PPFrame

    Things to flow within frames...
        PPPara - flowing text
        PPPreformatted - text with line breaks and tabs, for code..
        PPImage

    Things to draw directly on the page...
        PPRect
        PPRoundRect
        PPDrawingElement - user base class for graphics
        PPLine
        PPEllipse

"""

import os
import string
import pprint
import imp

from reportlab.pdfgen import canvas
from reportlab.platypus import layout
import stdparser 




        
class PPPresentation:
    def __init__(self):
        self.filename = None
        self.description = None
        self.slides = []
        self.effectName = None
        self.showOutline = 0   #should it be displayed when opening?
        
        #assume landscape        
        self.pageWidth = layout.DEFAULT_PAGE_SIZE[1]  
        self.pageHeight = layout.DEFAULT_PAGE_SIZE[0]  

    def save(self):
        """This writes out the PDF document"""
        canv = canvas.Canvas(self.filename,
                                pagesize = (self.pageWidth, self.pageHeight)
                               )
        canv.setPageCompression(0)
        canv.outlineNames = []   #HACK - not a normal attribute of a canvas, we are stashing
                        #stuff here
            
        for slide in self.slides:
            slide.drawOn(canv)
            canv.showPage()

        #draw the outline
        if canv.outlineNames <> []:
            apply(canv.setOutlineNames0, canv.outlineNames)
        if self.showOutline:
            canv.showOutline0()
        canv.save()        

class PPSection:
    """A section can hold graphics which will be drawn on all
    pages within it, before frames and other content are done.
    In other words, a background template."""
    def __init__(self, name):
        self.name = name
        self.graphics = []
        
    def drawOn(self, canv):
        for graphic in self.graphics:
            graphic.drawOn(canv)
            
        
class PPSlide:
    def __init__(self):
        self.id = None
        self.title = None
        self.outlineEntry = None
        self.effectName = None
        self.effectDirection = 0
        self.effectDimension = 'H'
        self.effectMotion = 'I'
        self.frames = []
        self.graphics = []
        self.section = None

    def drawOn(self, canv):
        if self.effectName:
            canv.setPageTransition(
                        effectname=self.effectName,
                        direction = self.effectDirection,
                        dimension = self.effectDimension,
                        motion = self.effectMotion
                        )
        if self.title:
            #put an outline entry in the left pane
            tag = self.title
            canv._inPage0()
            canv.bookmarkPage0(tag)
            canv.outlineNames.append(tag)
            
            
        
        if self.section:
            self.section.drawOn(canv)
                
        canv.drawRightString(800, 36, 'id: %s, title: %s' % (self.id, self.title))
        for graphic in self.graphics:
            graphic.drawOn(canv)
            
        for frame in self.frames:
            frame.drawOn(canv)

class PPFrame:
    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.content = []

        #others which can be set
        self.leftMargin = 0
        self.rightMargin = 0
        self.topMargin = 0
        self.bottomMargin = 0

        self.showBoundary = 0        

    def drawOn(self, canv):
        #make a layout frame
        frame = layout.SimpleFrame(canv, self.x, self.y, self.width, self.height)
        frame.showBoundary = self.showBoundary
        # terminology difference, must fix
        frame.leftPadding = self.leftMargin
        frame.topPadding = self.topMargin
        frame.rightPadding = self.topMargin
        frame.bottomPadding = self.bottomMargin
        
        #build a story for the frame
        story = []
        for thingy in self.content:
            #ask it for any drawables
            story.append(thingy.getDrawable())
        #draw it
        
        frame.addFromList(story)

        
class PPPara:
    """This is a placeholder for a paragraph."""
    def __init__(self):
        self.rawtext = ''
        self.style = None

    def getDrawable(self):
        return layout.Paragraph(
                    self.rawtext,
                    getStyles()[self.style],
                    self.bulletText
                    )

class PPPreformattedText:
    """Use this for source code, or stuff you wo not want to wrap"""
    def __init__(self):
        self.rawtext = ''
        self.style = None

    def getDrawable(self):
        return layout.Preformatted(self.rawtext, getStyles()[self.style])

class PPImage:
    """Flowing image within the text"""
    def __init__(self):
        self.filename = None
        self.width = None
        self.height = None

    def getDrawable(self):
        return layout.Image(self.filename, self.width, self.height)



    #############################################################
    #
    #   The following are things you can draw on a page directly.
    #
    ##############################################################

class PPDrawingElement:
    """Base class for something which you draw directly on the page."""
    def drawOn(selg, canv):
        raise "NotImplementedError", "Abstract base class!"

        
class PPFixedImage(PPDrawingElement):
    """You place this on the page, rather than flowing it"""
    def __init__(self):
        self.filename = None
        self.x = 0
        self.y = 0
        self.width = None
        self.height = None

    def drawOn(self, canv):
        if self.filename:
            canv.drawInlineImage(
                                self.filename,
                                self.x,
                                self.y,
                                self.width,
                                self.height
                                   )
class PPRectangle:
    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.fillColor = None
        self.strokeColor = (1,1,1)
        self.lineWidth=0

    def drawOn(self, canv):
        canv.saveState()
        canv.setLineWidth(self.lineWidth)
        if self.fillColor:
            r,g,b = self.fillColor
            canv.setFillColorRGB(r,g,b)
        if self.strokeColor:
            r,g,b = self.strokeColor
            canv.setStrokeColorRGB(r,g,b)
        canv.rect(self.x, self.y, self.width, self.height,
                    stroke=(self.strokeColor<>None),
                    fill = (self.fillColor<>None)
                    )
        canv.restoreState()
                                   
class PPRoundRect:
    def __init__(self, x, y, width, height, radius):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.radius = radius
        self.fillColor = None
        self.strokeColor = (1,1,1)
        self.lineWidth=0
        
    def drawOn(self, canv):
        canv.saveState()
        canv.setLineWidth(self.lineWidth)
        if self.fillColor:
            r,g,b = self.fillColor
            canv.setFillColorRGB(r,g,b)
        if self.strokeColor:
            r,g,b = self.strokeColor
            canv.setStrokeColorRGB(r,g,b)
        canv.roundRect(self.x, self.y, self.width, self.height,
                    self.radius,
                    stroke=(self.strokeColor<>None),
                    fill = (self.fillColor<>None)
                    )
        canv.restoreState()

class PPLine:
    def __init__(self, x1, y1, x2, y2):
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2
        self.fillColor = None
        self.strokeColor = (1,1,1)
        self.lineWidth=0
        

    def drawOn(self, canv):
        canv.saveState()
        canv.setLineWidth(self.lineWidth)
        if self.strokeColor:
            r,g,b = self.strokeColor
            canv.setStrokeColorRGB(r,g,b)
        canv.line(self.x1, self.y1, self.x2, self.y2)
        canv.restoreState()

class PPEllipse:
    def __init__(self, x1, y1, x2, y2):
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2
        self.fillColor = None
        self.strokeColor = (1,1,1)
        self.lineWidth=0
        

    def drawOn(self, canv):
        canv.saveState()
        canv.setLineWidth(self.lineWidth)
        if self.strokeColor:
            r,g,b = self.strokeColor
            canv.setStrokeColorRGB(r,g,b)
        if self.fillColor:
            r,g,b = self.fillColor
            canv.setFillColorRGB(r,g,b)
        canv.ellipse(self.x1, self.y1, self.x2, self.y2,
                    stroke=(self.strokeColor<>None),
                    fill = (self.fillColor<>None)
                     )
        canv.restoreState()

class PPPolygon:
    def __init__(self, pointlist):
        self.points = pointlist
        self.fillColor = None
        self.strokeColor = (1,1,1)
        self.lineWidth=0
        

    def drawOn(self, canv):
        canv.saveState()
        canv.setLineWidth(self.lineWidth)
        if self.strokeColor:
            r,g,b = self.strokeColor
            canv.setStrokeColorRGB(r,g,b)

        path = canv.beginPath()
        (x,y) = self.points[0]
        path.moveTo(x,y)
        for (x,y) in self.points[1:]:
            path.lineTo(x,y)
        path.close()
        canv.drawPath(path, stroke=(self.strokeColor<>None))
        canv.restoreState()

    
class PPString:
    def __init__(self, x, y):
        self.text = ''
        self.x = x
        self.y = y
        self.align = layout.TA_LEFT
        self.font = 'Times-Roman'
        self.size = 12
        self.color = (0,0,0)

    def normalizeText(self):
        """It contains literal XML text typed over several lines.
        We want to throw away
        tabs, newlines and so on, and only accept embedded string
        like '\n'"""
        lines = string.split(self.text, '\n')
        newtext = []
        for line in lines:
            newtext.append(string.strip(line))
        #eval turns all the escape sequences into real data
        self.text = eval(string.join(newtext, ' '))
        
    def drawOn(self, canv):
        if self.color is None:
            return
        lines = string.split(string.strip(self.text), '\n')
        canv.saveState()
        canv.setFont(self.font, self.size)
        r,g,b = self.color
        canv.setFillColorRGB(r,g,b)
        cur_y = self.y
        for line in lines:
            if self.align == layout.TA_LEFT:
                canv.drawString(self.x, cur_y, line)
            elif self.align == layout.TA_CENTER:
                canv.drawCentredString(self.x, cur_y, line)
            elif self.align == layout.TA_RIGHT:
                canv.drawRightString(self.x, cur_y, line)
            cur_y = cur_y - 1.2*self.size
                
        canv.restoreState()


def getSampleStyleSheet():
    """Returns a dictionary of styles to get you started.  We will
    provide a way to specify a module of these."""
    stylesheet = {}
    ParagraphStyle = layout.ParagraphStyle
    
    para = ParagraphStyle('Normal', None)   #the ancestor of all
    para.fontName = 'Times-Roman'
    para.fontSize = 24
    para.leading = 28
    stylesheet['Normal'] = para

    #This one is spaced out a bit...
    para = ParagraphStyle('BodyText', stylesheet['Normal'])
    para.spaceBefore = 12
    stylesheet['BodyText'] = para
    
    #Indented, for lists
    para = ParagraphStyle('Indent', stylesheet['Normal'])
    para.leftIndent = 36
    para.firstLineIndent = 36
    stylesheet['Indent'] = para

    para = ParagraphStyle('Centered', stylesheet['Normal'])
    para.alignment = layout.TA_CENTER
    stylesheet['Centered'] = para
    
    para = ParagraphStyle('BigCentered', stylesheet['Normal'])
    para.spaceBefore = 12
    para.alignment = layout.TA_CENTER
    stylesheet['BigCentered'] = para

    para = ParagraphStyle('Italic', stylesheet['BodyText'])
    para.fontName = 'Times-Italic'
    stylesheet['Italic'] = para

    para = ParagraphStyle('Title', stylesheet['Normal'])
    para.fontName = 'Times-Roman'
    para.fontSize = 48
    para.Leading = 58
    para.alignment = layout.TA_CENTER
    stylesheet['Title'] = para
    
    para = ParagraphStyle('Heading1', stylesheet['Normal'])
    para.fontName = 'Times-Bold'
    para.fontSize = 36
    para.leading = 44
    para.alignment = layout.TA_CENTER
    stylesheet['Heading1'] = para
    
    para = ParagraphStyle('Heading2', stylesheet['Normal'])
    para.fontName = 'Times-Bold'
    para.fontSize = 28
    para.leading = 34
    para.spaceBefore = 24
    stylesheet['Heading2'] = para
    
    para = ParagraphStyle('Heading3', stylesheet['Normal'])
    para.fontName = 'Times-BoldItalic'
    para.spaceBefore = 24
    stylesheet['Heading3'] = para

    para = ParagraphStyle('Bullet', stylesheet['Normal'])
    para.firstLineIndent = 40
    para.leftIndent = 80
    para.spaceBefore = 6
    #para.bulletFontName = 'Symbol'
    para.bulletFontSize = 24
    para.bulletIndent = 20
    stylesheet['Bullet'] = para

    para = ParagraphStyle('Definition', stylesheet['Normal'])
    #use this for definition lists
    para.firstLineIndent = 72
    para.leftIndent = 72
    para.bulletIndent = 0
    para.spaceBefore = 12
    para.bulletFontName = 'Helvetica-BoldOblique'
    stylesheet['Definition'] = para

    para = ParagraphStyle('Code', stylesheet['Normal'])
    para.fontName = 'Courier'
    para.fontSize = 16
    para.leading = 18
    para.leftIndent = 36
    stylesheet['Code'] = para

    return stylesheet

#make a singleton and a function to access it        
_styles = None
def getStyles():
    global _styles
    if not _styles:
        _styles = getSampleStyleSheet()
    return _styles

def setStyles(newStyleSheet):
    global _styles
    _styles = newStyleSheet

        
def test():
    p = stdparser.PPMLParser()
    p.feed(sample)
    p.getPresentation().save()
    p.close()

def process(datafilename):
    parser = stdparser.PPMLParser()
    rawdata = open(datafilename).read()
    parser.feed(rawdata)
    pres = parser.getPresentation()
    pres.save()
    parser.close()

if __name__ == '__main__':
    import sys
    if len(sys.argv) > 1:
        datafile = sys.argv[1]
        if os.path.isfile(datafile):
            process(datafile)   #see just above
        else:
            print 'Data file not found:',datafile
    else:
        print """PythonPoint - copyright ReportLab Inc. 1999-2000
usage:
    pythonpoint.py my_presentation.xml

To create the PythonPoint user guide, do:
    pythonpoint.py pythonpoint.xml

Read it, then look at the XML; all should be clear!"""
        