"""Tests for the Platypus TableOfContents class.

Currently there is only one such test. Most such tests, like this
one, will be generating a PDF document that needs to be eye-balled
in order to find out if it is 'correct'.
"""


import sys, os, tempfile
from os.path import join, basename, splitext
from math import sqrt

from reportlab.test import unittest
from reportlab.lib.units import inch, cm
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus.paragraph import Paragraph
from reportlab.platypus.xpreformatted import XPreformatted
from reportlab.platypus.frames import Frame
from reportlab.platypus.doctemplate \
     import PageTemplate, BaseDocTemplate
from reportlab.platypus import tableofcontents
from reportlab.platypus.tableofcontents import TableOfContents0
from reportlab.platypus.tables import TableStyle, Table


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
        "Registers TOC entries and makes outline entries."
        
        if flowable.__class__.__name__ == 'Paragraph':
            styleName = flowable.style.name
            if styleName[:7] == 'Heading':
                # Register TOC entries.
                level = int(styleName[7:])
                text = flowable.getPlainText()
                pageNum = self.page 
                self.notify0('TOCEntry', (level, text, pageNum))

                # Add PDF outline entries (not really needed/tested here).
                key = str(hash(flowable))
                c = self.canv
                c.bookmarkPage(key)
                c.addOutlineEntry(text, key, level=level, closed=0)


def makeHeaderStyle(level, fontName='Times-Roman'):
    "Make a header style for different levels."

    assert level >= 0, "Level must be >= 0."
    
    PS = ParagraphStyle
    size = 24.0 / sqrt(1+level)
    style = PS(name = 'Heading' + str(level),
               fontName = fontName,
               fontSize = size,
               leading = size*1.2,
               spaceBefore = size/4.0,
               spaceAfter = size/8.0)

    return style


def makeTocHeaderStyle(level, delta, epsilon, fontName='Times-Roman'):
    "Make a header style for different levels."

    assert level >= 0, "Level must be >= 0."
    
    PS = ParagraphStyle
    size = 12
    style = PS(name = 'Heading' + str(level),
               fontName = fontName,
               fontSize = size,
               leading = size*1.2,
               spaceBefore = size/4.0,
               spaceAfter = size/8.0,
               firstLineIndent = -epsilon,
               leftIndent = level*delta + epsilon)

    return style


class TocTestCase(unittest.TestCase):
    "Test TableOfContents0 class (eyeball-test)."
    
    def test1(self):
        """Test story with TOC and a cascaded header hierarchy.

        The story should contain exactly one table of contents that is
        immediatly followed by a list of of cascaded levels of header
        lines, each nested one level deeper than the previous one.

        Features to be visually confirmed by a human being are:

            1. TOC lines are indented in multiples of 1 cm. 
            2. Wrapped TOC lines continue with additional 0.5 cm indentation.
            3. ...
        """

        maxLevels = 12

        # Create styles to be used for document headers
        # on differnet levels.
        headerLevelStyles = []
        for i in range(maxLevels):
            headerLevelStyles.append(makeHeaderStyle(i))

        # Create styles to be used for TOC entry lines
        # for headers on differnet levels.
        tocLevelStyles = []
        d, e = tableofcontents.delta, tableofcontents.epsilon
        for i in range(maxLevels):
            tocLevelStyles.append(makeTocHeaderStyle(i, d, e))

        # Build story.
        story = []
        styleSheet = getSampleStyleSheet()
        bt = styleSheet['BodyText']

        description = '<font color=red>%s</font>' % self.test1.__doc__
        story.append(XPreformatted(description, bt))

        toc = TableOfContents0()
        toc.levelStyles = tocLevelStyles
        story.append(toc)

        for i in range(maxLevels):
            story.append(Paragraph('HEADER, LEVEL %d' % i,
                                   headerLevelStyles[i]))

        tempfile.tempdir = os.curdir
        path = join(tempfile.tempdir, 'test_platypus_toc.pdf')
        doc = MyDocTemplate(path)
        doc.multiBuild0(story)
        

def makeSuite():
    suite = unittest.TestSuite()
    suite.addTest(TocTestCase('test1'))
    return suite


#noruntests
if __name__ == "__main__":
    unittest.TextTestRunner().run(makeSuite())
