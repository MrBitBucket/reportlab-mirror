#Copyright ReportLab Europe Ltd. 2000-2008
#see license.txt for license details
"""Tests for the Platypus SimpleIndex and AlphabeticIndex classes.
"""
__version__='''$Id$'''
from reportlab.lib.testutils import setOutDir,makeSuiteForClasses, outputfile, printLocation
setOutDir(__name__)
import sys, os
from os.path import join, basename, splitext
from math import sqrt
import unittest
from reportlab.lib.units import inch, cm
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus.paragraph import Paragraph
from reportlab.platypus.xpreformatted import XPreformatted
from reportlab.platypus.frames import Frame
from reportlab.platypus.doctemplate \
     import PageTemplate, BaseDocTemplate
from reportlab.platypus.tableofcontents import SimpleIndex, AlphabeticIndex
from reportlab.lib import randomtext
import re
from xml.sax.saxutils import quoteattr

def myMainPageFrame(canvas, doc):
    "The page frame used for all PDF documents."

    canvas.saveState()

    canvas.rect(2.5*cm, 2.5*cm, 15*cm, 25*cm)
    canvas.setFont('Times-Roman', 12)
    pageNumber = canvas.getPageNumber()
    canvas.drawString(10*cm, cm, str(pageNumber))

    canvas.restoreState()


class MyDocTemplate(BaseDocTemplate):
    "The document template used for all PDF documents."

    _invalidInitArgs = ('pageTemplates',)

    def __init__(self, filename, **kw):
        frame1 = Frame(2.5*cm, 2.5*cm, 15*cm, 25*cm, id='F1')
        self.allowSplitting = 0
        apply(BaseDocTemplate.__init__, (self, filename), kw)
        template = PageTemplate('normal', [frame1], myMainPageFrame)
        self.addPageTemplates(template)


    def afterFlowable(self, flowable):
        "Registers TOC entries."

        if flowable.__class__.__name__ == 'Paragraph':
            styleName = flowable.style.name
            if styleName[:7] == 'Heading':
                key = str(hash(flowable))
                self.canv.bookmarkPage(key)

                # Register TOC entries.
                level = int(styleName[7:])
                text = flowable.getPlainText()
                pageNum = self.page
                # Try calling this with and without a key to test both
                # Entries of every second level will have links, others won't
                if level % 2 == 1:
                    self.notify('TOCEntry', (level, text, pageNum, key))
                else:
                    self.notify('TOCEntry', (level, text, pageNum))

def makeBodyStyle():
    "Body text style - the default will do"
    return ParagraphStyle('body', spaceBefore=20)
    
class IndexTestCase(unittest.TestCase):
    "Test (Simple|Alphabetic)Index classes (eyeball-test)."

    def test0(self):
        # Build story.
        
        for cls in SimpleIndex, AlphabeticIndex:
            path = outputfile('test_platypus_%s.pdf' % cls.__name__.lower())
            doc = MyDocTemplate(path)
            story = []
            styleSheet = getSampleStyleSheet()
            bt = styleSheet['BodyText']
    
            description = '<font color=red>%s</font>' % self.test0.__doc__
            story.append(XPreformatted(description, bt))
            index = cls(None, ' . ')
    
            for i in range(20):
                words = randomtext.randomText(randomtext.PYTHON, 5).split(' ')
                txt = ' '.join(((len(w) > 5 and '<onDraw name="_indexAdd" label=%s/>%s' % (quoteattr(repr(w)), w) or w) for w in words))
                para = Paragraph(txt, makeBodyStyle())
                story.append(para)
            story.append(index)
    
            doc.multiBuild(story, canvasmaker=index.getCanvasMaker())

def makeSuite():
    return makeSuiteForClasses(IndexTestCase)


#noruntests
if __name__ == "__main__":
    unittest.TextTestRunner().run(makeSuite())
    printLocation()
