#copyright ReportLab Inc. 2000
#see license.txt for license details
#history http://cvs.sourceforge.net/cgi-bin/cvsweb.cgi/reportlab/pdfgen/test/testPageMode.py?cvsroot=reportlab
#$Header: /tmp/reportlab/reportlab/pdfgen/test/Attic/testPageMode.py,v 1.2 2000/10/25 08:57:45 rgbecker Exp $
# full screen test
from reportlab.pdfgen.canvas import Canvas

def test():

    filename = 'testPageMode_FullScreen.pdf'
    c = Canvas(filename)
    c.showFullScreen0()
    c.setFont('Helvetica', 20)
    c.drawString(100, 700, 'This should open in full screen mode')
    c.save()
    print 'saved',filename

    filename = 'testPageMode_Outline.pdf'
    c = Canvas(filename)
    c.bookmarkPage('page1')
    c.addOutlineEntry('Token Outline Entry','page1')
    c.showOutline()
    c.setFont('Helvetica', 20)
    c.drawString(100, 700, 'This should open with outline visible')
    c.save()
    print 'saved',filename

    filename = 'testPageMode_UseNone.pdf'
    c = Canvas(filename)
    c.setFont('Helvetica', 20)
    c.drawString(100, 700, "This should open in the user's default mode")
    c.save()
    print 'saved',filename

if __name__=='__main__':
    test()
