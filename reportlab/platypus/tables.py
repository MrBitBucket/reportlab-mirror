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
#	$Log: tables.py,v $
#	Revision 1.2  2000/02/15 15:47:09  rgbecker
#	Added license, __version__ and Logi comment
#
__version__=''' $Id: tables.py,v 1.2 2000/02/15 15:47:09 rgbecker Exp $ '''
"""
Tables are created by passing the constructor a tuple of column widths, a tuple of row heights and the data in
row order. Drawing of the table can be controlled by using a TableStyle instance. This allows control of the
color and weight of the lines (if any), and the font, alignment and padding of the text.
"""
import layout
import operator

_stringtype = type('')

class CellStyle(layout.PropertySet):
    defaults = {
        'fontname':'Times-Roman',
        'fontsize':10,
        'leading':12,
        'leftPadding':6,
        'rightPadding':6,
        'topPadding':3,
        'bottomPadding':3,
        'firstLineIndent':0,
        'color':(0,0,0),
        'alignment': 'LEFT',
        'background': (1,1,1),
        }

class TableStyle:
    def __init__(self, cmds=None):
        self._cmds = cmds
        if cmds is None:
            self._cmds = []
    def add(self, *cmd):
        self._cmds.append(cmd)
    def getCommands(self):
        return self._cmds
        
class Table(layout.Drawable):
    def __init__(self, colWidths, rowHeights, data):
        if not colWidths:
            raise ValueError, "Table must have at least 1 column"
        if not rowHeights:
            raise ValueError, "Table must have at least 1 row"
        nrows = self._nrows = len(rowHeights)
        if len(data) != nrows:
            raise ValueError, "Data error - %d rows in data but %d in grid" % (len(data), nrows)
        ncols = self._ncols = len(colWidths)
        for i in range(nrows):
            if len(data[i]) != ncols:
                raise ValueError, "Not enough data points in row %d!" % i
        self._rowHeights = rowHeights
        self._colWidths = colWidths
        self._cellvalues = data
        dflt = CellStyle('<default>')
        self._cellstyles = [None]*nrows
        for i in range(nrows):
            self._cellstyles[i] = [dflt]*ncols
        self._bkgrndcmds = []
        self._linecmds = []
        height = self._height = reduce(operator.add, rowHeights, 0)
        self._rowpositions = [height]    # index 0 is actually topline; we skip when processing cells
        for h in rowHeights:
            height = height - h
            self._rowpositions.append(height)
        assert height == 0
        width = 0
        self._colpositions = [0]        #index -1 is right side boundary; we skip when processing cells
        for w in colWidths:
            width = width + w
            self._colpositions.append(width)
        self._width = width
        self._curweight = self._curcolor = self._curcellstyle = None

    def setStyle(self, tblstyle):
        for cmd in tblstyle.getCommands():
            if cmd[0] == 'BACKGROUND':
                self._bkgrndcmds.append(cmd)
            elif _isLineCommand(cmd):
                self._linecmds.append(cmd)
            else:
                (op, (sc, sr), (ec, er)), values = cmd[:3] , cmd[3:]
                if sc < 0: sc = sc + self._ncols
                if ec < 0: ec = ec + self._ncols
                if sr < 0: sr = sr + self._nrows
                if er < 0: er = er + self._nrows
                for i in range(sr, er+1):
                    for j in range(sc, ec+1):
                        _setCellStyle(self._cellstyles, i, j, op, values)

    def _drawLines(self):
        for op, (sc, sr), (ec, er), weight, color in self._linecmds:
            if sc < 0: sc = sc + self._ncols
            if ec < 0: ec = ec + self._ncols
            if sr < 0: sr = sr + self._nrows
            if er < 0: er = er + self._nrows
            if op == 'GRID':
                self._drawBox( (sc, sr), (ec, er), weight, color)
                self._drawInnerGrid( (sc, sr), (ec, er), weight, color)
            elif op in ('BOX',  'OUTLINE',):
                self._drawBox( (sc, sr), (ec, er), weight, color)
            elif op == 'INNERGRID':
                self._drawInnerGrid( (sc, sr), (ec, er), weight, color)
            elif op == 'LINEBELOW':
                self._drawHLines((sc, sr+1), (ec, er+1), weight, color)
            elif op == 'LINEABOVE':
                self._drawHLines((sc, sr), (ec, er), weight, color)
            elif op == 'LINEBEFORE':
                self._drawVLines((sc, sr), (ec, er), weight, color)
            elif op == 'LINEAFTER':
                self._drawVLines((sc+1, sr), (ec+1, er), weight, color)
            else:
                raise ValueError, "Unknown line style %s" % op
        self._curcolor = None

    def _drawBox(self,  (sc, sr), (ec, er), weight, color):
        self._drawHLines((sc, sr), (ec, sr), weight, color)
        self._drawHLines((sc, er+1), (ec, er+1), weight, color)
        self._drawVLines((sc, sr), (sc, er), weight, color)
        self._drawVLines((ec+1, sr), (ec+1, er), weight, color)
    def _drawInnerGrid(self, (sc, sr), (ec, er), weight, color):
        self._drawHLines((sc, sr+1), (ec, er), weight, color)
        self._drawVLines((sc+1, sr), (ec, er), weight, color)
    def _prepLine(self, weight, color):
        if type(color) is _stringtype:
            color = COLORS.get(color, (0,0,0))
        if color != self._curcolor:
            apply(self.canv.setStrokeColorRGB, color)
            self._curcolor = color
        if weight != self._curweight:
            self.canv.setLineWidth(weight)
            self._curweight = weight
    def _drawHLines(self, (sc, sr), (ec, er), weight, color):
        self._prepLine(weight, color)
        scp = self._colpositions[sc]
        ecp = self._colpositions[ec+1]
        for rowpos in self._rowpositions[sr:er+1]:
            self.canv.line(scp, rowpos, ecp, rowpos)
    def _drawVLines(self, (sc, sr), (ec, er), weight, color):
        self._prepLine(weight, color)
        srp = self._rowpositions[sr]
        erp = self._rowpositions[er+1]
        for colpos in self._colpositions[sc:ec+1]:
            self.canv.line(colpos, srp, colpos, erp)


    def wrap(self, availWidth, availHeight):
        #nice and easy, since they are predetermined size
        self.availWidth = availWidth
        return (self._width, self._height)
                
    def draw(self):
        nudge = 0.5 * (self.availWidth - self._width)
        self.canv.translate(nudge, 0)
        self._drawBkgrnd()
        self._drawLines()
        for row, rowstyle, rowpos, rowheight in map(None, self._cellvalues, self._cellstyles, self._rowpositions[1:], self._rowHeights):
            for cellval, cellstyle, colpos, colwidth in map(None, row, rowstyle, self._colpositions[:-1], self._colWidths):
                self._drawCell(cellval, cellstyle, (colpos, rowpos), (colwidth, rowheight))

    def _drawBkgrnd(self):
        for cmd, (sc, sr), (ec, er), color in self._bkgrndcmds:
            if sc < 0: sc = sc + self._ncols
            if ec < 0: ec = ec + self._ncols
            if sr < 0: sr = sr + self._nrows
            if er < 0: er = er + self._nrows
            if type(color) is _stringtype:
                color = COLORS.get(values[0], (1,1,1))
            x0 = self._colpositions[sc]
            y0 = self._rowpositions[sr]
            x1 = self._colpositions[ec+1]
            y1 = self._rowpositions[er+1]
            apply(self.canv.setFillColorRGB, color)
            self.canv.rect(x0, y0, x1-x0, y1-y0,stroke=0,fill=1)
    def _drawCell(self, cellval, cellstyle, (colpos, rowpos), (colwidth, rowheight)):
        #print "cellstyle is ", repr(cellstyle), id(cellstyle)
        if self._curcellstyle is not cellstyle:
            cur = self._curcellstyle
            if cur is None or cellstyle.color != cur.color:
                #print "setting cell color to %s" % `cellstyle.color`
                apply(self.canv.setFillColorRGB, cellstyle.color)
            if cur is None or cellstyle.leading != cur.leading or cellstyle.fontname != cur.fontname or cellstyle.fontsize != cur.fontsize:
                #print "setting font: %s, %s, %s" % (cellstyle.fontname, cellstyle.fontsize, cellstyle.leading)
                self.canv.setFont(cellstyle.fontname, cellstyle.fontsize, cellstyle.leading)
            self._curcellstyle = cellstyle
        just = cellstyle.alignment
        #print "alignment is ", just
        if just == 'LEFT':
            draw = self.canv.drawString
            x = colpos + cellstyle.leftPadding
        elif just in ('CENTRE', 'CENTER'):
            draw = self.canv.drawCentredString
            x = colpos + colwidth * 0.5
        else:
            draw = self.canv.drawRightString
            x = colpos + colwidth - cellstyle.rightPadding
        y = rowpos + cellstyle.bottomPadding
        if type(cellval) is _stringtype:
            val = cellval
        else:
            val = str(cellval)
        draw(x, y, val)
        
# for text,
#   drawCentredString(self, x, y, text) where x is center
#   drawRightString(self, x, y, text) where x is right
#   drawString(self, x, y, text) where x is left

LINECOMMANDS = (
    'GRID', 'BOX', 'OUTLINE', 'INNERGRID', 'LINEBELOW', 'LINEABOVE', 'LINEBEFORE', 'LINEAFTER', )

COLORS = {
    'BLACK': (0,0,0),
    'RED': (1,0,0),
    'GREEN': (0,1,0),
    'BLUE': (0,0,1),
    'WHITE':(1,1,1),
    }

def _isLineCommand(cmd):
    return cmd[0] in LINECOMMANDS

def _setCellStyle(cellstyles, i, j, op, values):
    new = CellStyle('<%d, %d>' % (i,j), cellstyles[i][j])
    cellstyles[i][j] = new
    if op == 'FONT':
        new.fontname = values[0]
        new.fontsize = values[1]
    elif op == 'TEXTCOLOR':
        if type(values[0]) is _stringtype:
            new.color = COLORS.get(values[0], (0,0,0))
        else:
            new.color = values[0]
    elif op in ('ALIGN', 'ALIGNMENT'):
        new.alignment = values[0]
    elif op == 'LEFTPADDING':
        new.leftPadding = values[0]
    elif op == 'RIGHTPADDING':
        new.rightPadding = values[0]
    elif op == 'TOPPADDING':
        new.topPadding = values[0]
    elif op == 'BOTTOMPADDING':
        new.bottomPadding = values[0]

GRID_STYLE = TableStyle(
    [('GRID', (0,0), (-1,-1), 0.25, 'BLACK'),
     ('ALIGN', (1,1), (-1,-1), 'RIGHT')]
    )
BOX_STYLE = TableStyle(
    [('BOX', (0,0), (-1,-1), 0.50, 'BLACK'),
     ('ALIGN', (1,1), (-1,-1), 'RIGHT')]
    )
LABELED_GRID_STYLE = TableStyle(
    [('INNERGRID', (0,0), (-1,-1), 0.25, 'BLACK'),
     ('BOX', (0,0), (-1,-1), 2, 'BLACK'),
     ('LINEBELOW', (0,0), (-1,0), 2, 'BLACK'),
     ('LINEAFTER', (0,0), (0,-1), 2, 'BLACK'),
     ('ALIGN', (1,1), (-1,-1), 'RIGHT')]
    )
COLORED_GRID_STYLE = TableStyle(
    [('INNERGRID', (0,0), (-1,-1), 0.25, 'BLACK'),
     ('BOX', (0,0), (-1,-1), 2, 'RED'),
     ('LINEBELOW', (0,0), (-1,0), 2, 'BLACK'),
     ('LINEAFTER', (0,0), (0,-1), 2, 'BLACK'),
     ('ALIGN', (1,1), (-1,-1), 'RIGHT')]
    )
LIST_STYLE = TableStyle(
    [('LINEABOVE', (0,0), (-1,0), 2, 'GREEN'),
     ('LINEABOVE', (0,1), (-1,-1), 0.25, 'BLACK'),
     ('LINEBELOW', (0,-1), (-1,-1), 2, 'GREEN'),
     ('ALIGN', (1,1), (-1,-1), 'RIGHT')]
    )

def test():
    rowheights = (24, 16, 16, 16, 16)
    colwidths = (50, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32)
    data = (
        ('', 'Jan', 'Feb', 'Mar','Apr','May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'),
        ('Mugs', 0, 4, 17, 3, 21, 47, 12, 33, 2, -2, 44, 89),
        ('T-Shirts', 0, 42, 9, -3, 16, 4, 72, 89, 3, 19, 32, 119),
        ('Key Ring', 0,0,0,0,0,0,1,0,0,0,2,13),
        ('Hats', 893, 912, '1,212', 643, 789, 159, 888, '1,298', 832, 453, '1,344','2,843')
        )
    doc = layout.SimpleFlowDocument('testtables.pdf', platypus.DEFAULT_PAGE_SIZE, 1)
    styleSheet = layout.getSampleStyleSheet()
    lst = []
    lst.append(layout.Paragraph("Tables", styleSheet['Heading1']))
    lst.append(layout.Paragraph(__doc__, styleSheet['BodyText']))
    lst.append(layout.Paragraph("The Tables (shown in different styles below) were created using the following code:", styleSheet['BodyText']))
    lst.append(layout.Preformatted("""
    colwidths = (50, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32)
    rowheights = (24, 16, 16, 16, 16)
    data = (
        ('', 'Jan', 'Feb', 'Mar','Apr','May', 'Jun',
           'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'),
        ('Mugs', 0, 4, 17, 3, 21, 47, 12, 33, 2, -2, 44, 89),
        ('T-Shirts', 0, 42, 9, -3, 16, 4, 72, 89, 3, 19, 32, 119),
        ('Key Ring', 0,0,0,0,0,0,1,0,0,0,2,13),
        ('Hats', 893, 912, '1,212', 643, 789, 159,
             888, '1,298', 832, 453, '1,344','2,843')
        )   
    t = Table(colwidths, rowheights,  data)
    """, styleSheet['Code'], dedent=4))
    lst.append(layout.Paragraph("""
    You can then give the Table a TableStyle object to control its format. The first TableStyle used was
    created as follows:
    """, styleSheet['BodyText']))
    lst.append(layout.Preformatted("""
GRID_STYLE = TableStyle(
    [('GRID', (0,0), (-1,-1), 0.25, 'BLACK'),
     ('ALIGN', (1,1), (-1,-1), 'RIGHT')]
    )
    """, styleSheet['Code']))
    lst.append(layout.Paragraph("""
    TableStyles are created by passing in a list of commands. There are two types of commands - line commands
    and cell formatting commands. In all cases, the first three elements of a command are the command name,
    the starting cell and the ending cell.
    """, styleSheet['BodyText']))
    lst.append(layout.Paragraph("""
    Line commands always follow this with the weight and color of the desired lines. Colors can be names,
    or they can be specified as a (R,G,B) tuple, where R, G and B are floats and (0,0,0) is black. The line
    command names are: GRID, BOX, OUTLINE, INNERGRID, LINEBELOW, LINEABOVE, LINEBEFORE
    and LINEAFTER. BOX and OUTLINE are equivalent, and GRID is the equivalent of applying both BOX and
    INNERGRID.
    """, styleSheet['BodyText']))
    lst.append(layout.Paragraph("""
    Cell formatting commands are:
    """, styleSheet['BodyText']))
    lst.append(layout.Paragraph("""
    FONT - takes fontname, fontsize and (optional) leading.
    """, styleSheet['Definition']))
    lst.append(layout.Paragraph("""
    TEXTCOLOR - takes a color name or (R,G,B) tuple.
    """, styleSheet['Definition']))
    lst.append(layout.Paragraph("""
    ALIGNMENT (or ALIGN) - takes one of LEFT, RIGHT and CENTRE (or CENTER).
    """, styleSheet['Definition']))
    lst.append(layout.Paragraph("""
    LEFTPADDING - defaults to 6.
    """, styleSheet['Definition']))
    lst.append(layout.Paragraph("""
    RIGHTPADDING - defaults to 6.
    """, styleSheet['Definition']))
    lst.append(layout.Paragraph("""
    BOTTOMPADDING - defaults to 3.
    """, styleSheet['Definition']))
    lst.append(layout.Paragraph("""
    A tablestyle is applied to a table by calling Table.setStyle(tablestyle).
    """, styleSheet['BodyText']))
    t = Table(colwidths, rowheights,  data)
    t.setStyle(GRID_STYLE)
    lst.append(layout.PageBreak())
    lst.append(layout.Paragraph("This is GRID_STYLE\n", styleSheet['BodyText']))
    lst.append(t)
    
    t = Table(colwidths, rowheights,  data)
    t.setStyle(BOX_STYLE)
    lst.append(layout.Paragraph("This is BOX_STYLE\n", styleSheet['BodyText']))
    lst.append(t)
    lst.append(layout.Paragraph("""
    It was created as follows:
    """, styleSheet['BodyText']))
    lst.append(layout.Preformatted("""
BOX_STYLE = TableStyle(
    [('BOX', (0,0), (-1,-1), 0.50, 'BLACK'),
     ('ALIGN', (1,1), (-1,-1), 'RIGHT')]
    )
    """, styleSheet['Code']))
    
    t = Table(colwidths, rowheights,  data)
    t.setStyle(LABELED_GRID_STYLE)
    lst.append(layout.Paragraph("This is LABELED_GRID_STYLE\n", styleSheet['BodyText']))
    lst.append(t)
    lst.append(layout.Paragraph("""
    It was created as follows:
    """, styleSheet['BodyText']))
    lst.append(layout.Preformatted("""
LABELED_GRID_STYLE = TableStyle(
    [('INNERGRID', (0,0), (-1,-1), 0.25, 'BLACK'),
     ('BOX', (0,0), (-1,-1), 2, 'BLACK'),
     ('LINEBELOW', (0,0), (-1,0), 2, 'BLACK'),
     ('LINEAFTER', (0,0), (0,-1), 2, 'BLACK'),
     ('ALIGN', (1,1), (-1,-1), 'RIGHT')]
    )
    """, styleSheet['Code']))
    lst.append(layout.PageBreak())
    
    t = Table(colwidths, rowheights,  data)
    t.setStyle(COLORED_GRID_STYLE)
    lst.append(layout.Paragraph("This is COLORED_GRID_STYLE\n", styleSheet['BodyText']))
    lst.append(t)
    lst.append(layout.Paragraph("""
    It was created as follows:
    """, styleSheet['BodyText']))
    lst.append(layout.Preformatted("""
COLORED_GRID_STYLE = TableStyle(
    [('INNERGRID', (0,0), (-1,-1), 0.25, 'BLACK'),
     ('BOX', (0,0), (-1,-1), 2, 'RED'),
     ('LINEBELOW', (0,0), (-1,0), 2, 'BLACK'),
     ('LINEAFTER', (0,0), (0,-1), 2, 'BLACK'),
     ('ALIGN', (1,1), (-1,-1), 'RIGHT')]
    )
    """, styleSheet['Code']))
    
    t = Table(colwidths, rowheights,  data)
    t.setStyle(LIST_STYLE)
    lst.append(layout.Paragraph("This is LIST_STYLE\n", styleSheet['BodyText']))
    lst.append(t)
    lst.append(layout.Paragraph("""
    It was created as follows:
    """, styleSheet['BodyText']))
    lst.append(layout.Preformatted("""
LIST_STYLE = TableStyle(
    [('LINEABOVE', (0,0), (-1,0), 2, 'GREEN'),
     ('LINEABOVE', (0,1), (-1,-1), 0.25, 'BLACK'),
     ('LINEBELOW', (0,-1), (-1,-1), 2, 'GREEN'),
     ('ALIGN', (1,1), (-1,-1), 'RIGHT')]
    )
    """, styleSheet['Code']))
   
    t = Table(colwidths, rowheights,  data)
    ts = TableStyle(
    [('LINEABOVE', (0,0), (-1,0), 2, 'GREEN'),
     ('LINEABOVE', (0,1), (-1,-1), 0.25, 'BLACK'),
     ('LINEBELOW', (0,-1), (-1,-1), 2, 'GREEN'),
     ('ALIGN', (1,1), (-1,-1), 'RIGHT'),
     ('TEXTCOLOR', (0,1), (0,-1), 'RED'),
     ('BACKGROUND', (0,0), (-1,0), (0,0.7,0.7))]
    )
    t.setStyle(ts)
    lst.append(layout.Paragraph("This is a custom style\n", styleSheet['BodyText']))
    lst.append(t)
    lst.append(layout.Paragraph("""
    It was created as follows:
    """, styleSheet['BodyText']))
    lst.append(layout.Preformatted("""
   ts = TableStyle(
    [('LINEABOVE', (0,0), (-1,0), 2, 'GREEN'),
     ('LINEABOVE', (0,1), (-1,-1), 0.25, 'BLACK'),
     ('LINEBELOW', (0,-1), (-1,-1), 2, 'GREEN'),
     ('ALIGN', (1,1), (-1,-1), 'RIGHT'),
     ('TEXTCOLOR', (0,1), (0,-1), 'RED'),
     ('BACKGROUND', (0,0), (-1,0), (0,0.7,0.7))]
    )
    """, styleSheet['Code']))
    doc.build(lst)

if __name__ == '__main__':
    test()
