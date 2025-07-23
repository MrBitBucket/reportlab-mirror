#Copyright ReportLab Europe Ltd. 2000-2017
#see license.txt for license details
__version__='3.3.0'
__doc__=''

#REPORTLAB_TEST_SCRIPT
import sys, copy, os
from reportlab.platypus import *
_NEW_PARA=os.environ.get('NEW_PARA','0')[0] in ('y','Y','1')
_REDCAP=int(os.environ.get('REDCAP','0'))
_CALLBACK=os.environ.get('CALLBACK','0')[0] in ('y','Y','1')
if _NEW_PARA:
    def Paragraph(s,style):
        from rlextra.radxml.para import Paragraph as PPPP
        return PPPP(s,style)

from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.enums import TA_LEFT, TA_RIGHT, TA_CENTER, TA_JUSTIFY

import reportlab.rl_config
reportlab.rl_config.invariant = 1

styles = getSampleStyleSheet()

Title = "The Odyssey"
Author = "Homer"

def myTitlePage(canvas, doc):
    canvas.saveState()
    canvas.restoreState()

def myLaterPages(canvas, doc):
    canvas.saveState()
    canvas.setFont('Times-Roman',9)
    canvas.drawString(inch, 0.75 * inch, "Page %d" % doc.page)
    canvas.restoreState()

def go():
    def myCanvasMaker(fn,**kw):
        from reportlab.pdfgen.canvas import Canvas
        canv = Canvas(fn,**kw)
        # attach our callback to the canvas
        canv.myOnDrawCB = myOnDrawCB
        return canv

    doc = BaseDocTemplate('dodyssey.pdf',showBoundary=0)

    #normal frame as for SimpleFlowDocument
    frameT = Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height, id='normal')

    #Two Columns
    frame1 = Frame(doc.leftMargin, doc.bottomMargin, doc.width/2-6, doc.height, id='col1')
    frame2 = Frame(doc.leftMargin+doc.width/2+6, doc.bottomMargin, doc.width/2-6,
                        doc.height, id='col2')
    doc.addPageTemplates([PageTemplate(id='First',frames=frameT, onPage=myTitlePage),
                        PageTemplate(id='OneCol',frames=frameT, onPage=myLaterPages),
                        PageTemplate(id='TwoCol',frames=[frame1,frame2], onPage=myLaterPages),
                        ])
    doc.build(Elements,canvasmaker=myCanvasMaker)

Elements = []

ChapterStyle = copy.deepcopy(styles["Heading1"])
ChapterStyle.alignment = TA_CENTER
ChapterStyle.fontsize = 14
InitialStyle = copy.deepcopy(ChapterStyle)
InitialStyle.fontsize = 16
InitialStyle.leading = 20
PreStyle = styles["Code"]

def newPage():
    Elements.append(PageBreak())

chNum = 0
def myOnDrawCB(canv,kind,label):
    print('myOnDrawCB(%s)'%kind, 'Page number=', canv.getPageNumber(), 'label value=', label)

def chapter(txt, style=ChapterStyle):
    global chNum
    Elements.append(NextPageTemplate('OneCol'))
    newPage()
    chNum += 1
    if _NEW_PARA or not _CALLBACK:
        Elements.append(Paragraph(txt, style))
    else:
        Elements.append(Paragraph(('foo<onDraw name="myOnDrawCB" label="chap %d"/> '%chNum)+txt, style))
    Elements.append(Spacer(0.2*inch, 0.3*inch))
    if useTwoCol:
        Elements.append(NextPageTemplate('TwoCol'))

def fTitle(txt,style=InitialStyle):
    Elements.append(Paragraph(txt, style))

ParaStyle = copy.deepcopy(styles["Normal"])
ParaStyle.spaceBefore = 0.1*inch
if 'right' in sys.argv:
    ParaStyle.alignment = TA_RIGHT
elif 'left' in sys.argv:
    ParaStyle.alignment = TA_LEFT
elif 'justify' in sys.argv:
    ParaStyle.alignment = TA_JUSTIFY
elif 'center' in sys.argv or 'centre' in sys.argv:
    ParaStyle.alignment = TA_CENTER
else:
    ParaStyle.alignment = TA_JUSTIFY

useTwoCol = 'notwocol' not in sys.argv
def spacer(inches):
    Elements.append(Spacer(0.1*inch, inches*inch))

def p(txt, style=ParaStyle):
    if _REDCAP:
        fs, fe = '<font color="red" size="+2">', '</font>'
        n = len(txt)
        for i in range(n):
            if 'a'<=txt[i]<='z' or 'A'<=txt[i]<='Z':
                txt = (txt[:i]+(fs+txt[i]+fe))+txt[i+1:]
                break
        if _REDCAP>=2 and n>20:
            j = i+len(fs)+len(fe)+1+int((n-1)/2)
            while not ('a'<=txt[j]<='z' or 'A'<=txt[j]<='Z'): j += 1
            txt = (txt[:j]+('<b><i><font size="+2" color="blue">'+txt[j]+'</font></i></b>'))+txt[j+1:]

        if _REDCAP==3 and n>20:
            n = len(txt)
            fs = '<font color="green" size="+1">'
            for i in range(n-1,-1,-1):
                if 'a'<=txt[i]<='z' or 'A'<=txt[i]<='Z':
                    txt = txt[:i]+((fs+txt[i]+fe)+txt[i+1:])
                    break

    Elements.append(Paragraph(txt, style))

firstPre = 1
def pre(txt, style=PreStyle):
    global firstPre
    if firstPre:
        Elements.append(NextPageTemplate('OneCol'))
        newPage()
        firstPre = 0

    spacer(0.1)
    p = Preformatted(txt, style)
    Elements.append(p)

def parseOdyssey(fn):
    from time import time
    E = []
    t0=time()
    text = open(fn,'r').read()
    i0 = text.index('Book I')
    endMarker = 'covenant of peace between the two contending parties.'
    i1 = text.index(endMarker)+len(endMarker)
    PREAMBLE=list(map(str.strip,text[0:i0].split('\n')))
    L=list(map(str.strip,text[i0:i1].split('\n')))
    POSTAMBLE=list(map(str.strip,text[i1:].split('\n')))

    def ambleText(L):
        while L and not L[0]: L.pop(0)
        while L:
            T=[]
            while L and L[0]:
                T.append(L.pop(0))
            yield T
            while L and not L[0]: L.pop(0)

    def mainText(L):
        while L:
            B = L.pop(0)
            while not L[0]: L.pop(0)
            T=[]
            while L and L[0]:
                T.append(L.pop(0))
            while not L[0]: L.pop(0)
            P = []
            while L and not (L[0].startswith('Book ') and len(L[0].split())==2):
                E=[]
                while L and L[0]:
                    E.append(L.pop(0))
                P.append(E)
                if L:
                    while not L[0]: L.pop(0)
            yield B,T,P

    t1 = time()
    print("open(%s,'r').read() took %.4f seconds" %(fn,t1-t0))

    E.append([spacer,2])
    E.append([fTitle,'<font color="red">%s</font>' % Title, InitialStyle])
    E.append([fTitle,'<font size="-4">by</font> <font color="green">%s</font>' % Author, InitialStyle])

    for T in ambleText(PREAMBLE):
        E.append([p,'\n'.join(T)])

    for (B,T,P) in mainText(L):
        E.append([chapter,B])
        E.append([p,'<font size="+1" color="Blue"><b>%s</b></font>' % '\n'.join(T),ParaStyle])
        for x in P:
            E.append([p,' '.join(x)])
    firstPre = 1
    for T in ambleText(POSTAMBLE):
        E.append([p,'\n'.join(T)])

    t3 = time()
    print("Parsing into memory took %.4f seconds" %(t3-t1))
    del L
    t4 = time()
    print("Deleting list of lines took %.4f seconds" %(t4-t3))
    for i in range(len(E)):
        E[i][0](*E[i][1:])
    t5 = time()
    print("Moving into platypus took %.4f seconds" %(t5-t4))
    del E
    t6 = time()
    print("Deleting list of actions took %.4f seconds" %(t6-t5))
    go()
    t7 = time()
    print("saving to PDF took %.4f seconds" %(t7-t6))
    print("Total run took %.4f seconds"%(t7-t0))

    import hashlib
    print('file digest: %s' % hashlib.md5(open('dodyssey.pdf','rb').read(),usedforsecurity=False).hexdigest())

def run():
    for fn in ('odyssey.full.txt','odyssey.txt'):
        if os.path.isfile(fn):
            parseOdyssey(fn)
            break

def doProf(profname,func,*args,**kwd):
        import hotshot, hotshot.stats
        prof = hotshot.Profile(profname)
        prof.runcall(func)
        prof.close()
        stats = hotshot.stats.load(profname)
        stats.strip_dirs()
        stats.sort_stats('time', 'calls')
        stats.print_stats(20)

if __name__=='__main__':
    if '--prof' in sys.argv:
        doProf('dodyssey.prof',run)
    else:
        run()
