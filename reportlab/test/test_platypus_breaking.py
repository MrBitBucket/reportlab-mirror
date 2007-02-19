#Copyright ReportLab Europe Ltd. 2000-2004
#see license.txt for license details
#history http://www.reportlab.co.uk/cgi-bin/viewcvs.cgi/public/reportlab/trunk/reportlab/test/test_platypus_breaking.py
"""Tests pageBreakBefore, frameBreakBefore, keepWithNext...
"""

import sys, os, time
from string import split, strip, join, whitespace
from operator import truth
from types import StringType, ListType

from reportlab.test import unittest
from reportlab.test.utils import makeSuiteForClasses, outputfile, printLocation

from reportlab.platypus.flowables import Flowable
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.lib.enums import TA_LEFT, TA_RIGHT, TA_CENTER, TA_JUSTIFY
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus.paragraph import Paragraph
from reportlab.platypus.frames import Frame
from reportlab.lib.randomtext import randomText, PYTHON
from reportlab.platypus.doctemplate import PageTemplate, BaseDocTemplate, Indenter, SimpleDocTemplate
from reportlab.platypus.paragraph import *


def myMainPageFrame(canvas, doc):
    "The page frame used for all PDF documents."

    canvas.saveState()
    canvas.setFont('Times-Roman', 12)
    pageNumber = canvas.getPageNumber()
    canvas.drawString(10*cm, cm, str(pageNumber))
    canvas.restoreState()


class MyDocTemplate(BaseDocTemplate):
    _invalidInitArgs = ('pageTemplates',)

    def __init__(self, filename, **kw):
        frame1 = Frame(2.5*cm, 15.5*cm, 6*cm, 10*cm, id='F1')
        frame2 = Frame(11.5*cm, 15.5*cm, 6*cm, 10*cm, id='F2')
        frame3 = Frame(2.5*cm, 2.5*cm, 6*cm, 10*cm, id='F3')
        frame4 = Frame(11.5*cm, 2.5*cm, 6*cm, 10*cm, id='F4')
        self.allowSplitting = 0
        self.showBoundary = 1
        apply(BaseDocTemplate.__init__, (self, filename), kw)
        template = PageTemplate('normal', [frame1, frame2, frame3, frame4], myMainPageFrame)
        self.addPageTemplates(template)

_text1='''Furthermore, the fundamental error of regarding functional notions as
categorial delimits a general convention regarding the forms of the
grammar.  I suggested that these results would follow from the
assumption that the descriptive power of the base component may remedy
and, at the same time, eliminate a descriptive fact.  Thus a subset of
English sentences interesting on quite independent grounds raises
serious doubts about the ultimate standard that determines the accuracy
of any proposed grammar.  Of course, the natural general principle that
will subsume this case can be defined in such a way as to impose the
strong generative capacity of the theory.  By combining adjunctions and
certain deformations, the descriptive power of the base component is not
subject to the levels of acceptability from fairly high (e.g. (99a)) to
virtual gibberish (e.g. (98d)).
'''
def _test0(self):
    "This makes one long multi-page paragraph."

    # Build story.
    story = []
    a = story.append

    styleSheet = getSampleStyleSheet()
    h1 = styleSheet['Heading1']
    h1.pageBreakBefore = 1
    h1.keepWithNext = 1

    h2 = styleSheet['Heading2']
    h2.frameBreakBefore = 1
    h2.keepWithNext = 1

    h3 = styleSheet['Heading3']
    h3.backColor = colors.cyan
    h3.keepWithNext = 1

    bt = styleSheet['BodyText']
    a(Paragraph("""
        Subsequent pages test pageBreakBefore, frameBreakBefore and
        keepTogether attributes.  Generated at %s.  The number in brackets
        at the end of each paragraph is its position in the story. (%d)""" % (
            time.ctime(time.time()), len(story)), bt))

    for i in xrange(10):
        a(Paragraph('Heading 1 always starts a new page (%d)' % len(story), h1))
        for j in xrange(3):
            a(Paragraph('Heading1 paragraphs should always'
                            'have a page break before.  Heading 2 on the other hand'
                            'should always have a FRAME break before (%d)' % len(story), bt))
            a(Paragraph('Heading 2 always starts a new frame (%d)' % len(story), h2))
            a(Paragraph('Heading1 paragraphs should always'
                            'have a page break before.  Heading 2 on the other hand'
                            'should always have a FRAME break before (%d)' % len(story), bt))
            for j in xrange(3):
                a(Paragraph(randomText(theme=PYTHON, sentences=2)+' (%d)' % len(story), bt))
                a(Paragraph('I should never be at the bottom of a frame (%d)' % len(story), h3))
                a(Paragraph(randomText(theme=PYTHON, sentences=1)+' (%d)' % len(story), bt))

    a(Paragraph('Now we do &lt;br/&gt; tests', h1))
    a(Paragraph('First off no br tags',h3))
    a(Paragraph(_text1,bt))
    a(Paragraph("&lt;br/&gt; after 'the' in line 4",h3))
    a(Paragraph(_text1.replace('forms of the','forms of the<br/>',1),bt))
    a(Paragraph("2*&lt;br/&gt; after 'the' in line 4",h3))
    a(Paragraph(_text1.replace('forms of the','forms of the<br/><br/>',1),bt))
    a(Paragraph("&lt;br/&gt; after 'I suggested ' in line 5",h3))
    a(Paragraph(_text1.replace('I suggested ','I suggested<br/>',1),bt))
    a(Paragraph("2*&lt;br/&gt; after 'I suggested ' in line 5",h3))
    a(Paragraph(_text1.replace('I suggested ','I suggested<br/><br/>',1),bt))
    a(Paragraph("&lt;br/&gt; at the end of the paragraph!",h3))
    a(Paragraph("""text one<br/>text two<br/>""",bt))
    a(Paragraph("Border with &lt;nr/&gt; at the end of the paragraph!",h3))
    bt1 = ParagraphStyle('bodyText1',bt)
    bt1.borderWidth = 0.5
    bt1.borderColor = colors.toColor('red')
    bt1.backColor = colors.pink
    bt1.borderRadius = 2
    bt1.borderPadding = 3
    a(Paragraph("""text one<br/>text two<br/>""",bt1))
    a(Paragraph("Border no &lt;nr/&gt; at the end of the paragraph!",h3))
    bt1 = ParagraphStyle('bodyText1',bt)
    bt1.borderWidth = 0.5
    bt1.borderColor = colors.toColor('red')
    bt1.backColor = colors.pink
    bt1.borderRadius = 2
    bt1.borderPadding = 3
    a(Paragraph("""text one<br/>text two""",bt1))
    a(Paragraph("Different border style!",h3))
    bt2 = ParagraphStyle('bodyText1',bt1)
    bt2.borderWidth = 1.5
    bt2.borderColor = colors.toColor('blue')
    bt2.backColor = colors.gray
    bt2.borderRadius = 3
    bt2.borderPadding = 3
    a(Paragraph("""text one<br/>text two<br/>""",bt2))

    doc = MyDocTemplate(outputfile('test_platypus_breaking.pdf'))
    doc.multiBuild(story)


class BreakingTestCase(unittest.TestCase):
    "Test multi-page splitting of paragraphs (eyeball-test)."
    def test0(self):
        _test0(self)

    def test1(self):
        '''Ilpo Nyyss\xf6nen posted this broken test'''
        normalStyle = ParagraphStyle(name = 'normal')
        keepStyle = ParagraphStyle(name = 'keep', keepWithNext = True)
        content = [
            Paragraph("line 1", keepStyle),
            Indenter(left = 1 * cm),
            Paragraph("line 2", normalStyle),
            ]
        doc = SimpleDocTemplate(outputfile('test_platypus_breaking1.pdf'))
        doc.build(content)


def makeSuite():
    return makeSuiteForClasses(BreakingTestCase)


#noruntests
if __name__ == "__main__": #NORUNTESTS
    if 'debug' in sys.argv:
        _test0(None)
    else:
        unittest.TextTestRunner().run(makeSuite())
        printLocation()
