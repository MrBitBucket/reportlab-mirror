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
#	$Log: layout.py,v $
#	Revision 1.8  2000/04/06 09:52:02  andy_robinson
#	Removed some old comments; tweaks to experimental Outline methods.
#
#	Revision 1.7  2000/03/08 13:06:39  andy_robinson
#	Moved inch and cm definitions to reportlab.lib.units and amended all demos
#	
#	Revision 1.6  2000/02/23 10:53:33  rgbecker
#	GMCM's memleak fixed
#	
#	Revision 1.5  2000/02/17 02:09:05  rgbecker
#	Docstring & other fixes
#	
#	Revision 1.4  2000/02/16 09:42:50  rgbecker
#	Conversion to reportlab package
#	
#	Revision 1.3  2000/02/15 17:55:59  rgbecker
#	License text fixes
#	
#	Revision 1.2  2000/02/15 15:47:09  rgbecker
#	Added license, __version__ and Logi comment
#	
__version__=''' $Id: layout.py,v 1.8 2000/04/06 09:52:02 andy_robinson Exp $ '''
__doc__="""
Page Layout And TYPography Using Scripts
a page layout API on top of PDFgen
currently working on paragraph wrapping stuff.
"""

# 200-10-13 gmcm
#   packagizing
#   rewrote grid stuff - now in tables.py

import string
import types

from reportlab.pdfbase import pdfmetrics
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch


DEFAULT_PAGE_SIZE = (595.27,841.89)
PAGE_HEIGHT = DEFAULT_PAGE_SIZE[1]
TA_LEFT = 0
TA_CENTER = 1
TA_RIGHT = 2
TA_JUSTIFY = 4




###########################################################
#
#   Styles.  This class provides an 'instance inheritance'
# mechanism for its desecndants, simpler than acquisition
# but not as far-reaching
###########################################################

class PropertySet:
    defaults = {}

    def __init__(self, name, parent=None):
        self.name = name
        self.parent = parent
        self.attributes = {}

    def __setattr__(self, key, value):
        if self.defaults.has_key(key):
            self.attributes[key] = value
        else:
            self.__dict__[key] = value

    def __getattr__(self, key):
        if self.defaults.has_key(key):
            if self.attributes.has_key(key):
                found = self.attributes[key]
            elif self.parent:
                found = getattr(self.parent, key)
            else:  #take the class default
                found = self.defaults[key]
        else:
            found = self.__dict__[key]
        return found

    def __repr__(self):
        return "<%s '%s'>" % (self.__class__.__name__, self.name)

    def listAttrs(self):
        print 'name =', self.name
        print 'parent =', self.parent
        keylist = self.defaults.keys()
        keylist.sort()
        for key in keylist:
            value = self.attributes.get(key, None)
            if value:
                print '%s = %s (direct)' % (key, value)
            else: #try for inherited
                value = getattr(self.parent, key, None)
                if value:
                    print '%s = %s (inherited)' % (key, value)
                else:
                    value = self.defaults[key]
                    print '%s = %s (class default)' % (key, value)



class ParagraphStyle(PropertySet):
    defaults = {
        'fontName':'Times-Roman',
        'fontSize':10,
        'leading':12,
        'leftIndent':0,
        'rightIndent':0,
        'firstLineIndent':0,
        'alignment':TA_LEFT,
        'spaceBefore':0,
        'spaceAfter':0,
        'bulletFontName':'Times-Roman',
        'bulletFontSize':10,
        'bulletIndent':0
        }

class LineStyle(PropertySet):
    defaults = {
        'width':1,
        'color': (0,0,0)
        }
    def prepareCanvas(self, canvas):
        """You can ask a LineStyle to set up the canvas for drawing
        the lines."""
        canvas.setLineWidth(1)
        #etc. etc.

class CellStyle(PropertySet):
    defaults = {
        'fontname':'Times-Roman',
        'fontsize':10,
        'leading':12,
        'leftPadding':6,
        'rightPadding':6,
        'topPadding':3,
        'bottomPadding':3,
        'firstLineIndent':0,
        'color':(1,1,1),
        'alignment': 'LEFT',
        }

def testStyles():
    pNormal = ParagraphStyle('Normal',None)
    pNormal.fontName = 'Times-Roman'
    pNormal.fontSize = 12
    pNormal.leading = 14.4

    pNormal.listAttrs()
    print
    pPre = ParagraphStyle('Literal', pNormal)
    pPre.fontName = 'Courier'
    pPre.listAttrs()
    return pNormal, pPre

def getSampleStyleSheet():
    """Returns a dictionary of styles to get you started.  Should be
    usable for fairly basic word processing tasks.  We should really have
    a class for StyleSheets, which can list itself and avoid the
    duplication of item names seen below."""
    stylesheet = {}

    para = ParagraphStyle('Normal', None)   #the ancestor of all
    para.fontName = 'Times-Roman'
    para.fontSize = 10
    para.leading = 12
    stylesheet['Normal'] = para

    para = ParagraphStyle('BodyText', stylesheet['Normal'])
    para.spaceBefore = 6
    stylesheet['BodyText'] = para

    para = ParagraphStyle('Italic', stylesheet['BodyText'])
    para.fontName = 'Times-Italic'
    stylesheet['Italic'] = para

    para = ParagraphStyle('Heading1', stylesheet['Normal'])
    para.fontName = 'Times-Bold'
    para.fontSize = 18
    para.spaceAfter = 6
    stylesheet['Heading1'] = para

    para = ParagraphStyle('Heading2', stylesheet['Normal'])
    para.fontName = 'Times-Bold'
    para.fontSize = 14
    para.spaceBefore = 12
    para.spaceAfter = 6
    stylesheet['Heading2'] = para

    para = ParagraphStyle('Heading3', stylesheet['Normal'])
    para.fontName = 'Times-BoldItalic'
    para.fontSize = 12
    para.spaceBefore = 12
    para.spaceAfter = 6
    stylesheet['Heading3'] = para

    para = ParagraphStyle('Bullet', stylesheet['Normal'])
    para.firstLineIndent = 36
    para.leftIndent = 36
    para.spaceBefore = 3
    stylesheet['Bullet'] = para

    para = ParagraphStyle('Definition', stylesheet['Normal'])
    #use this for definition lists
    para.firstLineIndent = 36
    para.leftIndent = 36
    para.bulletIndent = 0
    para.spaceBefore = 6
    para.bulletFontName = 'Times-BoldItalic'
    stylesheet['Definition'] = para

    para = ParagraphStyle('Code', stylesheet['Normal'])
    para.fontName = 'Courier'
    para.fontSize = 8
    para.leading = 8.8
    para.leftIndent = 36
    stylesheet['Code'] = para


    return stylesheet


def cleanBlockQuotedText(text):
    """This is an internal utility which takes triple-
    quoted text form within the document and returns
    (hopefully) the paragraph the user intended originally."""
    stripped = string.strip(text)
    lines = string.split(stripped, '\n')
    trimmed_lines = map(string.lstrip, lines)
    return string.join(trimmed_lines, ' ')




#############################################################
#
#       Drawable Objects - a base class and a few examples.
#       One is just a box to get some metrics.  We also have
#       a paragraph, an image and a special 'page break'
#       object which fills the space.
#
#############################################################

class Drawable:
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

class XBox(Drawable):
    """Example drawable - a box with an x through it and a caption.
    This has a known size, so does not need to respond to wrap()."""
    def __init__(self, width, height, text = 'A Box'):
        Drawable.__init__(self)
        self.width = width
        self.height = height
        self.text = text

    def draw(self):
        self.canv.rect(0, 0, self.width, self.height)
        self.canv.line(0, 0, self.width, self.height)
        self.canv.line(0, self.height, self.width, 0)

        #centre the text
        self.canv.setFont('Times-Roman',12)
        self.canv.drawCentredString(0.5*self.width, 0.5*self.height, self.text)


class Paragraph(Drawable):
    def __init__(self, text, style, bulletText = None):
        self.text = cleanBlockQuotedText(text)
        self.style = style
        self.bulletText = bulletText
        self.debug = 0   #turn this on to see a pretty one with all the margins etc.

    def wrap(self, availWidth, availHeight):
        # work out widths array for breaking
        self.width = availWidth
        first_line_width = availWidth - self.style.firstLineIndent - self.style.rightIndent
        later_widths = availWidth - self.style.leftIndent - self.style.rightIndent
        wrap_widths = [first_line_width, later_widths]

        # break it up and store the results internally
        self.lines = self.breakLines(self.text, wrap_widths, self.style.fontName, self.style.fontSize)

        linecount = len(self.lines)

        #estimate the size
        self.height = (self.style.spaceBefore +
                  linecount * self.style.leading +
                  self.style.spaceAfter)
        return (self.width, self.height)

    def draw(self):
        #call another method for historical reasons.  Besides, I
        #suspect I will be playing with alternate drawing routines
        #so not doing it here makes it easier to switch.
        self.drawPara(self.debug)

    def breakLines(self, text, width, fontName, fontSize):
        """Returns a structure broken into lines.  Each line has two items.  Item one
        is the extra points of space available on that line; item two is the list of
        words themselves.  This structure can be used to easily draw paragraphs
        with the various alignments.  You can supply either a single width or a list
        of widths; the latter will have its last item repeated until necessary.  A
        2-element list is useful when there is a different first line indent; a longer
        list could be created to facilitate custom wraps around irregular objects."""
        if type(width) <> types.ListType:
            maxwidths = [width]
        else:
            maxwidths = width
        lines = []
        spacewidth = pdfmetrics.stringwidth(' ', fontName) * 0.001 * fontSize
        words = string.split(text, ' ')
        currentline = []
        lineno = 0
        maxwidth = maxwidths[lineno]
        currentwidth = - spacewidth   # hack to get around extra space for word 1

        #for bullets, work out its width and ensure we wrap the right amount onto
        #line one
        if self.bulletText <> None:
            bulletWidth = pdfmetrics.stringwidth(
                self.bulletText,
                self.style.bulletFontName) * 0.001 * self.style.bulletFontSize
            bulletRight = self.style.bulletIndent + bulletWidth
            if bulletRight > self.style.firstLineIndent:
                #..then it overruns, and we have less space available on line 1
                maxwidths[0] = maxwidths[0] - (bulletRight - self.style.firstLineIndent)

        for word in words:
            wordwidth = pdfmetrics.stringwidth(word, fontName) * 0.001 * fontSize
            space_available = maxwidth - (currentwidth + spacewidth + wordwidth)
##            print 'FIXME Word %s, width %0.2f, used %0.2f, remaining %0.2f' % (
##                word, wordwidth, currentwidth, space_available)
            if  space_available > 0:
                # fit one more on this line
                currentline.append(word)
                currentwidth = currentwidth + spacewidth + wordwidth
            else:
                #end of line
                lines.append((maxwidth - currentwidth, currentline))
                currentline = [word]
                currentwidth = wordwidth
                lineno = lineno + 1
                try:
                    maxwidth = maxwidths[lineno]
                except IndexError:
                    maxwidth = maxwidths[-1]  # use the last one
        #deal with any leftovers on the final line
        if currentline <> []:
            lines.append((space_available, currentline))

        return lines



    def drawPara(self,debug=0):
        """Draws a paragraph according to the given style.
        Returns the final y position at the bottom. Not safe for
        paragraphs without spaces e.g. Japanese; wrapping
        algorithm will go infinite."""
        text = cleanBlockQuotedText(self.text)

        #stash the key facts locally for speed
        text = self.text
        canvas = self.canv

        #work out the origin for line 1
        cur_x = self.style.leftIndent
        cur_y = self.height - self.style.fontSize - self.style.spaceBefore

        if debug:
            # This boxes and shades stuff to show how the paragraph
            # uses its space.  Useful for self-documentation so
            # the debug code stays!

            # box the lot
            canvas.rect(0, 0, self.width, self.height)
            #left and right margins
            canvas.saveState()
            canvas.setFillColorRGB(0.9,0.9,0.9)
            canvas.rect(0, 0, self.style.leftIndent, self.height)
            canvas.rect(self.width - self.style.rightIndent, 0, self.style.rightIndent, self.height)
            # shade above and below
            canvas.setFillColorRGB(1.0,1.0,0.0)
            canvas.rect(0, self.height - self.style.spaceBefore, self.width,  self.style.spaceBefore)
            canvas.rect(0, 0, self.width, self.style.spaceAfter)
            canvas.restoreState()

            #self.drawLine(x + style.leftIndent, y, x + style.leftIndent, cur_y)


        canvas.addLiteral('% textcanvas.drawParagraph()')
        #set up the font etc.

    ##    color = style.textColor
    ##    r,g,b = color.red, color.green, color.blue
    ##    self.code.append('%s %s %s rg' % (r,g,b))
    ##
        #is there a bullet?  if so, draw it first

        if len(self.lines) > 0:
            #begin drawing line one.  Unless the wrapping was
            #perfect, we will have a few mm of extra space to allocate;
            #this means moving the line origin to the right depending
            #on whether it is centred, right-aligned or left-aligned
            offset = self.style.firstLineIndent - self.style.leftIndent


            if self.bulletText <> None:
                tx2 = canvas.beginText(self.style.bulletIndent, cur_y)
                tx2.setFont(self.style.bulletFontName, self.style.bulletFontSize)
                tx2.textOut(self.bulletText)
                bulletEnd = tx2.getX()
                offset = max(offset, bulletEnd - self.style.leftIndent)
                canvas.drawText(tx2)

            tx = canvas.beginText(cur_x, cur_y)

            #now the font for the rest of the paragraph
            tx.setFont(self.style.fontName,
                   self.style.fontSize,
                   self.style.leading)

            (extraspace, words) = self.lines[0]
            text  = string.join(words)
            if self.style.alignment == TA_LEFT:
                tx.moveCursor(offset, 0)
                tx.textLine(text)
                tx.moveCursor(-offset, 0)
            elif self.style.alignment == TA_CENTER:
                tx.moveCursor(offset + 0.5 * extraspace, 0)
                tx.textLine(text)
                tx.moveCursor(-offset + 0.5 * extraspace, 0)
            elif self.style.alignment == TA_RIGHT:
                tx.moveCursor(offset + extraspace, 0)
                tx.textLine(text)
                tx.moveCursor(-offset + extraspace, 0)
            elif self.style.alignment == TA_JUSTIFY:
                tx.setTextWordSpacing(1.0 * extraspace / len(words))
                tx.textLine(text)
                tx.setTextWordSpacing()

            cur_y = cur_y + self.style.leading

        #now the middle of the paragraph, aligned with the left margin which is our
        #origin.

            for lineno in range(1, len(self.lines)):
                (extraspace, words) = self.lines[lineno]
                text = string.join(words)
                if self.style.alignment == TA_LEFT:
                    tx.textLine(text)
                elif self.style.alignment == TA_CENTER:
                    tx.moveCursor(offset + 0.5 * extraspace, 0)
                    tx.textLine(text)
                    tx.moveCursor(-offset + 0.5 * extraspace, 0)
                elif style.alignment == TA_RIGHT:
                    tx.moveCursor(offset + extraspace, 0)
                    tx.textLine(text)
                    tx.moveCursor(-offset + extraspace, 0)
                elif style.alignment == TA_JUSTIFY:
                    if lineno == len(lines) - 1:
                        #last one, left align
                        tx.textLine(text)
                    else:
                        tx.setTextWordSpacing(1.0 * extraspace / len(words))
                        tx.textLine(text)
                        tx.setTextWordSpacing()

                cur_y = cur_y - self.style.leading
        canvas.drawText(tx)
        #move down a bit, correct for the extra fontSize move at the  start

class Preformatted(Drawable):
    """This is like the HTML <PRE> tag.  The line breaks are exactly where you put
    them, and it will not be wrapped.  So it is much simpler to implement!"""
    def __init__(self, text, style, bulletText = None, dedent=0):
        self.style = style
        self.bulletText = bulletText

        #tidy up text - carefully, it is probably code.  If people want to
        #indent code within a source script, you can supply an arg to dedent
        #and it will chop off that many character, otherwise it leaves
        #left edge intact.

        templines = string.split(text, '\n')
        self.lines = []
        for line in templines:
            line = string.rstrip(line[dedent:])
            self.lines.append(line)
        #don't want the first or last to be empty
        while string.strip(self.lines[0]) == '':
            self.lines = self.lines[1:]
        while string.strip(self.lines[-1]) == '':
            self.lines = self.lines[:-1]



    def wrap(self, availWidth, availHeight):
        self.width = availWidth
        self.height = (self.style.spaceBefore +
                      self.style.leading * len(self.lines) +
                      self.style.spaceAfter)
        return (self.width, self.height)

    def draw(self):
        #call another method for historical reasons.  Besides, I
        #suspect I will be playing with alternate drawing routines
        #so not doing it here makes it easier to switch.

        cur_x = self.style.leftIndent
        cur_y = self.height - self.style.spaceBefore - self.style.fontSize
        self.canv.addLiteral('%PreformattedPara')

        tx = self.canv.beginText(cur_x, cur_y)
        #set up the font etc.
        tx.setFont(self.style.fontName,
                   self.style.fontSize,
                   self.style.leading)

        for text in self.lines:
            tx.textLine(text)
        self.canv.drawText(tx)




class Image(Drawable):
    def __init__(self, filename, width=None, height=None):
        """If size to draw at not specified, get it from the image."""
        import Image  #this will raise an error if they do not have PIL.
        self.filename = filename
        print 'Creating Image for', filename
        img = Image.open(filename)
        (self.imageWidth, self.imageHeight) = img.size
        if width:
            self.drawWidth = width
        else:
            self.drawWidth = self.imageWidth
        if height:
            self.drawHeight = height
        else:
            self.drawHeight = self.imageHeight

    def wrap(self, availWidth, availHeight):
        #the caller may decide it does not fit.
        self.availWidth = availWidth
        return (self.drawWidth, self.drawHeight)

    def draw(self):
        #center it
        startx = 0.5 * (self.availWidth - self.drawWidth)
        self.canv.drawInlineImage(self.filename,
                                  startx,
                                  0,
                                  self.drawWidth,
                                  self.drawHeight
                                  )
class Spacer(Drawable):
    """A spacer just takes up space and doesn't draw anything - it can
    ensure a gap between objects."""
    def __init__(self, width, height):
        self.width = width
        self.height = height

    def wrap(self, availWidth, availHeight):
        return (self.width, self.height)

    def draw(self):
        pass

class PageBreak(Drawable):
    """This works by consuming all remaining space in the frame!"""

    def wrap(self, availWidth, availHeight):
        self.width = availWidth
        self.height = availHeight
        return (availWidth,availHeight)  #step back a point

    def draw(self):
        pass
        #
        #self.canv.drawRect(0, 0, self.width, self.height)
        #self.canv.drawLine(0, 0, self.width, self.height)
        #self.canv.drawLine(0, self.height, self.width, 0)
        #self.text = 'Page Break Object (%d x %d)' % (self.width, self.height)
        ##centre the text
        #self.canv._currentFont = self.canv.defaultFont
        #f = Font(size=24,bold=1)
        #w = self.canv.stringWidth(self.text, f)
        #x = 0.5 * (self.width - w)
        #y = 0.33 * (self.height + f.size)

        #self.canv.drawString(self.text, x, y, font=f)

class Macro(Drawable):
    """This is not actually drawn (i.e. it has zero height)
    but is executed when it would fit in the frame.  Allows direct
    access to the canvas through the object 'canvas'"""
    def __init__(self, command):
        self.command = command
    def wrap(self, availWidth, availHeight):
        return (0,0)
    def draw(self):
        exec self.command in globals(), {'canvas':self.canv}




#############################################################
#
#       Basic paragraph-drawing routine.  Not sure where
#       this should go, so did it as a separate function.
#
#############################################################


#############################################################
#
#       A Frame, and a Document Model
#
#############################################################

FrameFullError = "FrameFullError"
LayoutError = "LayoutError"

class SimpleFrame:
    """A region into which drawable objects are to be packed.
    Flows downwards.  A more general solution is needed which
    will allow flows in any direction, including 'across and then
    down' for small objects, but this is useful for
    many languages now, as long as each object is 'full-width'
    (i.e. a paragraph and not a word)."""
    def __init__(self, canvas, x1, y1, width,height):
        self.canvas = canvas

        #these say where it goes on the page
        x2 = x1 + width
        y2 = y1 + height
        self.leftMargin = x1
        self.bottomMargin = y1
        self.rightMargin = x2
        self.topMargin = y2

        #these create some padding.
        self.leftPadding = 6
        self.bottomPadding = 6
        self.rightPadding = 6
        self.topPadding = 6

        #work out the available space
        self.width = x2 - x1 - self.leftPadding - self.rightPadding
        self.height = y2 - y1 - self.topPadding - self.bottomPadding
        self.objects = []   #it keeps a list of objects
        self.showBoundary = 0
        #drawing starts at top left
        self.x = x1 + self.leftPadding
        self.y = y2 - self.topPadding


    def add(self, drawable):
        """ Draws the object at the current position.
        Returns 1 if successful, 0 if it would not fit.
        Raises a LayoutError if the object is too wide,
        or if it is too high for a totally empty frame,
        to avoid infinite loops"""
        w, h = drawable.wrap(self.width, self.y - self.bottomMargin - self.bottomPadding)

        if h > self.height:
            raise "LayoutError", "Object (%d points) too high for frame (%d points)." % (h, self.height)
        if w > self.width:
            raise "LayoutError", "Object (%d points) too wide for frame (%d points)." % (w, self.width)
        if self.y - h < (self.bottomMargin - self.bottomPadding):
            return 0
        else:
            #now we can draw it, and update the current point.
            drawable.drawOn(self.canvas, self.x, self.y - h)
            self.y = self.y - h
            self.objects.append(drawable)
            return 1

    def addFromList(self, drawlist):
        """Consumes objects from the front of the list until the
        frame is full.  If it cannot fit one object, raises
        an exception."""

        if self.showBoundary:
            self.canvas.rect(
                        self.leftMargin,
                        self.bottomMargin,
                        self.rightMargin - self.leftMargin,
                        self.topMargin - self.bottomMargin
                        )

        while len(drawlist) > 0:
            head = drawlist[0]
            if self.add(head):
                del drawlist[0]
            else:
                #leave it in the list for later
                break
class Sequencer:
    """Something to make it easy to number paragraphs, sections,
    images and anything else. Usage:
        >>> seq = layout.Sequencer()
        >>> seq.next('Bullets')
        1
        >>> seq.next('Bullets')
        2
        >>> seq.next('Bullets')
        3
        >>> seq.reset('Bullets')
        >>> seq.next('Bullets')
        1
        >>> seq.next('Figures')
        1
        >>>
    I plan to add multi-level linkages, so that Head2 could be reet
    """
    def __init__(self):
        self.dict = {}

    def next(self, category):
        if self.dict.has_key(category):
            self.dict[category] = self.dict[category] + 1
        else:
            self.dict[category] = 1
        return self.dict[category]

    def reset(self, category):
        self.dict[category] = 0

def _doNothing(drawables, doc):
    "Dummy callback for onFirstPage and onNewPage"
    pass

##########################################################
#
#
#
##########################################################
class SimpleFlowDocument:
    """A sample document that uses a single frame on each page.
    The intention is for programmers to create their own document
    models as needed.  This one accepts a list of drawables. You
    can provide callbacks to decorate the first page and
    subsequent pages; these should do headers, footers, sidebars
    as needed."""
    def __init__(self, filename, pagesize, showBoundary=0):
        self.filename = filename
        self.pagesize = pagesize
        self.showBoundary=showBoundary
        #sensibel defaults; override if you wish
        self.leftMargin =  inch
        self.bottomMargin = inch
        self.rightMargin = self.pagesize[0] - inch
        self.topMargin = self.pagesize[1] - inch

        # 1-based counting is friendlier for readers
        self.page = 1
        #set these to drawing procedures of your own
        self.onFirstPage = _doNothing
        self.onNewPage = _doNothing


    def build(self, drawables):
        canv = canvas.Canvas(self.filename)
        #canv.setPageTransition('Dissolve')

        # do page 1
        self.onFirstPage(canv, self)
        frame1 = SimpleFrame(
                    canv,
                    self.leftMargin,
                    self.bottomMargin,
                    self.rightMargin - self.leftMargin,
                    self.topMargin - inch - self.bottomMargin
                            )
        frame1.showBoundary = self.showBoundary
        frame1.addFromList(drawables)
        #print 'drew page %d, %d objects remaining' % (self.page, len(drawables))
        # do subsequent pages
        while len(drawables) > 0:
            canv.showPage()
            self.page = self.page + 1
            self.onNewPage(canv, self)
            frame = SimpleFrame(
                    canv,
                    self.leftMargin,
                    self.bottomMargin,
                    self.rightMargin - self.leftMargin,
                    self.topMargin - self.bottomMargin
                            )
            frame.showBoundary = self.showBoundary
            frame.addFromList(drawables)

            #print 'drew page %d, %d objects remaining' % (self.page, len(drawables))

        canv.save()
    ##########################################################
    ##
    ##   testing
    ##
    ##########################################################

def randomText():
    #this may or may not be appropriate in your company
    from random import randint, choice

    RANDOMWORDS = ['strategic','direction','proactive',
    'reengineering','forecast','resources',
    'forward-thinking','profit','growth','doubletalk',
    'venture capital','IPO']

    sentences = 5
    output = ""
    for sentenceno in range(randint(1,5)):
        output = output + 'Blah'
        for wordno in range(randint(10,25)):
            if randint(0,4)==0:
                word = choice(RANDOMWORDS)
            else:
                word = 'blah'
            output = output + ' ' +word
        output = output+'.'
    return output


def myFirstPage(canvas, doc):
    canvas.saveState()
    canvas.setStrokeColorRGB(1,0,0)
    canvas.setLineWidth(5)
    canvas.line(66,72,66,PAGE_HEIGHT-72)
    canvas.setFont('Times-Bold',24)
    canvas.drawString(108, PAGE_HEIGHT-108, "PLATYPUS")
    canvas.setFont('Times-Roman',12)
    canvas.drawString(4 * inch, 0.75 * inch, "First Page")
    canvas.restoreState()

def myLaterPages(canvas, doc):
    #canvas.drawImage("snkanim.gif", 36, 36)
    canvas.saveState()
    canvas.setStrokeColorRGB(1,0,0)
    canvas.setLineWidth(5)
    canvas.line(66,72,66,PAGE_HEIGHT-72)
    canvas.setFont('Times-Roman',12)
    canvas.drawString(4 * inch, 0.75 * inch, "Page %d" % doc.page)
    canvas.restoreState()



def run():
    objects_to_draw = []

    #need a style
    normal = ParagraphStyle('normal')
    normal.firstLineIndent = 18
    normal.spaceBefore = 6
    import random
    for i in range(15):
        height = 0.5 + (2*random.random())
        box = XBox(6 * inch, height * inch, 'Box Number %d' % i)
        objects_to_draw.append(box)
        para = Paragraph(randomText(), normal)
        objects_to_draw.append(para)


    doc = SimpleFlowDocument('platypus.pdf',DEFAULT_PAGE_SIZE)
    doc.onFirstPage = myFirstPage
    doc.onNewPage = myLaterPages
    doc.build(objects_to_draw)


if __name__ == '__main__':
    run()
