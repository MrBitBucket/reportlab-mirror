#copyright ReportLab Inc. 2000
#see license.txt for license details
#history http://cvs.sourceforge.net/cgi-bin/cvsweb.cgi/reportlab/demos/pythonpoint/pythonpoint.py?cvsroot=reportlab
#$Header: /tmp/reportlab/reportlab/demos/pythonpoint/Attic/pythonpoint.py,v 1.26 2000/10/25 08:57:44 rgbecker Exp $
__version__=''' $Id: pythonpoint.py,v 1.26 2000/10/25 08:57:44 rgbecker Exp $ '''
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
flowable objects to go in the frames.  These know how to draw
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
        PPTable - bulk formatted tabular data
        PPSpacer

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
from reportlab.platypus import Preformatted, Paragraph, Frame, Image, \
     Table, TableStyle, Spacer
from reportlab.lib.enums import TA_LEFT, TA_RIGHT, TA_CENTER, TA_JUSTIFY
from reportlab.lib import styles
import stdparser 
from reportlab.lib.pagesizes import DEFAULT_PAGE_SIZE
from reportlab.lib import colors

class PPPresentation:
    def __init__(self):
        self.filename = None
        self.description = None
        self.speakerNotes = 0   # different printing mode
        self.slides = []
        self.effectName = None
        self.showOutline = 1   #should it be displayed when opening?
        
        #assume landscape        
        self.pageWidth = DEFAULT_PAGE_SIZE[1]  
        self.pageHeight = DEFAULT_PAGE_SIZE[0]  

    def save(self):
        """This writes out the PDF document"""
        canv = canvas.Canvas(self.filename,
                                pagesize = (self.pageWidth, self.pageHeight)
                               )
        canv.setPageCompression(0)
            
        for slide in self.slides:

            
            if self.speakerNotes:
                #frame and shift the slide
                canv.scale(0.67, 0.67)
                canv.translate(self.pageWidth / 6.0, self.pageHeight / 3.0)
                canv.rect(0,0,self.pageWidth, self.pageHeight)



            slide.drawOn(canv)
            canv.showPage()

        #ensure outline visible by default
        if self.showOutline:
            canv.showOutline()
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
        self.outlineLevel = 0   # can be higher for sub-headings
        self.effectName = None
        self.effectDirection = 0
        self.effectDimension = 'H'
        self.effectMotion = 'I'
        self.effectDuration = 1
        self.frames = []
        self.graphics = []
        self.section = None

    def drawOn(self, canv):
        if self.effectName:
            canv.setPageTransition(
                        effectname=self.effectName,
                        direction = self.effectDirection,
                        dimension = self.effectDimension,
                        motion = self.effectMotion,
                        duration = self.effectDuration
                        )
        if self.outlineEntry:
            #gets an outline automatically
            self.showOutline = 1
            #put an outline entry in the left pane
            tag = self.title
            canv.bookmarkPage(tag)
            canv.addOutlineEntry(tag, tag, self.outlineLevel)
            
            
        
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
        self.showBoundary = 0        

    def drawOn(self, canv):
        #make a frame
        frame = Frame( self.x,
                              self.y,
                              self.width,
                              self.height
                              )
        frame.showBoundary = self.showBoundary
 
        #build a story for the frame
        story = []
        for thingy in self.content:
            #ask it for any flowables
            story.append(thingy.getFlowable())
        #draw it
        frame.addFromList(story,canv)
 
class PPPara:
    """This is a placeholder for a paragraph."""
    def __init__(self):
        self.rawtext = ''
        self.style = None

    def getFlowable(self):
        p = Paragraph(
                    self.rawtext,
                    getStyles()[self.style],
                    self.bulletText
                    )
        return p

class PPPreformattedText:
    """Use this for source code, or stuff you do not want to wrap"""
    def __init__(self):
        self.rawtext = ''
        self.style = None

    def getFlowable(self):
        return Preformatted(self.rawtext, getStyles()[self.style])

class PPImage:
    """Flowing image within the text"""
    def __init__(self):
        self.filename = None
        self.width = None
        self.height = None

    def getFlowable(self):
        return Image(self.filename, self.width, self.height)

class PPTable:
    """Designed for bulk loading of data for use in presentations."""
    def __init__(self):
        self.rawBlocks = [] #parser stuffs things in here...
        self.fieldDelim = ','  #tag args can override
        self.rowDelim = '\n'   #tag args can override
        self.data = None
        self.style = None  #tag args must specify
        self.widths = None  #tag args can override
        self.heights = None #tag args can override

    def getFlowable(self):
        self.parseData()
        t = Table(
				self.data,
                self.widths,
                self.heights)
        if self.style:
            t.setStyle(getStyles()[self.style])

        return t
                
    def parseData(self):
        """Try to make sense of the table data!"""
        rawdata = string.strip(string.join(self.rawBlocks, ''))
        lines = string.split(rawdata, self.rowDelim)
        #clean up...
        lines = map(string.strip, lines)
        self.data = []
        for line in lines:
            cells = string.split(line, self.fieldDelim)
            self.data.append(cells)

        #get the width list if not given
        if not self.widths:
            self.widths = [None] * len(self.data[0])
        if not self.heights:
            self.heights = [None] * len(self.data)
        
    
##        import pprint
##        print 'table data:'
##        print 'style=',self.style
##        print 'widths=',self.widths
##        print 'heights=',self.heights
##        print 'fieldDelim=',repr(self.fieldDelim)
##        print 'rowDelim=',repr(self.rowDelim)
##        pprint.pprint(self.data)

class PPSpacer:
    def __init__(self):
        self.height = 24  #points

    def getFlowable(self):
        return Spacer(72, self.height)

    #############################################################
    #
    #   The following are things you can draw on a page directly.
    #
    ##############################################################

class PPDrawingElement:
    """Base class for something which you draw directly on the page."""
    def drawOn(self, canv):
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
        self.align = TA_LEFT
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
        #accept all the '\n' as newlines
            
        self.text = newtext
        
    def drawOn(self, canv):
        if self.color is None:
            return
        lines = string.split(string.strip(self.text), '\\n')
        canv.saveState()
        canv.setFont(self.font, self.size)
        r,g,b = self.color
        canv.setFillColorRGB(r,g,b)
        cur_y = self.y
        for line in lines:
            if self.align == TA_LEFT:
                canv.drawString(self.x, cur_y, line)
            elif self.align == TA_CENTER:
                canv.drawCentredString(self.x, cur_y, line)
            elif self.align == TA_RIGHT:
                canv.drawRightString(self.x, cur_y, line)
            cur_y = cur_y - 1.2*self.size
                
        canv.restoreState()


def getSampleStyleSheet():
    """Returns a dictionary of styles to get you started.  We will
    provide a way to specify a module of these.  Note that this
    ust includes TableStyles as well as ParagraphStyles for any
    tables you wish to use."""
    stylesheet = {}
    ParagraphStyle = styles.ParagraphStyle
    
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
    para.alignment = TA_CENTER
    stylesheet['Centered'] = para
    
    para = ParagraphStyle('BigCentered', stylesheet['Normal'])
    para.spaceBefore = 12
    para.alignment = TA_CENTER
    stylesheet['BigCentered'] = para

    para = ParagraphStyle('Italic', stylesheet['BodyText'])
    para.fontName = 'Times-Italic'
    stylesheet['Italic'] = para

    para = ParagraphStyle('Title', stylesheet['Normal'])
    para.fontName = 'Times-Roman'
    para.fontSize = 48
    para.Leading = 58
    para.alignment = TA_CENTER
    stylesheet['Title'] = para
    
    para = ParagraphStyle('Heading1', stylesheet['Normal'])
    para.fontName = 'Times-Bold'
    para.fontSize = 36
    para.leading = 44
    para.alignment = TA_CENTER
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

    para = ParagraphStyle('Heading4', stylesheet['Normal'])
    para.fontName = 'Times-BoldItalic'
    para.spaceBefore = 6
    stylesheet['Heading4'] = para

    para = ParagraphStyle('Bullet', stylesheet['Normal'])
    para.firstLineIndent = 40
    para.leftIndent = 56
    para.spaceBefore = 6
    para.bulletFontName = 'Symbol'
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
    para.bulletFontSize = 24
    stylesheet['Definition'] = para

    para = ParagraphStyle('Code', stylesheet['Normal'])
    para.fontName = 'Courier'
    para.fontSize = 16
    para.leading = 18
    para.leftIndent = 36
    stylesheet['Code'] = para

    para = ParagraphStyle('Small', stylesheet['Normal'])
    para.fontSize = 12
    para.leading = 14
    stylesheet['Small'] = para

    #now for a table
    ts = TableStyle([
         ('FONT', (0,0), (-1,-1), 'Times-Roman', 24),
         ('LINEABOVE', (0,0), (-1,0), 2, colors.green),
         ('LINEABOVE', (0,1), (-1,-1), 0.25, colors.black),
         ('LINEBELOW', (0,-1), (-1,-1), 2, colors.green),
         ('LINEBEFORE', (-1,0), (-1,-1), 2, colors.black),
         ('ALIGN', (1,1), (-1,-1), 'RIGHT'),   #all numeric cells right aligned
         ('TEXTCOLOR', (0,1), (0,-1), colors.red),
         ('BACKGROUND', (0,0), (-1,0), colors.Color(0,0.7,0.7))
         ])
    stylesheet['table1'] = ts

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

def process(datafilename, speakerNotes=0):
    parser = stdparser.PPMLParser()
    rawdata = open(datafilename).read()
    parser.feed(rawdata)
    pres = parser.getPresentation()
    pres.speakerNotes = speakerNotes
    pres.save()
    print 'saved presentation %s.pdf' % os.path.splitext(datafilename)[0]
    parser.close()

if __name__ == '__main__':
    import sys
    #see if there is a '/n' argument
    speakernotes = 0
    for arg in sys.argv:
        if arg in ['/n','/no','/not','/note','/notes']:
            speakernotes = 1
            sys.argv.remove(arg)
            print 'speaker notes mode'
            
    if len(sys.argv) == 1 and os.path.isfile('pythonpoint.xml'):
		sys.argv.append('pythonpoint.xml')
    if len(sys.argv) == 1:
        print """PythonPoint - copyright ReportLab Inc. 1999-2000
usage:
    pythonpoint.py my_presentation.xml

To create the PythonPoint user guide, do:
    pythonpoint.py pythonpoint.xml

Read it, then look at the XML; all should be clear!"""
    else:
        for datafile in sys.argv[1:]:
            if os.path.isfile(datafile):
                process(datafile, speakernotes)   #see just above
            else:
                print 'Data file not found:', datafile
