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
#	Revision 1.10  2000/07/11 15:00:39  rgbecker
#	Added end_spacer
#
#	Revision 1.9  2000/07/10 15:25:47  andy_robinson
#	Added tables to PythonPoint
#	
#	Revision 1.8  2000/06/01 15:23:06  rgbecker
#	Platypus re-organisation
#	
#	Revision 1.7  2000/05/16 23:52:38  andy_robinson
#	Bug in Image tag
#	
#	Revision 1.6  2000/05/16 23:48:00  andy_robinson
#	Allowed intra-paragraph text; fixed various bugs
#	
#	Revision 1.5  2000/05/11 13:53:51  rgbecker
#	Change to allow different xmllib
#	
#	Revision 1.4  2000/04/28 17:04:28  andy_robinson
#	Changed to display multiple outline levels
#	
#	Revision 1.3  2000/04/14 12:17:05  rgbecker
#	Splitting layout.py
#	
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

from reportlab.lib import xmllib
import string
import imp
import pythonpoint
from reportlab.lib.enums import TA_LEFT, TA_RIGHT, TA_CENTER, TA_JUSTIFY

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
            'border':'false',
            'leftmargin':'0',  #this is ignored
            'topmargin':'0',  #this is ignored
            'rightmargin':'0',  #this is ignored
            'bottommargin':'0',  #this is ignored
            },
        'slide': {
            'id':'None',
            'title':'None',
            'effectname':'None',   # Split, Blinds, Box, Wipe, Dissolve, Glitter
            'effectdirection':'0',   # 0,90,180,270
            'effectdimension':'H',   # H or V - horizontal or vertical
            'effectmotion':'I',     # Inwards or Outwards
            'effectduration':'1',    #seconds,
            'outlineentry':'None',
            'outlinelevel':'0'       # 1 is a child, 2 is a grandchild etc.
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
        'table': {
            'widths':'None',
            'heights':'None',
            'fieldDelim':',',
            'rowDelim':'\n',
            'style':'None'
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
        #yes, I know a generic stack would be easier...
        #still, testing if we are 'in' something gives
        #a degree of validation.
        self._curPres = None
        self._curSection = None
        self._curSlide = None
        self._curFrame = None
        self._curPara = None  #the only places we are interested in
        self._curPrefmt = None
        self._curString = None
        self._curTable = None
        xmllib.XMLParser.__init__(self)

    def _arg(self,tag,args,name):
        if args.has_key(name):
            v = args[name]
        else:
            if self.attributes.has_key(tag):
                v = self.attributes[tag][name]
            else:
                v = None
        return v

    def ceval(self,tag,args,name):
        if args.has_key(name):
            v = args[name]
        else:
            if self.attributes.has_key(tag):
                v = self.attributes[tag][name]
            else:
                return None
        return eval(v)

    def getPresentation(self):
        return self._curPres
        
    def handle_data(self, data):
        #the only data should be paragraph text, preformatted para
        #text, 'string text' for a fixed string on the page,
        #or table data
        
        if self._curPara:
            self._curPara.rawtext = self._curPara.rawtext + data
        elif self._curPrefmt:
            self._curPrefmt.rawtext = self._curPrefmt.rawtext + data
        elif  self._curString:
            self._curString.text = self._curString.text + data
        elif self._curTable:
            self._curTable.rawBlocks.append(data)
            
    def handle_cdata(self, data):
        #just append to current paragraph text, so we can quote XML
        if self._curPara:
            self._curPara.rawtext = self._curPara.rawtext + data
        if self._curPrefmt:
            self._curPrefmt.rawtext = self._curPrefmt.rawtext + data
        
            
    def start_presentation(self, args):
        #print 'started presentation:', args['filename']
        self._curPres = pythonpoint.PPPresentation()
        self._curPres.filename = self._arg('presentation',args,'filename')
        self._curPres.effectName = self._arg('presentation',args,'effect')

    def end_presentation(self):
        #print 'ended presentation'
        print 'Fully parsed presentation',self._curPres.filename

    def start_stylesheet(self, args):
        #makes it the current style sheet.
        path = self._arg('stylesheet',args,'path')
        if path=='None':
            path = None
        modulename = self._arg('stylesheet',args,'module')
        funcname = self._arg('stylesheet',args,'function')
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

    def start_section(self, args):
        name = self._arg('section',args,'name')
        self._curSection = pythonpoint.PPSection(name)

    def end_section(self):
        self._curSection = None

    def start_slide(self, args):
        s = pythonpoint.PPSlide()
        s.id = self._arg('slide',args,'id')
        s.title = self._arg('slide',args,'title')
        a = self._arg('slide',args,'effectname')
        if a <> 'None': s.effectName = a
        s.effectDirection = self.ceval('slide',args,'effectdirection')
        s.effectDimension = self._arg('slide',args,'effectdimension')
        s.effectMotion = self._arg('slide',args,'effectmotion')


        #HACK - may not belong here in the long run...
        a = self._arg('slide',args,'outlineentry')
        if a <> 'None':
            s.outlineEntry = a
        else:
            s.outlineEntry = s.title
        s.outlineLevel = self.ceval('slide',args,'outlinelevel')
        

        #let it know its section, which may be none
        s.section = self._curSection
        self._curSlide = s
        
    def end_slide(self):
        self._curPres.slides.append(self._curSlide)
        self._curSlide = None

    def start_frame(self, args):
        self._curFrame = pythonpoint.PPFrame(
            self.ceval('frame',args,'x'),
            self.ceval('frame',args,'y'),
            self.ceval('frame',args,'width'),
            self.ceval('frame',args,'height')
            )
        if self._arg('frame',args,'border')=='true':
            self._curFrame.showBoundary = 1

    def end_frame(self):
        self._curSlide.frames.append(self._curFrame)
        self._curFrame = None

    def start_para(self, args):
        self._curPara = pythonpoint.PPPara()
        self._curPara.style = self._arg('para',args,'style')

        # hack - bullet character if bullet style        
        bt = self._arg('para',args,'bullettext')
        if self._curPara.style == 'Bullet' and bt == '':
            bt = '\267'  # Symbol Font bullet character, reasonable default
        self._curPara.bulletText = bt
        
    def end_para(self):
        self._curFrame.content.append(self._curPara)
        self._curPara = None

    def start_prefmt(self, args):
        self._curPrefmt = pythonpoint.PPPreformattedText()
        self._curPrefmt.style = self._arg('prefmt',args,'style')

    def end_prefmt(self):
        self._curFrame.content.append(self._curPrefmt)
        self._curPrefmt = None

    def start_image(self, args):
        self._curImage = pythonpoint.PPImage()
        self._curImage.filename = self._arg('image',args,'filename')
        self._curImage.width = self.ceval('image',args,'width')
        self._curImage.height = self.ceval('image',args,'height')
        
    def end_image(self):
        self._curFrame.content.append(self._curImage)
        self._curImage = None

    def start_table(self, args):
        self._curTable = pythonpoint.PPTable()
        self._curTable.widths = self.ceval('table',args,'widths')
        self._curTable.heights = self.ceval('table',args,'heights')
        #these may contain escapes like tabs - handle with
        #a bit more care.
        if args.has_key('fieldDelim'):
            self._curTable.fieldDelim = eval('"' + args['fieldDelim'] + '"')
        if args.has_key('rowDelim'):
            self._curTable.rowDelim = eval('"' + args['rowDelim'] + '"')
        if args.has_key('style'):
            self._curTable.style = args['style']
        
        
        
    def end_table(self):
        self._curFrame.content.append(self._curTable)
        self._curTable = None

    def start_spacer(self, args):
        """No contents so deal with it here."""
        sp = pythonpoint.PPSpacer()
        sp.height = eval(args['height'])
        self._curFrame.content.append(sp)

    def end_spacer(self):
        pass

    ## the graphics objects - go into either the current section
    ## or the current slide.
    def start_fixedimage(self, args):
        img = pythonpoint.PPFixedImage()
        img.filename = self._arg('fixedimage',args,'filename')
        img.x = self.ceval('fixedimage',args,'x')
        img.y = self.ceval('fixedimage',args,'y')
        img.width = self.ceval('fixedimage',args,'width')
        img.height = self.ceval('fixedimage',args,'height')
        self._curFixedImage = img

    def end_fixedimage(self):
        if self._curSlide:
            self._curSlide.graphics.append(self._curFixedImage)
        elif self._curSection:
            self._curSection.graphics.append(self._curFixedImage)
        self._curFixedImage = None

    def start_rectangle(self, args):
        rect = pythonpoint.PPRectangle(
                    self.ceval('rectangle',args,'x'),
                    self.ceval('rectangle',args,'y'),
                    self.ceval('rectangle',args,'width'),
                    self.ceval('rectangle',args,'height')
                    )
        rect.fillColor = self.ceval('rectangle',args,'fill')
        rect.strokeColor = self.ceval('rectangle',args,'stroke')
        self._curRectangle = rect

    def end_rectangle(self):
        if self._curSlide:
            self._curSlide.graphics.append(self._curRectangle)
        elif self._curSection:
            self._curSection.graphics.append(self._curRectangle)
        self._curRectangle = None

    def start_roundrect(self, args):
        rrect = pythonpoint.PPRoundRect(
                    self.ceval('roundrect',args,'x'),
                    self.ceval('roundrect',args,'y'),
                    self.ceval('roundrect',args,'width'),
                    self.ceval('roundrect',args,'height'),
                    self.ceval('roundrect',args,'radius')
                    )
        rrect.fillColor = self.ceval('roundrect',args,'fill')
        rrect.strokeColor = self.ceval('roundrect',args,'stroke')
        self._curRoundRect = rrect

    def end_roundrect(self):
        if self._curSlide:
            self._curSlide.graphics.append(self._curRoundRect)
        elif self._curSection:
            self._curSection.graphics.append(self._curRoundRect)
        self._curRoundRect = None

    def start_line(self, args):
        self._curLine = pythonpoint.PPLine(
                    self.ceval('line',args,'x1'),
                    self.ceval('line',args,'y1'),
                    self.ceval('line',args,'x2'),
                    self.ceval('line',args,'y2')
                    )
        self._curLine.strokeColor = self.ceval('line',args,'stroke')

    def end_line(self):
        if self._curSlide:
            self._curSlide.graphics.append(self._curLine)
        elif self._curSection:
            self._curSection.graphics.append(self._curLine)
        self._curLine = None

    def start_ellipse(self, args):
        self._curEllipse = pythonpoint.PPEllipse(
                    self.ceval('ellipse',args,'x1'),
                    self.ceval('ellipse',args,'y1'),
                    self.ceval('ellipse',args,'x2'),
                    self.ceval('ellipse',args,'y2')
                    )
        self._curEllipse.strokeColor = self.ceval('ellipse',args,'stroke')
        self._curEllipse.fillColor = self.ceval('ellipse',args,'fill')
        
    def end_ellipse(self):
        if self._curSlide:
            self._curSlide.graphics.append(self._curEllipse)
        elif self._curSection:
            self._curSection.graphics.append(self._curEllipse)
        self._curEllipse = None

    def start_polygon(self, args):
        self._curPolygon = pythonpoint.PPPolygon(self.ceval('polygon',args,'points'))
        self._curPolygon.strokeColor = self.ceval('polygon',args,'stroke')

    def end_polygon(self):
        if self._curSlide:
            self._curSlide.graphics.append(self._curPolygon)
        elif self._curSection:
            self._curSection.graphics.append(self._curPolygon)
        self._curEllipse = None

    def start_string(self, args):
        self._curString = pythonpoint.PPString(
                            self.ceval('string',args,'x'),
                            self.ceval('string',args,'y')
                            )
        self._curString.color = self.ceval('string',args,'color')
        self._curString.font = self._arg('string',args,'font')
        self._curString.size = self.ceval('string',args,'size')
        if args['align'] == 'left':
            self._curString.align = TA_LEFT
        elif args['align'] == 'center':
            self._curString.align = TA_CENTER
        elif args['align'] == 'right':
            self._curString.align = TA_RIGHT
        elif args['align'] == 'justify':
            self._curString.align = TA_JUSTIFY
        #text comes later within the tag
        
    def end_string(self):
        #controller should have set the text
        if self._curSlide:
            self._curSlide.graphics.append(self._curString)
        elif self._curSection:
            self._curSection.graphics.append(self._curString)
        self._curString = None

    def start_customshape(self, args):
        #loads one
        path = self._arg('customshape',args,'path')
        if path=='None':
            path = None
        modulename = self._arg('customshape',args,'module')
        funcname = self._arg('customshape',args,'class')
        found = imp.find_module(modulename, path)
        assert found, "CustomShape %s not found" % modulename
        (file, pathname, description) = found
        mod = imp.load_module(modulename, file, pathname, description)
        
        #now get the function
        
        func = getattr(mod, funcname)
        initargs = self.ceval('customshape',args,'initargs')
        self._curCustomShape = apply(func, initargs)
        
        
    def end_customshape(self):
        if self._curSlide:
            self._curSlide.graphics.append(self._curCustomShape)
        elif self._curSection:
            self._curSection.graphics.append(self._curCustomShape)
        self._curCustomShape = None


    ## intra-paragraph XML should be allowed through into PLATYPUS
    def unknown_starttag(self, tag, attrs):
        if  self._curPara:
            echo = '<%s' % tag
            for (key, value) in attrs.items():
                echo = echo + ' %s="%s"' % (key, value)
            echo = echo + '>'
            self._curPara.rawtext = self._curPara.rawtext + echo
        else:
            print 'Unknown start tag %s' % tag
    def unknown_endtag(self, tag):
        if  self._curPara:
            self._curPara.rawtext = self._curPara.rawtext + '</%s>'% tag
        else:
            print 'Unknown end tag %s' % tag
    
