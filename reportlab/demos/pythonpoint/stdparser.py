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
#	$Log: stdparser.py,v $
#	Revision 1.2  2000/04/06 12:15:38  andy_robinson
#	Updated example XML to include full tag reference
#
#	Revision 1.1  2000/04/06 09:47:20  andy_robinson
#	Added several new shape tags.
#	Broke out parser into separate module, to
#	allow for alternative parsers in future.
#	Broke out 'user guide' into pythonpoint.xml
#	
#	
__version__=''' $Id $ '''
__doc__="""
Parser for PythonPoint using the xmllib.py in the standard Python
distribution.  Slow, but always present.  We intend to add new parsers
as Python 1.6 and the xml package spread in popularity.

The parser has a getPresentation method; it is called from
pythonpoint.py.
"""

import xmllib
import string
import imp
import pythonpoint
from reportlab.platypus import layout

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
            'effectduration':'1',    #seconds,
            'outlineEntry':'None'
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
            'stroke':'(0,0,0)',
            'linewidth':'0'
            },
        'roundrect': {
            'x':'0',
            'y':'0',
            'width':'100',
            'height':'100',
            'radius':'6',
            'fill':'None',
            'stroke':'(0,0,0)',
            'linewidth':'0'
            
            },
        'line': {
            'x1':'0',
            'y1':'0',
            'x2':'100',
            'y2':'100',
            'stroke':'(0,0,0)',
            'width':'0'
            
            },
        'ellipse': {
            'x1':'0',
            'y1':'0',
            'x2':'100',
            'y2':'100',
            'stroke':'(0,0,0)',
            'fill':'None',
            'linewidth':'0'
            
            },
        'polygon': {
            'points':'(0,0),(50,0),(25,25)',
            'stroke':'(0,0,0)',
            'linewidth':'0',
            'stroke':'(0,0,0)',
            'fill':'None'
            
            },
        'string':{
            'x':'0',
            'y':'0',
            'color':'(0,0,0)',
            'font':'Times-Roman',
            'size':'12',
            'align':'left'
            },
        'customshape':{
            'path':'None',
            'module':'None',
            'class':'None',
            'initargs':'None'
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
        self._curString = None
        xmllib.XMLParser.__init__(self)

    def getPresentation(self):
        return self._curPres
        
    def handle_data(self, data):
        #the only data should be paragraph text, preformatted para
        #text, or 'string text' for a fixed string on the page
        
        if self._curPara:
            self._curPara.rawtext = self._curPara.rawtext + data
        elif self._curPrefmt:
            self._curPrefmt.rawtext = self._curPrefmt.rawtext + data
        elif  self._curString:
            self._curString.text = self._curString.text + data
            
    def handle_cdata(self, data):
        #just append to current paragraph text, so we can quote XML
        if self._curPara:
            self._curPara.rawtext = self._curPara.rawtext + data
        if self._curPrefmt:
            self._curPrefmt.rawtext = self._curPrefmt.rawtext + data
        
            
    def start_presentation(self, args):
        #print 'started presentation:', args['filename']
        self._curPres = pythonpoint.PPPresentation()
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
        pythonpoint.setStyles(func())
        print 'set global stylesheet to %s.%s()' % (modulename, funcname)
        
    def end_stylesheet(self):
        pass

    def start_section(self, attributes):
        name = attributes['name']
        self._curSection = pythonpoint.PPSection(name)

    def end_section(self):
        self._curSection = None

    def start_slide(self, args):
        s = pythonpoint.PPSlide()
        s.id = args['id']
        s.title = args['title']
        if args['effectname'] <> 'None':
            s.effectName = args['effectname']
        s.effectDirection = string.atoi(args['effectdirection'])
        s.effectDimension = args['effectdimension']
        s.effectMotion = args['effectmotion']


        #HACK - may not belong here in the long run...
        if args['outlineEntry'] <> 'None':
            s.outlineEntry = args['outlineEntry']
        

        #let it know its section, which may be none
        s.section = self._curSection
        self._curSlide = s
        
    def end_slide(self):
        self._curPres.slides.append(self._curSlide)
        self._curSlide = None

    def start_frame(self, args):
        self._curFrame = pythonpoint.PPFrame(
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
        self._curPara = pythonpoint.PPPara()
        self._curPara.style = args['style']
        # hack - we want to allow octal escape sequences in the input -
        # treat as raw string and evaluate
        self._curPara.bulletText = args['bullettext']
        
    def end_para(self):
        self._curFrame.content.append(self._curPara)
        self._curPara = None

    def start_prefmt(self, args):
        self._curPrefmt = pythonpoint.PPPreformattedText()
        self._curPrefmt.style = args['style']

    def end_prefmt(self):
        self._curFrame.content.append(self._curPrefmt)
        self._curPrefmt = None

    def start_image(self, args):
        self._curImage = pythonpoint.PPImage()
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
        img = pythonpoint.PPFixedImage()
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
        rect = pythonpoint.PPRectangle(
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

    def start_roundrect(self, args):
        rrect = pythonpoint.PPRoundRect(
                    eval(args['x']),
                    eval(args['y']),
                    eval(args['width']),
                    eval(args['height']),
                    eval(args['radius'])
                    )
        self._curRoundRect = rrect
        self._curRoundRect.fillColor = eval(args['fill'])
        self._curRoundRect.strokeColor = eval(args['stroke'])

    def end_roundrect(self):
        if self._curSlide:
            self._curSlide.graphics.append(self._curRoundRect)
        elif self._curSection:
            self._curSection.graphics.append(self._curRoundRect)
        self._curRoundRect = None

    def start_line(self, args):
        self._curLine = pythonpoint.PPLine(
                    eval(args['x1']),
                    eval(args['y1']),
                    eval(args['x2']),
                    eval(args['y2'])
                    )
        self._curLine.strokeColor = eval(args['stroke'])

    def end_line(self):
        if self._curSlide:
            self._curSlide.graphics.append(self._curLine)
        elif self._curSection:
            self._curSection.graphics.append(self._curLine)
        self._curLine = None

    def start_ellipse(self, args):
        self._curEllipse = pythonpoint.PPEllipse(
                    eval(args['x1']),
                    eval(args['y1']),
                    eval(args['x2']),
                    eval(args['y2'])
                    )
        self._curEllipse.strokeColor = eval(args['stroke'])
        self._curEllipse.fillColor = eval(args['fill'])
        
    def end_ellipse(self):
        if self._curSlide:
            self._curSlide.graphics.append(self._curEllipse)
        elif self._curSection:
            self._curSection.graphics.append(self._curEllipse)
        self._curEllipse = None

    def start_polygon(self, args):
        self._curPolygon = pythonpoint.PPPolygon(eval(args['points']))
        self._curPolygon.strokeColor = eval(args['stroke'])

    def end_polygon(self):
        if self._curSlide:
            self._curSlide.graphics.append(self._curPolygon)
        elif self._curSection:
            self._curSection.graphics.append(self._curPolygon)
        self._curEllipse = None

    def start_string(self, args):
        self._curString = pythonpoint.PPString(
                            eval(args['x']),
                            eval(args['y'])
                            )
        self._curString.color = eval(args['color'])
        self._curString.font = args['font']
        self._curString.size = eval(args['size'])
        if args['align'] == 'left':
            self._curString.align = layout.TA_LEFT
        elif args['align'] == 'center':
            self._curString.align = layout.TA_CENTER
        elif args['align'] == 'right':
            self._curString.align = layout.TA_RIGHT
        #text comes later within the tag
        
    def end_string(self):
        #controller should have set the text
        if self._curSlide:
            self._curSlide.graphics.append(self._curString)
        elif self._curSection:
            self._curSection.graphics.append(self._curString)
        self._curString = None

    def start_customshape(self, attributes):
        #loads one
        path = attributes['path']
        if path=='None':
            path = None
        modulename = attributes['module']
        funcname = attributes['class']
        found = imp.find_module(modulename, path)
        assert found, "CustomShape %s not found" % modulename
        (file, pathname, description) = found
        mod = imp.load_module(modulename, file, pathname, description)
        
        #now get the function
        
        func = getattr(mod, funcname)
        initargs = eval(attributes['initargs'])
        self._curCustomShape = apply(func, initargs)
        
        
    def end_customshape(self):
        if self._curSlide:
            self._curSlide.graphics.append(self._curCustomShape)
        elif self._curSection:
            self._curSection.graphics.append(self._curCustomShape)
        self._curCustomShape = None
