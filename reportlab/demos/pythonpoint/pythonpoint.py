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
__version__=''' $Id: pythonpoint.py,v 1.4 2000/02/17 02:06:28 rgbecker Exp $ '''
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

The parser turns the XML sample into an object tree.  There is a
simple class hierarchy of items, the inner levels of which create
drawable objects to go in the frames.

"""

import os
import string
import xmllib
import pprint
import imp

from reportlab.pdfgen import canvas
from reportlab.platypus import layout

sample = """
<presentation filename='pythonpoint.pdf'>
  <section name = 'Main'>
  	<!-- any graphics in the scetion go on all its paages as a backdrop -->
    <rectangle x="20" y="510" width="800" height="65" fill="(0,0,1)"/>
    <rectangle x="20" y="20" width="65" height="555" fill="(0,0,1)"/>
        
    <slide id="Slide001" title="My First Slide" effectname='Wipe'>
        <frame x="96" y="72" width="700" height="432" leftmargin="36" rightmargin="36">
            <para style='Heading1'>Welcome to PythonPoint</para>
            <para style='BodyText'>...a library for creating presentation slides.</para>
            <para style='BodyText'>
                PythonPoint lets you create attractive and consistent presentation slides
                on any platform.  It is a demo app built on top of the PDFgen PDF library
                and the PLATYPUS Page Layout library.  Essentially, it converts slides
                in an XML format to PDF.
            </para>
        </frame>
    </slide>
    <slide id="Slide002" title="XML Notation" effectname='Blinds' effectdirection='0'>
        <frame x="96" y="72" width="700" height="432" leftmargin="36" rightmargin="36">
            <para style='Heading1'>XML Notation</para>
            <para style='BodyText'>You create slides in a text editor with 
				a basic XML	syntax looking like this:
			</para>
            <prefmt style='Code'><![CDATA[
<frame x="160" y="72" width="600" height="432"
    leftmargin="36" rightmargin="36">
    <para style='Heading1'>
        Welcome to PythonPoint
    </para>
    <para style='BodyText'>
        ...a library for creating presentation slides.
    </para>
</frame>        ]]>
            </prefmt>
            <para style='BodyText'>Pythonpoint then converts these into slides.  Just enter
				"pythonpoint.py myfile.xml" to create a PDF document (usually called "myfile.pdf").
			</para>

			
        </frame>
    </slide>

    <slide id="Slide003" title="Page Layout" effectname='Box'>
        <frame x="96" y="72" width="700" height="432" leftmargin="36" rightmargin="36" border='true'>
            <para style='Heading1'>Page Layout Model</para>
            <para style='BodyText'>
                The Page Layout model comes from PLATYPUS (Page Layout and Typography Using Scripts),
                a key component of the toolkit.  This covers concepts such as:
            </para>
            <para style='Bullet' bullettext = '¥'>Reusable 'Drawable Objects'</para>
            <para style='Bullet' bullettext = '¥'>Frames into which objects flow (like this)</para>
            <para style='Bullet' bullettext = '¥'>Style Sheets for text, table cells, line styles etc.</para>
            <para style='Bullet' bullettext = '¥'>Wrapping, page breaking an document management logic</para>
            <para style='BodyText'>Everything is open and extensible.  I hope a library of reusable objects
            such as charts and diagrams will grow up.</para>
        </frame>
    </slide>

    <slide id="Slide004" title="Reuse" effectname='Wipe'>
        <frame x="96" y="72" width="700" height="432" leftmargin="36" rightmargin="36">
            <para style='Heading1'>Reuse and Consistency - Sections</para>
            <para style='BodyText'>
				You can create a 'section' spanning some or all tags in the presentation and place graphics
				on this.  The blue border and title come from the section.  Here's how we did the border:
			</para>
			<prefmt style='Code'><![CDATA[
<presentation filename='pythonpoint.pdf'>
  <section name = 'Main'>
  	<!-- any graphics in the section go on all its pages as a backdrop -->
    <rectangle x="20" y="510" width="800" height="65" fill="(0,0,1)"/>
    <rectangle x="20" y="20" width="65" height="555" fill="(0,0,1)"/>
	...all slides go here...
  </section>
</presentation>	]]>
           
			</prefmt>
			<para style='BodyText'> Thus you can re-brand an entire
				presentation for a  new audience in seconds.
            </para>
		</frame>
	</slide>

    <slide id="Slide005" title="Styles" effectname='Dissolve'>
        <frame x="96" y="72" width="700" height="432" leftmargin="36" rightmargin="36">
            <para style='Heading1'>Style Sheets</para>
            <para style='BodyText'>
                Paragraph styles are defined externally.  You may specify a filename
				from which to load a stylesheet with the stylesheet tag.
            </para>
            <para style='BodyText'>
				Thus you can have different sizes and formats by switching stylesheets,
				or colour and black-and-white options.
            </para>
			<para style='BodyText'>
				When they are added, tables will be driven by line and cell styles in a 
				similar way.
            </para>
			
        </frame>
    </slide>
	
    <slide id="Slide006" title="Special Effects" effectname='Dissolve'>
        <frame x="96" y="72" width="700" height="432" leftmargin="36" rightmargin="36">
            <para style='Heading1'>Special Effects</para>
            <para style='BodyText'>
                Acrobat Reader supports tags to define page transition effects.  If you
				are reading this on screen, you should have seen a selection of these:
            </para>
	        <para style='Bullet' bullettext = '¥'>Split</para>
	        <para style='Bullet' bullettext = '¥'>Blinds</para>
	        <para style='Bullet' bullettext = '¥'>Box</para>
	        <para style='Bullet' bullettext = '¥'>Wipe</para>
	        <para style='Bullet' bullettext = '¥'>Dissolve</para>
	        <para style='Bullet' bullettext = '¥'>Glitter</para>
    		<para style='BodyText'>
				Each has a range of options to fine-tune.
            </para>
			<para style='BodyText'>
				When they are added, tables will be driven by line and cell styles in a 
				similar way.
            </para>
			
        </frame>
    </slide>
	
	<slide id="Slide007" title="Future Features" effectname='Glitter'>
        <frame x="96" y="72" width="700" height="432" leftmargin="36" rightmargin="36">
            <para style='Heading1'>Features Coming Soon</para>
            <para style='BodyText'>
                This is the first version that runs.  A lot can now be added fairly easily:
            </para>
            <para style='Bullet' bullettext = '¥'>Preprocessor to let you enter paragraphs 
				and bullets as one block of text, with less tag typing!</para>
            <para style='Bullet' bullettext = '¥'>PIDDLE drawings</para>
            <para style='Bullet' bullettext = '¥'>Inline images within the frames</para>
            <para style='Bullet' bullettext = '¥'>'Object Graphics' tags with grouping and coordinate transformations</para>
            <para style='Bullet' bullettext = '¥'>Speaker notes and a mode to print them</para>
            <para style='Bullet' bullettext = '¥'>Tools to archive slides in a database and build presentations to order</para>
            <para style='Italic' bullettext = '¥'>...what else can YOU think of?</para>
        </frame>
    </slide>

  </section>
</presentation>
"""

class PPMLParser(xmllib.XMLParser):
    attributes = {
        #this defines the available attributes for all objects,
        #and their default values.  Although these don't have to
        #be strings, the ones parsed from the XML do, so
        #everything is a quoted string and the parser has to
        #convert these to numbers where appropriate.
        'stylesheet': {
            'path':'None',
            'module':'None',
            'function':'getParagraphStyles'
            },
        'frame': {
            'x':'0',
            'y':'0',
            'width':'0',
            'height':'0',
            'leftmargin':'0',
            'rightmargin':'0',
            'topmargin':'0',
            'bottommargin':'0',
            'border':'false'
            },
        'slide': {
            'id':'None',
            'title':'None',
            'effectname':'None',   # Split, Blinds, Box, Wipe, Dissolve, Glitter
            'effectdirection':'0',   # 0,90,180,270
            'effectdimension':'H',   # H or V - horizontal or vertical
            'effectmotion':'I',     # Inwards or Outwards
            'effectduration':'1'    #seconds
            },
        'para': {
            'style':'Normal',
            'bullettext':''
            },
        'image': {
            'filename':'',
            'width':'None',
            'height':'None'
            },
        'rectangle': {
            'x':'0',
            'y':'0',
            'width':'100',
            'height':'100',
            'fill':'None',
            'stroke':'None'
            }
        }
    
    def __init__(self):
        self.presentations = []
        self._curPres = None
        self._curSection = None
        self._curSlide = None
        self._curFrame = None
        self._curPara = None  #the only places we are interested in
        self._curPrefmt = None
        xmllib.XMLParser.__init__(self)

    def getPresentation(self):
        return self._curPres
        
    def handle_data(self, data):
        #the only data should be paragraph text
        if self._curPara:
            self._curPara.rawtext = self._curPara.rawtext + data
        if self._curPrefmt:
            self._curPrefmt.rawtext = self._curPrefmt.rawtext + data
            
    def handle_cdata(self, data):
        #just append to current paragraph text, so we can quote XML
        if self._curPara:
            self._curPara.rawtext = self._curPara.rawtext + data
        if self._curPrefmt:
            self._curPrefmt.rawtext = self._curPrefmt.rawtext + data
        
            
    def start_presentation(self, args):
        #print 'started presentation:', args['filename']
        self._curPres = PPPresentation()
        self._curPres.filename = args['filename']
        if args.has_key('effect'):
            self._curPres.effectName = args['effect']

    def end_presentation(self):
        #print 'ended presentation'
        print 'Fully parsed presentation',self._curPres.filename

    def start_stylesheet(self, attributes):
        #makes it the current style sheet.
        path = attributes['path']
        if path=='None':
            path = None
        modulename = attributes['module']
        funcname = attributes['function']
        found = imp.find_module(modulename, path)
        assert found, "StyleSheet %s not found" % modulename
        (file, pathname, description) = found
        mod = imp.load_module(modulename, file, pathname, description)
        
        #now get the function
        func = getattr(mod, funcname)
        setStyles(func())
        print 'set global stylesheet to %s.%s()' % (modulename, funcname)
        
    def end_stylesheet(self):
        pass

    def start_section(self, attributes):
        name = attributes['name']
        self._curSection = PPSection(name)

    def end_section(self):
        self._curSection = None

    def start_slide(self, args):
        s = PPSlide()
        s.id = args['id']
        s.title = args['title']
        if args['effectname'] <> 'None':
            s.effectName = args['effectname']
        s.effectDirection = string.atoi(args['effectdirection'])
        s.effectDimension = args['effectdimension']
        s.effectMotion = args['effectmotion']

        #let it know its section, which may be none
        s.section = self._curSection
        self._curSlide = s
        
    def end_slide(self):
        self._curPres.slides.append(self._curSlide)
        self._curSlide = None

    def start_frame(self, args):
        self._curFrame = PPFrame(
            string.atof(args['x']),
            string.atof(args['y']),
            string.atof(args['width']),
            string.atof(args['height'])
            )
        self._curFrame.leftMargin = string.atof(args['leftmargin'])
        self._curFrame.topMargin = string.atof(args['topmargin'])
        self._curFrame.rightMargin = string.atof(args['rightmargin'])
        self._curFrame.bottomMargin = string.atof(args['bottommargin'])
        if args['border']=='true':
            self._curFrame.showBoundary = 1

    def end_frame(self):
        self._curSlide.frames.append(self._curFrame)
        self._curFrame = None

    def start_para(self, args):
        self._curPara = PPPara()
        self._curPara.style = args['style']
        self._curPara.bulletText = args['bullettext']

    def end_para(self):
        self._curFrame.content.append(self._curPara)
        self._curPara = None

    def start_prefmt(self, args):
        self._curPrefmt = PPPreformattedText()
        self._curPrefmt.style = args['style']

    def end_prefmt(self):
        self._curFrame.content.append(self._curPrefmt)
        self._curPrefmt = None

    def start_image(self, args):
        self._curImage = PPImage()
        self._curImage.filename = args['filename']
        if args['width'] <> 'None':
            self._curImage.width = string.atof(args['width'])
        if args['height'] <> 'None':
            self._curImage.height = string.atof(args['height'])
        
    def end_image(self):
        self._curFrame.content.append(self._curImage)
        self._curImage = None


    ## the graphics objects - go into either the current section
    ## or the current slide.
    def start_fixedimage(self, args):
        img = PPFixedImage()
        img.filename = args['filename']
        img.x = eval(args['x'])
        img.y = eval(args['y'])
        img.width = eval(args['width'])
        img.height = eval(args['height'])
        self._curFixedImage = img

    def end_fixedimage(self):
        if self._curSlide:
            self._curSlide.graphics.append(self._curFixedImage)
        elif self._curSection:
            self._curSection.graphics.append(self._curFixedImage)
        self._curFixedImage = None

    def start_rectangle(self, args):
        rect = PPRectangle(
                    eval(args['x']),
                    eval(args['y']),
                    eval(args['width']),
                    eval(args['height'])
                    )
        self._curRectangle = rect
        self._curRectangle.fillColor = eval(args['fill'])
        self._curRectangle.strokeColor = eval(args['stroke'])

    def end_rectangle(self):
        if self._curSlide:
            self._curSlide.graphics.append(self._curRectangle)
        elif self._curSection:
            self._curSection.graphics.append(self._curRectangle)
        self._curRectangle = None


        
class PPPresentation:
    def __init__(self):
        self.filename = None
        self.description = None
        self.slides = []
        self.effectName = None
        
        #assume landscape        
        self.pageWidth = layout.DEFAULT_PAGE_SIZE[1]  
        self.pageHeight = layout.DEFAULT_PAGE_SIZE[0]  

    def save(self):
        """This writes out the PDF document"""
        canv = canvas.Canvas(self.filename,
                                pagesize = (self.pageWidth, self.pageHeight)
                               )
        canv.setPageCompression(0)
            
        for slide in self.slides:
            slide.drawOn(canv)
            canv.showPage()
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

class PPImage:
    """Flowing image within the text"""
    def __init__(self):
        self.filename = None
        self.width = None
        self.height = None

    def getDrawable(self):
        return layout.Image(self.filename, self.width, self.height)


class PPDrawingElement:
    """Base class for something which you draw directly on the page."""
    def drawOn(selg, canv):
        raise "NotImplementedError", "Abstract base class!"

class PPRectangle:
    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.fillColor = None
        self.strokeColor = (1,1,1)

    def drawOn(self, canv):
        canv.saveState()
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
                                   

class PPPreformattedText:
    """Use this for source code, or stuff you wo not want to wrap"""
    def __init__(self):
        self.rawtext = ''
        self.style = None

    def getDrawable(self):
        return layout.Preformatted(self.rawtext, getStyles()[self.style])



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

    para = ParagraphStyle('BodyText', stylesheet['Normal'])
    para.spaceBefore = 12
    stylesheet['BodyText'] = para
    
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
    para.spaceAfter = 36
    para.alignment = layout.TA_CENTER
    stylesheet['Title'] = para
    
    para = ParagraphStyle('Heading1', stylesheet['Normal'])
    para.fontName = 'Times-Bold'
    para.fontSize = 36
    para.leading = 44
    para.spaceAfter = 36
    para.alignment = layout.TA_CENTER
    stylesheet['Heading1'] = para
    
    para = ParagraphStyle('Heading2', stylesheet['Normal'])
    para.fontName = 'Times-Bold'
    para.fontSize = 28
    para.leading = 34
    para.spaceBefore = 24
    para.spaceAfter = 12
    stylesheet['Heading2'] = para
    
    para = ParagraphStyle('Heading3', stylesheet['Normal'])
    para.fontName = 'Times-BoldItalic'
    para.spaceBefore = 24
    para.spaceAfter = 12
    stylesheet['Heading3'] = para

    para = ParagraphStyle('Bullet', stylesheet['Normal'])
    para.firstLineIndent = 40
    para.leftIndent = 80
    para.spaceBefore = 6
    #para.bulletFontName = 'Symbol'
    para.bulletFontSize = 24
    para.bulletIndent = 36
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
    p = PPMLParser()
    p.feed(sample)
    p.getPresentation().save()

def process(datafilename):
    parser = PPMLParser()
    rawdata = open(datafilename).read()
    parser.feed(rawdata)
    pres = parser.getPresentation()
    pres.save()


if __name__ == '__main__':
    import sys
    if len(sys.argv) > 1:
        datafile = sys.argv[1]
        if os.path.isfile(datafile):
            process(datafile)   #see just above
        else:
            print 'Data file not found:',datafile
    else:
        print "Creating demo file pythonpoint.pdf"
        test()
    
