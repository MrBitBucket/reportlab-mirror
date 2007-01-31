#Copyright ReportLab Europe Ltd. 2000-2004
#see license.txt for license details
#history http://www.reportlab.co.uk/cgi-bin/viewcvs.cgi/public/reportlab/trunk/reportlab/test/test_platypus_paragraphs.py
"""Tests for the reportlab.platypus.paragraphs module.
"""

import sys, os
from string import split, strip, join, whitespace
from operator import truth
from types import StringType, ListType

from reportlab.test import unittest
from reportlab.test.utils import makeSuiteForClasses, outputfile, printLocation

from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.platypus.paraparser import ParaParser
from reportlab.platypus.flowables import Flowable
from reportlab.lib.colors import Color
from reportlab.lib.units import cm
from reportlab.lib.enums import TA_LEFT, TA_RIGHT, TA_CENTER, TA_JUSTIFY
from reportlab.lib.utils import _className
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus.paragraph import Paragraph
from reportlab.platypus.frames import Frame, ShowBoundaryValue
from reportlab.platypus.doctemplate import PageTemplate, BaseDocTemplate, PageBreak, NextPageTemplate
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
        frame2 = Frame(2.5*cm, 2.5*cm, 310, 25*cm, id='F2')
        self.allowSplitting = 0
        apply(BaseDocTemplate.__init__, (self, filename), kw)
        template = PageTemplate('normal', [frame1], myMainPageFrame)
        template1 = PageTemplate('special', [frame2], myMainPageFrame)
        self.addPageTemplates([template,template1])

class ParagraphCorners(unittest.TestCase):
    "some corner cases which should parse"
    def check(text,bt = getSampleStyleSheet()['BodyText']):
        try:
            P = Paragraph(text,st)
        except:
            raise AssertionError("'%s' should parse"%text)
            
    def test0(self):
        self.check('<para />')
        self.check('<para/>')
        self.check('\t\t\t\n\n\n<para />')
        self.check('\t\t\t\n\n\n<para/>')
        self.check('<para\t\t\t\t/>')
        self.check('<para></para>')
        self.check('<para>      </para>')
        self.check('\t\t\n\t\t\t   <para>      </para>')
        
class ParagraphSplitTestCase(unittest.TestCase):
    "Test multi-page splitting of paragraphs (eyeball-test)."

    def test0(self):
        "This makes one long multi-page paragraph."

        # Build story.
        story = []
        styleSheet = getSampleStyleSheet()
        bt = styleSheet['BodyText']
        text = '''If you imagine that the box of X's tothe left is
an image, what I want to be able to do is flow a
series of paragraphs around the image
so that once the bottom of the image is reached, then text will flow back to the
left margin. I know that it would be possible to something like this
using tables, but I can't see how to have a generic solution.
There are two examples of this in the demonstration section of the reportlab
site.
If you look at the "minimal" euro python conference brochure, at the end of the
timetable section (page 8), there are adverts for "AdSu" and "O'Reilly". I can
see how the AdSu one might be done generically, but the O'Reilly, unsure...
I guess I'm hoping that I've missed something, and that
it's actually easy to do using platypus.
'''
        from reportlab.platypus.flowables import ParagraphAndImage, Image
        from reportlab.lib.utils import _RL_DIR
        gif = os.path.join(_RL_DIR,'test','pythonpowered.gif')
        story.append(ParagraphAndImage(Paragraph(text,bt),Image(gif)))
        phrase = 'This should be a paragraph spanning at least three pages. '
        description = ''.join([('%d: '%i)+phrase for i in xrange(250)])
        story.append(ParagraphAndImage(Paragraph(description, bt),Image(gif),side='left'))

        doc = MyDocTemplate(outputfile('test_platypus_paragraphandimage.pdf'))
        doc.multiBuild(story)

    def test1(self):
        "This makes one long multi-page paragraph."

        # Build story.
        story = []
        styleSheet = getSampleStyleSheet()
        h3 = styleSheet['Heading3']
        bt = styleSheet['BodyText']
        text = '''If you imagine that the box of X's tothe left is
an image, what I want to be able to do is flow a
series of paragraphs around the image
so that once the bottom of the image is reached, then text will flow back to the
left margin. I know that it would be possible to something like this
using tables, but I can't see how to have a generic solution.
There are two examples of this in the demonstration section of the reportlab
site.
If you look at the "minimal" euro python conference brochure, at the end of the
timetable section (page 8), there are adverts for "AdSu" and "O'Reilly". I can
see how the AdSu one might be done generically, but the O'Reilly, unsure...
I guess I'm hoping that I've missed something, and that
it's actually easy to do using platypus.We can do greek letters <greek>mDngG</greek>. This should be a
u with a dieresis on top &lt;unichar code=0xfc/&gt;="<unichar code=0xfc/>" and this &amp;#xfc;="&#xfc;" and this \\xc3\\xbc="\xc3\xbc". On the other hand this
should be a pound sign &amp;pound;="&pound;" and this an alpha &amp;alpha;="&alpha;". You can have links in the page <link href=http://www.reportlab.com color=blue>ReportLab</link> &amp; <a href=http://www.reportlab.org color=green>ReportLab.org</a>.
Use scheme "pdf:" to indicate an external PDF link, "http:", "https:" to indicate an external link eg something to open in
your browser. If an internal link begins with something that looks like a scheme, precede with "document:". <strike>This text should have a strike through it.</strike>
'''
        from reportlab.platypus.flowables import ImageAndFlowables, Image
        from reportlab.lib.utils import _RL_DIR
        gif = os.path.join(_RL_DIR,'test','pythonpowered.gif')
        heading = Paragraph('This is a heading',h3)
        story.append(ImageAndFlowables(Image(gif),[heading,Paragraph(text,bt)]))
        phrase = 'This should be a paragraph spanning at least three pages. '
        description = ''.join([('%d: '%i)+phrase for i in xrange(250)])
        story.append(ImageAndFlowables(Image(gif),[heading,Paragraph(description, bt)],imageSide='left'))
        story.append(NextPageTemplate('special'))
        story.append(PageBreak())
        story.append(ImageAndFlowables(
                        Image(gif,width=280,height=120),
                        Paragraph('''The concept of an integrated one box solution for advanced voice and
data applications began with the introduction of the IMACS. The
IMACS 200 carries on that tradition with an integrated solution
optimized for smaller port size applications that the IMACS could not
economically address. An array of the most popular interfaces and
features from the IMACS has been bundled into a small 2U chassis
providing the ultimate in ease of installation.''',
                        style=ParagraphStyle(
                                name="base",
                                fontName="Helvetica",
                                leading=12,
                                leftIndent=0,
                                firstLineIndent=0,
                                spaceBefore = 9.5,
                                fontSize=9.5,
                                )
                            ),
                    imageSide='left',
                    )
                )
        story.append(ImageAndFlowables(
                        Image(gif,width=240,height=120),
                        Paragraph('''The concept of an integrated one box solution for advanced voice and
data applications began with the introduction of the IMACS. The
IMACS 200 carries on that tradition with an integrated solution
optimized for smaller port size applications that the IMACS could not
economically address. An array of the most popular interfaces and
features from the IMACS has been bundled into a small 2U chassis
providing the ultimate in ease of installation.''',
                        style=ParagraphStyle(
                                name="base",
                                fontName="Helvetica",
                                leading=12,
                                leftIndent=0,
                                firstLineIndent=0,
                                spaceBefore = 9.5,
                                fontSize=9.5,
                                )
                            ),
                    imageSide='left',
                    )
                )

        
        doc = MyDocTemplate(outputfile('test_platypus_imageandflowables.pdf'),showBoundary=1)
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

class ULTestCase(unittest.TestCase):
    "Test underlining and overstriking of paragraphs."
    def testUl(self):
        from reportlab.platypus import BaseDocTemplate, PageTemplate, Frame, PageBegin
        from reportlab.lib.units import inch
        from reportlab.platypus.flowables import AnchorFlowable
        class MyDocTemplate(BaseDocTemplate):
            _invalidInitArgs = ('pageTemplates',)

            def __init__(self, filename, **kw):
                self.allowSplitting = 0
                kw['showBoundary']=1
                BaseDocTemplate.__init__(self, filename, **kw)
                self.addPageTemplates(
                        [
                        PageTemplate('normal',
                                [Frame(inch, inch, 6.27*inch, 9.69*inch, id='first',topPadding=0,rightPadding=0,leftPadding=0,bottomPadding=0,showBoundary=ShowBoundaryValue(color="red"))],
                                ),
                        ])

        styleSheet = getSampleStyleSheet()
        normal = ParagraphStyle(name='normal',fontName='Times-Roman',fontSize=12,leading=1.2*12,parent=styleSheet['Normal'])
        normal_sp = ParagraphStyle(name='normal_sp',parent=normal,alignment=TA_JUSTIFY,spaceBefore=12)
        normal_just = ParagraphStyle(name='normal_just',parent=normal,alignment=TA_JUSTIFY)
        normal_right = ParagraphStyle(name='normal_right',parent=normal,alignment=TA_RIGHT)
        normal_center = ParagraphStyle(name='normal_center',parent=normal,alignment=TA_CENTER)
        normal_indent = ParagraphStyle(name='normal_indent',firstLineIndent=0.5*inch,parent=normal)
        normal_indent_lv_2 = ParagraphStyle(name='normal_indent_lv_2',firstLineIndent=1.0*inch,parent=normal)
        texts = ['''Furthermore, a subset of English sentences interesting on quite
independent grounds is not quite equivalent to a stipulation to place
the constructions into these various categories.''',
        '''We will bring evidence in favor of
The following thesis:  most of the methodological work in modern
linguistics can be defined in such a way as to impose problems of
phonemic and morphological analysis.''']
        story =[]
        a = story.append
        a(Paragraph("This should &lt;a href=\"#theEnd\" color=\"blue\"&gt;<a href=\"#theEnd\" color=\"blue\">jump</a>&lt;/a&gt; jump to the end!",style=normal))
        a(Paragraph("This should &lt;a href=\"#thePenultimate\" color=\"blue\"&gt;<a href=\"#thePenultimate\" color=\"blue\">jump</a>&lt;/a&gt; jump to the penultimate page!",style=normal))
        a(Paragraph("This should &lt;a href=\"#theThird\" color=\"blue\"&gt;<a href=\"#theThird\" color=\"blue\">jump</a>&lt;/a&gt; jump to a justified para!",style=normal))
        a(Paragraph("This should &lt;a href=\"#theFourth\" color=\"blue\"&gt;<a href=\"#theFourth\" color=\"blue\">jump</a>&lt;/a&gt; jump to an indented para!",style=normal))
        for mode in (0,1):
            text0 = texts[0]
            text1 = texts[1]
            if mode:
                text0 = text0.replace('English sentences','<b>English sentences</b>').replace('quite equivalent','<i>quite equivalent</i>')
                text1 = text1.replace('the methodological work','<b>the methodological work</b>').replace('to impose problems','<i>to impose problems</i>')
            for t in ('u','strike'):
                for n in xrange(6):
                    for s in (normal,normal_center,normal_right,normal_just,normal_indent, normal_indent_lv_2):
                        if n==4 and s==normal_center and t=='strike' and mode==1:
                            a(Paragraph("<font color=green>The second jump at the beginning should come here &lt;a name=\"thePenultimate\"/&gt;<a name=\"thePenultimate\"/>!</font>",style=normal))
                        elif n==4 and s==normal_just and t=='strike' and mode==1:
                            a(Paragraph("<font color=green>The third jump at the beginning should come just below here to a paragraph with just an a tag in it!</font>",style=normal))
                            a(Paragraph("<a name=\"theThird\"/>",style=normal))
                        elif n==4 and s==normal_indent and t=='strike' and mode==1:
                            a(Paragraph("<font color=green>The fourth jump at the beginning should come just below here!</font>",style=normal))
                            a(AnchorFlowable('theFourth'))
                        a(Paragraph('n=%d style=%s tag=%s'%(n,s.name,t),style=normal_sp))
                        a(Paragraph('%s<%s>%s</%s>. %s <%s>%s</%s>. %s' % (
                        (s==normal_indent_lv_2 and '<seq id="document" inc="no"/>.<seq id="document_lv_2"/>' or ''),
                        t,' '.join((n+1)*['A']),t,text0,t,' '.join((n+1)*['A']),t,text1),
                        style=s))
        a(Paragraph("The jump at the beginning should come here &lt;a name=\"theEnd\"/&gt;<a name=\"theEnd\"/>!",style=normal))
        doc = MyDocTemplate(outputfile('test_platypus_paragraphs_ul.pdf'))
        doc.build(story)

class JustifyTestCase(unittest.TestCase):
    "Test justification of paragraphs."
    def testUl(self):
        from reportlab.platypus import BaseDocTemplate, PageTemplate, Frame, PageBegin
        from reportlab.lib.units import inch
        class MyDocTemplate(BaseDocTemplate):
            _invalidInitArgs = ('pageTemplates',)

            def __init__(self, filename, **kw):
                self.allowSplitting = 0
                BaseDocTemplate.__init__(self, filename, **kw)
                self.addPageTemplates(
                        [
                        PageTemplate('normal',
                                [Frame(inch, inch, 6.27*inch, 9.69*inch, id='first',topPadding=0,rightPadding=0,leftPadding=0,bottomPadding=0,showBoundary=ShowBoundaryValue(color="red"))],
                                ),
                        ])

        styleSheet = getSampleStyleSheet()
        normal = ParagraphStyle(name='normal',fontName='Times-Roman',fontSize=12,leading=1.2*12,parent=styleSheet['Normal'])
        normal_sp = ParagraphStyle(name='normal_sp',parent=normal,alignment=TA_JUSTIFY,spaceBefore=12)
        normal_just = ParagraphStyle(name='normal_just',parent=normal,alignment=TA_JUSTIFY,spaceAfter=12)
        normal_right = ParagraphStyle(name='normal_right',parent=normal,alignment=TA_RIGHT)
        normal_center = ParagraphStyle(name='normal_center',parent=normal,alignment=TA_CENTER)
        normal_indent = ParagraphStyle(name='normal_indent',firstLineIndent=0.5*inch,parent=normal)
        normal_indent_lv_2 = ParagraphStyle(name='normal_indent_lv_2',firstLineIndent=1.0*inch,parent=normal)
        text0 = '''Furthermore, a subset of English sentences interesting on quite
independent grounds is not quite equivalent to a stipulation to place
the constructions into these various categories. We will bring evidence in favor of
The following thesis:  most of the methodological work in modern
linguistics can be defined in such a way as to impose problems of
phonemic and morphological analysis.'''
        story =[]
        a = story.append
        for mode in (0,1,2,3):
            text = text0
            if mode==1:
                text = text.replace('English sentences','<b>English sentences</b>').replace('quite equivalent','<i>quite equivalent</i>')
                text = text.replace('the methodological work','<b>the methodological work</b>').replace('to impose problems','<i>to impose problems</i>')
                a(Paragraph('Justified paragraph in normal/bold/italic font',style=normal))
            elif mode==2:
                text = '<b>%s</b>' % text
                a(Paragraph('Justified paragraph in bold font',style=normal))
            elif mode==3:
                text = '<i>%s</i>' % text
                a(Paragraph('Justified paragraph in italic font',style=normal))
            else:
                a(Paragraph('Justified paragraph in normal font',style=normal))

            a(Paragraph(text,style=normal_just))
        doc = MyDocTemplate(outputfile('test_platypus_paragraphs_just.pdf'))
        doc.build(story)

#noruntests
def makeSuite():
    return makeSuiteForClasses(FragmentTestCase, ParagraphSplitTestCase, ULTestCase, JustifyTestCase)

#noruntests
if __name__ == "__main__":
    unittest.TextTestRunner().run(makeSuite())
    printLocation()
