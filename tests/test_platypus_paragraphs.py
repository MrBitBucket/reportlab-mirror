#Copyright ReportLab Europe Ltd. 2000-2017
#see license.txt for license details
"""Tests for the reportlab.platypus.paragraphs module.
"""
__version__='3.3.0'
from reportlab.lib.testutils import (setOutDir,makeSuiteForClasses, outputfile, 
                                    printLocation, rlSkipUnless, haveDejaVu, DEJAVUSANS)
setOutDir(__name__)
import sys, os, unittest
from operator import truth
from reportlab.pdfgen.canvas import Canvas, ShowBoundaryValue
from reportlab.pdfbase.pdfmetrics import stringWidth, registerFont, registerFontFamily, getFont
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus.paraparser import ParaParser
from reportlab.platypus.flowables import Flowable, DocAssert
from reportlab.lib.colors import Color
from reportlab.lib.units import cm
from reportlab.lib.enums import TA_LEFT, TA_RIGHT, TA_CENTER, TA_JUSTIFY
from reportlab.lib.utils import _className, asBytes, asUnicode, asNative
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus.xpreformatted import XPreformatted
from reportlab.platypus import Frame
from reportlab.platypus.doctemplate import PageTemplate, BaseDocTemplate, PageBreak, NextPageTemplate
from reportlab.platypus import tableofcontents
from reportlab.platypus.tableofcontents import TableOfContents
from reportlab.platypus.tables import TableStyle, Table
from reportlab.platypus.paragraph import Paragraph, _getFragWords, _splitWord, _splitFragWord, \
                                            _fragWordSplitRep, ABag, pyphen
from reportlab.rl_config import trustedHosts, trustedSchemes
from reportlab.pdfgen.textobject import rtlSupport

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
        BaseDocTemplate.__init__(self, filename, **kw)
        template = PageTemplate('normal', [frame1], myMainPageFrame)
        template1 = PageTemplate('special', [frame2], myMainPageFrame)
        template2 = PageTemplate('template2', [Frame(395, 108, 165, 645, id='second2')])
        self.addPageTemplates([template,template1,template2])

class ParagraphCorners(unittest.TestCase):
    "some corner cases which should parse"
    def check(self,text,bt = getSampleStyleSheet()['BodyText']):
        try:
            P = Paragraph(text,style=bt)
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

    def test1(self):
        "This makes several special paragraphs."

        # Build story.
        story = []
        styleSheet = getSampleStyleSheet()
        bt = styleSheet['BodyText']
        btN = ParagraphStyle('BodyTextTTNone',parent=bt,textTransform='none')
        btL = ParagraphStyle('BodyTextTTLower',parent=bt,textTransform='lowercase')
        btU = ParagraphStyle('BodyTextTTUpper',parent=bt,textTransform='uppercase')
        btC = ParagraphStyle('BodyTextTTCapitalize',parent=bt,textTransform='capitalize')
        story.append(Paragraph('''This should be ORDINARY text.''',style=bt))
        story.append(Paragraph('''This should be ORDINARY text.''',style=btN))
        story.append(Paragraph('''This should be LOWER text.''',style=btL))
        story.append(Paragraph('''This should be upper text.''',style=btU))
        story.append(Paragraph('''This should be cAPITALIZED text.''',style=btC))

        story.append(Paragraph('''T<i>hi</i>s shoul<font color="red">d b</font>e <b>ORDINARY</b> text.''',style=bt))
        story.append(Paragraph('''T<i>hi</i>s shoul<font color="red">d b</font>e <b>ORDINARY</b> text.''',style=btN))
        story.append(Paragraph('''T<i>hi</i>s shoul<font color="red">d b</font>e <b>LOWER</b> text.''',style=btL))
        story.append(Paragraph('''T<i>hi</i>s shoul<font color="red">d b</font>e <b>upper</b> text.''',style=btU))
        story.append(Paragraph('''T<i>hi</i>s shoul<font color="red">d b</font>e <b>cAPITALIZED</b> text.''',style=btC))
        doc = MyDocTemplate(outputfile('test_platypus_specialparagraphs.pdf'))
        doc.multiBuild(story)

    def test2(self):
        '''CJK splitting in multi-frag case'''
        style = ParagraphStyle('test', wordWrap = 'CJK')
        p = Paragraph('bla <i>blub</i> '*130 , style)
        aW,aH=439.275590551,121.88976378
        w,h=p.wrap(aW,aH)
        S=p.split(aW,aH)
        assert len(S)==2, 'Multi frag CJK splitting failed'
        w0,h0=S[0].wrap(aW,aH)
        assert h0<=aH,'Multi-frag CJK split[0] has wrong height %s >= available %s' % (H0,aH)
        w1,h1=S[1].wrap(aW,aH)
        assert h0+h1==h, 'Multi-frag-CJK split[0].height(%s)+split[1].height(%s) don\'t add to original %s' % (h0,h1,h)

    def test3(self):
        '''compare CJK splitting in some edge cases'''
        from reportlab.platypus.paragraph import Paragraph
        from reportlab.lib.styles import ParagraphStyle
        from reportlab.pdfbase import pdfmetrics
        from reportlab.lib.enums import TA_LEFT
        sty = ParagraphStyle('A')
        sty.fontSize = 15
        sty.leading = sty.fontSize*1.2
        sty.fontName = 'Courier'
        sty.alignment = TA_LEFT
        sty.wordWrap = 'CJK'
        p0=Paragraph('ABCDEFGHIJKL]N',sty)
        p1=Paragraph('AB<font color="red">C</font>DEFGHIJKL]N',sty)
        canv = Canvas(outputfile('test_platypus_paragraph_cjk3.pdf'))
        ix = len(canv._code)
        aW = pdfmetrics.stringWidth('ABCD','Courier',15)
        w,h=p0.wrap(aW,1000000)
        y = canv._pagesize[1]-72-h
        p0.drawOn(canv,72,y)
        w,h=p1.wrap(aW,1000000)
        y -= h+10
        p1.drawOn(canv,72,y)
        w,h=p0.wrap(aW*0.25-2,1000000)
        y -= h+10
        p0.drawOn(canv,72,y)
        w,h=p1.wrap(aW/4.-2,1000000)
        y -= h+10
        p1.drawOn(canv,72,y)
        assert canv._code[ix:]==['q', '1 0 0 1 72 697.8898 cm', 'q', '0 0 0 rg', 'BT 1 0 0 1 0 57 Tm /F2 15 Tf 18 TL (ABCD) Tj T* (EFGH) Tj T* (IJKL]) Tj T* (N) Tj T* ET', 'Q', 'Q', 'q', '1 0 0 1 72 615.8898 cm', 'q', 'BT 1 0 0 1 0 57 Tm 18 TL /F2 15 Tf 0 0 0 rg (AB) Tj 1 0 0 rg (C) Tj 0 0 0 rg (D) Tj T* (EFGH) Tj T* (IJKL]) Tj T* (N) Tj T* ET', 'Q', 'Q', 'q', '1 0 0 1 72 353.8898 cm', 'q', '0 0 0 rg', 'BT 1 0 0 1 0 237 Tm /F2 15 Tf 18 TL (A) Tj T* (B) Tj T* (C) Tj T* (D) Tj T* (E) Tj T* (F) Tj T* (G) Tj T* (H) Tj T* (I) Tj T* (J) Tj T* (K) Tj T* (L) Tj T* (]) Tj T* (N) Tj T* ET', 'Q', 'Q', 'q', '1 0 0 1 72 91.88976 cm', 'q', 'BT 1 0 0 1 0 237 Tm 18 TL /F2 15 Tf 0 0 0 rg (A) Tj T* (B) Tj T* 1 0 0 rg (C) Tj T* 0 0 0 rg (D) Tj T* (E) Tj T* (F) Tj T* (G) Tj T* (H) Tj T* (I) Tj T* (J) Tj T* (K) Tj T* (L) Tj T* (]) Tj T* (N) Tj T* ET', 'Q', 'Q']
        canv.showPage()
        canv.save()

    def test4(self):
        from reportlab.platypus.paragraph import _SHYIndexedStr, stringWidth, _SHYWord, ABag, _shyUnsplit
        fontName = 'Helvetica'
        fontSize = 10
        f = ABag(fontName=fontName,fontSize=fontSize)
        sW = lambda _: stringWidth(_,fontName,fontSize)
        text = 'Super\xadcali\xadfragi\xadlistic\xadexpi\xadali\xaddocious'
        u = _SHYIndexedStr(text)
        self.assertEqual(u,'Supercalifragilisticexpialidocious','_SHYIndexStr not as expected')
        self.assertEqual(u._shyIndices,[5, 9, 14, 20, 24, 27], '_SHYIndexStr._shyIndices are wrong')
        shyW = _SHYWord([sW(u),(f,u)])
        hsw = shyW.shyphenate(shyW[0],50)
        self.assertTrue(hsw,'shyphenate failed')
        self.assertTrue(
                hsw[0][0] == 45.01
                and hsw[0][1][0].__dict__== ABag(fontName='Helvetica', fontSize=10).__dict__
                and hsw[0][1][1]=='Supercali-'
                and hsw[0][1][1]._shyIndices==[5,9], 'left part of shyphenate split failed')
        self.assertTrue(
                hsw[1][0] == 101.69000000000001
                and hsw[1][1][0].__dict__== ABag(fontName='Helvetica', fontSize=10).__dict__
                and hsw[1][1][1]=='fragilisticexpialidocious'
                and hsw[1][1][1]._shyIndices== [5, 11, 15, 18], 'right part of shyphenate split failed')
        uj = _shyUnsplit(hsw[0][1][1],hsw[1][1][1])
        self.assertTrue(
                uj == u
                and uj._shyIndices==u._shyIndices, '_shyUnsplit failed')

    def test5(self):
        '''some soft hyphenation'''
        from reportlab.pdfgen import canvas
        from reportlab.platypus import Frame, Paragraph
        from reportlab.lib.styles import ParagraphStyle

        pagesize = (80+20, 400)
        c = canvas.Canvas(  outputfile('test_platypus_soft_hyphenation.pdf'), pagesize=pagesize)
        f = Frame(10, 0, 68, 400,
                showBoundary=ShowBoundaryValue(dashArray=(1,1)),
                leftPadding=0,
                rightPadding=0,
                topPadding=0,
                bottomPadding=0,
                )
        style = ParagraphStyle(
            'normal', fontName='Helvetica', fontSize=12,
            embeddedHyphenation=1, splitLongWords=0, hyphenationLang='en-GB')
        shy = asNative('\xad')
        text = shy.join(('Super','cali','fragi','listic','expi','ali','docious'))
        f.addFromList([Paragraph(text, style)], c)
        text = '<span color="red">Super</span><span color="pink">&#173;cali&#173;</span>fragi&#173;listic&#173;expi&#173;ali&#173;docious'
        f.addFromList([Paragraph(text, style)], c)
        c.showPage()
        c.save() 

    def test_platypus_paragraphs_embedded2(self):
        from hashlib import md5 as hashlib_md5

        fontName = 'Helvetica'
        fontSize = 10

        texts = [asUnicode(text) for text
                in  [
                    b'UU\xc2\xadDIS\xc2\xadTU\xc2\xadSA\xc2\xadLA JA TAI\xc2\xadMIK\xc2\xadKO',
                    b'NUO\xc2\xadRI KAS\xc2\xadVA\xc2\xadTUS\xc2\xadMET\xc2\xadSIK\xc2\xadK\xc3\x96',
                    b'VART\xc2\xadTU\xc2\xadNUT KAS\xc2\xadVA\xc2\xadTUS\xc2\xadMET\xc2\xadSIK\xc2\xadK\xc3\x96',
                    b'UU\xc2\xadDIS\xc2\xadTUS-KYP\xc2\xadS\xc3\x84 MET\xc2\xadSIK\xc2\xadK\xc3\x96',
                    b'SIE\xc2\xadMEN- JA SUO-JUS\xc2\xadPUU-MET\xc2\xadSIK\xc2\xadK\xc3\x96',
                    b'E\xc2\xadRI-I\xc2\xadK\xc3\x84\xc2\xadIS-RA\xc2\xadKEN\xc2\xadTEI\xc2\xadNEN MET\xc2\xadSIK\xc2\xadK\xc3\x96',
                    ]
                ]
        maxWidth = stringWidth('VARTTUNUT KAS', fontName, fontSize)+0.5
        span = lambda _t, _c: "<span color='%s'>%s</span>" % (_c, _t)

        pagesize = (20+maxWidth, 800)
        c = Canvas(outputfile('test_platypus_paragraphs_embedded2.pdf'), pagesize=pagesize)

        expected = [
                (163, b':\n\x16\x8c\xa9\x87\xf4C\xe0\xe6\xfd/\x07\xe7\xde8'),
                (163, b'4\x98_\t\xd0\xde\x9a:8\xa7E\xfc\x13\xad\xfbk'),
                (163, b'9m\xec\xdfX\xe4\x85\xe9tL,\xe5ob\x13w'),
                (163, b"\xf39*6\x85\xd2\xf9`:<\xe8'\xa9\x8a\xec["),
                (163, b'\x85\x07\x83\xee\x8d\x11Bp\xd0p\xaa\xcbp\x98\xf4\xb7'),
                (163, b'\xf0"wp\x91vN\xc8<\xef\xe7\xc8s\xae\xf8\x10'),
                ]
        observed = []
        for eh in 0, 1, 2:
            for slw in 0, 1:
                f = Frame(10, 10, maxWidth, 780,
                        showBoundary=ShowBoundaryValue(dashArray=(1,1)),
                        leftPadding=0,
                        rightPadding=0,
                        topPadding=0,
                        bottomPadding=0,
                        )
                style = ParagraphStyle(
                    'normal', fontName=fontName, fontSize=fontSize,
                    embeddedHyphenation=eh, splitLongWords=slw,
                    hyphenationLang=None)
                f.addFromList([Paragraph('slw=%d eh=%d' % (slw,eh), style)], c)
                for text in texts:
                    f.addFromList([Paragraph(text, style)], c)
                    mfText = text.split('\xad')
                    mfText[0] = span(mfText[0],'red')
                    if len(mfText)>1:
                        mfText[1] = span(mfText[1],'pink')
                        if len(mfText)>2:
                            mfText[-1] = span(mfText[-1],'blue')
                    mfText = '&#173;'.join(mfText)
                    f.addFromList([Paragraph(mfText, style)], c)
                observed.append((len(c._code), hashlib_md5(b"".join((asBytes(b,"latin1") for b in c._code)),usedforsecurity=False).digest()))
                c.showPage()
        c.save() 
        self.assertEqual(observed, expected)

    def test_lele_img(self):
        from reportlab.pdfgen.canvas import Canvas
        from reportlab.platypus import Paragraph
        from reportlab.lib.styles import getSampleStyleSheet
        from reportlab.rl_config import defaultPageSize
        from reportlab.lib.units import cm
        from reportlab.lib.testutils import testsFolder

        styles = getSampleStyleSheet()
        c = Canvas(outputfile('test_lele_img.pdf'), pagesize=defaultPageSize)
        s = styles["Normal"]
        t = '<img src="%s/pythonpowered.gif" valign="middle"/>' % testsFolder
        p = Paragraph(t, s)
        owh = p.wrap(cm,cm)
        cx0 = len(c._code)
        p.drawOn(c, cm, 2*cm)
        xcode = ['q', '1 0 0 1 28.34646 56.69291 cm', 'q', 'q', '110 0 0 44 0 -16 cm', '/FormXob.00cb676cb2b2da8ec875fe2c13cf2496 Do', 'Q', 'BT 1 0 0 1 0 2 Tm 12 TL 110 0 Td /F1 10 Tf 12 TL  T* -110 0 Td ET', 'Q', 'Q']
        xwh = (28.346456692913385, 12)
        ocode = c._code[cx0:]
        c.showPage()
        c.save()
        self.assertEqual((owh,ocode),(xwh,xcode),
                "\n(owh,ocode)=%r\nfor test_lele_img.pdf doesn't match expected\n(xwh,xcode)=%r" %(
                    (xwh,xcode),(owh,ocode)))

class ParagraphSplitTestCase(unittest.TestCase):
    "Test multi-page splitting of paragraphs (eyeball-test)."

    def test0(self):
        "ParagraphSplitTestCase.test0"

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
        from reportlab.lib.testutils import testsFolder
        gif = os.path.join(testsFolder,'pythonpowered.gif')
        story.append(ParagraphAndImage(Paragraph(text,bt),Image(gif)))
        phrase = 'This should be a paragraph spanning at least three pages. '
        description = ''.join([('%d: '%i)+phrase for i in range(250)])
        story.append(ParagraphAndImage(Paragraph(description, bt),Image(gif),side='left'))

        doc = MyDocTemplate(outputfile('test_platypus_paragraphandimage.pdf'))
        doc.multiBuild(story)

    def test1(self):
        "ParagraphSplitTestCase.test1"

        # Build story.
        story = []
        styleSheet = getSampleStyleSheet()
        h3 = styleSheet['Heading3']
        bt = styleSheet['BodyText']
        st=ParagraphStyle(
                            name="base",
                            fontName="Helvetica",
                            leading=12,
                            leftIndent=0,
                            firstLineIndent=0,
                            spaceBefore = 9.5,
                            fontSize=9.5,
                            )
        text = b'''If you imagine that the box of X's to the left is
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
u with a dieresis on top &lt;unichar code=0xfc/&gt;="<unichar code="0xfc"/>" and this &amp;#xfc;="&#xfc;" and this \\xc3\\xbc="\xc3\xbc". On the other hand this
should be a pound sign &amp;pound;="&pound;" and this an alpha &amp;alpha;="&alpha;". You can have links in the page <link href="http://www.reportlab.com" color="blue">ReportLab</link> &amp; <a href="http://www.reportlab.org" color="green">ReportLab.org</a>.
Use scheme "pdf:" to indicate an external PDF link, "http:", "https:" to indicate an external link eg something to open in
your browser. If an internal link begins with something that looks like a scheme, precede with "document:". Empty hrefs should be allowed ie <a href="">&lt;a href=""&gt;test&lt;/a&gt;</a> should be allowed.
<u>This text should be underlined.</u><br/>
<strike>This text should have a strike through it.</strike><br/>
<span backcolor="yellow"><strike>This text should have a strike through it and be highlighted.</strike></span><br/>
<span backcolor="yellow"><strike><u>This text should have a strike through it and be highlighted and underlined.</u></strike></span><br/>
This should be a mailto link <a href="mailto:reportlab-users@lists2.reportlab.com"><font color="blue">reportlab-users at lists2.reportlab.com</font></a>.<br/>
This should be an underlined mailto link <a underline="1" href="mailto:reportlab-users@lists2.reportlab.com"><font color="blue">reportlab-users at lists2.reportlab.com</font></a>.<br/>
This should be a highlighted mailto link <span backcolor="yellow"><a href="mailto:reportlab-users@lists2.reportlab.com"><font color="blue">reportlab-users at lists2.reportlab.com</font></a></span>.<br/>
This should be a highlighted &amp; underlined mailto link <span backcolor="yellow"><a underline="1" ucolor="red" uwidth="0.01*F" href="mailto:reportlab-users@lists2.reportlab.com"><font color="blue">reportlab-users at lists2.reportlab.com</font></a></span>.<br/>
<u offset="-.125*F">Underlined <font size="-1">Underlined</font></u><br/>
This is A<sup><u>underlined</u></sup> as is A<u><sup>this</sup></u>
<u color="red">This is A<sup><u>underlined</u></sup> as is A<u><sup>this</sup></u></u>
'''
        from reportlab.platypus.flowables import ImageAndFlowables, Image
        from reportlab.lib.testutils import testsFolder
        gif = os.path.join(testsFolder,'pythonpowered.gif')
        heading = Paragraph('This is a heading',h3)
        story.append(ImageAndFlowables(Image(gif),[heading,Paragraph(text,bt)]))
        phrase = 'This should be a paragraph spanning at least three pages. '
        description = ''.join([('%d: '%i)+phrase for i in range(250)])
        story.append(ImageAndFlowables(Image(gif),[heading,Paragraph(description, bt)],imageSide='left'))
        story.append(NextPageTemplate('special'))
        story.append(PageBreak())
        VERA = ('Vera','VeraBd','VeraIt','VeraBI')
        for v in VERA:
            registerFont(TTFont(v,v+'.ttf'))
        registerFontFamily(*(VERA[:1]+VERA))
        story.append(ImageAndFlowables(
                        Image(gif,width=280,height=120),
                        Paragraph('''<font name="Vera">The <b>concept</b> of an <i>integrated</i> one <b><i>box</i></b> solution for <i><b>advanced</b></i> voice and
data applications began with the introduction of the IMACS. The
IMACS 200 carries on that tradition with an integrated solution
optimized for smaller port size applications that the IMACS could not
economically address. An array of the most popular interfaces and
features from the IMACS has been bundled into a small 2U chassis
providing the ultimate in ease of installation.</font>''',
                        style=st,
                        ),
                    imageSide='left',
                    )
                )
        story.append(Paragraph('Width 240 single frag',h3))
        story.append(ImageAndFlowables(
                        Image(gif,width=240,height=120),
                        Paragraph('''The concept of an integrated one box solution for advanced voice and
data applications began with the introduction of the IMACS. The
IMACS 200 carries on that tradition with an integrated solution
optimized for smaller port size applications that the IMACS could not
economically address. An array of the most popular interfaces and
features from the IMACS has been bundled into a small 2U chassis
providing the ultimate in ease of installation.''',
                        style=st,
                        ),
                    imageSide='left',
                    )
                )

        story.append(PageBreak())
        story.append(Paragraph('Image larger than the frame',h3))
        story.append(ImageAndFlowables(
                        Image(gif,width=6*110,height=6*44),
                        Paragraph('''The concept of an integrated one box solution for advanced voice and
data applications began with the introduction of the IMACS. The
IMACS 200 carries on that tradition with an integrated solution
optimized for smaller port size applications that the IMACS could not
economically address. An array of the most popular interfaces and
features from the IMACS has been bundled into a small 2U chassis
providing the ultimate in ease of installation.''',
                        style=st,
                        ),
                    imageSide='left',
                    )
                )
        text = '''With this clarification, an important property of these three types of
EC can be defined in such a way as to impose problems of phonemic and
morphological analysis.  Another superficial similarity is the interest
in simulation of behavior, this analysis of a formative as a pair of
sets of features does not readily tolerate a stipulation to place the
constructions into these various categories.  We will bring evidence in
favor of the following thesis:  the earlier discussion of deviance is
not to be considered in determining the extended c-command discussed in
connection with (34).  Another superficial similarity is the interest in
simulation of behavior, relational information may remedy and, at the
same time, eliminate a descriptive fact.  There is also a different
approach to the [unification] problem, the descriptive power of the base
component delimits the traditional practice of grammarians.'''
        gif = os.path.join(testsFolder,'pythonpowered.gif')
        heading = Paragraph('This is a heading',h3)
        story.append(NextPageTemplate('template2'))
        story.append(PageBreak())
        story.append(heading)
        story.append(ImageAndFlowables(Image(gif,width=66,height=81),[Paragraph(text,bt)],imageSide='left',imageRightPadding=10))

        story.append(NextPageTemplate('special'))
        story.append(PageBreak())
        story.append(Paragraph('Width 240, multi-frag free hyphenation',h3))
        story.append(ImageAndFlowables(
                        Image(gif,width=240,height=120),
                        Paragraph('''The concept of an <span color="red">integ</span><span color="green">rated</span> one box solution for advanced voice and
data applications began with the introduction of the IMACS. The
IMACS 200 carries on that tradition with an integrated solution
<span color="pink">optimized</span> for smaller port size applications that the IMACS could not
<span color="lightgreen">eco</span><span color="blue">nomically</span> address. An array of the most popular interfaces and
features from the IMACS has been bundled into a small 2U chassis
providing the ultimate in ease of installation.''',
                        style=st,
                        ),
                    imageSide='left',
                    )
                )
        story.append(PageBreak())
        story.append(Paragraph('Width 240, multi-frag soft hyphenation',h3))
        story.append(ImageAndFlowables(
                        Image(gif,width=240,height=120),
                        Paragraph('''The concept of an <span color="red">integ</span><span color="green">\xadrated</span> one box solution for advanced voice and
data applica\xadtions began with the in\xadtroduction of the IMACS. The
IMACS 200 carries on that tradition with an integrated solution
<span color="pink">op\xadtimized</span> for smaller port size applications that the IMACS could not
<span color="lightgreen">eco</span><span color="blue">\xadnomically</span> address. An array of the most popular interfaces and
fea\xadtures from the IMACS has been bundled into a small 2U chassis
providing the ultimate in ease of installation.''',
                        style=st,
                        ),
                    imageSide='left',
                    )
                )
        story.append(PageBreak())
        story.append(Paragraph('Width 240, single-frag soft hyphenation',h3))
        story.append(ImageAndFlowables(
                        Image(gif,width=240,height=120),
                        Paragraph('''The concept of an integ\xadrated one box solution for advanced voice and
data applica\xadtions began with the in\xadtroduction of the IMACS. The
IMACS 200 carries on that tradition with an integrated solution
op\xadtimized for smaller port size applications that the IMACS could not
eco\xadnomically address. An array of the most popular interfaces and
fea\xadtures from the IMACS has been bundled into a small 2U chassis
providing the ultimate in ease of installation.''',
                        style=st,
                        ),
                    imageSide='left',
                    )
                )
        doc = MyDocTemplate(outputfile('test_platypus_imageandflowables.pdf'),showBoundary=1)
        doc.multiBuild(story)

    @rlSkipUnless(rtlSupport,'no RTL support')
    def test1_RTL(self):
        "ParagraphSplitTestCase.test_RTL"
        from reportlab.platypus.flowables import ImageAndFlowables, Image
        from reportlab.lib.testutils import testsFolder
        from test_paragraphs import getAFont
        # Build story.
        fontName = getAFont()
        story = []
        styleSheet = getSampleStyleSheet()
        h3 = styleSheet['Heading3']
        bt = styleSheet['BodyText']
        h3.wordWrap = bt.wordWrap = 'RTL'
        h3.alignment = bt.alignment = TA_RIGHT
        h3.fontName = bt.fontName = fontName
        st=ParagraphStyle(
                            name="base",
                            fontName="Helvetica",
                            leading=12,
                            leftIndent=0,
                            firstLineIndent=0,
                            spaceBefore = 9.5,
                            fontSize=9.5,
                            wordWrap='RTL',
                            alignment=TA_RIGHT,
                            )
        text=b'''\xd7\x94\xd7\xa0\xd7\x93\xd7\xa1\xd7\xaa \xd7\x90\xd7\x99\xd7\xa0\xd7\x98\xd7\xa8\xd7\xa0\xd7\x98 \xd7\xa2\xd7\x9c
        \xd7\xa9\xd7\x9e\xd7\x95. \xd7\x91\xd7\x94 \xd7\xa2\xd7\x96\xd7\x94 \xd7\x90\xd7\x97\xd7\xa8\xd7\x95\xd7\xaa
        \xd7\x9c\xd7\xa2\xd7\xa8\xd7\x99\xd7\x9b\xd7\xaa \xd7\x94\xd7\xa0\xd7\x90\xd7\x9e\xd7\xa0\xd7\x99\xd7\x9d,
        \xd7\x94\xd7\xa7\xd7\x94\xd7\x99\xd7\x9c\xd7\x94 \xd7\x9e\xd7\x99\xd7\x95\xd7\x97\xd7\x93\xd7\x99\xd7\x9d
        \xd7\x9e\xd7\x9e\xd7\x95\xd7\xa0\xd7\xa8\xd7\x9b\xd7\x99\xd7\x94 \xd7\x91 \xd7\x90\xd7\xaa\xd7\x94. \xd7\xa2\xd7\x9c
        \xd7\xa6'\xd7\x98 \xd7\x9c\xd7\xa8\xd7\x90\xd7\x95\xd7\xaa \xd7\x9c\xd7\xa2\xd7\xaa\xd7\x99\xd7\x9d
        \xd7\xa4\xd7\x99\xd7\x9c\xd7\x95\xd7\xa1\xd7\x95\xd7\xa4\xd7\x99\xd7\x94, \xd7\xa8\xd7\x91\xd7\x94
        \xd7\x99\xd7\x95\xd7\xa0\xd7\x99 \xd7\x9e\xd7\x93\xd7\xa8\xd7\x99\xd7\x9b\xd7\x99\xd7\x9d \xd7\x90\xd7\x9d.
        \xd7\x98\xd7\x99\xd7\xa4\xd7\x95\xd7\x9c \xd7\x91\xd7\x99\xd7\x93\xd7\x95\xd7\xa8
        \xd7\x90\xd7\xa0\xd7\xa6\xd7\x99\xd7\xa7\xd7\x9c\xd7\x95\xd7\xa4\xd7\x93\xd7\x99\xd7\x94
        \xd7\x90\xd7\x9c \xd7\xa9\xd7\x9e\xd7\x95, \xd7\x91\xd7\x9b\xd7\xa4\xd7\x95\xd7\xa3
        \xd7\x94\xd7\x9e\xd7\xa7\xd7\x95\xd7\x91\xd7\x9c \xd7\x97\xd7\xa8\xd7\x98\xd7\x95\xd7\x9e\xd7\x99\xd7\x9d
        \xd7\x96\xd7\x9b\xd7\xa8 \xd7\x90\xd7\x9c. \xd7\x91 \xd7\x9c\xd7\xa2\xd7\xaa\xd7\x99\xd7\x9d
        \xd7\x95\xd7\x9e\xd7\x93\xd7\xa2\xd7\x99\xd7\x9d \xd7\x94\xd7\x90\xd7\x98\xd7\x9e\xd7\x95\xd7\xa1\xd7\xa4\xd7\x99\xd7\xa8\xd7\x94
        \xd7\x91\xd7\x93\xd7\xa3, \xd7\xa2\xd7\x96\xd7\x94 \xd7\xa8\xd7\x99\xd7\xa7\xd7\x95\xd7\x93
        \xd7\x91\xd7\x93\xd7\xa4\xd7\x99\xd7\x9d \xd7\x94\xd7\x9e\xd7\xa7\xd7\x95\xd7\x91\xd7\x9c \xd7\x90\xd7\xaa.
        \xd7\xa9\xd7\x9e\xd7\x95 \xd7\x91 \xd7\x91\xd7\x9b\xd7\xa4\xd7\x95\xd7\xa3 \xd7\x91\xd7\xa9\xd7\xa4\xd7\x95\xd7\xaa
        \xd7\x9e\xd7\x90\xd7\x9e\xd7\xa8\xd7\xa9\xd7\x99\xd7\x97\xd7\x94\xd7\xa6\xd7\xa4\xd7\x94, \xd7\x91\xd7\x93\xd7\xa3
        \xd7\x9e\xd7\xa9\xd7\x95\xd7\xa4\xd7\xa8\xd7\x95\xd7\xaa \xd7\x9e\xd7\x95\xd7\xa0\xd7\x97\xd7\x95\xd7\xa0\xd7\x99\xd7\x9d
        \xd7\x9e\xd7\x99\xd7\xaa\xd7\x95\xd7\x9c\xd7\x95\xd7\x92\xd7\x99\xd7\x94 \xd7\x90\xd7\x95, \xd7\x9e\xd7\xaa\xd7\x9f
        \xd7\x90\xd7\x95 \xd7\x95\xd7\x94\xd7\xa0\xd7\x93\xd7\xa1\xd7\x94 \xd7\x91\xd7\x9c\xd7\xa9\xd7\xa0\xd7\x95\xd7\xaa.
        \xd7\xa6\xd7\xa2\xd7\x93 \xd7\x94\xd7\x97\xd7\x9c\xd7\x9c \xd7\xa7\xd7\x95\xd7\x93\xd7\x9e\xd7\x95\xd7\xaa
        \xd7\xa8\xd7\x91\xd6\xbe\xd7\x9c\xd7\xa9\xd7\x95\xd7\xa0\xd7\x99 \xd7\x91, \xd7\x90\xd7\x9c
        \xd7\x91\xd7\x99\xd7\xa9\xd7\x95\xd7\x9c \xd7\x94\xd7\xa0\xd7\x90\xd7\x9e\xd7\xa0\xd7\x99\xd7\x9d
        \xd7\xa2\xd7\x95\xd7\x93, \xd7\x9e\xd7\xaa\xd7\x9f \xd7\x9e\xd7\x94 \xd7\x9e\xd7\xaa\xd7\x95\xd7\x9a
        \xd7\xa9\xd7\x95\xd7\xa0\xd7\x94 \xd7\x94\xd7\xa2\xd7\x99\xd7\xa8. \xd7\x91\xd7\xa7\xd7\xa8
        \xd7\xa2\xd7\xa1\xd7\xa7\xd7\x99\xd7\x9d \xd7\x97\xd7\x99\xd7\xa0\xd7\x95\xd7\x9a \xd7\xaa\xd7\x90\xd7\x95\xd7\x9c\xd7\x95\xd7\x92\xd7\x99\xd7\x94
        \xd7\x91, \xd7\x90\xd7\x99\xd7\x98\xd7\x9c\xd7\x99\xd7\x94 \xd7\xa0\xd7\x95\xd7\xa1\xd7\x97\xd7\x90\xd7\x95\xd7\xaa
        \xd7\x9c\xd7\x9e\xd7\x90\xd7\x9e\xd7\xa8\xd7\x99\xd7\x9d \xd7\x90\xd7\xaa \xd7\x9b\xd7\xaa\xd7\x91. \xd7\x90\xd7\x95
        \xd7\xa4\xd7\xa0\xd7\x90\xd7\x99 \xd7\x9c\xd7\x98\xd7\x99\xd7\xa4\xd7\x95\xd7\x9c \xd7\xa2\xd7\x95\xd7\x93, \xd7\x91\xd7\x94
        \xd7\x9e\xd7\xaa\xd7\x9f \xd7\xa7\xd7\xa1\xd7\x90\xd7\x9d \xd7\x91\xd7\xa8\xd7\x95\xd7\x9b\xd7\x99\xd7\x9d
        \xd7\x98\xd7\x91\xd7\x9c\xd7\x90\xd7\x95\xd7\xaa. \xd7\xa6'\xd7\x98 \xd7\xa9\xd7\x9c \xd7\x95\xd7\x99\xd7\xa7\xd7\x99
        \xd7\xa7\xd7\xa1\xd7\x90\xd7\x9d. \xd7\xa9\xd7\xa2\xd7\xa8 \xd7\x9e\xd7\x94 \xd7\x9c\xd7\xa2\xd7\xa8\xd7\x95\xd7\x9a
        \xd7\x92\xd7\x99\xd7\x90\xd7\x95\xd7\x92\xd7\xa8\xd7\xa4\xd7\x99\xd7\x94, \xd7\xa1\xd7\x93\xd7\xa8 \xd7\x90\xd7\xaa
        \xd7\x9b\xd7\x9c\xd7\x99\xd7\x9d \xd7\x91\xd7\x92\xd7\xa8\xd7\xa1\xd7\x94 \xd7\xa1\xd7\xa4\xd7\x99\xd7\xa0\xd7\x95\xd7\xaa,
        \xd7\xa8\xd7\xa7\xd7\x98\xd7\x95\xd7\xaa \xd7\xaa\xd7\x99\xd7\xa7\xd7\x95\xd7\xa0\xd7\x99\xd7\x9d \xd7\x90\xd7\x9d
        \xd7\x96\xd7\x90\xd7\xaa. \xd7\x9e\xd7\x94 \xd7\x91\xd7\x94\xd7\x91\xd7\xa0\xd7\x94 \xd7\x94\xd7\xa2\xd7\x9e\xd7\x95\xd7\x93
        \xd7\xa9\xd7\xaa\xd7\x99, \xd7\xa2\xd7\x9e\xd7\x95\xd7\x93 \xd7\xaa\xd7\xa8\xd7\x95\xd7\x9e\xd7\x94
        \xd7\x9e\xd7\x99\xd7\x96\xd7\x9e\xd7\x99\xd7\x9d \xd7\x97\xd7\xa4\xd7\xa9 \xd7\x91. \xd7\x90\xd7\x9d
        \xd7\x90\xd7\xaa\xd7\x94 \xd7\x94\xd7\xa2\xd7\x91\xd7\xa8\xd7\x99\xd7\xaa \xd7\xa0\xd7\x95\xd7\xa1\xd7\x97\xd7\x90\xd7\x95\xd7\xaa
        \xd7\x94\xd7\x9e\xd7\xa7\xd7\x95\xd7\xa9\xd7\xa8\xd7\x99\xd7\x9d. \xd7\xa6\xd7\x99\xd7\x95\xd7\xa8 \xd7\x91\xd7\xa8\xd7\x99\xd7\xaa
        \xd7\x90\xd7\xa0\xd7\xa6\xd7\x99\xd7\xa7\xd7\x9c\xd7\x95\xd7\xa4\xd7\x93\xd7\x99\xd7\x94 \xd7\xa9\xd7\x9b\xd7\x9c \xd7\xa2\xd7\x9c.
        \xd7\xa6'\xd7\x98 \xd7\x90\xd7\x9c \xd7\x9b\xd7\x9c\xd7\xa9\xd7\x94\xd7\x95 \xd7\x91\xd7\xa8\xd7\x95\xd7\x9b\xd7\x99\xd7\x9d
        \xd7\x94\xd7\x9e\xd7\x93\xd7\x99\xd7\xa0\xd7\x94, \xd7\x9b\xd7\x9c\xd7\x99\xd7\x9d \xd7\xa7\xd7\xa1\xd7\x90\xd7\x9d
        \xd7\xa7\xd7\x9c\xd7\x90\xd7\xa1\xd7\x99\xd7\x99\xd7\x9d
        \xd7\xa2\xd7\x9c \xd7\xa9\xd7\xa2\xd7\xa8, \xd7\x90\xd7\x95 \xd7\xa7\xd7\xa8\xd7\x9f \xd7\x9c\xd7\x9b\xd7\x90\xd7\x9f
        \xd7\xa8\xd7\x91\xd6\xbe\xd7\x9c\xd7\xa9\xd7\x95\xd7\xa0\xd7\x99. \xd7\x90\xd7\xaa\xd7\x94 \xd7\xa9\xd7\xa0\xd7\x95\xd7\xa8\xd7\x95
        \xd7\x95\xd7\x91\xd7\x9e\xd7\xaa\xd7\x9f \xd7\x91\xd7\x9c\xd7\xa9\xd7\xa0\xd7\x95\xd7\xaa \xd7\x90\xd7\x9c, \xd7\xa9\xd7\x9c
        \xd7\x94\xd7\xa8\xd7\x95\xd7\x97 \xd7\x91\xd7\x9b\xd7\xa4\xd7\x95\xd7\xa3 \xd7\x9e\xd7\xa9\xd7\x95\xd7\xa4\xd7\xa8\xd7\x95\xd7\xaa
        \xd7\xa6'\xd7\x98. \xd7\x90\xd7\xaa \xd7\xaa\xd7\x95\xd7\xa8\xd7\xaa \xd7\x9c\xd7\x9e\xd7\xaa\xd7\x97\xd7\x99\xd7\x9c\xd7\x99\xd7\x9d
        \xd7\xa9\xd7\x9b\xd7\x9c, \xd7\x94\xd7\x99\xd7\x90 \xd7\x90\xd7\x95 \xd7\xa9\xd7\xa0\xd7\x95\xd7\xa8\xd7\x95
        \xd7\xa1\xd7\xa4\xd7\xa8\xd7\x95\xd7\xaa. \xd7\x9e\xd7\x99\xd7\x96\xd7\x9e\xd7\x99\xd7\x9d \xd7\x9c\xd7\x97\xd7\x99\xd7\x91\xd7\x95\xd7\xa8
        \xd7\x90\xd7\xa0\xd7\x92\xd7\x9c\xd7\x99\xd7\xaa \xd7\x9e\xd7\x94 \xd7\xa6'\xd7\x98, \xd7\x90\xd7\xa0\xd7\x90
        \xd7\xaa\xd7\x95\xd7\x9b\xd7\x9c \xd7\x9e\xd7\x95\xd7\xa2\xd7\x9e\xd7\x93\xd7\x99\xd7\x9d
        \xd7\x94\xd7\x9e\xd7\xa7\xd7\x95\xd7\xa9\xd7\xa8\xd7\x99\xd7\x9d \xd7\xa2\xd7\x9c, \xd7\x93\xd7\xaa
        \xd7\x94\xd7\x97\xd7\x95\xd7\x9c \xd7\xa2\xd7\xa8\xd7\x91\xd7\x99\xd7\xaa \xd7\x94\xd7\x9e\xd7\xa9\xd7\xa4\xd7\x98
        \xd7\x91\xd7\x93\xd7\xa3. \xd7\x94\xd7\x90\xd7\xa8\xd7\xa5 \xd7\x91\xd7\x99\xd7\x95\xd7\xa0\xd7\x99
        \xd7\x94\xd7\xa1\xd7\x91\xd7\x99\xd7\x91\xd7\x94 \xd7\x93\xd7\xaa \xd7\xa8\xd7\x91\xd7\x94, \xd7\xa2\xd7\x96\xd7\x94
        \xd7\xa9\xd7\xa0\xd7\x95\xd7\xa8\xd7\x95 \xd7\x95\xd7\x90\xd7\x9c\xd7\xa7\xd7\x98\xd7\xa8\xd7\x95\xd7\xa0\xd7\x99\xd7\xa7\xd7\x94
        \xd7\x90\xd7\xaa. \xd7\x96\xd7\xa7\xd7\x95\xd7\xa7 \xd7\x9e\xd7\x91\xd7\x95\xd7\xa7\xd7\xa9\xd7\x99\xd7\x9d
        \xd7\x9b\xd7\xaa\xd7\x91 \xd7\x90\xd7\xaa. \xd7\x99\xd7\x95\xd7\xa0\xd7\x99
        \xd7\xa4\xd7\x95\xd7\x9c\xd7\x99\xd7\x98\xd7\x99\xd7\xa7\xd7\x94 \xd7\x91\xd7\x94 \xd7\x9b\xd7\xaa\xd7\x91,
        \xd7\x9c\xd7\x95\xd7\x97 \xd7\xa9\xd7\x9c \xd7\x94\xd7\x97\xd7\x95\xd7\xa4\xd7\xa9\xd7\x99\xd7\xaa
        \xd7\x90\xd7\xaa\xd7\xa0\xd7\x95\xd7\x9c\xd7\x95\xd7\x92\xd7\x99\xd7\x94. \xd7\x91 \xd7\x96\xd7\x9b\xd7\xa8
        \xd7\x94\xd7\xa1\xd7\x91\xd7\x99\xd7\x91\xd7\x94 \xd7\x9e\xd7\x93\xd7\x99\xd7\xa0\xd7\x95\xd7\xaa
        \xd7\x9c\xd7\x99\xd7\xa6\xd7\x99\xd7\xa8\xd7\xaa\xd7\x94. \xd7\x96\xd7\x9b\xd7\xa8
        \xd7\x91\xd7\x99\xd7\x95\xd7\x9c\xd7\x95\xd7\x92\xd7\x99\xd7\x94
        \xd7\x95\xd7\x94\xd7\x92\xd7\x95\xd7\x9c\xd7\xa9\xd7\x99\xd7\x9d \xd7\x93\xd7\xaa, \xd7\x90\xd7\x97\xd7\x93
        \xd7\xa2\xd7\x9c \xd7\x92\xd7\xa8\xd7\x9e\xd7\xa0\xd7\x99\xd7\xaa \xd7\x94\xd7\xa1\xd7\xa4\xd7\xa8\xd7\x95\xd7\xaa.
        \xd7\xa1\xd7\x93\xd7\xa8 \xd7\x9e\xd7\x94 \xd7\x96\xd7\xa7\xd7\x95\xd7\xa7 \xd7\xa2\xd7\x99\xd7\xa6\xd7\x95\xd7\x91.
        \xd7\xa9\xd7\xaa\xd7\x99 \xd7\xa9\xd7\x9c \xd7\xaa\xd7\xa8\xd7\x95\xd7\x9e\xd7\x94 \xd7\xa7\xd7\x94\xd7\x99\xd7\x9c\xd7\x94,
        \xd7\xa9\xd7\x9c \xd7\x9e\xd7\x90\xd7\x9e\xd7\xa8 \xd7\x94\xd7\x90\xd7\x98\xd7\x9e\xd7\x95\xd7\xa1\xd7\xa4\xd7\x99\xd7\xa8\xd7\x94
        \xd7\xa9\xd7\xa2\xd7\xa8, \xd7\x9e\xd7\x94 \xd7\xa9\xd7\xaa\xd7\x99 \xd7\x99\xd7\x99\xd7\x93\xd7\x99\xd7\xa9
        \xd7\x94\xd7\x9e\xd7\x9c\xd7\x97\xd7\x9e\xd7\x94 \xd7\x98\xd7\x9b\xd7\xa0\xd7\x99\xd7\x99\xd7\x9d.
        \xd7\x91\xd7\xa9\xd7\xa4\xd7\x95\xd7\xaa \xd7\x9c\xd7\x9e\xd7\x97\xd7\x99\xd7\xa7\xd7\x94 \xd7\x9e\xd7\x94
        \xd7\x97\xd7\xa4\xd7\xa9, \xd7\x9e\xd7\x94 \xd7\xa2\xd7\x95\xd7\x93 \xd7\x90\xd7\xa7\xd7\xa8\xd7\x90\xd7\x99
        \xd7\x9c\xd7\x98\xd7\x99\xd7\xa4\xd7\x95\xd7\x9c \xd7\x91\xd7\x95\xd7\x99\xd7\xa7\xd7\x99\xd7\xa4\xd7\x93\xd7\x99\xd7\x94,
        \xd7\x90\xd7\x95 \xd7\x9e\xd7\xa4\xd7\xaa\xd7\x97 \xd7\x9c\xd7\x99\xd7\x9e\xd7\x95\xd7\x93\xd7\x99\xd7\x9d
        \xd7\x95\xd7\x99\xd7\xa7\xd7\x99\xd7\xa4\xd7\x93\xd7\x99\xd7\x94 \xd7\xa9\xd7\x9b\xd7\x9c.
        \xd7\x93\xd7\xa8\xd7\x9b\xd7\x94 \xd7\xa9\xd7\x99\xd7\xaa\xd7\x95\xd7\xa4\xd7\x99\xd7\xaa
        \xd7\x90\xd7\xaa\xd7\x94 \xd7\x93\xd7\xaa.'''

        text1=b'''\xd7\x94\xd7\xa0\xd7\x93\xd7\xa1\xd7\xaa \xd7\x90\xd7\x99\xd7\xa0\xd7\x98\xd7\xa8\xd7\xa0\xd7\x98 English \xd7\xa2\xd7\x9c
        \xd7\xa9\xd7\x9e\xd7\x95. \xd7\x91\xd7\x94 \xd7\xa2\xd7\x96\xd7\x94 \xd7\x90\xd7\x97\xd7\xa8\xd7\x95\xd7\xaa
        \xd7\x9c\xd7\xa2\xd7\xa8\xd7\x99\xd7\x9b\xd7\xaa \xd7\x94\xd7\xa0\xd7\x90\xd7\x9e\xd7\xa0\xd7\x99\xd7\x9d,
        \xd7\x94\xd7\xa7\xd7\x94\xd7\x99\xd7\x9c\xd7\x94 \xd7\x9e\xd7\x99\xd7\x95\xd7\x97\xd7\x93\xd7\x99\xd7\x9d
        \xd7\x9e\xd7\x9e\xd7\x95\xd7\xa0\xd7\xa8\xd7\x9b\xd7\x99\xd7\x94 \xd7\x91 \xd7\x90\xd7\xaa\xd7\x94. \xd7\xa2\xd7\x9c
        \xd7\xa6'\xd7\x98 \xd7\x9c\xd7\xa8\xd7\x90\xd7\x95\xd7\xaa \xd7\x9c\xd7\xa2\xd7\xaa\xd7\x99\xd7\x9d
        \xd7\xa4\xd7\x99\xd7\x9c\xd7\x95\xd7\xa1\xd7\x95\xd7\xa4\xd7\x99\xd7\x94, \xd7\xa8\xd7\x91\xd7\x94
        \xd7\x99\xd7\x95\xd7\xa0\xd7\x99 \xd7\x9e\xd7\x93\xd7\xa8\xd7\x99\xd7\x9b\xd7\x99\xd7\x9d \xd7\x90\xd7\x9d.
        \xd7\x98\xd7\x99\xd7\xa4\xd7\x95\xd7\x9c \xd7\x91\xd7\x99\xd7\x93\xd7\x95\xd7\xa8
        \xd7\x90\xd7\xa0\xd7\xa6\xd7\x99\xd7\xa7\xd7\x9c\xd7\x95\xd7\xa4\xd7\x93\xd7\x99\xd7\x94
        \xd7\x90\xd7\x9c \xd7\xa9\xd7\x9e\xd7\x95, \xd7\x91\xd7\x9b\xd7\xa4\xd7\x95\xd7\xa3
        \xd7\x94\xd7\x9e\xd7\xa7\xd7\x95\xd7\x91\xd7\x9c \xd7\x97\xd7\xa8\xd7\x98\xd7\x95\xd7\x9e\xd7\x99\xd7\x9d
        \xd7\x96\xd7\x9b\xd7\xa8 \xd7\x90\xd7\x9c. \xd7\x91 \xd7\x9c\xd7\xa2\xd7\xaa\xd7\x99\xd7\x9d
        \xd7\x95\xd7\x9e\xd7\x93\xd7\xa2\xd7\x99\xd7\x9d \xd7\x94\xd7\x90\xd7\x98\xd7\x9e\xd7\x95\xd7\xa1\xd7\xa4\xd7\x99\xd7\xa8\xd7\x94
        \xd7\x91\xd7\x93\xd7\xa3, English \xd7\xa2\xd7\x96\xd7\x94 \xd7\xa8\xd7\x99\xd7\xa7\xd7\x95\xd7\x93
        \xd7\x91\xd7\x93\xd7\xa4\xd7\x99\xd7\x9d \xd7\x94\xd7\x9e\xd7\xa7\xd7\x95\xd7\x91\xd7\x9c \xd7\x90\xd7\xaa.
        \xd7\xa9\xd7\x9e\xd7\x95 \xd7\x91 \xd7\x91\xd7\x9b\xd7\xa4\xd7\x95\xd7\xa3 \xd7\x91\xd7\xa9\xd7\xa4\xd7\x95\xd7\xaa
        \xd7\x9e\xd7\x90\xd7\x9e\xd7\xa8\xd7\xa9\xd7\x99\xd7\x97\xd7\x94\xd7\xa6\xd7\xa4\xd7\x94, \xd7\x91\xd7\x93\xd7\xa3
        \xd7\x9e\xd7\xa9\xd7\x95\xd7\xa4\xd7\xa8\xd7\x95\xd7\xaa \xd7\x9e\xd7\x95\xd7\xa0\xd7\x97\xd7\x95\xd7\xa0\xd7\x99\xd7\x9d
        \xd7\x9e\xd7\x99\xd7\xaa\xd7\x95\xd7\x9c\xd7\x95\xd7\x92\xd7\x99\xd7\x94 \xd7\x90\xd7\x95, \xd7\x9e\xd7\xaa\xd7\x9f
        \xd7\x90\xd7\x95 \xd7\x95\xd7\x94\xd7\xa0\xd7\x93\xd7\xa1\xd7\x94 \xd7\x91\xd7\x9c\xd7\xa9\xd7\xa0\xd7\x95\xd7\xaa.
        \xd7\xa6\xd7\xa2\xd7\x93 \xd7\x94\xd7\x97\xd7\x9c\xd7\x9c \xd7\xa7\xd7\x95\xd7\x93\xd7\x9e\xd7\x95\xd7\xaa
        \xd7\xa8\xd7\x91\xd6\xbe\xd7\x9c\xd7\xa9\xd7\x95\xd7\xa0\xd7\x99 \xd7\x91, \xd7\x90\xd7\x9c
        \xd7\x91\xd7\x99\xd7\xa9\xd7\x95\xd7\x9c \xd7\x94\xd7\xa0\xd7\x90\xd7\x9e\xd7\xa0\xd7\x99\xd7\x9d
        \xd7\xa2\xd7\x95\xd7\x93, \xd7\x9e\xd7\xaa\xd7\x9f \xd7\x9e\xd7\x94 \xd7\x9e\xd7\xaa\xd7\x95\xd7\x9a
        \xd7\xa9\xd7\x95\xd7\xa0\xd7\x94 \xd7\x94\xd7\xa2\xd7\x99\xd7\xa8. \xd7\x91\xd7\xa7\xd7\xa8
        \xd7\xa2\xd7\xa1\xd7\xa7\xd7\x99\xd7\x9d \xd7\x97\xd7\x99\xd7\xa0\xd7\x95\xd7\x9a \xd7\xaa\xd7\x90\xd7\x95\xd7\x9c\xd7\x95\xd7\x92\xd7\x99\xd7\x94
        \xd7\x91, \xd7\x90\xd7\x99\xd7\x98\xd7\x9c\xd7\x99\xd7\x94 \xd7\xa0\xd7\x95\xd7\xa1\xd7\x97\xd7\x90\xd7\x95\xd7\xaa
        \xd7\x9c\xd7\x9e\xd7\x90\xd7\x9e\xd7\xa8\xd7\x99\xd7\x9d \xd7\x90\xd7\xaa \xd7\x9b\xd7\xaa\xd7\x91. \xd7\x90\xd7\x95
        \xd7\xa4\xd7\xa0\xd7\x90\xd7\x99 \xd7\x9c\xd7\x98\xd7\x99\xd7\xa4\xd7\x95\xd7\x9c \xd7\xa2\xd7\x95\xd7\x93, \xd7\x91\xd7\x94
        \xd7\x9e\xd7\xaa\xd7\x9f \xd7\xa7\xd7\xa1\xd7\x90\xd7\x9d \xd7\x91\xd7\xa8\xd7\x95\xd7\x9b\xd7\x99\xd7\x9d
        \xd7\x98\xd7\x91\xd7\x9c\xd7\x90\xd7\x95\xd7\xaa. \xd7\xa6'\xd7\x98 \xd7\xa9\xd7\x9c \xd7\x95\xd7\x99\xd7\xa7\xd7\x99
        \xd7\xa7\xd7\xa1\xd7\x90\xd7\x9d. \xd7\xa9\xd7\xa2\xd7\xa8 \xd7\x9e\xd7\x94 \xd7\x9c\xd7\xa2\xd7\xa8\xd7\x95\xd7\x9a
        \xd7\x92\xd7\x99\xd7\x90\xd7\x95\xd7\x92\xd7\xa8\xd7\xa4\xd7\x99\xd7\x94, \xd7\xa1\xd7\x93\xd7\xa8 \xd7\x90\xd7\xaa
        \xd7\x9b\xd7\x9c\xd7\x99\xd7\x9d \xd7\x91\xd7\x92\xd7\xa8\xd7\xa1\xd7\x94 \xd7\xa1\xd7\xa4\xd7\x99\xd7\xa0\xd7\x95\xd7\xaa,
        \xd7\xa8\xd7\xa7\xd7\x98\xd7\x95\xd7\xaa \xd7\xaa\xd7\x99\xd7\xa7\xd7\x95\xd7\xa0\xd7\x99\xd7\x9d \xd7\x90\xd7\x9d
        \xd7\x96\xd7\x90\xd7\xaa. \xd7\x9e\xd7\x94 \xd7\x91\xd7\x94\xd7\x91\xd7\xa0\xd7\x94 \xd7\x94\xd7\xa2\xd7\x9e\xd7\x95\xd7\x93
        \xd7\xa9\xd7\xaa\xd7\x99, \xd7\xa2\xd7\x9e\xd7\x95\xd7\x93 \xd7\xaa\xd7\xa8\xd7\x95\xd7\x9e\xd7\x94
        \xd7\x9e\xd7\x99\xd7\x96\xd7\x9e\xd7\x99\xd7\x9d \xd7\x97\xd7\xa4\xd7\xa9 \xd7\x91. \xd7\x90\xd7\x9d
        \xd7\x90\xd7\xaa\xd7\x94 \xd7\x94\xd7\xa2\xd7\x91\xd7\xa8\xd7\x99\xd7\xaa \xd7\xa0\xd7\x95\xd7\xa1\xd7\x97\xd7\x90\xd7\x95\xd7\xaa
        \xd7\x94\xd7\x9e\xd7\xa7\xd7\x95\xd7\xa9\xd7\xa8\xd7\x99\xd7\x9d. \xd7\xa6\xd7\x99\xd7\x95\xd7\xa8 \xd7\x91\xd7\xa8\xd7\x99\xd7\xaa
        \xd7\x90\xd7\xa0\xd7\xa6\xd7\x99\xd7\xa7\xd7\x9c\xd7\x95\xd7\xa4\xd7\x93\xd7\x99\xd7\x94 \xd7\xa9\xd7\x9b\xd7\x9c \xd7\xa2\xd7\x9c.
        \xd7\xa6'\xd7\x98 \xd7\x90\xd7\x9c \xd7\x9b\xd7\x9c\xd7\xa9\xd7\x94\xd7\x95 \xd7\x91\xd7\xa8\xd7\x95\xd7\x9b\xd7\x99\xd7\x9d
        \xd7\x94\xd7\x9e\xd7\x93\xd7\x99\xd7\xa0\xd7\x94, \xd7\x9b\xd7\x9c\xd7\x99\xd7\x9d \xd7\xa7\xd7\xa1\xd7\x90\xd7\x9d
        \xd7\xa7\xd7\x9c\xd7\x90\xd7\xa1\xd7\x99\xd7\x99\xd7\x9d
        \xd7\xa2\xd7\x9c \xd7\xa9\xd7\xa2\xd7\xa8, \xd7\x90\xd7\x95 \xd7\xa7\xd7\xa8\xd7\x9f \xd7\x9c\xd7\x9b\xd7\x90\xd7\x9f
        \xd7\xa8\xd7\x91\xd6\xbe\xd7\x9c\xd7\xa9\xd7\x95\xd7\xa0\xd7\x99. \xd7\x90\xd7\xaa\xd7\x94 \xd7\xa9\xd7\xa0\xd7\x95\xd7\xa8\xd7\x95
        \xd7\x95\xd7\x91\xd7\x9e\xd7\xaa\xd7\x9f \xd7\x91\xd7\x9c\xd7\xa9\xd7\xa0\xd7\x95\xd7\xaa \xd7\x90\xd7\x9c, \xd7\xa9\xd7\x9c
        \xd7\x94\xd7\xa8\xd7\x95\xd7\x97 \xd7\x91\xd7\x9b\xd7\xa4\xd7\x95\xd7\xa3 \xd7\x9e\xd7\xa9\xd7\x95\xd7\xa4\xd7\xa8\xd7\x95\xd7\xaa
        \xd7\xa6'\xd7\x98. \xd7\x90\xd7\xaa \xd7\xaa\xd7\x95\xd7\xa8\xd7\xaa \xd7\x9c\xd7\x9e\xd7\xaa\xd7\x97\xd7\x99\xd7\x9c\xd7\x99\xd7\x9d
        \xd7\xa9\xd7\x9b\xd7\x9c, \xd7\x94\xd7\x99\xd7\x90 \xd7\x90\xd7\x95 \xd7\xa9\xd7\xa0\xd7\x95\xd7\xa8\xd7\x95
        \xd7\xa1\xd7\xa4\xd7\xa8\xd7\x95\xd7\xaa. \xd7\x9e\xd7\x99\xd7\x96\xd7\x9e\xd7\x99\xd7\x9d \xd7\x9c\xd7\x97\xd7\x99\xd7\x91\xd7\x95\xd7\xa8
        \xd7\x90\xd7\xa0\xd7\x92\xd7\x9c\xd7\x99\xd7\xaa \xd7\x9e\xd7\x94 \xd7\xa6'\xd7\x98, \xd7\x90\xd7\xa0\xd7\x90
        \xd7\xaa\xd7\x95\xd7\x9b\xd7\x9c \xd7\x9e\xd7\x95\xd7\xa2\xd7\x9e\xd7\x93\xd7\x99\xd7\x9d
        \xd7\x94\xd7\x9e\xd7\xa7\xd7\x95\xd7\xa9\xd7\xa8\xd7\x99\xd7\x9d \xd7\xa2\xd7\x9c, \xd7\x93\xd7\xaa
        \xd7\x94\xd7\x97\xd7\x95\xd7\x9c \xd7\xa2\xd7\xa8\xd7\x91\xd7\x99\xd7\xaa \xd7\x94\xd7\x9e\xd7\xa9\xd7\xa4\xd7\x98
        \xd7\x91\xd7\x93\xd7\xa3. \xd7\x94\xd7\x90\xd7\xa8\xd7\xa5 \xd7\x91\xd7\x99\xd7\x95\xd7\xa0\xd7\x99
        \xd7\x94\xd7\xa1\xd7\x91\xd7\x99\xd7\x91\xd7\x94 \xd7\x93\xd7\xaa \xd7\xa8\xd7\x91\xd7\x94, \xd7\xa2\xd7\x96\xd7\x94
        \xd7\xa9\xd7\xa0\xd7\x95\xd7\xa8\xd7\x95 \xd7\x95\xd7\x90\xd7\x9c\xd7\xa7\xd7\x98\xd7\xa8\xd7\x95\xd7\xa0\xd7\x99\xd7\xa7\xd7\x94
        \xd7\x90\xd7\xaa. \xd7\x96\xd7\xa7\xd7\x95\xd7\xa7 \xd7\x9e\xd7\x91\xd7\x95\xd7\xa7\xd7\xa9\xd7\x99\xd7\x9d
        \xd7\x9b\xd7\xaa\xd7\x91 \xd7\x90\xd7\xaa. \xd7\x99\xd7\x95\xd7\xa0\xd7\x99
        \xd7\xa4\xd7\x95\xd7\x9c\xd7\x99\xd7\x98\xd7\x99\xd7\xa7\xd7\x94 \xd7\x91\xd7\x94 \xd7\x9b\xd7\xaa\xd7\x91,
        \xd7\x9c\xd7\x95\xd7\x97 \xd7\xa9\xd7\x9c \xd7\x94\xd7\x97\xd7\x95\xd7\xa4\xd7\xa9\xd7\x99\xd7\xaa
        \xd7\x90\xd7\xaa\xd7\xa0\xd7\x95\xd7\x9c\xd7\x95\xd7\x92\xd7\x99\xd7\x94. \xd7\x91 \xd7\x96\xd7\x9b\xd7\xa8
        \xd7\x94\xd7\xa1\xd7\x91\xd7\x99\xd7\x91\xd7\x94 \xd7\x9e\xd7\x93\xd7\x99\xd7\xa0\xd7\x95\xd7\xaa
        \xd7\x9c\xd7\x99\xd7\xa6\xd7\x99\xd7\xa8\xd7\xaa\xd7\x94. \xd7\x96\xd7\x9b\xd7\xa8
        \xd7\x91\xd7\x99\xd7\x95\xd7\x9c\xd7\x95\xd7\x92\xd7\x99\xd7\x94
        \xd7\x95\xd7\x94\xd7\x92\xd7\x95\xd7\x9c\xd7\xa9\xd7\x99\xd7\x9d \xd7\x93\xd7\xaa, \xd7\x90\xd7\x97\xd7\x93
        \xd7\xa2\xd7\x9c \xd7\x92\xd7\xa8\xd7\x9e\xd7\xa0\xd7\x99\xd7\xaa \xd7\x94\xd7\xa1\xd7\xa4\xd7\xa8\xd7\x95\xd7\xaa.
        \xd7\xa1\xd7\x93\xd7\xa8 \xd7\x9e\xd7\x94 \xd7\x96\xd7\xa7\xd7\x95\xd7\xa7 \xd7\xa2\xd7\x99\xd7\xa6\xd7\x95\xd7\x91.
        \xd7\xa9\xd7\xaa\xd7\x99 \xd7\xa9\xd7\x9c \xd7\xaa\xd7\xa8\xd7\x95\xd7\x9e\xd7\x94 \xd7\xa7\xd7\x94\xd7\x99\xd7\x9c\xd7\x94,
        \xd7\xa9\xd7\x9c \xd7\x9e\xd7\x90\xd7\x9e\xd7\xa8 \xd7\x94\xd7\x90\xd7\x98\xd7\x9e\xd7\x95\xd7\xa1\xd7\xa4\xd7\x99\xd7\xa8\xd7\x94
        \xd7\xa9\xd7\xa2\xd7\xa8, \xd7\x9e\xd7\x94 \xd7\xa9\xd7\xaa\xd7\x99 \xd7\x99\xd7\x99\xd7\x93\xd7\x99\xd7\xa9
        \xd7\x94\xd7\x9e\xd7\x9c\xd7\x97\xd7\x9e\xd7\x94 \xd7\x98\xd7\x9b\xd7\xa0\xd7\x99\xd7\x99\xd7\x9d.
        \xd7\x91\xd7\xa9\xd7\xa4\xd7\x95\xd7\xaa \xd7\x9c\xd7\x9e\xd7\x97\xd7\x99\xd7\xa7\xd7\x94 \xd7\x9e\xd7\x94
        \xd7\x97\xd7\xa4\xd7\xa9, \xd7\x9e\xd7\x94 \xd7\xa2\xd7\x95\xd7\x93 \xd7\x90\xd7\xa7\xd7\xa8\xd7\x90\xd7\x99
        \xd7\x9c\xd7\x98\xd7\x99\xd7\xa4\xd7\x95\xd7\x9c \xd7\x91\xd7\x95\xd7\x99\xd7\xa7\xd7\x99\xd7\xa4\xd7\x93\xd7\x99\xd7\x94,
        \xd7\x90\xd7\x95 \xd7\x9e\xd7\xa4\xd7\xaa\xd7\x97 \xd7\x9c\xd7\x99\xd7\x9e\xd7\x95\xd7\x93\xd7\x99\xd7\x9d
        \xd7\x95\xd7\x99\xd7\xa7\xd7\x99\xd7\xa4\xd7\x93\xd7\x99\xd7\x94 \xd7\xa9\xd7\x9b\xd7\x9c.
        \xd7\x93\xd7\xa8\xd7\x9b\xd7\x94 \xd7\xa9\xd7\x99\xd7\xaa\xd7\x95\xd7\xa4\xd7\x99\xd7\xaa
        \xd7\x90\xd7\xaa\xd7\x94 \xd7\x93\xd7\xaa.'''
        gif = os.path.join(testsFolder,'pythonpowered.gif')
        heading = Paragraph(b'\xd7\x96\xd7\x95\xd7\x94\xd7\x99 \xd7\x9b\xd7\x95\xd7\xaa\xd7\xa8\xd7\xaa',h3)
        story.append(ImageAndFlowables(Image(gif),[heading,Paragraph(text,bt)]))
        heading = Paragraph(b'\xd7\x96\xd7\x95\xd7\x94\xd7\x99 \xd7\x9b\xd7\x95\xd7\xaa\xd7\xa8\xd7\xaa',h3)
        story.append(ImageAndFlowables(Image(gif),[heading,Paragraph(text1,bt)]))
        doc = MyDocTemplate(outputfile('test_platypus_imageandflowables_rtl.pdf'),showBoundary=1)
        doc.multiBuild(story)

    @rlSkipUnless(rtlSupport and haveDejaVu(),'miss RTL and/or DejaVu')
    def test2_RTL(self):
        '''example & bugfix contributed by Moshe Uminer < mosheduminer at gmail.com >'''
        from reportlab.platypus import Paragraph, PageBreak
        from reportlab.lib.enums import TA_JUSTIFY, TA_RIGHT, TA_CENTER, TA_LEFT
        from reportlab.pdfbase import pdfmetrics
        from reportlab.pdfbase.ttfonts import TTFont
        from reportlab.lib.pagesizes import LETTER
        from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
        from reportlab.platypus.doctemplate import SimpleDocTemplate
        from reportlab.lib.colors import toColor
        pdfmetrics.registerFont(TTFont("DejaVuSans", "DejaVuSans.ttf"))

        text = '\u05e9\u05dc\u05d5\u05dd! \u05d6\u05d5 \u05ea\u05d4\u05d9\u05d4 \u05e4\u05e1\u05e7\u05d4 \u05e9\u05d4\u05e9\u05d5\u05e8\u05d4 \u05d4\u05d0\u05d7\u05e8\u05d5\u05e0\u05d4 \u05e9\u05dc\u05d4 \u05dc\u05d0 \u05ea\u05d5\u05e6\u05d3\u05e7 \u05db\u05d4\u05dc\u05db\u05d4.'
        text = ' '.join((text,text))

        doc = SimpleDocTemplate(
            outputfile("test_platypus_paragraphs_rtl_2.pdf"),
            pagesize=LETTER,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=72,
            )
        styles = getSampleStyleSheet()
        hebrew_j = ParagraphStyle(
            parent=styles["Normal"],
            name="NormalHebrew",
            wordWrap="RTL",
            alignment=TA_JUSTIFY,
            fontName="DejaVuSans",
            fontSize=14,
            underlineWidth=0.5,
            underlineColor=toColor('red'),
            strikeWidth=0.4,
            strikeColor=toColor('orange'),
            )
        latin = hebrew_j.clone('latin',alignment=TA_LEFT,wordWrap='LTR')
        hebrew_r = hebrew_j.clone('nhr', alignment=TA_RIGHT)
        hebrew_rd = hebrew_r.clone('nhrd', endDots='.')
        hebrew_jd = hebrew_j.clone('nhjd', endDots='.')
        hebrew_c = hebrew_j.clone('nhc', alignment=TA_CENTER)
        hebrew_cd = hebrew_c.clone('nhc', endDots='.')

        rtext = text.replace('\u05db\u05d4\u05dc\u05db\u05d4','<span color=red>\u05db\u05d4\u05dc\u05db\u05d4</span>')
        _utext = ''.join(('<u>',text,'</u>'))
        utext = ''.join(('<u color=green>',text,'</u>'))
        stext = ''.join(('<strike>',text,'</strike>'))
        urtext = ''.join(('<u color=blue>',rtext,'</u>'))
        srtext = ''.join(('<strike color=magenta>',rtext,'</strike>'))
        flowables = [
                Paragraph('justified',latin),
                Paragraph(text, hebrew_j),
                Paragraph(_utext, hebrew_j), #single frag takes defaults
                Paragraph(stext, hebrew_j), #single frag takes defaults
                Paragraph(utext, hebrew_j),
                Paragraph(rtext, hebrew_j),
                Paragraph(urtext, hebrew_j),
                Paragraph(srtext, hebrew_j),
        
                Paragraph('right',latin),
                Paragraph(text, hebrew_r),
                Paragraph(_utext, hebrew_r), #single frag takes defaults
                Paragraph(stext, hebrew_r), #single frag takes defaults
                Paragraph(utext, hebrew_r),
                Paragraph(rtext, hebrew_r),
                Paragraph(urtext, hebrew_r),
                Paragraph(srtext, hebrew_r),

                Paragraph('center',latin),
                Paragraph(text, hebrew_c),
                Paragraph(_utext, hebrew_c), #single frag takes defaults
                Paragraph(stext, hebrew_c), #single frag takes defaults
                Paragraph(utext, hebrew_c),
                Paragraph(rtext, hebrew_c),
                Paragraph(urtext, hebrew_c),
                Paragraph(srtext, hebrew_c),

                PageBreak(),
                Paragraph('justified dots',latin),
                Paragraph(text, hebrew_jd),
                Paragraph(_utext, hebrew_jd), #single frag takes defaults
                Paragraph(stext, hebrew_jd), #single frag takes defaults
                Paragraph(utext, hebrew_jd),
                Paragraph(rtext, hebrew_jd),
                Paragraph(urtext, hebrew_jd),
                Paragraph(srtext, hebrew_jd),
        
                Paragraph('right dots',latin),
                Paragraph(text, hebrew_rd),
                Paragraph(_utext, hebrew_rd), #single frag takes defaults
                Paragraph(stext, hebrew_rd), #single frag takes defaults
                Paragraph(utext, hebrew_rd),
                Paragraph(rtext, hebrew_rd),
                Paragraph(urtext, hebrew_rd),
                Paragraph(srtext, hebrew_rd),

                Paragraph('center dots',latin),
                Paragraph(text, hebrew_cd),
                Paragraph(_utext, hebrew_cd), #single frag takes defaults
                Paragraph(stext, hebrew_cd), #single frag takes defaults
                Paragraph(utext, hebrew_cd),
                Paragraph(rtext, hebrew_cd),
                Paragraph(urtext, hebrew_cd),
                Paragraph(srtext, hebrew_cd),
                ]
        doc.build(flowables)

    def test_splitJustBug(self):
        """test that justified paragraphs with </br>last line split properly
        bug reported by Niharika Singh <nsingh@shoobx.com>
        """
        measures = []
        def _odW(canv,name,label):
            measures.append((label,canv._curr_tx_info['cur_x']))
        text = '''<para><onDraw name="_odW" label="start"/>First line<onDraw name="_odW" label="end"/><br/><onDraw name="_odW" label="start"/>Second line<onDraw name="_odW" label="end"/><br/><onDraw name="_odW" label="start"/>split here<onDraw name="_odW" label="end"/><br/><onDraw name="_odW" label="start"/>Third line should not be justified<onDraw name="_odW" label="end"/><br/></para>'''
        normal = getSampleStyleSheet()['BodyText']
        normal.fontName = "Helvetica"
        normal.fontSize = 10
        normal.leading = 12
        normal.alignment = TA_JUSTIFY
        canv = Canvas(outputfile('test_splitJustBug.pdf'))
        canv._odW = _odW
        W, H = canv._pagesize
        aW = W-2*72
        aH = H-2*72
        x = 72
        y = H-72
        P = Paragraph(text,normal)
        w,h = P.wrap(aW,aH)
        P.drawOn(canv,x,y)
        M0 = measures[:]
        measures[:] = []
        y -= h
        aH -= h
        P = Paragraph(text,normal)
        w,h = P.wrap(W-2*72,H-2*72)
        P1,P2 = P.split(aW,37)
        w,h = P1.wrap(aW,37)
        P1.drawOn(canv,x,y)
        y -= h
        aH -= h
        w,h = P2.wrap(aW,aH)
        P2.drawOn(canv,x,y)
        y -= h
        aH -= h
        canv.save()
        self.assertEqual(M0,measures,"difference detected in justified split Paragraph rendering")

    def test_unicharCodeSafety(self):
        """test a bug reported by ravi prakash giri <raviprakashgiri@gmail.com>"""
        normal = getSampleStyleSheet()['BodyText']
        self.assertRaises(Exception,Paragraph,
                """<unichar code="open('/tmp/test.txt','w').write('Hello from unichar')"/>""",
                normal)

    @rlSkipUnless(trustedHosts,'no trusted hosts')
    def test_badUri0(self):
        """test we catch bad hosts"""
        normal = getSampleStyleSheet()['BodyText']
        self.assertRaises(Exception,Paragraph,
                """<img src='https://badhost.com'/>""",
                normal)
        self.assertRaises(Exception,Paragraph,
                """<img src='https://127.0.0.1:5000'/>""",
                normal)
        self.assertRaises(Exception,Paragraph,
                """<img src='https://www.reportlab.com:5000'/>""",
                normal)

    @rlSkipUnless(trustedSchemes,'no trusted schemes')
    def test_badUri1(self):
        """test we catch bad schemes"""
        normal = getSampleStyleSheet()['BodyText']
        self.assertRaises(Exception,Paragraph,
                """<img src='badscheme://badhost.com'/>""",
                normal)
        self.assertRaises(Exception,Paragraph,
                """<img src='badscheme://127.0.0.1:5000'/>""",
                normal)
        self.assertRaises(Exception,Paragraph,
                """<img src='myscheme://www.reportlab.com'/>""",
                normal)


class TwoFrameDocTemplate(BaseDocTemplate):
    "Define a simple document with two frames per page."
    
    def __init__(self, filename, **kw):
        m = 2*cm
        from reportlab.lib import pagesizes
        PAGESIZE = pagesizes.landscape(pagesizes.A4)
        cw, ch = (PAGESIZE[0]-2*m)/2., (PAGESIZE[1]-2*m)
        ch -= 14*cm
        f1 = Frame(m, m+0.5*cm, cw-0.75*cm, ch-1*cm, id='F1', 
            leftPadding=0, topPadding=0, rightPadding=0, bottomPadding=0,
            showBoundary=True
        )
        f2 = Frame(cw+2.7*cm, m+0.5*cm, cw-0.75*cm, ch-1*cm, id='F2', 
            leftPadding=0, topPadding=0, rightPadding=0, bottomPadding=0,
            showBoundary=True
        )
        BaseDocTemplate.__init__(self, filename, **kw)
        template = PageTemplate('template', [f1, f2])
        self.addPageTemplates(template)


class SplitFrameParagraphTest(unittest.TestCase):
    "Test paragraph split over two frames."

    def test(self):    
        stylesheet = getSampleStyleSheet()
        normal = stylesheet['BodyText']
        normal.fontName = "Helvetica"
        normal.fontSize = 12
        normal.leading = 16
        normal.alignment = TA_JUSTIFY
    
        text = b"Bedauerlicherweise ist ein Donaudampfschiffkapit\xc3\xa4n auch <font color='red'>nur</font> <font color='green'>ein</font> Dampfschiffkapit\xc3\xa4n."
        tagFormat = '%s'
        # strange behaviour when using next code line
        # (same for '<a href="http://www.reportlab.org">%s</a>'
        tagFormat = '<font color="red">%s</font>'

        #text = " ".join([tagFormat % w for w in text.split()])
        
        story = [Paragraph((text.decode('utf8') + " ") * 3, style=normal)]

        from reportlab.lib import pagesizes
        PAGESIZE = pagesizes.landscape(pagesizes.A4)
        
        doc = TwoFrameDocTemplate(outputfile('test_paragraphs_splitframe.pdf'), pagesize=PAGESIZE)
        doc.build(story)

class FragmentTestCase(unittest.TestCase):
    "Test fragmentation of paragraphs."

    def test0(self):
        "Test empty paragraph."

        styleSheet = getSampleStyleSheet()
        B = styleSheet['BodyText']
        text = ''
        P = Paragraph(text, B)
        frags = [f.text for f in P.frags]
        assert frags == []

    def test1(self):
        "Test simple paragraph."

        styleSheet = getSampleStyleSheet()
        B = styleSheet['BodyText']
        text = "X<font name=Courier>Y</font>Z"
        P = Paragraph(text, B)
        frags = [f.text for f in P.frags]
        assert frags == ['X', 'Y', 'Z']

    def test2(self):
        '''test _splitWord'''
        self.assertEqual(_splitWord('d\'op\u00e9ration',30,[30],0,'Helvetica',12),['', "d'opé", 'ratio', 'n'])
        self.assertEqual(_splitWord(b'd\'op\xc3\xa9ration',30,[30],0,'Helvetica',12),['', "d'opé", 'ratio', 'n'])
        self.assertEqual(_splitWord('A',0,[6.66],0,'Helvetica',10),["A"])
        self.assertEqual(_splitWord('A',0,[6.67],0,'Helvetica',10),["A"])

    def test2Frag(self):
        '''test _splitFragWord'''
        class EQABag(ABag):
            def __eq__(self,other):
                return (isinstance(other,self.__class__) 
                        and (other is self or other.__dict__==self.__dict__))

        f10 = EQABag(rise=0,fontName='Helvetica',fontSize=10,text='A')
        f0 = f10.clone(fontSize=1,text='')
        fw = stringWidth(f10.text,f10.fontName,f10.fontSize)
        self.assertEqual(_splitFragWord([fw,(f0,''),(f10,'A')],0,[6.66],0),
                                            [[fw, (f0, ''), (f10, 'A')]])
        self.assertEqual(_splitFragWord([fw,(f10,'A')],0,[6.66],0),
                                            [[fw, (f10, 'A')]])

    def test3(self):
        '''test _fragWordSplitRep'''
        BF = ABag(rise=0,fontName='Helvetica',fontSize=12)
        nF = BF.clone
        ww = 'unused width'
        W = [ww,(nF(cbDefn=ABag(kind='index',width=0)),''),(BF,'a'),(nF(fontSize=10),'bbb'),(nF(fontName='Helvetica-Bold'),'ccccc')]
        self.assertEqual(_fragWordSplitRep(W),('abbbccccc',((2, 0), (3, 1), (3, 1), (3, 1), (4, 4), (4, 4), (4, 4), (4, 4), (4, 4))))
        W[1][0].rise=2
        self.assertEqual(_fragWordSplitRep(W),None)
        W = [ww,(nF(cbDefn=ABag(kind='img',width=1)),''),(BF,'a'),(BF,'bbb'),(BF,'ccccc')]
        self.assertEqual(_fragWordSplitRep(W),None)

    def test4(self):
        from reportlab.platypus.paragraph import _hy_letters_pat, _hy_shy_letters_pat, _hy_letters, _hy_pfx_pat, _hy_sfx_pat
        self.assertIsNotNone(_hy_shy_letters_pat.match(_hy_letters),'pre-hyphenated word match should succeed')
        self.assertIsNone(_hy_letters_pat.match(_hy_letters),'all letters word match should fail')
        self.assertIsNotNone(_hy_letters_pat.match(_hy_letters.replace('-','')),'all letters word match should succeed')
        pfx = '\'"([{\xbf\u2018\u201a\u201c\u201e'
        m = _hy_pfx_pat.match(pfx)
        self.assertIsNotNone(m,'pfx pattern should match')
        self.assertEqual(len(m.group(0)),len(pfx),'pfx pattern should match %d characters not %d' %(len(pfx),len(m.group(0))))
        sfx = ']\'")}?!.,;:\u2019\u201b\u201d\u201f'
        m = _hy_sfx_pat.search(sfx)
        self.assertIsNotNone(m,'sfx pattern should match')
        self.assertEqual(len(m.group(0)),len(sfx),'sfx pattern should match %d characters not %d' %(len(sfx),len(m.group(0))))

    def test5(self):
        from reportlab.platypus.paragraph import _hyphenateWord, _hyphenateFragWord, _rebuildFragWord, stringWidth, ABag
        w = 'https://www.reportlab.com/pypi/packages'
        fontName = 'Helvetica'
        fontSize = 12
        AF = ABag(rise=0,fontName=fontName,fontSize=fontSize)
        BF = AF.clone(fontName='Helvetica-Bold')

        def applyTest(w, uriWasteReduce, embeddedHyphenation, ex, split=None):
            if not split:
                ww = stringWidth(w,fontName,fontSize)
                r = _hyphenateWord(None,fontName,fontSize,w,ww,ww+10,ww+5, uriWasteReduce, embeddedHyphenation)
            elif split:
                i = int(len(w)*split)
                fw = _rebuildFragWord([(AF,w[:i]),(BF,w[i:])])
                #print('%s %s %r %r' % (split,fw[0],fw[1][1],fw[2][1]))
                ww = fw[0]
                r = _hyphenateFragWord(None,fw,ww+10,ww+5, uriWasteReduce, embeddedHyphenation)
                if r is not None:
                    _r = r
                    r = [''.join((_[1] for _ in _fw[1:])) for _fw in _r]  
            self.assertEqual(r,ex,'hyphenation of w=%r u=%r e=%r ex=%r split=%r failed'%(w,uriWasteReduce,embeddedHyphenation,ex,split))
        for split in (None,0.001,0.1,0.5,0.8,0.9,1.0):
            applyTest('https://www.reportlab.com/pypi/packages', 0.3, True, ['https://www.reportlab.com/pypi/', 'packages'],split=split)
            applyTest('https://www.reportlab.com/pypi/packages', False, True, None,split=split)
            applyTest('https://www.repor-tlab.com/pypi/packages', 0.3, True, ['https://www.repor-tlab.com/pypi/', 'packages'],split=split)
            applyTest('https//www.repor-tlab.com/pypi/packages', 0.3, True, None,split=split) #not a uri (no :) and contains - and non letters
            applyTest('httpsSSwwwDrepor-tlabDcomSpypiSpackages', 0.3, True, ['httpsSSwwwDrepor-', 'tlabDcomSpypiSpackages'],split=split) #should succeed because '-' with no non-letters
            applyTest('httpsSSwwwDrepor-tlabDcomSpypiSpackages', 0.3, False, None, split=split) #fails because embeddedHyphenation=False

    @rlSkipUnless(pyphen,'pyphen missing')
    def test6(self):
        bt = getSampleStyleSheet()['BodyText']
        bt.fontName = 'Helvetica'
        bt.fontSize = 10
        bt.leading = 12
        bt.alignment = TA_JUSTIFY
        canv = Canvas(outputfile('test_platypus_paragraphs_hyphenations.pdf'))
        x = 72
        y = canv._pagesize[1] - 72

        def _t(p,x,y,aW,aH=0x7fffffff,dy=5):
            w, h = p.wrap(aW,aH)
            y0 = y
            y -= h
            canv.saveState()
            canv.setLineWidth(0.5)
            if aH!=0x7fffffff:
                canv.setLineWidth(1)
                canv.setStrokeColor((1,0,0))
                canv.rect(x,y0-aH,aW,aH)
                ny = y0 - max(aH,h)
            else:
                ny = y
            canv.setLineWidth(0.5)
            canv.setStrokeColor((0.5,0.5,0.5))
            canv.rect(x,y,w,h)
            p.drawOn(canv,x,y)
            canv.restoreState()
            return ny-dy
        def t(x,y,aW,aH=0x7fffffff,style=bt):
            p = Paragraph(text,style=style)
            return _t(p,x,y,aW,aH=aH)

        raw = """This is a splittable word 'disestablishment'!"""
        for text in ("""This is a splittable word '<span color="red">dis</span><span color="blue">estab</span><span color="green">lish</span><span color="magenta">ment</span>'!""",
                     """This is a splittable word 'd<span color="red">ise</span><span color="blue">stabl</span><span color="green">ishm</span><span color="magenta">ent</span>'!""",
                     """This is a splittable word 'di<span color="red">ses</span><span color="blue">tabli</span><span color="green">shme</span><span color="magenta">ent</span>'!""",
                    """This is a splittable word 'disestablishment'!""",
                     ):
            aW = stringWidth("This is a splittable word 'dis",bt.fontName,bt.fontSize)
            y = t(x,y,aW)
            aW = stringWidth("This is a splittable word 'dise",bt.fontName,bt.fontSize)
            y = t(x,y,aW)
            aW = stringWidth("This is a splittable word 'disestabl",bt.fontName,bt.fontSize)
            y = t(x,y,aW)
            aW = stringWidth("This is a splittable word 'disestabli",bt.fontName,bt.fontSize)
            y = t(x,y,aW)
            aW = stringWidth("This is a splittable word 'disestablishm",bt.fontName,bt.fontSize)
            y = t(x,y,aW)

        canv.showPage()
        y = canv._pagesize[1] - 72
        nt = bt.clone('nt',fontName='Helvetica', fontSize = 12,leading = 16, alignment = TA_JUSTIFY)
        naW, naH = 342.992125984252, 56.69291338582681
        for ntext in (  b"Bedauerlicherweise ist ein Donaudampfschiffkapit\xc3\xa4n auch <font color='red'>nur</font> <font color='green'>ein</font> Dampfschiffkapit\xc3\xa4n.",
                        b"Bedauerlicherweise ist ein Donaudampfschiffkapit\xc3\xa4n auch nur ein Dampfschiffkapit\xc3\xa4n.",
                        ):
            ntext = (ntext.decode('utf8') + " ") * 3
            p = Paragraph(ntext,style=nt)
            y = _t(p,x,y,naW,aH=naH)

            S = p.split(naW,naH)
            self.assertEqual(len(S),2)
            y = _t(S[0],x,y,naW,aH=naH)
            y = _t(S[1],x,y,naW,aH=naH)
        canv.save()

    @rlSkipUnless(pyphen,'need pyphen')
    def test7(self):
        """test various ways to adjust the hypenationMinWordLength"""
        registerFont(TTFont("Vera", "Vera.ttf"))
        aW = 51.0236220472
        text  = '\u0440\u044b\u0431\u0430 \u043f\u0438\u043b\u0430 \u0438 \u0431\u0430\u0431\u0443 \u0434\u0430\u0436\u0435 \u0432\u0435\u043b\u0430 \u043d\u0430 \u043c\u0430\u044f\u043a'
        text1 = '\u0440\u044b\u0431\u0430 <span color="blue">\u043f\u0438\u043b\u0430</span> \u0438 \u0431\u0430\u0431\u0443 \u0434\u0430\u0436\u0435 \u0432\u0435\u043b\u0430 \u043d\u0430 \u043c\u0430\u044f\u043a'
        tmpls = [
                '%(text)s',
                '<para hyphenationMinWordLength="%(hymwl)d">%(text)s</para>',
                '<para>%(text)s</para>',
                '%(text1)s',
                '<para hyphenationMinWordLength="%(hymwl)d">%(text1)s</para>',
                '<para>%(text1)s</para>',
                ]
        for shaping in (False,True) if getFont('Vera').shapable else (False,):
            for ex,x,hymwl in [
                    (72,0,None),
                    (72,0,5),
                    (72,0,4),
                    (72,2,None),
                    (72,1,5),
                    (72,1,4),
                    (72,3,None),
                    (72,4,5),
                    (72,5,4),
                    ] if shaping else [
                    (72,0,None),    #default is 5
                    (72,0,5),
                    (60,0,4),
                    (72,2,None),    #default is 5
                    (72,1,5),
                    (60,1,4),
                    (72,3,None),    #default is 5
                    (72,4,5),
                    (60,5,4),
                    ]:
                kwds = dict(hyphenationMinWordLength=hymwl) if hymwl!=None else {}
                template = tmpls[x]
                t = template % locals()
                p = Paragraph(
                        template % locals(),
                        style = ParagraphStyle('P10H5', fontSize=10, fontName="Vera", hyphenationLang="ru_RU",shaping=shaping,**kwds),
                        )
                w,h = p.wrap(aW,0x7fffffff)
                self.assertEqual(h,ex,f'Russion hyphenation test failed for {ex=} {template=!a} {hymwl=!a} {h=} {shaping=}\n{text=!r}')

    @rlSkipUnless(pyphen,'need pyphen')
    def test8(self):
        """display splitting of hyphenated words"""
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.styles import ParagraphStyle
        from reportlab.lib.utils import isBytes
        import hashlib
        from reportlab.pdfgen.canvas import Canvas
        from reportlab.platypus.paragraph import Paragraph
        pW, pH = A4
        canv = Canvas(outputfile('test_platypus_paragraphs_hysplit.pdf'),pagesize=(pW,pH))
        text = 'Supercalifragilisticexpialidocious'
        mtext = '<span color="red">Super</span>califragilisticexpialidocious'
        mtext1 = 'Supercalifragilisticexpiali<span color="green">docious</span>'
        stext = 'Super\xadcali\xadfragi\xadlistic\xadexpi\xadali\xaddocious'
        mstext = '<span color="red">Super\xad</span>cali\xadfragi\xadlistic\xadexpi\xadali\xaddocious'
        mstext1 = 'Super\xadcali\xadfragi\xadlistic\xadexpi\xadali\xad<span color="green">docious</span>'
        text =   'Supercalifragilisticexpialidocious'
        mtext2 = 'converted to a <b>Python</b> <font name=Courier><nobr>string</nobr></font>.'
        mtext3 = 'This one uses fonts with size "14pt" and also uses the em and strong tags: Here comes <font face="Helvetica" size="14pt">Helvetica 14</font> with <Strong>strong</Strong> <em>emphasis</em>.'
        textF = 'Figure [seq template="%(Chapter)s-%(FigureNo+)s"/] - Multi-level templates'
        mtextF = 'Figure &lt;seq template="%(Chapter)s-%(FigureNo+)s"/&gt; - Multi-level templates'
        sty0=ParagraphStyle(
                            name="base",
                            fontName="Helvetica",
                            leading=12,
                            leftIndent=0,
                            firstLineIndent=0,
                            spaceBefore = 9.5,
                            fontSize=10,
                            hyphenationLang="en_GB",
                            )
        sty1=ParagraphStyle(
                            name="base",
                            fontName="Times-Roman",
                            leading=12,
                            leftIndent=0,
                            firstLineIndent=0,
                            spaceBefore = 9.5,
                            fontSize=10,
                            hyphenationLang="en_GB",
                            )
        styN =  ParagraphStyle('normal', hyphenationLang="en_GB")
        styF=ParagraphStyle(
                            name = 'styF',
                            fontName='Courier',
                            fontSize=8,
                            leading=9.6,
                            hyphenationLang="en_GB",
                            )
        def box(x, y, aW, h):
            canv.saveState()
            canv.setDash(1,1)
            canv.setLineWidth(0.1)
            canv.rect(x,y,aW,h)
            canv.restoreState()

        def doPara(P,x,y,aW, wc=1):
            for _ in range(wc):
                w,h = P.wrap(aW,900)
            #print('w=%s h=%s' % (w,h))
            y -= h
            box(x, y, aW, h)
            P.drawOn(canv, x, y)
            return y

        def doTest(msg, t,x,y,aW, st=None, split=True, wc=1):
            if not st: st = sty0
            canv.drawString(x+aW+5,y-12,msg) 
            P = Paragraph(t,st)
            y = doPara(P, x, y, aW, wc=wc) - 5
            if split:
                P = Paragraph(t,st)
                S = P.split(aW, st.leading*2+0.1)
                y = doPara(S[0], x, y, aW) - 5
                y = doPara(S[1], x, y, aW) - 5
            return y

        aW = 55
        x = 72
        y = pH - 72

        cp0 = len(canv._code)
        y = doTest('Single Frag Free Hyphenation', text, x, y, aW) - 5
        y = doTest('Single Frag Soft Hyphenation', stext, x, y, aW) - 5
        y = doTest('Multi Frag Free Hyphenation', mtext, x, y, aW) - 5
        y = doTest('Multi Frag Free Hyphenation 1', mtext1, x, y, aW) - 5
        y = doTest('Multi Frag Free Hyphenation 2', mtext2, x, y, 77, st=sty1, split=False, wc=2) - 5
        y = doTest('Multi Frag Free Hyphenation 3', mtext3, x, y, 439.27559055118115, st=styN, split=False, wc=1) - 5
        y = doTest('Multi Frag Soft Hyphenation', mstext, x, y, aW) - 5
        y = doTest('Multi Frag Soft Hyphenation 1', mstext1, x, y, aW) - 5
        y = doTest('Single Frag Free F', textF, x, y, 158.13921259842525, st=styF, split=False, wc=3) - 5
        y = doTest('Multi Frag Free F', mtextF, x, y, 158.13921259842525, st=styF, split=False, wc=3) - 5
        c = '\n'.join(canv._code[cp0:])
        if not isBytes(c):
            c = c.encode('utf8')
        h = hashlib.md5(c,usedforsecurity=False).hexdigest()
        canv.showPage()
        canv.save()
        #xh = '32e0e490cc4a53c31bb19f1cc52debdd'
        xh = 'eee06395aa68a727d58e688006c85d79'
        self.assertEqual(xh, h, 'test8 code is no longer correct %s != expected %s' % (h,xh))

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
        texts = ['''Furthermore, a subset of <font size="14">English sentences</font> interesting on quite
independent grounds is not quite equivalent to a stipulation to place
the constructions into these various categories.''',
        '''We will bring evidence in favor of
The following thesis:  most of the methodological work in modern
linguistics can be defined in such a way as to impose problems of
phonemic and morphological analysis.''']
        story =[]
        a = story.append
        a(Paragraph("This should &lt;a href=\"#theEnd\" color=\"blue\"&gt;<a href=\"#theEnd\" color=\"blue\">jump</a>&lt;/a&gt; jump to the end!",style=normal))
        a(XPreformatted("This should &lt;a href=\"#theEnd\" color=\"blue\"&gt;<a href=\"#theEnd\" color=\"blue\">jump</a>&lt;/a&gt; jump to the end!",style=normal))
        a(Paragraph("<a href=\"#theEnd\"><u><font color=\"blue\">ditto</font></u></a>",style=normal))
        a(XPreformatted("<a href=\"#theEnd\"><u><font color=\"blue\">ditto</font></u></a>",style=normal))
        a(Paragraph("This <font color='CMYKColor(0,0.6,0.94,0)'>should</font> &lt;a href=\"#thePenultimate\" color=\"blue\"&gt;<a href=\"#thePenultimate\" color=\"blue\">jump</a>&lt;/a&gt; jump to the penultimate page!",style=normal))
        a(Paragraph("This should &lt;a href=\"#theThird\" color=\"blue\"&gt;<a href=\"#theThird\" color=\"blue\">jump</a>&lt;/a&gt; jump to a justified para!",style=normal))
        a(Paragraph("This should &lt;a href=\"#theFourth\" color=\"blue\"&gt;<a href=\"#theFourth\" color=\"blue\">jump</a>&lt;/a&gt; jump to an indented para!",style=normal))
        for mode in (0,1):
            text0 = texts[0]
            text1 = texts[1]
            if mode:
                text0 = text0.replace('English sentences','<b>English sentences</b>').replace('quite equivalent','<i>quite equivalent</i>')
                text1 = text1.replace('the methodological work','<b>the methodological work</b>').replace('to impose problems','<i>to impose problems</i>')
            for t in ('u','strike'):
                for n in range(6):
                    for s in (normal,normal_center,normal_right,normal_just,normal_indent, normal_indent_lv_2):
                        for autoLeading in ('','min','max'):
                            if n==4 and s==normal_center and t=='strike' and mode==1:
                                a(Paragraph("<font color=green>The second jump at the beginning should come here &lt;a name=\"thePenultimate\"/&gt;<a name=\"thePenultimate\"/>!</font>",style=normal))
                            elif n==4 and s==normal_just and t=='strike' and mode==1:
                                a(Paragraph("<font color=green>The third jump at the beginning should come just below here to a paragraph with just an a tag in it!</font>",style=normal))
                                a(Paragraph("<a name=\"theThird\"/>",style=normal))
                            elif n==4 and s==normal_indent and t=='strike' and mode==1:
                                a(Paragraph("<font color=green>The fourth jump at the beginning should come just below here!</font>",style=normal))
                                a(AnchorFlowable('theFourth'))
                            a(Paragraph('n=%d style=%s(autoLeading=%s) tag=%s'%(n,s.name,autoLeading,t),style=normal_sp))
                            a(Paragraph('<para autoleading="%s">%s<%s>%s</%s>. %s <%s>%s</%s>. %s</para>' % (
                            autoLeading,
                            (s==normal_indent_lv_2 and '<seq id="document" inc="no"/>.<seq id="document_lv_2"/>' or ''),
                            t,' '.join((n+1)*['A']),t,text0,t,' '.join((n+1)*['A']),t,text1),
                            style=s))
        a(Paragraph("The jump at the beginning should come here &lt;a name=\"theEnd\"/&gt;<a name=\"theEnd\"/>!",style=normal))
        a(Paragraph('Underlining <span fontSize="11"><u color="red">A<u color="green">B</u><u color="blue">C</u>D<sup><strike width="0.5" color="magenta">2</strike><sup><u color="darkgreen" width="0.2">3</u></sup></sup></u></span>',normal))
        a(Paragraph('<para autoLeading="max" spaceAfter="10">this is in 12 <font size=30>this is in 30</font> <u offset="-0.5" width="0.5" color="red"><u offset="-1.5" width="0.5" color="blue">and</u></u> <link underline="1" ucolor="blue" href="http://google.com/">the link box<sup><a color="red" ucolor="green" underline="1" href="https://www.reportlab.com">2</a></sup> is right (twice).</link></para>''',normal))
        a(Paragraph('<para autoLeading="max" spaceAfter="10">this is in 12 <font size=30>this is in 30</font> and <link underline="1" ucolor="blue" href="http://google.com/">the link box is right.</link></para>''',normal))
        a(Paragraph('Underlining <u><span color="red">underlined in red? <span color="blue"><u>or blue</u></span> or red again?</span></u>',normal))
        a(Paragraph('Link <a href="#theEnd" color="blue">jump</a> to end.<br/>Underlined link <a href="#theEnd" underline="1" ucolor="red" color="blue">jump</a> to end!',style=normal))
        a(Paragraph('<para autoleading=""><u>A</u>. Furthermore, a subset of <font size="14">English sentences</font> interesting on quite\nindependent grounds is not quite equivalent to a stipulation to place\nthe constructions into these various categories. <u>A</u>. We will bring evidence in favor of\nThe following thesis: most of the methodological work in modern\nlinguistics can be defined in such a way as to impose problems of\nphonemic and morphological analysis.</para>',normal))
        a(Paragraph('<para autoleading=""><u>A</u>. Furthermore, a subset of <font size="14">English sentences</font> interesting on quite<br/><u>A</u>.</para>',normal))
        a(Paragraph("<para>This is a <sup rise=5><span color='red'>sup</span></sup>rise=5.</para>",normal))
        a(Paragraph('<span fontSize="11"><u color="green"><strike color="blue">AAAAAA</strike></u></span>',normal))
        a(Paragraph("Underlining &amp; width proportional to first use font size ('f' suffix) <u offset='-0.125*f' width='0.05*f'>underlined <span size=14>underlined</span></u>!",style=normal))
        a(Paragraph("Underlining &amp; width proportional to first use font size ('F' suffix) <u offset='-0.125*F' width='0.05*F'>underlined <span size=14>underlined</span></u>!",style=normal))
        a(Paragraph('''<para spaceBefore="10">This is underlined &lt;sup&gt;: a<sup><u><span color="red">sup</span></u></sup></para>''',style=normal))
        a(Paragraph('''<para spaceBefore="10">This is <u>underlined</u></para>''',style=normal))
        a(Paragraph('''<para spaceBefore="10">This is <u kind="double">underlined double</u></para>''',style=normal))
        a(Paragraph('''<para spaceBefore="10">This is <strike>striken</strike></para>''',style=normal))
        a(Paragraph('''<para spaceBefore="10">This is <strike><u>both</u></strike></para>''',style=normal))
        a(Paragraph('''<para spaceBefore="10">This is <u width="0.5" offset="-1" kind="double">underlined kind="double"</u></para>''',style=normal))
        a(Paragraph('''<para spaceBefore="10">This is <u width="0.25" offset="-1" kind="double">double underlined with thinner lines</u></para>''',style=normal))
        a(Paragraph('''<para spaceBefore="10">This is <u width="0.5" offset="-0.5" color="red">underlined in red</u></para>''',style=normal))
        a(Paragraph('''<para spaceBefore="10">This is <strike width="0.5" color="red">overstruck in red</strike></para>''',style=normal))
        a(Paragraph('''<para spaceBefore="10">This is <strike width="0.5" color="red" kind="double">doubly overstruck in red</strike></para>''',style=normal))
        a(Paragraph('''<para spaceBefore="10">This is <strike width="0.5" offset="0.125*F" color="red" kind="triple" gap="0.5">triply overstruck in red</strike></para>''',style=normal))
        a(Paragraph('''<para autoLeading="max" spaceAfter="10" spaceBefore="30">this is in 12 <font size="30">this is in 30</font> <u offset="-0.5" width="0.5" color="red"><u offset="-1.5" width="0.5" color="blue">and</u></u> <link underline="1" ucolor="blue" href="http://google.com/">the link box<sup><a color="red" ucolor="green" underline="1" href="https://www.reportlab.com">2</a></sup> is right (twice).</link></para>''',style=normal))
        a(Paragraph("",style=normal))
        # 3.5.x had a bug with leftIndent and underlines, check that
        left_indent = ParagraphStyle(name='left_indent',leftIndent=80,parent=styleSheet['Normal'])
        a(Paragraph("<u>Replicating a left indent underline bug.</u>",style=left_indent))

        #testing PR 49
        a(Paragraph("This paragraph contains <strike>really</strike> large <u>spaces</u> <strike color='blue' offset='1' width='0.5'><u color='red' offset='-1' width='0.5'>between words</u></strike>. ThisLongWordDoesntFitIntoPreviousLineCausingWordsSpread",style=normal_just))

        doc = MyDocTemplate(outputfile('test_platypus_paragraphs_ul.pdf'))
        doc.build(story)

class AutoLeadingTestCase(unittest.TestCase):
    "Test underlining and overstriking of paragraphs."
    def testAutoLeading(self):
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

        from reportlab.lib.testutils import testsFolder
        styleSheet = getSampleStyleSheet()
        normal = ParagraphStyle(name='normal',fontName='Times-Roman',fontSize=12,leading=1.2*12,parent=styleSheet['Normal'])
        normal_sp = ParagraphStyle(name='normal_sp',parent=normal,alignment=TA_JUSTIFY,spaceBefore=12)
        texts = ['''Furthermore, a subset of <font size="14">English sentences</font> interesting on quite
independent grounds is not quite equivalent to a stipulation to place
<font color="blue">the constructions <img src="%(testsFolder)s/../docs/images/testimg.gif"/> into these various categories.</font>'''%dict(testsFolder=testsFolder),
        '''We will bring <font size="18">Ugly Things</font> in favor of
The following thesis:  most of the methodological work in Modern
Linguistics can be <img src="%(testsFolder)s/../docs/images/testimg.gif" valign="baseline" /> defined in such <img src="%(testsFolder)s/../docs/images/testimg.gif" valign="10" /> a way as to impose problems of
phonemic and <u>morphological <img src="%(testsFolder)s/../docs/images/testimg.gif" valign="top"/> </u> analysis.'''%dict(testsFolder=testsFolder)]
        story =[]
        a = story.append
        t = 'u'
        n = 1
        for s in (normal,normal_sp):
            for autoLeading in ('','min','max'):
                a(Paragraph('style=%s(autoLeading=%s)'%(s.name,autoLeading),style=normal_sp))
                a(Paragraph('<para autoleading="%s"><%s>%s</%s>. %s <%s>%s</%s>. %s</para>' % (
                            autoLeading,
                            t,' '.join((n+1)*['A']),t,texts[0],t,' '.join((n+1)*['A']),t,texts[1]),
                            style=s))
        a(Paragraph('''<img src="%(testsFolder)s/../docs/images/testimg.gif" valign="top"/> image is very first thing in the line.'''%dict(testsFolder=testsFolder), style=normal))
        a(Paragraph('some text.... some more.... some text.... some more....', normal))
        a(Paragraph('<img src="%(testsFolder)s/../docs/images/testimg.gif" width="0.57in" height="0.19in" /> some text <br /> '%dict(testsFolder=testsFolder), normal))
        a(Paragraph('some text.... some more.... some text.... some more....', normal))
        a(Paragraph('<img src="%(testsFolder)s/../docs/images/testimg.gif" width="0.57in" height="0.19in" /> <br /> '%dict(testsFolder=testsFolder), normal))
        a(Paragraph('some text.... some more.... some text.... some more....', normal))

        #Volker Haas' valign tests
        fmt = '''<font color="red">%(valign)s</font>: Furthermore, a <u>subset</u> <strike>of</strike> <font size="14">English sentences</font> interesting on quite
independent grounds is not quite equivalent to a stipulation to place <img src="%(testsFolder)s/../docs/images/redsquare.png" width="0.5in" height="0.5in" valign="%(valign)s"/>
the constructions into these <u>various</u> categories. We will bring <font size="18">Ugly Things</font> in favor of
The following thesis:  most of the methodological work in Modern
Linguistics can be defined in such a way as to impose problems of
phonemic and <u>morphological</u> <strike>analysis</strike>.'''

        p_style= ParagraphStyle('Normal')
        p_style.autoLeading = 'max'
        for valign in (
                'baseline',
                'sub',
                'super',
                'top',
                'text-top',
                'middle',
                'bottom',
                'text-bottom',
                '0%',
                '2in',
                ):
            a(Paragraph(fmt % dict(valign=valign,testsFolder=testsFolder),p_style))
            a(XPreformatted(fmt % dict(valign=valign,testsFolder=testsFolder),p_style))

        a(Paragraph('<br/><b>Some Paragraph tests of &lt;sup rise="pts" size="pts"</b>...', normal))
        a(Paragraph("<br/>This is a <sup><span color='red'>sup</span></sup>.",p_style))
        a(XPreformatted("This is a <sup><span color='red'>sup</span></sup>.",p_style))
        a(Paragraph("This is a <sup rise=5><span color='red'>sup</span></sup>rise=5.",p_style))
        a(XPreformatted("This is a <sup rise=5><span color='red'>sup</span></sup>rise=5.",p_style))
        a(Paragraph("This is a <sup rise=6><span color='red'>sup</span></sup>rise=6.",p_style))
        a(XPreformatted("This is a <sup rise=6><span color='red'>sup</span></sup>rise=6.",p_style))
        a(Paragraph("This is a <sup rise=7><span color='red'>sup</span></sup>rise=7.",p_style))
        a(XPreformatted("This is a <sup rise=7><span color='red'>sup</span></sup>rise=7.",p_style))
        a(Paragraph("This is a <sup rise=8><span color='red'>sup</span></sup>rise=8.",p_style))
        a(XPreformatted("This is a <sup rise=8><span color='red'>sup</span></sup>rise=8.",p_style))
        a(Paragraph("This is a <sup rise=9><span color='red'>sup</span></sup>rise=9.",p_style))
        a(XPreformatted("This is a <sup rise=9><span color='red'>sup</span></sup>rise=9.",p_style))
        a(Paragraph("This is a <sup size=7><span color='red'>sup</span></sup>size=7.",p_style))
        a(XPreformatted("This is a <sup size=7><span color='red'>sup</span></sup>size=7.",p_style))
        a(Paragraph("This is a <sup rise=5 size=7><span color='red'>sup</span></sup>rise=5 size=7.",p_style))
        a(XPreformatted("This is a <sup rise=5 size=7><span color='red'>sup</span></sup>rise=5 size=7.",p_style))
        a(Paragraph("This is a <sup rise=6 size=7><span color='red'>sup</span></sup>rise=6 size=7.",p_style))
        a(XPreformatted("This is a <sup rise=6 size=7><span color='red'>sup</span></sup>rise=6 size=7.",p_style))
        a(Paragraph("This is a <sup rise=7 size=7><span color='red'>sup</span></sup>rise=7 size=7.",p_style))
        a(XPreformatted("This is a <sup rise=7 size=7><span color='red'>sup</span></sup>rise=7 size=7.",p_style))
        a(Paragraph("This is a <sup rise=8 size=7><span color='red'>sup</span></sup>rise=8 size=7.",p_style))
        a(XPreformatted("This is a <sup rise=8 size=7><span color='red'>sup</span></sup>rise=8 size=7.",p_style))
        a(Paragraph("This is a <sup rise=9 size=7><span color='red'>sup</span></sup>rise=9 size=7.",p_style))
        a(XPreformatted("This is a <sup rise=9 size=7><span color='red'>sup</span></sup>rise=9 size=7.",p_style))
        a(Paragraph("This is a <sup rise=90% size=70%><span color='red'>sup</span></sup>rise=90% size=70%.",p_style))
        a(Paragraph("This is a <sup rise=-2 size=-2><span color='red'>sup</span></sup>rise=-2 size=-2.",p_style))
        a(Paragraph("This is a <sup rise=-4 size=-3><span color='red'>sup</span></sup>rise=-4 size=-3.",p_style))
        a(PageBreak())

        a(Paragraph('<br/><b>Some Paragraph tests of &lt;img width="x%" height="x%"</b>...', normal))
        a(Paragraph('H=10%% <img src="%(testsFolder)s/../docs/images/testimg.gif" width="0.57in" height="10%%" />'%dict(testsFolder=testsFolder), normal))
        a(Paragraph('H=50%% <img src="%(testsFolder)s/../docs/images/testimg.gif" width="0.57in" height="50%%" />'%dict(testsFolder=testsFolder), normal))
        a(Paragraph('H=100%% <img src="%(testsFolder)s/../docs/images/testimg.gif" width="0.57in" height="100%%" />'%dict(testsFolder=testsFolder), normal))
        a(Paragraph('H=100%% W=10%% <img src="%(testsFolder)s/../docs/images/testimg.gif" width="10%%" height="100%%" />'%dict(testsFolder=testsFolder), normal))
        a(Paragraph('H=100%% W=50%% <img src="%(testsFolder)s/../docs/images/testimg.gif" width="50%%" height="100%%" />'%dict(testsFolder=testsFolder), normal))
        a(Paragraph('H=50%% W=50%% <img src="%(testsFolder)s/../docs/images/testimg.gif" width="50%%" height="50%%" />'%dict(testsFolder=testsFolder), normal))
        a(Paragraph('<br/><b>Some XPreformatted tests of &lt;img width="x%" height="x%"</b>...', normal))
        a(XPreformatted('H=10%% <img src="%(testsFolder)s/../docs/images/testimg.gif" width="0.57in" height="10%%" />'%dict(testsFolder=testsFolder), normal))
        a(XPreformatted('H=50%% <img src="%(testsFolder)s/../docs/images/testimg.gif" width="0.57in" height="50%%" />'%dict(testsFolder=testsFolder), normal))
        a(XPreformatted('H=100%% <img src="%(testsFolder)s/../docs/images/testimg.gif" width="0.57in" height="100%%" />'%dict(testsFolder=testsFolder), normal))
        a(XPreformatted('H=100%% W=10%% <img src="%(testsFolder)s/../docs/images/testimg.gif" width="10%%" height="100%%" />'%dict(testsFolder=testsFolder), normal))
        a(XPreformatted('H=100%% W=50%% <img src="%(testsFolder)s/../docs/images/testimg.gif" width="50%%" height="100%%" />'%dict(testsFolder=testsFolder), normal))
        a(XPreformatted('H=50%% W=50%% <img src="%(testsFolder)s/../docs/images/testimg.gif" width="50%%" height="50%%" />'%dict(testsFolder=testsFolder), normal))
        a(Paragraph('<br/><b>Some CJK Paragraph tests of &lt;img width="x%" height="x%"</b>...', normal))
        normalCJK = ParagraphStyle('normalCJK', parent=normal, wordWrap = 'CJK')
        a(Paragraph('H=10%% <img src="%(testsFolder)s/../docs/images/testimg.gif" width="0.57in" height="10%%" />'%dict(testsFolder=testsFolder), normalCJK))
        a(Paragraph('H=50%% <img src="%(testsFolder)s/../docs/images/testimg.gif" width="0.57in" height="50%%" />'%dict(testsFolder=testsFolder), normalCJK))
        a(Paragraph('H=100%% <img src="%(testsFolder)s/../docs/images/testimg.gif" width="0.57in" height="100%%" />'%dict(testsFolder=testsFolder), normalCJK))
        a(Paragraph('H=100%% W=10%% <img src="%(testsFolder)s/../docs/images/testimg.gif" width="10%%" height="100%%" />'%dict(testsFolder=testsFolder), normalCJK))
        a(Paragraph('H=100%% W=50%% <img src="%(testsFolder)s/../docs/images/testimg.gif" width="50%%" height="100%%" />'%dict(testsFolder=testsFolder), normalCJK))
        a(Paragraph('H=50%% W=50%% <img src="%(testsFolder)s/../docs/images/testimg.gif" width="50%%" height="50%%" />'%dict(testsFolder=testsFolder), normalCJK))
        doc = MyDocTemplate(outputfile('test_platypus_paragraphs_autoleading.pdf'))
        doc.build(story)

def alphaSortedItems(d):
    return (i[1] for i in sorted((j[0].lower(),j) for j in d.items()))

def tentities(title, b, fn):
    from reportlab.platypus.paraparser import greeks
    from reportlab.platypus.doctemplate import SimpleDocTemplate
    from reportlab.pdfbase.pdfmetrics import stringWidth, registerFont, registerFontFamily
    from reportlab.pdfbase.ttfonts import TTFont
    from reportlab.platypus.tables import TableStyle, Table
    from reportlab.platypus.paragraph import Paragraph
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

    for v in DEJAVUSANS:
        registerFont(TTFont(v,v+'.ttf'))
    registerFontFamily(*(DEJAVUSANS[:1]+DEJAVUSANS))

    def bu(s):
        return asUnicode(s) if not b else asBytes(s)

    bt = getSampleStyleSheet()['BodyText']
    bt.fontName = 'DejaVuSans'
    doc = SimpleDocTemplate(fn)
    story = [Paragraph('<b>%s</b>' % asNative(title),bt)]
    story.extend([Paragraph(bu('&amp;%s; = <span color="red">&%s;</span>' % (k,k)), bt) for k, v in alphaSortedItems(greeks)])
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
        normal_just = ParagraphStyle(name='normal_just',parent=normal,alignment=TA_JUSTIFY,spaceAfter=12)
        text0 = '''Furthermore, a subset of English sentences interesting on quite
independent grounds is not quite equivalent to a stipulation to place
the constructions into these various categories. We will bring evidence in favor of
The following thesis:  most of the methodological work in modern
linguistics can be defined in such a way as to impose problems of
phonemic and morphological analysis.'''
        story =[]
        a = story.append
        for mode in (0,1,2,3,4,5,6,7):
            text = text0
            paraStyle = normal_just
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
            elif mode==4:
                text = text.replace('English ','English&nbsp;').replace('quite ','quite&nbsp;')
                text = text.replace(' methodological','&nbsp;methodological').replace(' impose','&nbsp;impose')
                a(Paragraph('Justified paragraph in normal font &amp; some hard spaces',style=normal))
            elif mode in (5,6,7):
                text = text.replace('as to impose','<br/>as to impose').replace(' most of the','<br/>most of the')
                text = text.replace(' grounds','<br/>grounds').replace(' various','<br/>various')
                if mode in (6,7):
                    msg = []
                    msg.append('justifyBreaks=1')
                    paraStyle = paraStyle.clone('paraStyle6',paraStyle,justifyBreaks=1)
                    if mode==7:
                        msg.append('justifyLastLine=3')
                        paraStyle = paraStyle.clone('paraStyle7',paraStyle,justifyLastLine=3)
                    msg = '(%s) ' % (' '.join(msg))
                else:
                    a(PageBreak())
                    msg = ' '

                a(Paragraph('Justified%swith some &lt;br/&gt; tags' % msg,style=normal))
            else:
                a(Paragraph('Justified paragraph in normal font',style=normal))

            a(Paragraph(text,style=paraStyle))
        doc = MyDocTemplate(outputfile('test_platypus_paragraphs_just.pdf'))
        doc.build(story)

    def testAutoPageTemplate(self):
        from reportlab.platypus import BaseDocTemplate, PageTemplate, Frame, PageBegin
        from reportlab.lib.units import inch
        class onPage:
            def __init__(self,label):
                self.label = label
            def __call__(self,canv,doc):
                canv.drawString(72,72,'This is pageTemplate(%s)' % (self.label,))
        class MyDocTemplate(BaseDocTemplate):
            _invalidInitArgs = ('pageTemplates',)

            def __init__(self, filename, **kw):
                self.allowSplitting = 0
                BaseDocTemplate.__init__(self, filename, **kw)
                self.addPageTemplates(
                        [
                        PageTemplate('normal',
                                [Frame(inch, inch, 6.27*inch, 9.69*inch, id='first',topPadding=0,rightPadding=0,leftPadding=0,bottomPadding=0,showBoundary=ShowBoundaryValue(color="red"))],
                                onPage = onPage('normal'),
                                ),
                        PageTemplate('auto',
                                [Frame(inch, inch, 6.27*inch, 9.69*inch, id='first',topPadding=0,rightPadding=0,leftPadding=0,bottomPadding=0,showBoundary=ShowBoundaryValue(color="red"))],
                                onPage = onPage('auto'),
                                autoNextPageTemplate = 'autoFollow',
                                ),
                        PageTemplate('autoFollow',
                                [Frame(inch, inch, 6.27*inch, 9.69*inch, id='first',topPadding=0,rightPadding=0,leftPadding=0,bottomPadding=0,showBoundary=ShowBoundaryValue(color="red"))],
                                onPage = onPage('autoFollow'),
                                ),
                        ])
        styleSheet = getSampleStyleSheet()
        normal = ParagraphStyle(name='normal',fontName='Times-Roman',fontSize=12,leading=1.2*12,parent=styleSheet['Normal'])
        story =[]
        a = story.append
        a(Paragraph('should be on page template normal', normal))
        a(NextPageTemplate('auto'))
        a(PageBreak())
        a(Paragraph('should be on page template auto', normal))
        a(PageBreak())
        a(DocAssert('doc.pageTemplate.id=="autoFollow"','expected doc.pageTemplate.id=="autoFollow"'))
        a(Paragraph('should be on page template autoFollow 1', normal))
        a(PageBreak())
        a(Paragraph('should be on page template autoFollow 2', normal))
        doc = MyDocTemplate(outputfile('test_platypus_paragraphs_AutoNextPageTemplate.pdf'))
        doc.build(story)

    def testParaBrFlowing(self):
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
                                [
                                Frame(inch, 4.845*inch, 3*inch, 3.645*inch, id='first',topPadding=0,rightPadding=0,leftPadding=0,bottomPadding=0,showBoundary=ShowBoundaryValue(color="red")),
                                Frame(4.27*inch, 4.845*inch, 3*inch, 3.645*inch, id='second',topPadding=0,rightPadding=0,leftPadding=0,bottomPadding=0,showBoundary=ShowBoundaryValue(color="red")),
                                Frame(inch, inch, 3*inch, 3.645*inch, id='third',topPadding=0,rightPadding=0,leftPadding=0,bottomPadding=0,showBoundary=ShowBoundaryValue(color="red")),
                                Frame(4.27*inch, inch, 3*inch, 3.645*inch, id='fourth',topPadding=0,rightPadding=0,leftPadding=0,bottomPadding=0,showBoundary=ShowBoundaryValue(color="red"))
                                ],
                                ),
                        ])
        styleSheet = getSampleStyleSheet()
        normal = ParagraphStyle(name='normal',fontName='Helvetica',fontSize=10,leading=12,parent=styleSheet['Normal'])
        bold = ParagraphStyle(name='bold',fontName='Helvetica-Bold',fontSize=12,leading=14.4,parent=normal)
        brText="""
Clearly, the natural general principle that will subsume this case is
not subject to a parasitic gap construction.  Presumably, most of the
methodological work in modern linguistics can be defined in such a way
as to impose the system of base rules exclusive of the lexicon.  In the
discussion of resumptive pronouns following (81), the fundamental error
of regarding functional notions as categorial is to be regarded as a
descriptive <span color="red">fact</span>.<br/>So far, the earlier discussion of deviance is not
quite equivalent to a parasitic gap construction.  To characterize a
linguistic level L, a case of semigrammaticalness of a different sort
may remedy and, at the same time, eliminate irrelevant intervening
contexts in selectional <span color="red">rules</span>.<br/>
Summarizing, then, we assume that the descriptive power of the base
component can be defined in such a way as to impose nondistinctness in
the sense of distinctive feature theory.  A lot of sophistication has
been developed about the utilization of machines for complex purposes,
the notion of level of grammaticalness delimits an abstract underlying
<span color="red">order</span>.<br/>To provide a constituent structure for T(Z,K), a subset of
English sentences interesting on quite independent grounds appears to
correlate rather closely with problems of phonemic and morphological
analysis.  For one thing, this analysis of a formative as a pair of sets
of features is rather different from a general convention regarding the
forms of the grammar.  A lot of sophistication has been developed about
the utilization of machines for complex purposes, a case of
semigrammaticalness of a different sort is not to be considered in
determining an important distinction in language <span color="red">use</span>.<br/>
We will bring evidence in favor of the following thesis:  a subset of
English sentences interesting on quite independent grounds delimits a
descriptive <span color="red">fact</span>.<br/>To characterize a linguistic level L, the notion of
level of grammaticalness is not to be considered in determining a
parasitic gap construction.  It must be emphasized, once again, that the
speaker-hearer's linguistic intuition can be defined in such a way as to
impose a stipulation to place the constructions into these various
categories.  On our assumptions, the appearance of parasitic gaps in
domains relatively inaccessible to ordinary extraction raises serious
doubts about problems of phonemic and morphological analysis.  For one
thing, the fundamental error of regarding functional notions as
categorial is not quite equivalent to a stipulation to place the
constructions into these various <span color="red">categories</span>.<br/>
Thus the descriptive power of the base component is unspecified with
respect to the strong generative capacity of the theory.  Presumably,
the theory of syntactic features developed earlier appears to correlate
rather closely with a corpus of utterance tokens upon which conformity
has been defined by the paired utterance test.  To provide a constituent
structure for T(Z,K), a case of semigrammaticalness of a different sort
is not to be considered in determining the ultimate standard that
determines the accuracy of any proposed grammar.  For any transformation
which is sufficiently diversified in application to be of any interest,
a subset of English sentences interesting on quite independent grounds
raises serious doubts about the requirement that branching is not
tolerated within the dominance scope of a complex symbol.  We will bring
evidence in favor of the following thesis:  an important property of
these three types of EC is not to be considered in determining the
system of base rules exclusive of the <span color="red">lexicon</span>.<br/>
With this clarification, the descriptive power of the base component is
not subject to the requirement that branching is not tolerated within
the dominance scope of a complex <span color="red">symbol</span>.<br/>In the discussion of
resumptive pronouns following (81), this selectionally introduced
contextual feature does not readily tolerate a parasitic gap
construction.  Another superficial similarity is the interest in
simulation of behavior, a descriptively adequate grammar does not affect
the structure of a corpus of utterance tokens upon which conformity has
been defined by the paired utterance <span color="red">test</span>.<br/>From C1, it follows that the
speaker-hearer's linguistic intuition is not to be considered in
determining the traditional practice of grammarians.  Let us continue to
suppose that the notion of level of grammaticalness is necessary to
impose an interpretation on the system of base rules exclusive of the
<span color="red">lexicon</span>.<br/>
"""
        story =[]
        a = story.append
        a(Paragraph('Paragraph Flowing', bold))
        a(Paragraph(brText, normal))
        doc = MyDocTemplate(outputfile('test_platypus_paragraphs_para_br_flowing.pdf'))
        doc.build(story)

    def testParaNBSP(self):
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
                                [
                                Frame(inch, 4.845*inch, 3*inch, 3.645*inch, id='first',topPadding=0,rightPadding=0,leftPadding=0,bottomPadding=0,showBoundary=ShowBoundaryValue(color="red")),
                                Frame(4.27*inch, 4.845*inch, 3*inch, 3.645*inch, id='second',topPadding=0,rightPadding=0,leftPadding=0,bottomPadding=0,showBoundary=ShowBoundaryValue(color="red")),
                                Frame(inch, inch, 3*inch, 3.645*inch, id='third',topPadding=0,rightPadding=0,leftPadding=0,bottomPadding=0,showBoundary=ShowBoundaryValue(color="red")),
                                Frame(4.27*inch, inch, 3*inch, 3.645*inch, id='fourth',topPadding=0,rightPadding=0,leftPadding=0,bottomPadding=0,showBoundary=ShowBoundaryValue(color="red"))
                                ],
                                ),
                        ])
        styleSheet = getSampleStyleSheet()
        normal = ParagraphStyle(name='normal',fontName='Helvetica',fontSize=10,leading=12,parent=styleSheet['Normal'])
        bold = ParagraphStyle(name='normal',fontName='Helvetica-Bold',fontSize=10,leading=12,parent=styleSheet['Normal'])
        registerFontFamily('Helvetica','Helvetica','Helvetica-Bold','Helvetica-Oblique','Helvetica-BoldOblique')
        story =[]
        a = story.append
        a(Paragraph('Paragraph Hard Space Handling', bold))
        a(Paragraph(''' <span backcolor="pink">ABCDEFGHI</span> ''', normal))
        a(Paragraph(''' <span backcolor="palegreen">&nbsp;ABCDEFGHI&nbsp;</span> ''', normal))
        a(Paragraph('''<span backcolor="lightblue">&nbsp;</span>''', normal))
        a(Paragraph('''<span backcolor="lightblue">&nbsp;</span><span backcolor="palegreen">&nbsp;</span> ''', normal))
        a(Paragraph('''<span backcolor="pink"><b>A</b></span><span backcolor="lightblue"> </span><span backcolor="pink"><b>B</b></span>''', normal))
        a(Paragraph('''<span backcolor="pink"><b>A</b></span> <span backcolor="lightblue"> </span><span backcolor="pink"><b>B</b></span>''', normal))
        a(Paragraph('''<span backcolor="pink"><b>A</b></span><span backcolor="lightblue">&nbsp;</span><span backcolor="pink"><b>B</b></span>''', normal))
        a(Paragraph('''<span backcolor="pink"><b>A</b></span> <span backcolor="lightblue">&nbsp;</span><span backcolor="pink"><b>B</b></span>''', normal))
        doc = MyDocTemplate(outputfile('test_platypus_paragraphs_nbsp.pdf'))
        doc.build(story)

    @rlSkipUnless(haveDejaVu(),'need DejaVu Font')
    def testParaEntities(self):
        tentities(b'unicode formatted paragraphs',False,outputfile('test_platypus_unicode_paragraph_entities.pdf'))
        tentities(b'byte formatted paragraphs',True,outputfile('test_platypus_bytes_paragraph_entities.pdf'))

    def testXPreUnderlining(self):
        styleSheet = getSampleStyleSheet()
        bt = styleSheet['BodyText']
        story = [
                XPreformatted("xpre<u><font size='1' color='red'>SS</font>        </u>",bt),
                XPreformatted("xpre<u><font size='1' color='red'>SS</font>        </u>|",bt),
                XPreformatted("<u><font size='1' color='red'>SS</font>        </u>",bt),
                XPreformatted("<u><font size='1' color='red'>SS</font>        </u>|",bt),
                ]
        doc = MyDocTemplate(outputfile('test_platypus_XPreUnderlining.pdf'))
        doc.build(story)

#noruntests
def makeSuite():
    return makeSuiteForClasses(ParagraphCorners,SplitFrameParagraphTest,FragmentTestCase, ParagraphSplitTestCase, ULTestCase, JustifyTestCase,
            AutoLeadingTestCase)

#noruntests
if __name__ == "__main__":
    unittest.TextTestRunner().run(makeSuite())
    printLocation()
