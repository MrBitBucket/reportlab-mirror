#copyright ReportLab Inc. 2000
#see license.txt for license details
#history http://cvs.sourceforge.net/cgi-bin/cvsweb.cgi/docs/tools/platdemos.py?cvsroot=reportlab
#$Header: /tmp/reportlab/reportlab/platypus/figures.py,v 1.8 2003/12/03 15:19:43 johnprecedo Exp $
"""This includes some demos of platypus for use in the API proposal"""
__version__=''' $Id: figures.py,v 1.8 2003/12/03 15:19:43 johnprecedo Exp $ '''

import os

from reportlab.lib import colors
from reportlab.pdfgen.canvas import Canvas
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.utils import recursiveImport
from reportlab.platypus import Frame
from reportlab.platypus import Flowable
from reportlab.platypus import Paragraph
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_LEFT, TA_RIGHT, TA_CENTER
from reportlab.lib.validators import isColor
from reportlab.lib.colors import toColor

captionStyle = ParagraphStyle('Caption', fontName='Times-Italic', fontSize=10, alignment=TA_CENTER)

class Figure(Flowable):
    def __init__(self, width, height, caption="",
                 captionFont="Times-Italic", captionSize=12, background=None):
        Flowable.__init__(self)
        self.width = width
        self.figureHeight = height
        self.captionHeight = 0  # work out later
        self.caption = caption
        self.background = background
        self.captionStyle = ParagraphStyle(
            'Caption',
            fontName=captionFont,
            fontSize=captionSize,
            leading=1.2*captionSize,
            spaceBefore=captionSize * 0.5,
            alignment=TA_CENTER)
        #must build paragraph now to get sequencing in synch
        #with rest of story
        self.captionPara = Paragraph(self.caption, self.captionStyle)

        self.spaceBefore = 12
        self.spaceAfter = 12

    def wrap(self, availWidth, availHeight):
        # try to get the caption aligned
        (w, h) = self.captionPara.wrap(self.width, availHeight - self.figureHeight)
        self.captionHeight = h
        self.height = self.captionHeight + self.figureHeight
        self.dx = 0.5 * (availWidth - self.width)
        return (self.width, self.height)

    def draw(self):
        self.canv.translate(self.dx, 0)
        self.drawCaption()
        self.canv.translate(0, self.captionHeight)
        if self.background:
            self.drawBackground()
        self.drawBorder()
        self.drawFigure()

    def drawBorder(self):
        self.canv.rect(0, 0, self.width, self.figureHeight)

    def _doBackground(self, color):
        self.canv.saveState()
        self.canv.setFillColor(self.background)
        self.canv.rect(0, 0, self.width, self.figureHeight, fill=1)
        self.canv.restoreState()

    def drawBackground(self):
        """For use when using a figure on a differently coloured background.
        Allows you to specify a colour to be used as a background for the figure."""
        if isColor(self.background):
            self._doBackground(self.background)
        else:
            try:
                c = toColor(self.background)
                self._doBackground(c)
            except:
                pass

    def drawCaption(self):
        self.captionPara.drawOn(self.canv, 0, 0)

    def drawFigure(self):
        pass

def drawPage(canvas,x, y, width, height):
    #draws something which looks like a page
    pth = canvas.beginPath()
    corner = 0.05*width

    # shaded backdrop offset a little
    canvas.setFillColorRGB(0.5,0.5,0.5)
    canvas.rect(x + corner, y - corner, width, height, stroke=0, fill=1)

    #'sheet of paper' in light yellow
    canvas.setFillColorRGB(1,1,0.9)
    canvas.setLineWidth(0)
    canvas.rect(x, y, width, height, stroke=1, fill=1)

    #reset
    canvas.setFillColorRGB(0,0,0)
    canvas.setStrokeColorRGB(0,0,0)



class PageFigure(Figure):
    """Shows a blank page in a frame, and draws on that.  Used in
    illustrations of how PLATYPUS works."""
    def __init__(self, background=None):
        Figure.__init__(self, 3*inch, 3*inch)
        self.caption = 'Figure 1 - a blank page'
        self.captionStyle = captionStyle
        self.background = background

    def drawVirtualPage(self):
        pass

    def drawFigure(self):
        drawPage(self.canv, 0.625*inch, 0.25*inch, 1.75*inch, 2.5*inch)
        self.canv.translate(0.625*inch, 0.25*inch)
        self.canv.scale(1.75/8.27, 2.5/11.69)
        self.drawVirtualPage()

class PlatPropFigure1(PageFigure):
    """This shows a page with a frame on it"""
    def __init__(self):
        PageFigure.__init__(self)
        self.caption = "Figure 1 - a page with a simple frame"
    def drawVirtualPage(self):
        demo1(self.canv)

class FlexFigure(Figure):
    """Base for a figure class with a caption. Can grow or shrink in proportion"""
    def __init__(self, width, height, caption, background=None):
        Figure.__init__(self, width, height, caption,
                        captionFont="Helvetica-Oblique", captionSize=8,
                        background=None)
        self.shrinkToFit = 1 #if set and wrap is too tight, shrinks
        self.growToFit = 1 #if set and wrap is too tight, shrinks
        self.scaleFactor = 1
        self.captionStyle = ParagraphStyle(
            'Caption',
            fontName='Times', #'Helvetica-Oblique',
            fontSize=4, #8, 
            spaceBefore=9, #3,
            alignment=TA_CENTER
            )
        self._scaledWidth = None
        self.background = background

    def wrap(self, availWidth, availHeight):
        "Rescale to fit according to the rules, but only once"
        if self._scaledWidth <> availWidth:
            self._scaledWidth = availWidth
            self.scaleFactor = availWidth / self.width
            #print 'width=%d, scale=%0.2f' % (self.width, self.scaleFactor)
            if self.scaleFactor < 1 and self.shrinkToFit:
                self.width = self.width * self.scaleFactor
                self.figureHeight = self.figureHeight * self.scaleFactor
            elif self.scaleFactor > 1 and self.growToFit:
                self.width = self.width * self.scaleFactor
                self.figureHeight = self.figureHeight * self.scaleFactor
        return Figure.wrap(self, availWidth, availHeight)


class ImageFigure(FlexFigure):
    """Image with a caption below it"""
    def __init__(self, filename, caption, background=None):
        assert os.path.isfile(filename), 'image file %s not found' % filename
        from reportlab.lib.utils import ImageReader
        w, h = ImageReader(filename).getSize()
        self.filename = filename
        FlexFigure.__init__(self, w, h, caption, background)

    def drawFigure(self):
        self.canv.drawInlineImage(self.filename,
                                  0, 0,self.width, self.figureHeight)
        

class DrawingFigure(FlexFigure):
    """Drawing with a caption below it.  Clunky, scaling fails."""
    def __init__(self, modulename, classname, caption, baseDir=None, background=None):
        module = recursiveImport(modulename, baseDir)
        klass = getattr(module, classname)
        self.drawing = klass()
        FlexFigure.__init__(self,
                            self.drawing.width,
                            self.drawing.height,
                            caption,
                            background)
        self.growToFit = 1
        
    def drawFigure(self):
        self.canv.scale(self.scaleFactor, self.scaleFactor)
        self.drawing.drawOn(self.canv, 0, 0)


    ####################################################################
    #
    #    PageCatcher plugins
    # These let you use our PageCatcher product to add figures
    # to other documents easily.
    ####################################################################

try:
    from rlextra.pageCatcher.pageCatcher import restoreForms, storeForms
    _hasPageCatcher = 1
except ImportError:
    _hasPageCatcher = 0
if _hasPageCatcher:

    class PageCatcherCachingMixIn:
        "Helper functions to cache pages for figures"

        def getFormName(self, pdfFileName, pageNo):
            #naming scheme works within a directory
            #only
            dirname, filename = os.path.split(pdfFileName)
            root, ext = os.path.splitext(filename)
            return '%s_page%d' % (root, pageNo)


        def needsProcessing(self, pdfFileName, pageNo):
            "returns 1 if no forms or form is older"
            formName = self.getFormName(pdfFileName, pageNo)
            if os.path.exists(formName + '.frm'):
                formModTime = os.stat(formName + '.frm')[8]
                pdfModTime = os.stat(pdfFileName)[8]
                return (pdfModTime > formModTime)
            else:
                return 1

        def processPDF(self, pdfFileName, pageNo):
            formName = self.getFormName(pdfFileName, pageNo)
            storeForms(pdfFileName, formName + '.frm',
                                    prefix= formName + '_',
                                    pagenumbers=[pageNo])
            print 'stored %s.frm' % formName
            return formName + '.frm'

        
    class PageFigure(FlexFigure, PageCatcherCachingMixIn):
        """PageCatcher page with a caption below it.  Presumes A4, Portrait.
        This needs our commercial PageCatcher product, or you'll get a blank."""

        def __init__(self, filename, pageNo, caption, width=595, height=842, background=None):
            self.dirname, self.filename = os.path.split(filename)
            if self.dirname == '':
                self.dirname = os.curdir
            self.pageNo = pageNo
            self.formName = self.getFormName(self.filename, self.pageNo) + '_' + str(pageNo)
            FlexFigure.__init__(self, width, height, caption, background)
            #print 'self.width=%0.2f, self.figureHeight=%0.2f' % (self.width, self.figureHeight)
            

        def drawFigure(self):
            #print 'drawing ',self.formName
            #print 'self.width=%0.2f, self.figureHeight=%0.2f' % (self.width, self.figureHeight)
            self.canv.saveState()
            if not self.canv.hasForm(self.formName):
                restorePath = self.dirname + os.sep + self.filename
                #does the form file exist?  if not, generate it.
                formFileName = self.getFormName(restorePath, self.pageNo) + '.frm'
                if self.needsProcessing(restorePath, self.pageNo):
                    print 'preprocessing PDF %s page %s' % (restorePath, self.pageNo)
                    self.processPDF(restorePath, self.pageNo)
                names = restoreForms(formFileName, self.canv)
                #print 'restored',names
            self.canv.scale(self.scaleFactor, self.scaleFactor)
            #print 'doing form',self.formName
            self.canv.doForm(self.formName)
            self.canv.restoreState()

    class PageFigureNonA4(FlexFigure, PageCatcherCachingMixIn):
        """PageCatcher page with a caption below it.  Size to be supplied."""
        # This should merge with PageFigure into one class that reuses
        # form information to determine the page orientation...
        def __init__(self, filename, pageNo, caption, width, height, background=None):
            self.dirname, self.filename = os.path.split(filename)
            if self.dirname == '':
                self.dirname = os.curdir
            self.pageNo = pageNo
            self.formName = self.getFormName(self.filename, self.pageNo) + '_' + str(pageNo)
            FlexFigure.__init__(self, width, height, caption, background)

        def drawFigure(self):
            self.canv.saveState()
            if not self.canv.hasForm(self.formName):
                restorePath = self.dirname + os.sep + self.filename
                #does the form file exist?  if not, generate it.
                formFileName = self.getFormName(restorePath, self.pageNo) + '.frm'
                if self.needsProcessing(restorePath, self.pageNo):
                    print 'preprocessing PDF %s page %s' % (restorePath, self.pageNo)
                    self.processPDF(restorePath, self.pageNo)
                names = restoreForms(formFileName, self.canv)
            self.canv.scale(self.scaleFactor, self.scaleFactor)
            self.canv.doForm(self.formName)
            self.canv.restoreState()



def demo1(canvas):
    frame = Frame(
                    2*inch,     # x
                    4*inch,     # y at bottom
                    4*inch,     # width
                    5*inch,     # height
                    showBoundary = 1  # helps us see what's going on
                    )

    bodyStyle = ParagraphStyle('Body', fontName='Times-Roman', fontSize=24, leading=28, spaceBefore=6)

    para1 = Paragraph('Spam spam spam spam. ' * 5, bodyStyle)
    para2 = Paragraph('Eggs eggs eggs. ' * 5, bodyStyle)

    mydata = [para1, para2]

    #this does the packing and drawing.  The frame will consume
    #items from the front of the list as it prints them
    frame.addFromList(mydata,canvas)


def test1():
    c  = Canvas('figures.pdf')
    f = Frame(inch, inch, 6*inch, 9*inch, showBoundary=1)
    v = PlatPropFigure1()
    f.addFromList([v],c)
    c.save()


if __name__ == '__main__':
    test1()