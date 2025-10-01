#Copyright ReportLab Europe Ltd. 2000-2017
#see license.txt for license details
"""Tests pageBreakBefore, frameBreakBefore, keepWithNext...
"""
__version__='3.3.0'
from reportlab.lib.testutils import setOutDir,makeSuiteForClasses, outputfile, printLocation, invariantSeed
setOutDir(__name__)
import sys, os, time, re
from reportlab.rl_config import invariant as rl_invariant
from operator import truth
import unittest
from reportlab.platypus.flowables import Flowable, KeepTogether, KeepTogetherSplitAtTop
from reportlab.lib import colors
from reportlab.lib.units import cm, mm
from reportlab.lib.enums import TA_LEFT, TA_RIGHT, TA_CENTER, TA_JUSTIFY
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus.frames import Frame
from reportlab.lib.randomtext import randomText, PYTHON
from reportlab.platypus.doctemplate import PageTemplate, BaseDocTemplate, Indenter, SimpleDocTemplate, LayoutError
from reportlab.platypus.paragraph import *
from reportlab.pdfgen.canvas import Canvas, ShowBoundaryValue
from reportlab.rl_config import paraFontSizeHeightOffset
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.lib.pagesizes import A4, portrait

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
        BaseDocTemplate.__init__(self, filename, **kw)
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
    "This makes one long multi-page paragraph in test_platypus_breaking."

    invariantSeed(1532760416)
    def RT(k,theme='PYTHON',sentences=1,cache={}):
        if k not in cache:
            cache[k] = randomText(theme=theme,sentences=sentences)
        return cache[k]

    # Build story.
    def makeStory():
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
        btj = ParagraphStyle('bodyText1j',parent=bt,alignment=TA_JUSTIFY)
        btr = ParagraphStyle('bodyText1r',parent=bt,alignment=TA_RIGHT)
        btc = ParagraphStyle('bodyText1c',parent=bt,alignment=TA_CENTER)
        from reportlab.lib.utils import TimeStamp
        ts = TimeStamp()
        a(Paragraph("""
            <a name='top'/>Subsequent pages test pageBreakBefore, frameBreakBefore and
            keepTogether attributes.  Generated at %s.  The number in brackets
            at the end of each paragraph is its position in the story. (%d)""" % (
                ts.asctime, len(story)), bt))

        for i in range(10):
            a(Paragraph('Heading 1 always starts a new page (%d)' % len(story), h1))
            for j in range(3):
                a(Paragraph('Heading1 paragraphs should always'
                                'have a page break before.  Heading 2 on the other hand'
                                'should always have a FRAME break before (%d)' % len(story), bt))
                a(Paragraph('Heading 2 always starts a new frame (%d)' % len(story), h2))
                a(Paragraph('Heading1 paragraphs should always'
                                'have a page break before.  Heading 2 on the other hand'
                                'should always have a FRAME break before (%d)' % len(story), bt))
                for j in range(3):
                    a(Paragraph(RT((i,j,0),theme=PYTHON, sentences=2)+' (%d)' % len(story), bt))
                    a(Paragraph('I should never be at the bottom of a frame (%d)' % len(story), h3))
                    a(Paragraph(RT((i,j,1),theme=PYTHON, sentences=1)+' (%d)' % len(story), bt))

        for align,bts in [('left',bt),('JUSTIFIED',btj),('RIGHT',btr),('CENTER',btc)]:
            a(Paragraph('Now we do &lt;br/&gt; tests(align=%s)' % align, h1))
            a(Paragraph('First off no br tags',h3))
            a(Paragraph(_text1,bts))
            a(Paragraph("&lt;br/&gt; after 'the' in line 4",h3))
            a(Paragraph(_text1.replace('forms of the','forms of the<br/>',1),bts))
            a(Paragraph("2*&lt;br/&gt; after 'the' in line 4",h3))
            a(Paragraph(_text1.replace('forms of the','forms of the<br/><br/>',1),bts))
            a(Paragraph("&lt;br/&gt; after 'I suggested ' in line 5",h3))
            a(Paragraph(_text1.replace('I suggested ','I suggested<br/>',1),bts))
            a(Paragraph("2*&lt;br/&gt; after 'I suggested ' in line 5",h3))
            a(Paragraph(_text1.replace('I suggested ','I suggested<br/><br/>',1),bts))
            a(Paragraph("&lt;br/&gt; at the end of the paragraph!",h3))
            a(Paragraph("""text one<br/>text two<br/>""",bts))
            a(Paragraph("Border with &lt;br/&gt; at the end of the paragraph!",h3))
            bt1 = ParagraphStyle('bodyText1',bts)
            bt1.borderWidth = 0.5
            bt1.borderColor = colors.toColor('red')
            bt1.backColor = colors.pink
            bt1.borderRadius = 2
            bt1.borderPadding = 3
            a(Paragraph("""text one<br/>text two<br/>""",bt1))
            a(Paragraph("Border no &lt;br/&gt; at the end of the paragraph!",h3))
            bt1 = ParagraphStyle('bodyText1',bts)
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
        for i in 0, 1, 2:
            P = Paragraph("""This is a paragraph with <font color='blue'><a href='#top'>with an incredibly
long and boring link in side of it that
contains lots and lots of stupidly boring and worthless information.
So that we can split the link and see if we get problems like Dinu's.
I hope we don't, but you never do Know.</a></font>""",bt)
            a(P)
        return story

    for sfx,klass in (('',KeepTogether),('_ktsat',KeepTogetherSplitAtTop)):
        doc = MyDocTemplate(outputfile('test_platypus_breaking%s.pdf'%sfx),keepTogetherClass=klass,
                displayDocTitle=(sfx==''),
                duplex='Simplex',
                )
        doc.multiBuild(makeStory())

class RenderMeasuringPara:
    def __init__(self,canv,style,aW,measuring=True,annotations=[],errors=[],length_errors=[],onDrawFuncName='_onDrawFunc'):
        ends = []
        def _onDrawFunc(canv,name,label):
            if measuring and label=='end':
                ends.append(canv._curr_tx_info)
            annotations.append(canv._curr_tx_info)
        setattr(canv,onDrawFuncName,_onDrawFunc)
        self._state = (canv,style,aW,measuring,ends,annotations,errors,length_errors)
        if measuring:
            self._end = ('<ondraw name="%s" label="end"/>' % onDrawFuncName)

    def __call__(self,x,y,text,wc,ns,n,hrep=' ',crep=' ',hdw=0,cdw=0):
        canv,style,aW,measuring,ends,annotations,errors,length_errors = self._state
        if measuring: text += self._end
        if '{H}' in text:
            text = text.replace('{H}',hrep)
            wc += hdw
        if '{C}' in text:
            text = text.replace('{C}',crep)
            wc += cdw
        p = Paragraph(text,style)
        w,h = p.wrap(aW,1000)
        annotations[:] = []
        if measuring:
            ends[:] = []
        p.drawOn(canv,x,y-h)
        canv.saveState()
        canv.setLineWidth(0.1)
        canv.setStrokeColorRGB(1,0,0)
        canv.rect(x,y-h,wc,h)

        if n is not None:
            canv.setFillColorRGB(0,1,0)
            canv.drawRightString(x,y-h,'%3d: ' % n)

        if annotations:
            canv.setLineWidth(0.1)
            canv.setStrokeColorRGB(0,1,0)
            canv.setFillColorRGB(0,0,1)
            canv.setFont('Helvetica',0.2)
            for info in annotations:
                cur_x = info['cur_x']+x
                cur_y = info['cur_y']+y-h
                canv.drawCentredString(cur_x, cur_y+0.3,'%.2f' % (cur_x-x))
                canv.line(cur_x,cur_y,cur_x,cur_y+0.299)
        if measuring:
            if not ends:
                errors.append('Paragraph measurement failure no ends found for %s\n%r' % (ns,text))
            elif len(ends)>1:
                errors.append('Paragraph measurement failure no len(ends)==%d for %s\n%r' % (len(ends),ns,text))
            else:
                cur_x = ends[0]['cur_x']
                adiff = abs(wc-cur_x)
                length_errors.append(adiff)
                if adiff>1e-8:
                    errors.append('Paragraph measurement error wc=%.4f measured=%.4f for %s\n%r' % (wc,cur_x,ns,text))
        canv.restoreState()
        return h

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

    def test2(self):
        sty = ParagraphStyle(name = 'normal')
        sty.fontName = 'Times-Roman'
        sty.fontSize = 10
        sty.leading = 12

        p = Paragraph('one two three',sty)
        p.wrap(20,36)
        self.assertEqual(len(p.split(20,24)),2) #widows allowed
        self.assertEqual(len(p.split(20,16)),0) #orphans disallowed
        p.allowWidows = 0
        self.assertEqual(len(p.split(20,24)),0) #widows disallowed
        p.allowOrphans = 1
        self.assertEqual(len(p.split(20,16)),2) #orphans allowed

    def test3(self):
        aW=307
        styleSheet = getSampleStyleSheet()
        bt = styleSheet['BodyText']
        btj = ParagraphStyle('bodyText1j',parent=bt,alignment=TA_JUSTIFY)
        p=Paragraph("""<a name='top'/>Subsequent pages test pageBreakBefore, frameBreakBefore and
                keepTogether attributes.  Generated at 1111. The number in brackets
                at the end of each paragraph is its position in the story. llllllllllllllllllllllllll 
                bbbbbbbbbbbbbbbbbbbbbb ccccccccccccccccccccccc ddddddddddddddddddddd eeeeyyy""",btj)

        w,h=p.wrap(aW,1000)
        canv=Canvas('test_platypus_paragraph_just.pdf',pagesize=(aW,h))
        i=len(canv._code)
        p.drawOn(canv,0,0)
        ParaCode=canv._code[i:]
        canv.saveState()
        canv.setLineWidth(0)
        canv.setStrokeColorRGB(1,0,0)
        canv.rect(0,0,aW,h)
        canv.restoreState()
        canv.showPage()
        canv.save()
        x = paraFontSizeHeightOffset and '50' or '53.17'
        good = ['q', '1 0 0 1 0 0 cm', 'q', 'BT 1 0 0 1 0 '+x+' Tm 3.59 Tw 12 TL /F1 10 Tf 0 0 0 rg (Subsequent pages test pageBreakBefore, frameBreakBefore and) Tj T* 0 Tw .23 Tw (keepTogether attributes. Generated at 1111. The number in brackets) Tj T* 0 Tw .299167 Tw (at the end of each paragraph is its position in the story. llllllllllllllllllllllllll) Tj T* 0 Tw 66.9 Tw (bbbbbbbbbbbbbbbbbbbbbb ccccccccccccccccccccccc) Tj T* 0 Tw (ddddddddddddddddddddd eeeeyyy) Tj T* ET', 'Q', 'Q']
        ok= ParaCode==good
        assert ok, "\nParaCode=%r\nexpected=%r" % (ParaCode,good)

    def test4(self):
        styleSheet = getSampleStyleSheet()
        bt = styleSheet['BodyText']
        bfn = bt.fontName = 'Helvetica'
        bfs = bt.fontSize
        bfl = bt.leading
        canv=Canvas(outputfile('test_platypus_paragraph_line_lengths.pdf'))
        canv.setFont('Courier',bfs,bfl)
        pageWidth, pageHeight = canv._pagesize
        y = pageHeight - 15
        x = stringWidth('999: ','Courier',bfs) + 5
        aW = int(pageWidth)-2*x

        swc = lambda t: stringWidth(t,'Courier',bfs)
        swcbo = lambda t: stringWidth(t,'Courier-BoldOblique',bfs)
        swh = lambda t: stringWidth(t,'Helvetica',bfs)
        swhbo = lambda t: stringWidth(t,'Helvetica-BoldOblique',bfs)
        swt = lambda t: stringWidth(t,'Times-Roman',bfs)
        swtb = lambda t: stringWidth(t,'Times-Bold',bfs)

        apat = re.compile("(<a\\s+name='a\\d+'/>)")
        argv = sys.argv[1:]
        data = (
            (0,"<span fontName='Courier'>Hello{C}</span> World.", swc('Hello ')+swh('World.')),
            (1,"<span fontName='Courier'>Hello</span>{H}World.", swc('Hello')+swh(' World.')),
            (2," <a name='a2'/><span fontName='Courier'>Hello{C}</span> World.", swc('Hello ')+swh('World.')),
            (3," <a name='a3'/><span fontName='Courier'>Hello</span>{H}World.", swc('Hello')+swh(' World.')),
            (4,"<span fontName='Courier'><a name='a4'/>Hello{C}</span> World.", swc('Hello ')+swh('World.')),
            (5,"<span fontName='Courier'><a name='a5'/>Hello</span>{H}World.", swc('Hello')+swh(' World.')),
            (6,"<span fontName='Courier'>Hello<a name='a6'/>{C}</span> World.", swc('Hello ')+swh('World.')),
            (7,"<span fontName='Courier'>Hello<a name='a7'/></span>{H}World.", swc('Hello')+swh(' World.')),
            (8,"<span fontName='Courier'>Hello{C}<a name='a8'/></span> World.", swc('Hello ')+swh('World.')),
            (9,"<span fontName='Courier'>Hello</span><a name='a9'/>{H}World.", swc('Hello')+swh(' World.')),
            (10,"<span fontName='Courier'>Hello{C}</span> <a name='a10'/>World.", swc('Hello ')+swh('World.')),
            (11,"<span fontName='Courier'>Hello</span>{H}<a name='a11'/>World.", swc('Hello')+swh(' World.')),
            (12,"<span fontName='Courier'>Hello{C}</span> World. <a name='a12'/>", swc('Hello ')+swh('World.')),
            (13,"<span fontName='Courier'>Hello</span>{H}World. <a name='a13'/>", swc('Hello')+swh(' World.')),
            (14," <a name='a2'/> <span fontName='Courier'>Hello{C}</span> World.", swc('Hello ')+swh('World.')),
            (15," <a name='a3'/> <span fontName='Courier'>Hello</span>{H}World.", swc('Hello')+swh(' World.')),
            (16," <a name='a2'/> <span fontName='Courier'>Hello{C}<a name='b'/> </span> <a name='b'/> World.", swc('Hello ')+swh('World.')),
            (17," <a name='a3'/> <span fontName='Courier'>Hello</span>{H}<a name='b'/> World.", swc('Hello')+swh(' World.')),
            (30,"<span fontName='Courier'>He<span face='Times-Roman' color='red'>l</span><span face='Times-Bold' color='orange'>lo</span>{C}</span> World.", swt('l')+swtb('lo')+swc('He ')+swh('World.')),
            (31,"<span fontName='Courier'>He<span face='Times-Roman' color='red'>l</span><span face='Times-Bold' color='orange'>lo</span></span>{H}World.", swt('l')+swtb('lo')+swc('He')+swh(' World.')),
            (32," <a name='a2'/><span fontName='Courier'>He<span face='Times-Roman' color='red'>l</span><span face='Times-Bold' color='orange'>lo</span>{C}</span> World.", swt('l')+swtb('lo')+swc('He ')+swh('World.')),
            (33," <a name='a3'/><span fontName='Courier'>He<span face='Times-Roman' color='red'>l</span><span face='Times-Bold' color='orange'>lo</span></span>{H}World.", swt('l')+swtb('lo')+swc('He')+swh(' World.')),
            (34,"<span fontName='Courier'><a name='a4'/>He<span face='Times-Roman' color='red'>l</span><span face='Times-Bold' color='orange'>lo</span> </span> World.", swt('l')+swtb('lo')+swc('He ')+swh('World.')),
            (35,"<span fontName='Courier'><a name='a5'/>He<span face='Times-Roman' color='red'>l</span><span face='Times-Bold' color='orange'>lo</span></span>{H}World.", swt('l')+swtb('lo')+swc('He')+swh(' World.')),
            (36,"<span fontName='Courier'>He<span face='Times-Roman' color='red'>l</span><span face='Times-Bold' color='orange'>lo</span><a name='a6'/> </span> World.", swt('l')+swtb('lo')+swc('He ')+swh('World.')),
            (37,"<span fontName='Courier'>He<span face='Times-Roman' color='red'>l</span><span face='Times-Bold' color='orange'>lo</span><a name='a7'/></span>{H}World.", swt('l')+swtb('lo')+swc('He')+swh(' World.')),
            (38,"<span fontName='Courier'>He<span face='Times-Roman' color='red'>l</span><span face='Times-Bold' color='orange'>lo</span>{C}<a name='a8'/></span> World.", swt('l')+swtb('lo')+swc('He ')+swh('World.')),
            (39,"<span fontName='Courier'>He<span face='Times-Roman' color='red'>l</span><span face='Times-Bold' color='orange'>lo</span></span><a name='a9'/>{H}World.", swt('l')+swtb('lo')+swc('He')+swh(' World.')),
            (40,"<span fontName='Courier'>He<span face='Times-Roman' color='red'>l</span><span face='Times-Bold' color='orange'>lo</span>{C}</span> <a name='a10'/>World.", swt('l')+swtb('lo')+swc('He ')+swh('World.')),
            (41,"<span fontName='Courier'>He<span face='Times-Roman' color='red'>l</span><span face='Times-Bold' color='orange'>lo</span></span>{H}<a name='a11'/>World.", swt('l')+swtb('lo')+swc('He')+swh(' World.')),
            (42,"<span fontName='Courier'>He<span face='Times-Roman' color='red'>l</span><span face='Times-Bold' color='orange'>lo</span>{C}</span> World. <a name='a12'/>", swt('l')+swtb('lo')+swc('He ')+swh('World.')),
            (43,"<span fontName='Courier'>He<span face='Times-Roman' color='red'>l</span><span face='Times-Bold' color='orange'>lo</span></span> World.{H}<a name='a13'/>", swt('l')+swtb('lo')+swc('He')+swh(' World.')),
            (44," <a name='a2'/> <span fontName='Courier'>He<span face='Times-Roman' color='red'>l</span><span face='Times-Bold' color='orange'>lo</span>{C}</span> World.", swt('l')+swtb('lo')+swc('He ')+swh('World.')),
            (45," <a name='a3'/> <span fontName='Courier'>He<span face='Times-Roman' color='red'>l</span><span face='Times-Bold' color='orange'>lo</span></span>{H}World.", swt('l')+swtb('lo')+swc('He')+swh(' World.')),
            (46," <a name='a2'/> <span fontName='Courier'>He<span face='Times-Roman' color='red'>l</span><span face='Times-Bold' color='orange'>lo</span>{C}<a name='b'/> </span> <a name='b'/> World.", swt('l')+swtb('lo')+swc('He ')+swh('World.')),
            (47," <a name='a3'/> <span fontName='Courier'>He<span face='Times-Roman' color='red'>l</span><span face='Times-Bold' color='orange'>lo</span></span>{H}<a name='b'/> World.", swt('l')+swtb('lo')+swc('He')+swh(' World.')),
            )
        _exceptions = {
                1:  {
                    8: swh(' '),
                    12: swh(' '),
                    13: swh(' '),
                    14: swh(' '),
                    15: swh(' '),
                    16: swh(' '),
                    17: swh(' '),
                    38: swh(' '),
                    42: swh(' '),
                    43: swh(' '),
                    44: swh(' '),
                    45: swh(' '),
                    46: swh(' '),
                    47: swh(' '),
                    },
                }
        def gex(n,v):
            return _exceptions[1].get(v,0)
        x1 = x + max(_tmp[2] for _tmp in data) + 5
        x2 = x1 + max(_tmp[2]+10+gex(1,_tmp[0]) for _tmp in data) + 5
        x3 = x2 + max(_tmp[2]+10+gex(2,_tmp[0]) for _tmp in data) + 5
        x4 = x3 + max(_tmp[2]+20+gex(3,_tmp[0]) for _tmp in data) + 5
        annotations = []
        errors = []
        measuring = True
        length_errors = []
        onDrawFuncName = '_onDrawFunc'
        doPara = RenderMeasuringPara(canv,bt,aW,measuring,annotations,errors,length_errors,onDrawFuncName)

        rep0 = '<ondraw name="%s"/>\\1' % onDrawFuncName
        for n,text,wc in data:
            if argv and str(n) not in argv: continue
            text0 = (apat.sub(rep0,text) if rep0 else text)
            ns = str(n)
            h = doPara(x,y,text0,wc,ns,n)
            if '<a' in text:
                text1 = apat.sub('<img width="10" height="5" src="pythonpowered.gif"/>',text0)
                doPara(x1,y,text1,wc+10+gex(1,n),ns+'.11',None)
                text2 = apat.sub('\\1<img width="10" height="5" src="pythonpowered.gif"/>',text0)
                doPara(x2,y,text1,wc+10+gex(2,n),ns+'.12',None)
                text3 = apat.sub('\\1<img width="10" height="5" src="pythonpowered.gif"/><img width="10" height="5" src="pythonpowered.gif"/>\\1',text0)
                doPara(x3,y,text3,wc+20+gex(3,n),ns+'.13',None)
                doPara(x4,y,text3,wc+20+gex(3,n),ns+'.14',None,
                        hrep='<span face="Courier-BoldOblique"> </span>',
                        crep='<span face="Helvetica-BoldOblique"> </span>',
                        hdw = swcbo(' ') - swhbo(' '),
                        cdw = swhbo(' ') - swcbo(' '),
                        )
            else:
                doPara(x1,y,text0,wc,ns+'.21',None,
                        hrep='<span face="Courier-BoldOblique"> </span>',
                        crep='<span face="Helvetica-BoldOblique"> </span>',
                        hdw = swcbo(' ') - swhbo(' '),
                        cdw = swhbo(' ') - swcbo(' '),
                        )
            y -= h+1
        canv.showPage()
        canv.save()
        if errors:
            raise ValueError('\n'.join(errors))
    
    def test5(self):
        '''extreme test inspired by Moritz Pfeiffer https://bitbucket.org/moritzpfeiffer/'''
        with self.assertRaises(LayoutError):
            text="""
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
            the sense of distinctive feature theory.
            """
            styleSheet = getSampleStyleSheet()
            story = []
            story.append(Paragraph(text, styleSheet['Normal']))
            doc = BaseDocTemplate(
                outputfile('test_platypus_much_too_large.pdf'),
                pagesize=portrait(A4),
                pageTemplates=[PageTemplate(
                    'page_template',
                    [Frame(0, 0, 0, 0, leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0, id='DUMMY_FRAME')],
                    )],
                )
            doc.build(story)

    def test6(self):
        """test of single/multi-frag text and shrinkSpace calculation"""
        pagesize = (200+20, 400)
        canv = Canvas(outputfile('test_platypus_breaking_lelegaifax.pdf'), pagesize=pagesize)
        f = Frame(10, 0, 200, 400,
                  showBoundary=ShowBoundaryValue(dashArray=(1,1)),
                  leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0)
        style = ParagraphStyle(
                                'normal',
                                fontName='Helvetica',
                                fontSize=11.333628,
                                spaceBefore=20,
                                hyphenationLang='en-US',
                                alignment=TA_JUSTIFY,
                                spaceShrinkage=0.05,
                                )
        text1 = """My recent use case was the preparation"""

        text2 = """<span color='red'>My </span> recent use case was the preparation"""
        ix0 = len(canv._code)
        f.addFromList([Paragraph(text1, style),
                   Paragraph(text2, style),
                   ],
                  canv)
        self.assertEqual(canv._code[ix0:],
                ['q', '0 0 0 RG', '.1 w', '[1 1] 0 d', 'n 10 0 200 400 re S', 'Q', 'q', '1 0 0 1 10 388 cm',
                    'q', '0 0 0 rg',
                    'BT 1 0 0 1 0 .666372 Tm /F1 11.33363 Tf 12 TL -0.157537 Tw'
                    ' (My recent use case was the preparation) Tj T* 0 Tw ET',
                    'Q', 'Q', 'q', '1 0 0 1 10 356 cm', 'q',
                    'BT 1 0 0 1 0 .666372 Tm -0.157537 Tw 12 TL /F1 11.33363 Tf 1 0 0 rg'
                    ' (My ) Tj 0 0 0 rg (recent use case was the preparation) Tj T* 0 Tw ET', 'Q', 'Q'],
                'Lele Gaifax bug example did not produce the right code',
                )
        canv.showPage()
        canv.save()

def makeSuite():
    return makeSuiteForClasses(BreakingTestCase)

#noruntests
if __name__ == "__main__": #NORUNTESTS
    if 'debug' in sys.argv:
        _test0(None)
    else:
        unittest.TextTestRunner().run(makeSuite())
        printLocation()
