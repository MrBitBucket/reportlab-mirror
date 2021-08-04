#Copyright ReportLab Europe Ltd. 2000-2017
#see license.txt for license details
"""Tests for context-dependent indentation
"""
__version__='3.3.0'
from reportlab.lib.testutils import setOutDir,makeSuiteForClasses, outputfile, printLocation
setOutDir(__name__)
import sys, os, random
from reportlab.rl_config import invariant as rl_invariant
from operator import truth
import unittest
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.platypus.paraparser import ParaParser
from reportlab.platypus.flowables import Flowable, PageBreak
from reportlab.lib.colors import Color, lightgreen, lightblue, toColor
from reportlab.lib.units import cm
from reportlab.lib.enums import TA_LEFT, TA_RIGHT, TA_CENTER, TA_JUSTIFY
from reportlab.lib.utils import _className
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus.paragraph import Paragraph
from reportlab.platypus.frames import Frame
from reportlab.platypus.doctemplate \
     import PageTemplate, BaseDocTemplate, Indenter, FrameBreak, NextPageTemplate
from reportlab.platypus.tables import TableStyle, Table
from reportlab.platypus.paragraph import *
from reportlab.platypus.paragraph import _getFragWords
from reportlab.platypus import FrameBG, FrameSplitter, Frame, Spacer, ShowBoundaryValue


def myMainPageFrame(canvas, doc):
    "The page frame used for all PDF documents."

    canvas.saveState()

    canvas.rect(2.5*cm, 2.5*cm, 15*cm, 25*cm)
    canvas.setFont('Times-Roman', 12)
    pageNumber = canvas.getPageNumber()
    canvas.drawString(10*cm, cm, str(pageNumber))

    canvas.restoreState()


class MyDocTemplate(BaseDocTemplate):
    _invalidInitArgs = ('pageTemplates',)

    def __init__(self, filename, **kw):
        frame1 = Frame(2.5*cm, 2.5*cm, 15*cm, 25*cm, id='F1')
        self.allowSplitting = 0
        BaseDocTemplate.__init__(self, filename, **kw)
        template1 = PageTemplate('normal', [frame1], myMainPageFrame)

        frame2 = Frame(2.5*cm, 16*cm, 15*cm, 10*cm, id='F2', showBoundary=1)
        frame3 = Frame(2.5*cm, 2.5*cm, 15*cm, 10*cm, id='F3', showBoundary=1)

        greenBoundary = ShowBoundaryValue(color=toColor('darkgreen'),width=0.5)
        templateX = PageTemplate('templateX',[Frame(3*cm, 7.5*cm, 14*cm, 4*cm, id='XF4', showBoundary=greenBoundary),
                        Frame(3*cm, 2.5*cm, 14*cm, 4*cm, id='XF5', showBoundary=greenBoundary)])

        template2 = PageTemplate('updown', [frame2, frame3])
        self.addPageTemplates([template1, template2, templateX])


class IndentTestCase(unittest.TestCase):
    "Test multi-page splitting of paragraphs (eyeball-test)."

    def test0(self):
        "IndentTestCase test0"
        if rl_invariant: random.seed(1479316371)

        # Build story.
        story = []
        doc = MyDocTemplate(outputfile('test_platypus_indents.pdf'))
        storyAdd = story.append

        styleSheet = getSampleStyleSheet()
        h1 = styleSheet['Heading1']
        h1.spaceBefore = 18
        bt = styleSheet['BodyText']
        bt.spaceBefore = 6

        storyAdd(Paragraph('Test of context-relative indentation',h1))

        storyAdd(Spacer(18,18))

        storyAdd(Indenter(0,0))
        storyAdd(Paragraph("This should be indented 0 points at each edge. " + ("spam " * 25),bt))
        storyAdd(Indenter(0,0))

        storyAdd(Indenter(36,0))
        storyAdd(Paragraph("This should be indented 36 points at the left. " + ("spam " * 25),bt))
        storyAdd(Indenter(-36,0))

        storyAdd(Indenter(0,36))
        storyAdd(Paragraph("This should be indented 36 points at the right. " + ("spam " * 25),bt))
        storyAdd(Indenter(0,-36))

        storyAdd(Indenter(36,36))
        storyAdd(Paragraph("This should be indented 36 points at each edge. " + ("spam " * 25),bt))
        storyAdd(Indenter(36,36))
        storyAdd(Paragraph("This should be indented a FURTHER 36 points at each edge. " + ("spam " * 25),bt))
        storyAdd(Indenter(-72,-72))

        storyAdd(Paragraph("This should be back to normal at each edge. " + ("spam " * 25),bt))


        storyAdd(Indenter(36,36))
        storyAdd(Paragraph(("""This should be indented 36 points at the left
        and right.  It should run over more than one page and the indent should
        continue on the next page. """ + (random.randint(0,10) * 'x') + ' ') * 20 ,bt))
        storyAdd(Indenter(-36,-36))

        storyAdd(NextPageTemplate('updown'))
        storyAdd(FrameBreak())
        storyAdd(Paragraph('Another test of context-relative indentation',h1))
        storyAdd(NextPageTemplate('normal'))  # so NEXT page is different template...
        storyAdd(Paragraph("""This time we see if the indent level is continued across
            frames...this page has 2 frames, let's see if it carries top to bottom. Then
            onto a totally different template.""",bt))

        storyAdd(Indenter(0,0))
        storyAdd(Paragraph("This should be indented 0 points at each edge. " + ("spam " * 25),bt))
        storyAdd(Indenter(0,0))
        storyAdd(Indenter(36,72))
        storyAdd(Paragraph(("""This should be indented 36 points at the left
        and 72 at the right.  It should run over more than one frame and one page, and the indent should
        continue on the next page. """ + (random.randint(0,10) * 'x') + ' ') * 35 ,bt))

        storyAdd(Indenter(-36,-72))
        storyAdd(Paragraph("This should be back to normal at each edge. " + ("spam " * 25),bt))
        storyAdd(PageBreak())

        storyAdd(PageBreak())
        storyAdd(Paragraph("Below we should colour the background lightgreen and have a red border",bt))
        storyAdd(FrameBG(start=True,color=lightgreen,strokeColor=toColor('red'),strokeWidth=1))
        storyAdd(Paragraph("We should have a light green background here",bt))
        storyAdd(Paragraph("We should have a light green background here",bt))
        storyAdd(Paragraph("We should have a light green background here",bt))
        storyAdd(Spacer(6,6))
        storyAdd(FrameBG(start=False))

        storyAdd(Paragraph("Below we should colour the background lightgreen",bt))
        storyAdd(FrameBG(start=True,color=lightgreen,strokeColor=toColor('red'),strokeWidth=None))
        storyAdd(Paragraph("We should have a light green background here",bt))
        storyAdd(Paragraph("We should have a light green background here",bt))
        storyAdd(Paragraph("We should have a light green background here",bt))
        storyAdd(Spacer(6,6))
        storyAdd(FrameBG(start=False))

        storyAdd(Paragraph("Below we split to two new frames with dark green borders",bt))
        storyAdd(FrameSplitter('templateX',['XF4','XF5'], adjustHeight=False))
        storyAdd(FrameBG(start=True,color=lightgreen,strokeColor=toColor('red'),strokeWidth=1))
        for i in range(15):
            storyAdd(Paragraph("We should have a light green background here %d" % i,bt))
        storyAdd(Spacer(6,6))
        storyAdd(FrameBG(start=False))
        storyAdd(NextPageTemplate('normal'))

        storyAdd(PageBreak())
        storyAdd(Paragraph("Below we should colour the background lightgreen",bt))
        storyAdd(FrameBG(start="frame",color=lightgreen))
        storyAdd(Paragraph("We should have a light green background here",bt))

        storyAdd(PageBreak())
        storyAdd(Paragraph("Here we should have no background.",bt))

        storyAdd(PageBreak())
        storyAdd(FrameBG(start="frame",color=lightblue))
        storyAdd(Paragraph("We should have a light blue background here and the whole frame should be filled in.",bt))

        storyAdd(PageBreak())
        storyAdd(Paragraph("Here we should have no background again.",bt))

        storyAdd(Paragraph("Below we should colour the background lightgreen",bt))
        storyAdd(FrameBG(start="frame-permanent",color=lightgreen))
        storyAdd(Paragraph("We should have a light green background here",bt))

        storyAdd(PageBreak())
        storyAdd(Paragraph("Here we should still have a lightgreen background.",bt))

        storyAdd(PageBreak())
        storyAdd(FrameBG(start="frame",color=lightblue, left=36, right=36))
        storyAdd(Paragraph("We should have a lighgreen/lightblue background.",bt))

        storyAdd(PageBreak())
        storyAdd(Paragraph("Here we should have only light green background.",bt))


        doc.multiBuild(story)


#noruntests
def makeSuite():
    return makeSuiteForClasses(IndentTestCase)


#noruntests
if __name__ == "__main__":
    unittest.TextTestRunner().run(makeSuite())
    printLocation()
