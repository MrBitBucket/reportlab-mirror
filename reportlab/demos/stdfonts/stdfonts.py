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
#	$Log: stdfonts.py,v $
#	Revision 1.1  2000/02/15 15:15:57  rgbecker
#	Initial revision
#
__version__=''' $Id: stdfonts.py,v 1.1 2000/02/15 15:15:57 rgbecker Exp $ '''
# standardfonts.py
#
# shows the 14 standard fonts in our encoding

from pdfbase import pdfmetrics
from pdfgen import canvas

def run():

    canv = canvas.Canvas('standardfonts.pdf')
    canv.setPageCompression(0)
    
    for fontname in pdfmetrics.StandardEnglishFonts:
        canv.setFont('Times-Bold', 18)
        canv.drawString(80, 744, fontname)
        
        #for dingbats, we need to use another font for the numbers.
        #do two parallel text objects.
        if fontname == 'ZapfDingbats':
            labelfont = 'Helvetica'
        else:
            labelfont = fontname

        for byt in range(32, 256):
            col, row = divmod(byt - 32, 32)
            x = 72 + (66*col)
            y = 720 - (18*row)
            canv.setFont(labelfont, 14)
            canv.drawString(x, y, '%d =' % byt)
            canv.setFont(fontname, 14)
            canv.drawString(x + 44, y , chr(byt))

        canv.showPage()            
            

    canv.save()

if __name__ == '__main__':
    run()
