#copyright ReportLab Inc. 2000-2001
#see license.txt for license details
#history http://cvs.sourceforge.net/cgi-bin/cvsweb.cgi/reportlab/test/test_platypus_paragraphs.py?cvsroot=reportlab
#$Header: /tmp/reportlab/reportlab/test/test_platypus_paragraphs.py,v 1.9 2002/07/24 19:56:38 andy_robinson Exp $
"""Tests for the reportlab.platypus.paragraphs module.
"""

import sys, os, tempfile
from string import split, strip, join, whitespace
from operator import truth
from types import StringType, ListType

from reportlab.test import unittest
from reportlab.test.utils import makeSuiteForClasses

from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.platypus.paraparser import ParaParser
from reportlab.platypus.flowables import Flowable
from reportlab.lib.colors import Color
from reportlab.lib.units import cm
from reportlab.lib.enums import TA_LEFT, TA_RIGHT, TA_CENTER, TA_JUSTIFY
from reportlab.lib.utils import _className
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus.paragraph import Paragraph
from reportlab.platypus.frames import Frame
from reportlab.platypus.doctemplate \
     import PageTemplate, BaseDocTemplate
from reportlab.platypus import tableofcontents
from reportlab.platypus.tableofcontents import TableOfContents
from reportlab.platypus.tables import TableStyle, Table
from reportlab.platypus.paragraph import *
from reportlab.platypus.paragraph import _getFragWords


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
        apply(BaseDocTemplate.__init__, (self, filename), kw)
        template = PageTemplate('normal', [frame1], myMainPageFrame)
        self.addPageTemplates(template)


class ParagraphSplitTestCase(unittest.TestCase):
    "Test multi-page splitting of paragraphs (eyeball-test)."

    def test0(self):
        "This makes one long multi-page paragraph."

        # Build story.
        story = []
        styleSheet = getSampleStyleSheet()
        bt = styleSheet['BodyText']

        phrase = 'This should be a paragraph spanning at least three pages. '
        description = phrase * 250
        story.append(Paragraph(description, bt))

        doc = MyDocTemplate('test_paragraphs_splitting.pdf')
        doc.multiBuild(story)


class FragmentTestCase(unittest.TestCase):
    "Test fragmentation of paragraphs."

    def test0(self):
        "Test empty paragraph."

        styleSheet = getSampleStyleSheet()
        B = styleSheet['BodyText']
        text = ''
        P = Paragraph(text, B)
        frags = map(lambda f:f.text, P.frags)
        assert frags == []


    def test1(self):
        "Test simple paragraph."

        styleSheet = getSampleStyleSheet()
        B = styleSheet['BodyText']
        text = "X<font name=Courier>Y</font>Z"
        P = Paragraph(text, B)
        frags = map(lambda f:f.text, P.frags)
        assert frags == ['X', 'Y', 'Z']


#noruntests
def makeSuite():
    return makeSuiteForClasses(FragmentTestCase, ParagraphSplitTestCase)


#noruntests
if __name__ == "__main__":
    unittest.TextTestRunner().run(makeSuite())

