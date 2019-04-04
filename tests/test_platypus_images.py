from reportlab.lib.testutils import setOutDir,makeSuiteForClasses, outputfile, printLocation
setOutDir(__name__)
import unittest, sys, os
from reportlab.lib.testutils import testsFolder

def getFurl(fn):
    furl = fn.replace(os.sep,'/')
    if sys.platform=='win32' and furl[1]==':': furl = furl[0]+'|'+furl[2:]
    if furl[0]!='/': furl = '/'+furl
    return 'file://'+furl

def run():
    from reportlab.platypus import  BaseDocTemplate, PageTemplate, Image, Frame, PageTemplate, \
                                    ShowBoundaryValue, SimpleDocTemplate, FrameBG, Paragraph, \
                                    FrameBreak
    from reportlab.lib.colors import toColor
    from reportlab.lib.utils import haveImages, _RL_DIR, rl_isfile, open_for_read, fileName2FSEnc, asNative
    from reportlab.lib.styles import getSampleStyleSheet
    styleSheet = getSampleStyleSheet()
    if haveImages:
        _GIF = os.path.join(testsFolder,'pythonpowered.gif')
        if not rl_isfile(_GIF): _GIF = None
        _GAPNG = os.path.join(testsFolder,'gray-alpha.png')
        if not rl_isfile(_GAPNG): _GAPNG = None
    else:
        _GIF = None
    if _GIF: _GIFFSEnc=fileName2FSEnc(_GIF)
    if _GAPNG: _GAPNGFSEnc=fileName2FSEnc(_GAPNG)

    _JPG = os.path.join(testsFolder,'..','docs','images','lj8100.jpg')
    if not rl_isfile(_JPG): _JPG = None

    
    doc = SimpleDocTemplate(outputfile('test_platypus_images.pdf'))
    story=[FrameBG(color=toColor('lightblue'),start='frame-permanent'),
            ]
    if _GIF:
        story.append(Paragraph("Here is an Image flowable obtained from a string GIF filename.",styleSheet['Italic']))
        story.append(Image(_GIF))
        story.append(Paragraph( "Here is an Image flowable obtained from a utf8 GIF filename.", styleSheet['Italic']))
        #story.append(Image(fileName2FSEnc(_GIF)))
        story.append(Paragraph("Here is an Image flowable obtained from a string GIF file url.",styleSheet['Italic']))
        story.append(Image(getFurl(_GIF)))
        story.append(Paragraph("Here is an Image flowable obtained from an open GIF file.",styleSheet['Italic']))
        story.append(Image(open_for_read(_GIF,'b')))
        story.append(FrameBreak())
        try:
            img = Image('http://www.reportlab.com/rsrc/encryption.gif')
            story.append(Paragraph("Here is an Image flowable obtained from a string GIF http url.",styleSheet['Italic']))
            story.append(img)
        except:
            story.append(Paragraph("The image could not be obtained from a string http GIF url.",styleSheet['Italic']))
        story.append(FrameBreak())

    if _GAPNG:
        story.append(Paragraph("Here is an Image flowable obtained from a string PNGA filename.",styleSheet['Italic']))
        story.append(Image('rltw-icon-tr.png'))
        story.append(Paragraph("Here is an Image flowable obtained from a string PNG filename.",styleSheet['Italic']))
        story.append(Image(_GAPNG))
        story.append(Paragraph( "Here is an Image flowable obtained from a utf8 PNG filename.", styleSheet['Italic']))
        #story.append(Image(fileName2FSEnc(_GAPNG)))
        story.append(Paragraph("Here is an Image flowable obtained from a string file PNG url.",styleSheet['Italic']))
        story.append(Image(getFurl(_GAPNG)))
        story.append(Paragraph("Here is an Image flowable obtained from an open PNG file.",styleSheet['Italic']))
        story.append(Image(open_for_read(_GAPNG,'b')))
        story.append(FrameBreak())

    if _JPG:
        img = Image(_JPG)
        story.append(Paragraph("Here is an JPEG Image flowable obtained from a JPEG filename.",styleSheet['Italic']))
        story.append(img)
        story.append(Paragraph("Here is an JPEG Image flowable obtained from an open JPEG file.",styleSheet['Italic']))
        img = Image(open_for_read(_JPG,'b'))
        story.append(img)
        story.append(FrameBreak())
    doc.build(story)

class PlatypusImagesTestCase(unittest.TestCase):
    def test0(self):
        "Make a platypus document"
        run()

def makeSuite():
    return makeSuiteForClasses(PlatypusImagesTestCase)

#noruntests
if __name__ == "__main__":
    if '-debug' in sys.argv:
        run()
    else:
        unittest.TextTestRunner().run(makeSuite())
        printLocation()
