###############################################################################
#
#	ReportLab Public License Version 1.0
#
#   Except for the change of names the spirit and intention of this
#   license is the same as that of Python
#
#	(C) Copyright ReportLab Inc. 1998-2000.
#
#
# All Rights Reserved
#
# Permission to use, copy, modify, and distribute this software and its
# documentation for any purpose and without fee is hereby granted, provided
# that the above copyright notice appear in all copies and that both that
# copyright notice and this permission notice appear in supporting
# documentation, and that the name of Robinson Analytics not be used
# in advertising or publicity pertaining to distribution of the software
# without specific, written prior permission. 
# 
#
# Disclaimer
#
# ReportLab Inc. DISCLAIMS ALL WARRANTIES WITH REGARD TO THIS
# SOFTWARE, INCLUDING ALL IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS,
# IN NO EVENT SHALL ReportLab BE LIABLE FOR ANY SPECIAL, INDIRECT
# OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES WHATSOEVER RESULTING FROM LOSS
# OF USE, DATA OR PROFITS, WHETHER IN AN ACTION OF CONTRACT, NEGLIGENCE OR
# OTHER TORTIOUS ACTION, ARISING OUT OF OR IN CONNECTION WITH THE USE OR
# PERFORMANCE OF THIS SOFTWARE. 
#
###############################################################################
#	$Log: odyssey.py,v $
#	Revision 1.1  2000/02/15 15:09:29  rgbecker
#	Initial revision
#
__version__=''' $Id: odyssey.py,v 1.1 2000/02/15 15:09:29 rgbecker Exp $ '''
#odyssey.py
#
#Demo/benchmark of PDFgen rendering Homer's Odyssey.



#results on my humble P266 with 64MB:
# Without page compression:
# 239 pages in 3.76 seconds = 77 pages per second

# With textOut rather than textLine, i.e. computing width
# of every word as we would for wrapping:
# 239 pages in 10.83 seconds = 22 pages per second

# With page compression and textLine():
# 239 pages in 39.39 seconds = 6 pages per second

from pdfgen import canvas
import time


#from pagesizes import A4  #from PIDDLE distribution
A4 = (595.275590551, 841.88976378)
inch = INCH = 72
cm = CM = inch / 2.54

#precalculate some basics
top_margin = A4[1] - inch
bottom_margin = inch
left_margin = inch
right_margin = A4[0] - inch
frame_width = right_margin - left_margin


def drawPageFrame(canv):
    canv.line(left_margin, top_margin, right_margin, top_margin)
    canv.setFont('Times-Italic',12)
    canv.drawString(left_margin, top_margin + 2, "Homer's Odyssey")
    canv.line(left_margin, top_margin, right_margin, top_margin)


    canv.line(left_margin, bottom_margin, right_margin, bottom_margin)
    canv.drawCentredString(0.5*A4[0], 0.5 * inch,
               "Page %d" % canv.getPageNumber())

    

def run():
    started = time.time()
    canv = canvas.Canvas('odyssey.pdf')
    canv.setPageCompression(0)
    drawPageFrame(canv)

    #do some title page stuff
    canv.setFont("Times-Bold", 36)
    canv.drawCentredString(0.5 * A4[0], 7 * inch, "Homer's Odyssey")

    canv.setFont("Times-Bold", 18)
    canv.drawCentredString(0.5 * A4[0], 5 * inch, "Translated by Samuel Burton")

    canv.setFont("Times-Bold", 12)
    tx = canv.beginText(left_margin, 3 * inch)
    tx.textLine("This is a demo-cum-benchmark for PDFgen.  It renders the complete text of Homer's Odyssey")
    tx.textLine("from a text file.  On my humble P266, it does 77 pages per secondwhile creating a 238 page")
    tx.textLine("document.  If it is asked to computer text metrics, measuring the width of each word as ")
    tx.textLine("one would for paragraph wrapping, it still manages 22 pages per second.")
    tx.textLine("")
    tx.textLine("Andy Robinson, Robinson Analytics Ltd.")
    canv.drawText(tx)
    
    canv.showPage()
    #on with the text...
    drawPageFrame(canv)
    
    canv.setFont('Times-Roman', 12)
    tx = canv.beginText(left_margin, top_margin - 0.5*inch)
    
    data = open('odyssey.txt','r').readlines()
    for line in data:
        #this just does it the fast way...
        tx.textLine(line)
        #this forces it to do text metrics, which would be the slow
        #part if we were wrappng paragraphs.
        #canv.textOut(line)
        #canv.textLine('')

        #page breaking        
        y = tx.getY()   #get y coordinate
        if y < bottom_margin + 0.5*inch:
            canv.drawText(tx)
            canv.showPage()
            drawPageFrame(canv)
            canv.setFont('Times-Roman', 12)
            tx = canv.beginText(left_margin, top_margin - 0.5*inch)

            #page
            pg = canv.getPageNumber()
            if pg % 10 == 0:
                print 'formatted page %d' % canv.getPageNumber()

    print 'about to write to disk...'
    
    canv.save()
    
    finished = time.time()
    elapsed = finished - started
    pages = canv.getPageNumber()
    speed =  pages / elapsed
    print '%d pages in %0.2f seconds = %0.2f pages per second' % (
                pages, elapsed, speed)
    
    



if __name__=='__main__':
    run()
