"""Tests for the reportlab.platypus.paragraphs module.
"""

import sys

from string import split, strip, join, whitespace
from operator import truth
from types import StringType, ListType

from reportlab.test import unittest
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.platypus.paraparser import ParaParser
from reportlab.platypus.flowables import Flowable
from reportlab.lib.colors import Color
from reportlab.lib.enums import TA_LEFT, TA_RIGHT, TA_CENTER, TA_JUSTIFY
from reportlab.lib.utils import _className
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from copy import deepcopy
from reportlab.lib.abag import ABag

from reportlab.platypus.paragraph import *
from reportlab.platypus.paragraph import _getFragWords


class FragmentTestCase(unittest.TestCase):
    "Test fragmentation of paragraphs."
    
    def test1(self):
        "Test empty paragraph."

        styleSheet = getSampleStyleSheet()
        B = styleSheet['BodyText']
        text = ''
        P = Paragraph(text, B)
        frags = map(lambda f:f.text, P.frags)
        assert frags == []


    def test2(self):
        "Test simple paragraph."

        styleSheet = getSampleStyleSheet()
        B = styleSheet['BodyText']
        text = "X<font name=Courier>Y</font>Z"
        P = Paragraph(text, B)
        frags = map(lambda f:f.text, P.frags)
        assert frags == ['X', 'Y', 'Z']


def makeSuite():
    suite = unittest.TestSuite()
    
    suite.addTest(FragmentTestCase('test1'))
    suite.addTest(FragmentTestCase('test2'))

    return suite


if __name__ == "__main__":
    unittest.TextTestRunner().run(makeSuite())
    
