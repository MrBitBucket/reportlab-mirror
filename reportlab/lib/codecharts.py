#copyright ReportLab Inc. 2001
#see license.txt for license details
#history http://cvs.sourceforge.net/cgi-bin/cvsweb.cgi/reportlab/lib/codecharts?cvsroot=reportlab
#$Header $
__version__=''' $Id '''
__doc__="""Routines to print code page (character set) drawings.

To be sure we can accurately represent characters in various encodings
and fonts, we need some routines to display all those characters.
These are defined herein.  The idea is to include flowable, drawable
and graphic objects for single and multi-byte fonts. """
import string

from reportlab.pdfgen.canvas import Canvas
from reportlab.platypus import Flowable
from reportlab.pdfbase import pdfmetrics, cidfonts


class CodeChartBase(Flowable):
    """Basic bits of drawing furniture used by
    single and multi-byte versions: ability to put letters
    into boxes."""

    def calcLayout(self):
        "Work out x and y positions for drawing"


        rows = self.codePoints * 1.0 / self.charsPerRow
        if rows == int(rows):
            self.rows = int(rows)
        else:
            self.rows = int(rows) + 1
        # size allows for a gray column of labels
        self.width = self.boxSize * (1+self.charsPerRow)
        self.height = self.boxSize * (1+self.rows)

        #handy lists
        self.ylist = []
        for row in range(self.rows + 2):
            self.ylist.append(row * self.boxSize)
        self.xlist = []
        for col in range(self.charsPerRow + 2):
            self.xlist.append(col * self.boxSize)
        
    def formatByte(self, byt):
        if self.hex:
            return '%02X' % byt
        else:
            return '%d' % byt

    def drawChars(self, charList):
        """Fills boxes in order.  None means skip a box.
        Empty boxes at end get filled with gray"""
        extraNeeded = (self.rows * self.charsPerRow - len(charList))
        charList = charList + [None] * extraNeeded
        row = 0
        col = 0
        self.canv.setFont(self.fontName, self.boxSize * 0.75)
        for ch in charList:  # may be 2 bytes or 1
            if ch is None:
                self.canv.setFillGray(0.9)
                self.canv.rect((1+col) * self.boxSize, (self.rows - row - 1) * self.boxSize,
                    self.boxSize, self.boxSize, stroke=0, fill=1)
                self.canv.setFillGray(0.0)
            else:
                self.canv.drawCentredString(
                            (col+1.5) * self.boxSize,
                            (self.rows - row - 0.875) * self.boxSize,
                            ch
                            )
            col = col + 1
            if col == self.charsPerRow:
                row = row + 1
                col = 0

    def drawLabels(self):
        """Writes little labels in the top row and first column"""
        self.canv.setFillGray(0.8)
        self.canv.rect(0, self.ylist[-2], self.width, self.boxSize, fill=1, stroke=0)
        self.canv.rect(0, 0, self.boxSize, self.ylist[-2], fill=1, stroke=0)
        self.canv.setFillGray(0.0)
        
        #label each row and column
        self.canv.setFont('Helvetica-Oblique',0.375 * self.boxSize)
        byt = 0
        for row in range(self.rows):
            startByte = row * self.charsPerRow
            self.canv.drawCentredString(0.5 * self.boxSize,
                                        (self.rows - row - 0.75) * self.boxSize,
                                        self.formatByte(startByte)
                                        )
        for col in range(self.charsPerRow):
            self.canv.drawCentredString((col + 1.5) * self.boxSize,
                                        (self.rows + 0.25) * self.boxSize,
                                        self.formatByte(col)
                                        )


class SingleByteEncodingChart(CodeChartBase):
    def __init__(self, faceName='Helvetica', encodingName='WinAnsiEncoding',
                 charsPerRow=16, boxSize=14, hex=1):
        self.codePoints = 256
        self.faceName = faceName
        self.encodingName = encodingName
        self.fontName = self.faceName + '-' + self.encodingName
        self.charsPerRow = charsPerRow
        self.boxSize = boxSize
        self.hex = hex

        pdfmetrics.registerFont(pdfmetrics.Font(self.fontName,
                                                self.faceName,
                                                self.encodingName)
                                )

        self.calcLayout()
        
        
    def draw(self):
        self.drawLabels()
        charList = [None] * 32 + map(chr, range(32, 256))
        self.drawChars(charList)
        self.canv.grid(self.xlist, self.ylist)
                    

class KutenRowCodeChart(CodeChartBase):
    """Formats one 'row' of the 94x94 space used in many Asian encodings.aliases

    These deliberately resemble the code charts in Ken Lunde's "Understanding
    CJKV Information Processing", to enable manual checking.  Due to the large
    numbers of characters, we don't try to make one graphic with 10,000 characters,
    but rather output a sequence of these."""
    #would be cleaner if both shared one base class whose job
    #was to draw the boxes, but never mind...
    def __init__(self, row, faceName, encodingName):
        self.row = row
        self.codePoints = 94
        self.boxSize = 18
        self.charsPerRow = 20
        self.rows = 5
        self.hex = 0
        self.faceName = faceName
        self.encodingName = encodingName

        try:
            # the dependent files might not be available
            font = cidfonts.CIDFont(self.faceName, self.encodingName)
            pdfmetrics.registerFont(font)
        except:
            # fall back to English and at least shwo we can draw the boxes
            self.faceName = 'Helvetica'
            self.encodingName = 'WinAnsiEncoding'
        self.fontName = self.faceName + '-' + self.encodingName
        self.calcLayout()        

    def makeRow(self, row):
        """Works out the character values for this kuten row"""
        cells = []
        if string.find(self.encodingName, 'EUC') > -1:
            # it is an EUC family encoding.
            for col in range(1, 95):
                ch = chr(row + 160) + chr(col+160)
                cells.append(ch)
        else:
            cells.append(None)
        return cells
                
    def draw(self):
        self.drawLabels()

        # work out which characters we need for the row
        assert string.find(self.encodingName, 'EUC') > -1, 'Only handles EUC encoding today!'
        
        # pad out by 1 to match Ken Lunde's tables
        charList = [None] + self.makeRow(self.row) 
        self.drawChars(charList)
        self.canv.grid(self.xlist, self.ylist)
        
def test():
    c = Canvas('codecharts.pdf')
    c.setFont('Helvetica-Bold', 24)
    c.drawString(72, 750, 'Testing code page charts')
    cc1 = SingleByteEncodingChart()
    cc1.drawOn(c, 72, 500)

    cc2 = SingleByteEncodingChart(charsPerRow=32)
    cc2.drawOn(c, 72, 300)

    cc3 = SingleByteEncodingChart(charsPerRow=25, hex=0)
    cc3.drawOn(c, 72, 100)

    c.showPage()

    c.setFont('Helvetica-Bold', 24)
    c.drawString(72, 750, 'Multi-byte code chart examples')
    KutenRowCodeChart(1, 'HeiseiMin-W3','EUC-H').drawOn(c, 72, 600)
    
    KutenRowCodeChart(16, 'HeiseiMin-W3','EUC-H').drawOn(c, 72, 450)

    KutenRowCodeChart(84, 'HeiseiMin-W3','EUC-H').drawOn(c, 72, 300)

    c.save()
    print 'saved codecharts.pdf'

if __name__=='__main__':
    test()

    
        