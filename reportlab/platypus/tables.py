#copyright ReportLab Inc. 2000
#see license.txt for license details
#history http://cvs.sourceforge.net/cgi-bin/cvsweb.cgi/reportlab/platypus/tables.py?cvsroot=reportlab
#$Header: /tmp/reportlab/reportlab/platypus/tables.py,v 1.74 2004/03/14 09:47:14 rgbecker Exp $
__version__=''' $Id: tables.py,v 1.74 2004/03/14 09:47:14 rgbecker Exp $ '''

__doc__="""
Tables are created by passing the constructor a tuple of column widths, a tuple of row heights and the data in
row order. Drawing of the table can be controlled by using a TableStyle instance. This allows control of the
color and weight of the lines (if any), and the font, alignment and padding of the text.

None values in the sequence of row heights or column widths, mean that the corresponding rows
or columns should be automatically sized.

All the cell values should be convertible to strings; embedded newline '\\n' characters
cause the value to wrap (ie are like a traditional linefeed).

See the test output from running this module as a script for a discussion of the method for constructing
tables and table styles.
"""

from reportlab.platypus.flowables import Flowable, Image, Macro, PageBreak, Preformatted, Spacer, XBox, \
                         CondPageBreak, KeepTogether, TraceInfo, FailOnWrap, FailOnDraw
from reportlab.platypus.paragraph import Paragraph, cleanBlockQuotedText, ParaLines
from reportlab.platypus.paraparser import ParaFrag
from reportlab.platypus.frames import Frame
from reportlab.platypus.doctemplate import BaseDocTemplate, NextPageTemplate, PageTemplate, ActionFlowable, \
                         SimpleDocTemplate, FrameBreak, PageBegin
from reportlab.platypus.xpreformatted import XPreformatted
from reportlab import rl_config
from reportlab.lib.styles import PropertySet, getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.utils import fp_str
from reportlab.pdfbase import pdfmetrics

import operator, string

from types import TupleType, ListType, StringType

class CellStyle(PropertySet):
    defaults = {
        'fontname':'Times-Roman',
        'fontsize':10,
        'leading':12,
        'leftPadding':6,
        'rightPadding':6,
        'topPadding':3,
        'bottomPadding':3,
        'firstLineIndent':0,
        'color':colors.black,
        'alignment': 'LEFT',
        'background': (1,1,1),
        'valign': 'BOTTOM',
        }

LINECAPS={'butt':0,'round':1,'projecting':2,'squared':2}
LINEJOINS={'miter':0,'round':1,'bevel':2}

# experimental replacement
class CellStyle1(PropertySet):
    fontname = "Times-Roman"
    fontsize = 10
    leading = 12
    leftPadding = 6
    rightPadding = 6
    topPadding = 3
    bottomPadding = 3
    firstLineIndent = 0
    color = colors.black
    alignment = 'LEFT'
    background = (1,1,1)
    valign = "BOTTOM"
    def __init__(self, name, parent=None):
        self.name = name
        if parent is not None:
            parent.copy(self)
    def copy(self, result=None):
        if result is None:
            result = CellStyle1()
        for name in dir(self):
            setattr(result, name, gettattr(self, name))
        return result

CellStyle = CellStyle1

class TableStyle:
    def __init__(self, cmds=None, parent=None, **kw):
        #handle inheritance from parent first.
        commands = []
        if parent:
            # copy the parents list at construction time
            commands = commands + parent.getCommands()
            self._opts = parent._opts
        if cmds:
            commands = commands + list(cmds)
        self._cmds = commands
        self._opts={}
        self._opts.update(kw)

    def add(self, *cmd):
        self._cmds.append(cmd)
    def __repr__(self):
        L = map(repr, self._cmds)
        import string
        L = string.join(L, "  \n")
        return "TableStyle(\n%s\n) # end TableStyle" % L
    def getCommands(self):
        return self._cmds

TableStyleType = type(TableStyle())
_SeqTypes = (TupleType, ListType)

def _rowLen(x):
    return type(x) not in _SeqTypes and 1 or len(x)


class Table(Flowable):
    def __init__(self, data, colWidths=None, rowHeights=None, style=None,
                repeatRows=0, repeatCols=0, splitByRow=1, emptyTableAction=None):
        #print "colWidths", colWidths
        self.hAlign = 'CENTER'
        self.vAlign = 'MIDDLE'
        if type(data) not in _SeqTypes:
            raise ValueError, "%s invalid data type" % self.identity()
        self._nrows = nrows = len(data)
        if nrows: self._ncols = ncols = max(map(_rowLen,data))
        elif colWidths: ncols = len(colWidths)
        else: ncols = 0
        if not emptyTableAction: emptyTableAction = rl_config.emptyTableAction
        if not (nrows and ncols):
            if emptyTableAction=='error':
                raise ValueError, "%s must have at least a row and column" % self.identity()
            elif emptyTableAction=='indicate':
                self.__class__ = Preformatted
                global _emptyTableStyle
                if '_emptyTableStyle' not in globals().keys():
                    _emptyTableStyle = ParagraphStyle('_emptyTableStyle')
                    _emptyTableStyle.textColor = colors.red
                    _emptyTableStyle.backColor = colors.yellow
                Preformatted.__init__(self,'%s(%d,%d)' % (self.__class__.__name__,nrows,ncols), _emptyTableStyle)
            elif emptyTableAction=='ignore':
                self.__class__ = Spacer
                Spacer.__init__(self,0,0)
            else:
                raise ValueError, '%s bad emptyTableAction: "%s"' % (self.identity(),emptyTableAction)
            return

        if colWidths is None: colWidths = ncols*[None]
        elif len(colWidths) != ncols:
            raise ValueError, "%s data error - %d columns in data but %d in grid" % (self.identity(),ncols, len(colWidths))
        if rowHeights is None: rowHeights = nrows*[None]
        elif len(rowHeights) != nrows:
            raise ValueError, "%s data error - %d rows in data but %d in grid" % (self.identity(),nrows, len(rowHeights))
        for i in range(nrows):
            if len(data[i]) != ncols:
                raise ValueError, "%s not enough data points in row %d!" % (self.identity(),i)
        self._cellvalues = data
        self._rowHeights = self._argH = rowHeights
        self._colWidths = self._argW = colWidths
        cellrows = []
        for i in range(nrows):
            cellcols = []
            for j in range(ncols):
                cellcols.append(CellStyle(`(i,j)`))
            cellrows.append(cellcols)
        self._cellStyles = cellrows

        self._bkgrndcmds = []
        self._linecmds = []
        self._spanCmds = []
        self.repeatRows = repeatRows
        self.repeatCols = repeatCols
        self.splitByRow = splitByRow

        if style:
            self.setStyle(style)
    def __repr__(self):
        "incomplete, but better than nothing"
        r = self._rowHeights
        c = self._colWidths
        cv = self._cellvalues
        import pprint, string
        cv = pprint.pformat(cv)
        cv = string.replace(cv, "\n", "\n  ")
        return "%s(\n rowHeights=%s,\n colWidths=%s,\n%s\n) # end table" % (self.__class__.__name__,r,c,cv)

    def identity(self, maxLen=30):
        '''Identify our selves as well as possible'''
        vx = None
        nr = getattr(self,'_nrows','unknown')
        nc = getattr(self,'_ncols','unknown')
        cv = self._cellvalues
        if cv and 'unknown' not in (nr,nc):
            b = 0
            for i in xrange(nr):
                for j in xrange(nc):
                    v = cv[i][j]
                    t = type(v)
                    if t in _SeqTypes or isinstance(v,Flowable):
                        if not t in _SeqTypes: v = (v,)
                        r = ''
                        for vij in v:
                            r = vij.identity(maxLen)
                            if r and r[-4:]!='>...':
                                break
                        if r and r[-4:]!='>...':
                            ix, jx, vx, b = i, j, r, 1
                    else:
                        v = v is None and '' or str(v)
                        ix, jx, vx = i, j, v
                        b = (vx and t is StringType) and 1 or 0
                        if maxLen: vx = vx[:maxLen]
                    if b: break
                if b: break
        if vx:
            vx = ' with cell(%d,%d) containing\n%s' % (ix,jx,repr(vx))
        else:
            vx = '...'

        return "<%s at %d %d rows x %s cols>%s" % (self.__class__.__name__, id(self), nr, nc, vx)

    def _listCellGeom(self, V,w,s,W=None,H=None,aH=72000):
        aW = w-s.leftPadding-s.rightPadding
        aH = aH - s.topPadding - s.bottomPadding
        t = 0
        w = 0
        canv = getattr(self,'canv',None)
        for v in V:
            vw, vh = v.wrapOn(canv,aW, aH)
            if W is not None: W.append(vw)
            if H is not None: H.append(vh)
            w = max(w,vw)
            t = t + vh + v.getSpaceBefore()+v.getSpaceAfter()
        return w, t - V[0].getSpaceBefore()-V[-1].getSpaceAfter()

    def _calc_width(self):
        #comments added by Andy to Robin's slightly
        #terse variable names
        W = self._argW  #widths array
        #print 'widths array = %s' % str(self._colWidths)
        canv = getattr(self,'canv',None)
        saved = None

        if None in W:  #some column widths are not given
            if self._spanCmds:
                colspans = self._colSpannedCells
            else:
                colspans = {}
##            k = colspans.keys()
##            k.sort()
##            print 'the following cells are part of spanned ranges: %s' % k
            W = W[:]
            self._colWidths = W
            while None in W:
                j = W.index(None) #find first unspecified column
                #print 'sizing column %d' % j
                f = lambda x,j=j: operator.getitem(x,j)
                V = map(f,self._cellvalues)  #values for this column
                S = map(f,self._cellStyles)  #styles for this column
                w = 0
                i = 0

                for v, s in map(None, V, S):
                    #if the current cell is part of a spanned region,
                    #assume a zero size.
                    if colspans.has_key((j, i)):
                        #print 'sizing a spanned cell (%d, %d) with content "%s"' % (j, i, str(v))
                        t = 0.0
                    else:#work out size
                        t = self._elementWidth(v,s)
                        if t is None:
                            raise ValueError, "Flowable %s in cell(%d,%d) can't have auto width\n%s" % (v.identity(30),i,j,self.identity(30))
                        t = t + s.leftPadding+s.rightPadding
                    if t>w: w = t   #record a new maximum
                    i = i + 1

                #print 'max width for column %d is %0.2f' % (j, w)
                W[j] = w

        width = 0
        self._colpositions = [0]        #index -1 is right side boundary; we skip when processing cells
        for w in W:
            #print w, width
            width = width + w
            self._colpositions.append(width)
        #print "final width", width

        self._width = width

    def _elementWidth(self,v,s):
        t = type(v)
        if t in _SeqTypes:
            w = 0
            for e in v:
                ew = self._elementWidth(self,v)
                if ew is None: return None
                w = max(w,ew)
            return w
        elif isinstance(v,Flowable) and v._fixedWidth:
            return v.width
        else:
            if t is not StringType: v = v is None and '' or str(v)
            v = string.split(v, "\n")
            return max(map(lambda a, b=s.fontname, c=s.fontsize,d=pdfmetrics.stringWidth: d(a,b,c), v))

    def _calc_height(self, availHeight):

        H = self._argH
        W = self._argW

        canv = getattr(self,'canv',None)
        saved = None

        #get a handy list of any cells which span rows.
        #these should be ignored for sizing
        if self._spanCmds:
            spans = self._rowSpannedCells
        else:
            spans = {}

        hmax = lim = len(H)
        longTable = getattr(self,'_longTableOptimize',None)

        if None in H:
            if canv: saved = canv._fontname, canv._fontsize, canv._leading
            H = H[:]    #make a copy as we'll change it
            self._rowHeights = H
            while None in H:
                i = H.index(None)
                if longTable:
                    hmax = i
                    height = reduce(operator.add, H[:i], 0)
                    # we can stop if we have filled up all available room
                    if height > availHeight: break
                V = self._cellvalues[i] # values for row i
                S = self._cellStyles[i] # styles for row i
                h = 0
                j = 0
                for v, s, w in map(None, V, S, W): # value, style, width (lengths must match)
                    if spans.has_key((j, i)):
                        t = 0.0  # don't count it, it's either occluded or unreliable
                    else:
                        t = type(v)
                        if t in _SeqTypes or isinstance(v,Flowable):
                            if not t in _SeqTypes: v = (v,)
                            if w is None:
                                raise ValueError, "Flowable %s in cell(%d,%d) can't have auto width in\n%s" % (v[0].identity(30),i,j,self.identity(30))
                            if canv: canv._fontname, canv._fontsize, canv._leading = s.fontname, s.fontsize, s.leading or 1.2*s.fontsize
                            dW,t = self._listCellGeom(v,w,s)
                            if canv: canv._fontname, canv._fontsize, canv._leading = saved
                            #print "leftpadding, rightpadding", s.leftPadding, s.rightPadding
                            dW = dW + s.leftPadding + s.rightPadding
                            if not rl_config.allowTableBoundsErrors and dW>w:
                                raise "LayoutError", "Flowable %s (%sx%s points) too wide for cell(%d,%d) (%sx* points) in\n%s" % (v[0].identity(30),fp_str(dW),fp_str(t),i,j, fp_str(w), self.identity(30))
                        else:
                            if t is not StringType:
                                v = v is None and '' or str(v)
                            v = string.split(v, "\n")
                            t = s.leading*len(v)
                        t = t+s.bottomPadding+s.topPadding
                    if t>h: h = t   #record a new maximum
                    j = j + 1
                H[i] = h
            if None not in H: hmax = lim

        height = self._height = reduce(operator.add, H[:hmax], 0)
        #print "height, H", height, H
        self._rowpositions = [height]    # index 0 is actually topline; we skip when processing cells
        for h in H[:hmax]:
            height = height - h
            self._rowpositions.append(height)
        assert abs(height)<1e-8, 'Internal height error'
        self._hmax = hmax

    def _calc(self, availWidth, availHeight):
        #if hasattr(self,'_width'): return

        #in some cases there are unsizable things in
        #cells.  If so, apply a different algorithm
        #and assign some withs in a dumb way.
        #this CHANGES the widths array.
        if None in self._colWidths:
            if self._hasVariWidthElements():
                self._calcPreliminaryWidths(availWidth)

        # need to know which cells are part of spanned
        # ranges, so _calc_height and _calc_width can ignore them
        # in sizing
        if self._spanCmds:
            self._calcSpanRanges()

        # calculate the full table height
        #print 'during calc, self._colWidths=', self._colWidths
        self._calc_height(availHeight)

        # if the width has already been calculated, don't calculate again
        # there's surely a better, more pythonic way to short circuit this FIXME FIXME
        if hasattr(self,'_width_calculated_once'): return
        self._width_calculated_once = 1

        # calculate the full table width
        self._calc_width()


        if self._spanCmds:
            #now work out the actual rect for each spanned cell
            #from the underlying grid
            self._calcSpanRects()

    def _hasVariWidthElements(self, upToRow=None):
        """Check for flowables in table cells and warn up front.

        Allow a couple which we know are fixed size such as
        images and graphics."""
        bad = 0
        if upToRow is None: upToRow = self._nrows
        for row in range(min(self._nrows, upToRow)):
            for col in range(self._ncols):
                value = self._cellvalues[row][col]
                if not self._canGetWidth(value):
                    bad = 1
                    #raise Exception('Unsizable elements found at row %d column %d in table with content:\n %s' % (row, col, value))
        return bad

    def _canGetWidth(self, thing):
        "Can we work out the width quickly?"
        if type(thing) in (ListType, TupleType):
            for elem in thing:
                if not self._canGetWidth(elem):
                    return 0
            return 1
        elif isinstance(thing, Flowable):
            return thing._fixedWidth  # must loosen this up
        else: #string, number, None etc.
            #anything else gets passed to str(...)
            # so should be sizable
            return 1

    def _calcPreliminaryWidths(self, availWidth):
        """Fallback algorithm for when main one fails.

        Where exact width info not given but things like
        paragraphs might be present, do a preliminary scan
        and assign some sensible values - just divide up
        all unsizeable columns by the remaining space."""
        verbose = 0
        totalDefined = 0.0
        numberUndefined = 0
        for w in self._colWidths:
            if w is None:
                numberUndefined = numberUndefined + 1
            else:
                totalDefined = totalDefined + w
        if verbose: print 'prelim width calculation.  %d columns, %d undefined width, %0.2f units remain' % (
            self._ncols, numberUndefined, availWidth - totalDefined)

        #check columnwise in each None column to see if they are sizable.
        given = []
        sizeable = []
        unsizeable = []
        for colNo in range(self._ncols):
            if self._colWidths[colNo] is None:
                siz = 1
                for rowNo in range(self._nrows):
                    value = self._cellvalues[rowNo][colNo]
                    if not self._canGetWidth(value):
                        siz = 0
                        break
                if siz:
                    sizeable.append(colNo)
                else:
                    unsizeable.append(colNo)
            else:
                given.append(colNo)
        if len(given) == self._ncols:
            return
        if verbose: print 'predefined width:   ',given
        if verbose: print 'uncomputable width: ',unsizeable
        if verbose: print 'computable width:    ',sizeable

        #how much width is left:
        # on the next iteration we could size the sizeable ones, for now I'll just
        # divide up the space
        newColWidths = list(self._colWidths)
        guessColWidth = (availWidth - totalDefined) / (len(unsizeable)+len(sizeable))
        assert guessColWidth >= 0, "table is too wide already, cannot choose a sane width for undefined columns"
        if verbose: print 'assigning width %0.2f to all undefined columns' % guessColWidth
        for colNo in sizeable:
            newColWidths[colNo] = guessColWidth
        for colNo in unsizeable:
            newColWidths[colNo] = guessColWidth

        self._colWidths = newColWidths
        self._argW = newColWidths
        if verbose: print 'new widths are:', self._colWidths

    def _calcSpanRanges(self):
        """Work out rects for tables which do row and column spanning.

        This creates some mappings to let the later code determine
        if a cell is part of a "spanned" range.
        self._spanRanges shows the 'coords' in integers of each
        'cell range', or None if it was clobbered:
          (col, row) -> (col0, row0, col1, row1)

        Any cell not in the key is not part of a spanned region
        """
        spanRanges = {}
        for row in range(self._nrows):
            for col in range(self._ncols):
                spanRanges[(col, row)] = (col, row, col, row)

        for (cmd, start, stop) in self._spanCmds:
            x0, y0 = start
            x1, y1 = stop

            #normalize
            if x0 < 0: x0 = x0 + self._ncols
            if x1 < 0: x1 = x1 + self._ncols
            if y0 < 0: y0 = y0 + self._nrows
            if y1 < 0: y1 = y1 + self._nrows

            if x0 > x1:
                x0, x1 = x1, x0
            if y0 > y1:
                y0, y1 = y1, y0

            # unset/clobber all the ones it
            # overwrites
            for y in range(y0, y1+1):
                for x in range(x0, x1+1):
                    spanRanges[x, y] = None

            # set the main entry
            spanRanges[x0,y0] = (x0, y0, x1, y1)
##            from pprint import pprint as pp
##            pp(spanRanges)
        self._spanRanges = spanRanges

        #now produce a "listing" of all cells which
        #are part of a spanned region, so the normal
        #sizing algorithm can not bother sizing such cells
        colSpannedCells = {}
        for (key, value) in spanRanges.items():
            if value is None:
                colSpannedCells[key] = 1
            elif len(value) == 4:
                if value[0] == value[2]:
                    #not colspanned
                    pass
                else:
                    colSpannedCells[key] = 1
        self._colSpannedCells = colSpannedCells
        #ditto for row-spanned ones.
        rowSpannedCells = {}
        for (key, value) in spanRanges.items():
            if value is None:
                rowSpannedCells[key] = 1
            elif len(value) == 4:
                if value[1] == value[3]:
                    #not rowspanned
                    pass
                else:
                    rowSpannedCells[key] = 1
        self._rowSpannedCells = rowSpannedCells


    def _calcSpanRects(self):
        """Work out rects for tables which do row and column spanning.

        Based on self._spanRanges, which is already known,
        and the widths which were given or previously calculated,
        self._spanRects shows the real coords for drawing:
          (col, row) -> (x, y, width, height)

        for each cell.  Any cell which 'does not exist' as another
        has spanned over it will get a None entry on the right
        """
        spanRects = {}
        for (coord, value) in self._spanRanges.items():
            if value is None:
                spanRects[coord] = None
            else:
                col,row = coord
                col0, row0, col1, row1 = value
                x = self._colpositions[col0]
                y = self._rowpositions[row1+1]  # should I add 1 for bottom left?
                width = self._colpositions[col1+1] - x
                height = self._rowpositions[row0] - y
                spanRects[coord] = (x, y, width, height)

        self._spanRects = spanRects


    def setStyle(self, tblstyle):
        if type(tblstyle) is not TableStyleType:
            tblstyle = TableStyle(tblstyle)
        for cmd in tblstyle.getCommands():
            self._addCommand(cmd)
        for k,v in tblstyle._opts.items():
            setattr(self,k,v)

    def _addCommand(self,cmd):
        if cmd[0] == 'BACKGROUND':
            self._bkgrndcmds.append(cmd)
        elif cmd[0] == 'SPAN':
            self._spanCmds.append(cmd)
        elif _isLineCommand(cmd):
            # we expect op, start, stop, weight, colour, cap, dashes, join
            cmd = tuple(cmd)
            if len(cmd)<5: raise ValueError('bad line command '+str(cmd))

            #determine line cap value at position 5. This can be string or numeric.
            if len(cmd)<6:
                cmd = cmd+(1,)  
            else:
                cap = cmd[5]  
                try:
                    if type(cap) is not type(int):
                        cap = LINECAPS[cap]
                    elif cap<0 or cap>2:
                        raise ValueError
                    cmd = cmd[:5]+(cap,)+cmd[6:]
                except:
                    ValueError('Bad cap value %s in %s'%(cap,str(cmd)))
            #dashes at index 6 - this is a dash array:
            if len(cmd)<7: cmd = cmd+(None,)

            #join mode at index 7 - can be string or numeric, look up as for caps
            if len(cmd)<8: cmd = cmd+(1,)
            else:
                join = cmd[7]
                try:
                    if type(join) is not type(int):
                        join = LINEJOINS[cap]
                    elif join<0 or join>2:
                        raise ValueError
                    cmd = cmd[:7]+(join,)
                except:
                    ValueError('Bad join value %s in %s'%(join,str(cmd)))

            #linecount at index 8.  Default is 1, set to 2 for double line.
            if len(cmd)<9:
                lineCount = 1
                cmd = cmd + (lineCount,)
            else:
                lineCount = cmd[8]
            assert lineCount >= 1
            #linespacing at index 9. Not applicable unless 2+ lines, defaults to 2*line
            #width so you get a visible gap between centres
            if len(cmd)<10: cmd = cmd + (cmd[3],)

            assert len(cmd) == 10
            
            self._linecmds.append(cmd)
        else:
            (op, (sc, sr), (ec, er)), values = cmd[:3] , cmd[3:]
            if sc < 0: sc = sc + self._ncols
            if ec < 0: ec = ec + self._ncols
            if sr < 0: sr = sr + self._nrows
            if er < 0: er = er + self._nrows
            for i in range(sr, er+1):
                for j in range(sc, ec+1):
                    _setCellStyle(self._cellStyles, i, j, op, values)

    def _drawLines(self):
        ccap, cdash, cjoin = None, None, None
        self.canv.saveState()
        for op, (sc,sr), (ec,er), weight, color, cap, dash, join, count, space in self._linecmds:
            if type(sr) is type('') and sr.startswith('split'): continue
            if sc < 0: sc = sc + self._ncols
            if ec < 0: ec = ec + self._ncols
            if sr < 0: sr = sr + self._nrows
            if er < 0: er = er + self._nrows
            if ccap!=cap:
                self.canv.setLineCap(cap)
                ccap = cap
            getattr(self,_LineOpMap.get(op, '_drawUnknown' ))( (sc, sr), (ec, er), weight, color, count, space)
        self.canv.restoreState()
        self._curcolor = None

    def _drawUnknown(self,  (sc, sr), (ec, er), weight, color, count, space):
        raise ValueError, "Unknown line command '%s'" % op

    def _drawGrid(self, (sc, sr), (ec, er), weight, color, count, space):
        self._drawBox( (sc, sr), (ec, er), weight, color, count, space)
        self._drawInnerGrid( (sc, sr), (ec, er), weight, color, count, space)

    def _drawBox(self,  (sc, sr), (ec, er), weight, color, count, space):
        self._drawHLines((sc, sr), (ec, sr), weight, color, count, space)
        self._drawHLines((sc, er+1), (ec, er+1), weight, color, count, space)
        self._drawVLines((sc, sr), (sc, er), weight, color, count, space)
        self._drawVLines((ec+1, sr), (ec+1, er), weight, color, count, space)

    def _drawInnerGrid(self, (sc, sr), (ec, er), weight, color, count, space):
        self._drawHLines((sc, sr+1), (ec, er), weight, color, count, space)
        self._drawVLines((sc+1, sr), (ec, er), weight, color, count, space)

    def _prepLine(self, weight, color):
        if color != self._curcolor:
            self.canv.setStrokeColor(color)
            self._curcolor = color
        if weight != self._curweight:
            self.canv.setLineWidth(weight)
            self._curweight = weight

    def _drawHLines(self, (sc, sr), (ec, er), weight, color, count, space):
        ecp = self._colpositions[sc:ec+2]
        rp = self._rowpositions[sr:er+1]
        if len(ecp)<=1 or len(rp)<1: return
        self._prepLine(weight, color)
        scp = ecp[0]
        ecp = ecp[-1]
        if count == 1:
            for rowpos in rp:
                self.canv.line(scp, rowpos, ecp, rowpos)
        else:
            #multi-lines; position so count==1 and no space gives origin
            ws = weight+space
            offset = 0.5*(count-1)*ws
            for rowpos in rp:
                y = rowpos+offset
                for idx in xrange(count):
                    self.canv.line(scp, y, ecp, y)
                    y -= ws

    def _drawHLinesB(self, (sc, sr), (ec, er), weight, color, count, space):
        self._drawHLines((sc, sr+1), (ec, er+1), weight, color, count, space)

    def _drawVLines(self, (sc, sr), (ec, er), weight, color, count, space):
        erp = self._rowpositions[sr:er+2]
        cp  = self._colpositions[sc:ec+1]
        if len(erp)<=1 or len(cp)<1: return
        self._prepLine(weight, color)
        srp = erp[0]
        erp = erp[-1]
        for colpos in cp:
            if count == 1:
                self.canv.line(colpos, srp, colpos, erp)
            else: #double/triple lines
                #position so count=1 and no space gives origin
                offset = (count-1) * (weight + space)
                for idx in range(count):
                    x = colpos + 0.5*offset - (idx * (weight+space))
                    self.canv.line(x, srp, x, erp)

    def _drawVLinesA(self, (sc, sr), (ec, er), weight, color, count, space):
        self._drawVLines((sc+1, sr), (ec+1, er), weight, color, count, space)

    def wrap(self, availWidth, availHeight):
        self._calc(availWidth, availHeight)
        #nice and easy, since they are predetermined size
        self.availWidth = availWidth
        return (self._width, self._height)

    def onSplit(self,T,byRow=1):
        '''
        This method will be called when the Table is split.
        Special purpose tables can override to do special stuff.
        '''
        pass

    def _cr_0(self,n,cmds):
        for c in cmds:
            c = tuple(c)
            (sc,sr), (ec,er) = c[1:3]
            if sr>=n: continue
            if er>=n: er = n-1
            self._addCommand((c[0],)+((sc, sr), (ec, er))+c[3:])

    def _cr_1_1(self,n,repeatRows, cmds):
        for c in cmds:
            c = tuple(c)
            (sc,sr), (ec,er) = c[1:3]
            if sr in ('splitfirst','splitlast'): self._addCommand(c)
            else:
                if sr>=0 and sr>=repeatRows and sr<n and er>=0 and er<n: continue
                if sr>=repeatRows and sr<n: sr=repeatRows
                elif sr>=repeatRows and sr>=n: sr=sr+repeatRows-n
                if er>=repeatRows and er<n: er=repeatRows
                elif er>=repeatRows and er>=n: er=er+repeatRows-n
                self._addCommand((c[0],)+((sc, sr), (ec, er))+c[3:])

    def _cr_1_0(self,n,cmds):
        for c in cmds:
            c = tuple(c)
            (sc,sr), (ec,er) = c[1:3]
            if sr in ('splitfirst','splitlast'): self._addCommand(c)
            else:
                if er>=0 and er<n: continue
                if sr>=0 and sr<n: sr=0
                if sr>=n: sr = sr-n
                if er>=n: er = er-n
                self._addCommand((c[0],)+((sc, sr), (ec, er))+c[3:])

    def _splitRows(self,availHeight):
        h = 0
        n = 0
        lim = len(self._rowHeights)
        while n<self._hmax:
            hn = h + self._rowHeights[n]
            if hn>availHeight: break
            h = hn
            n = n + 1

        if n<=self.repeatRows:
            return []

        if n==lim: return [self]

        repeatRows = self.repeatRows
        repeatCols = self.repeatCols
        splitByRow = self.splitByRow
        data = self._cellvalues

        #we're going to split into two superRows
        #R0 = slelf.__class__( data[:n], self._argW, self._argH[:n],
        R0 = self.__class__( data[:n], self._colWidths, self._argH[:n],
                repeatRows=repeatRows, repeatCols=repeatCols,
                splitByRow=splitByRow)

        #copy the styles and commands
        R0._cellStyles = self._cellStyles[:n]

        A = []
        # hack up the line commands
        for op, (sc,sr), (ec,er), weight, color, cap, dash, join, count, space in self._linecmds:
            if type(sr)is type('') and sr.startswith('split'):
                A.append((op,(sc,sr), (ec,sr), weight, color, cap, dash, join, count, space))
                if sr=='splitlast':
                    sr = er = n-1
                elif sr=='splitfirst':
                    sr = n
                    er = n

            if sc < 0: sc = sc + self._ncols
            if ec < 0: ec = ec + self._ncols
            if sr < 0: sr = sr + self._nrows
            if er < 0: er = er + self._nrows

            if op in ('BOX','OUTLINE','GRID'):
                if sr<n and er>=n:
                    # we have to split the BOX
                    A.append(('LINEABOVE',(sc,sr), (ec,sr), weight, color, cap, dash, join, count, space))
                    A.append(('LINEBEFORE',(sc,sr), (sc,er), weight, color, cap, dash, join, count, space))
                    A.append(('LINEAFTER',(ec,sr), (ec,er), weight, color, cap, dash, join, count, space))
                    A.append(('LINEBELOW',(sc,er), (ec,er), weight, color, cap, dash, join, count, space))
                    if op=='GRID':
                        A.append(('LINEBELOW',(sc,n-1), (ec,n-1), weight, color, cap, dash, join, count, space))
                        A.append(('LINEABOVE',(sc,n), (ec,n), weight, color, cap, dash, join, count, space))
                        A.append(('INNERGRID',(sc,sr), (ec,er), weight, color, cap, dash, join, count, space))
                else:
                    A.append((op,(sc,sr), (ec,er), weight, color, cap, dash, join, count, space))
            elif op in ('INNERGRID','LINEABOVE'):
                if sr<n and er>=n:
                    A.append(('LINEBELOW',(sc,n-1), (ec,n-1), weight, color, cap, dash, join, count, space))
                    A.append(('LINEABOVE',(sc,n), (ec,n), weight, color, cap, dash, join, count, space))
                A.append((op,(sc,sr), (ec,er), weight, color, cap, dash, join, count, space))
            elif op == 'LINEBELOW':
                if sr<n and er>=(n-1):
                    A.append(('LINEABOVE',(sc,n), (ec,n), weight, color, cap, dash, join, count, space))
                A.append((op,(sc,sr), (ec,er), weight, color))
            elif op == 'LINEABOVE':
                if sr<=n and er>=n:
                    A.append(('LINEBELOW',(sc,n-1), (ec,n-1), weight, color, cap, dash, join, count, space))
                A.append((op,(sc,sr), (ec,er), weight, color, cap, dash, join, count, space))
            else:
                A.append((op,(sc,sr), (ec,er), weight, color, cap, dash, join, count, space))

        R0._cr_0(n,A)
        R0._cr_0(n,self._bkgrndcmds)

        if repeatRows:
            #R1 = slelf.__class__(data[:repeatRows]+data[n:],self._argW,
            R1 = self.__class__(data[:repeatRows]+data[n:],self._colWidths,
                    self._argH[:repeatRows]+self._argH[n:],
                    repeatRows=repeatRows, repeatCols=repeatCols,
                    splitByRow=splitByRow)
            R1._cellStyles = self._cellStyles[:repeatRows]+self._cellStyles[n:]
            R1._cr_1_1(n,repeatRows,A)
            R1._cr_1_1(n,repeatRows,self._bkgrndcmds)
        else:
            #R1 = slelf.__class__(data[n:], self._argW, self._argH[n:],
            R1 = self.__class__(data[n:], self._colWidths, self._argH[n:],
                    repeatRows=repeatRows, repeatCols=repeatCols,
                    splitByRow=splitByRow)
            R1._cellStyles = self._cellStyles[n:]
            R1._cr_1_0(n,A)
            R1._cr_1_0(n,self._bkgrndcmds)


        R0.hAlign = R1.hAlign = self.hAlign
        R0.vAlign = R1.vAlign = self.vAlign
        self.onSplit(R0)
        self.onSplit(R1)
        return [R0,R1]

    def split(self, availWidth, availHeight):
        self._calc(availWidth, availHeight)
        if self.splitByRow:
            if not rl_config.allowTableBoundsErrors and self._width>availWidth: return []
            return self._splitRows(availHeight)
        else:
            raise NotImplementedError

    def draw(self):
        self._curweight = self._curcolor = self._curcellstyle = None
        self._drawBkgrnd()
        self._drawLines()
        if self._spanCmds == []:
            # old fashioned case, no spanning, steam on and do each cell
            for row, rowstyle, rowpos, rowheight in map(None, self._cellvalues, self._cellStyles, self._rowpositions[1:], self._rowHeights):
                for cellval, cellstyle, colpos, colwidth in map(None, row, rowstyle, self._colpositions[:-1], self._colWidths):
                    self._drawCell(cellval, cellstyle, (colpos, rowpos), (colwidth, rowheight))
        else:
            # we have some row or col spans, need a more complex algorithm
            # to find the rect for each
            for rowNo in range(self._nrows):
                for colNo in range(self._ncols):
                    cellRect = self._spanRects[colNo, rowNo]
                    if cellRect is not None:
                        (x, y, width, height) = cellRect
                        cellval = self._cellvalues[rowNo][colNo]
                        cellstyle = self._cellStyles[rowNo][colNo]
                        self._drawCell(cellval, cellstyle, (x, y), (width, height))


    def _drawBkgrnd(self):
        nrows = self._nrows
        ncols = self._ncols
        for cmd, (sc, sr), (ec, er), arg in self._bkgrndcmds:
            if sc < 0: sc = sc + ncols
            if ec < 0: ec = ec + ncols
            if sr < 0: sr = sr + nrows
            if er < 0: er = er + nrows
            x0 = self._colpositions[sc]
            y0 = self._rowpositions[sr]
            x1 = self._colpositions[min(ec+1,ncols)]
            y1 = self._rowpositions[min(er+1,nrows)]
            w, h = x1-x0, y1-y0
            canv = self.canv
            if callable(arg):
                apply(arg,(self,canv, x0, y0, w, h))
            else:
                canv.setFillColor(colors.toColor(arg))
                canv.rect(x0, y0, w, h, stroke=0,fill=1)

    def _drawCell(self, cellval, cellstyle, (colpos, rowpos), (colwidth, rowheight)):
        if self._curcellstyle is not cellstyle:
            cur = self._curcellstyle
            if cur is None or cellstyle.color != cur.color:
                self.canv.setFillColor(cellstyle.color)
            if cur is None or cellstyle.leading != cur.leading or cellstyle.fontname != cur.fontname or cellstyle.fontsize != cur.fontsize:
                self.canv.setFont(cellstyle.fontname, cellstyle.fontsize, cellstyle.leading)
            self._curcellstyle = cellstyle

        just = cellstyle.alignment
        valign = cellstyle.valign
        n = type(cellval)
        if n in _SeqTypes or isinstance(cellval,Flowable):
            if not n in _SeqTypes: cellval = (cellval,)
            # we assume it's a list of Flowables
            W = []
            H = []
            w, h = self._listCellGeom(cellval,colwidth,cellstyle,W=W, H=H,aH=rowheight)
            if valign=='TOP':
                y = rowpos + rowheight - cellstyle.topPadding
            elif valign=='BOTTOM':
                y = rowpos+cellstyle.bottomPadding + h
            else:
                y = rowpos+(rowheight+cellstyle.bottomPadding-cellstyle.topPadding+h)/2.0
            y = y+cellval[0].getSpaceBefore()
            for v, w, h in map(None,cellval,W,H):
                if just=='LEFT': x = colpos+cellstyle.leftPadding
                elif just=='RIGHT': x = colpos+colwidth-cellstyle.rightPadding - w
                elif just in ('CENTRE', 'CENTER'):
                    x = colpos+(colwidth+cellstyle.leftPadding-cellstyle.rightPadding-w)/2.0
                else:
                    raise ValueError, 'Invalid justification %s' % just
                y = y - v.getSpaceBefore()
                y = y - h
                v.drawOn(self.canv,x,y)
                y = y - v.getSpaceAfter()
        else:
            if just == 'LEFT':
                draw = self.canv.drawString
                x = colpos + cellstyle.leftPadding
            elif just in ('CENTRE', 'CENTER'):
                draw = self.canv.drawCentredString
                x = colpos + colwidth * 0.5
            elif just == 'RIGHT':
                draw = self.canv.drawRightString
                x = colpos + colwidth - cellstyle.rightPadding
            elif just == 'DECIMAL':
                draw = self.canv.drawAlignedString
                x = colpos + colwidth - cellstyle.rightPadding
            else:
                raise ValueError, 'Invalid justification %s' % just
            if n is StringType: val = cellval
            else: val = str(cellval)
            vals = string.split(val, "\n")
            n = len(vals)
            leading = cellstyle.leading
            fontsize = cellstyle.fontsize
            if valign=='BOTTOM':
                y = rowpos + cellstyle.bottomPadding+n*leading-fontsize
            elif valign=='TOP':
                y = rowpos + rowheight - cellstyle.topPadding - fontsize
            elif valign=='MIDDLE':
                y = rowpos + (cellstyle.bottomPadding + rowheight-cellstyle.topPadding+(n-1)*leading)/2.0
            else:
                raise ValueError, "Bad valign: '%s'" % str(valign)

            for v in vals:
                draw(x, y, v)
                y = y-leading

# for text,
#   drawCentredString(self, x, y, text) where x is center
#   drawRightString(self, x, y, text) where x is right
#   drawString(self, x, y, text) where x is left

_LineOpMap = {  'GRID':'_drawGrid',
                'BOX':'_drawBox',
                'OUTLINE':'_drawBox',
                'INNERGRID':'_drawInnerGrid',
                'LINEBELOW':'_drawHLinesB',
                'LINEABOVE':'_drawHLines',
                'LINEBEFORE':'_drawVLines',
                'LINEAFTER':'_drawVLinesA', }

class LongTable(Table):
    '''Henning von Bargen's changes will be active'''
    _longTableOptimize = 1

LINECOMMANDS = _LineOpMap.keys()

def _isLineCommand(cmd):
    return cmd[0] in LINECOMMANDS

def _setCellStyle(cellStyles, i, j, op, values):
    #new = CellStyle('<%d, %d>' % (i,j), cellStyles[i][j])
    #cellStyles[i][j] = new
    ## modify in place!!!
    new = cellStyles[i][j]
    if op == 'FONT':
        n = len(values)
        new.fontname = values[0]
        if n>1:
            new.fontsize = values[1]
            if n>2:
                new.leading = values[2]
            else:
                new.leading = new.fontsize*1.2
    elif op in ('FONTNAME', 'FACE'):
        new.fontname = values[0]
    elif op in ('SIZE', 'FONTSIZE'):
        new.fontsize = values[0]
    elif op == 'LEADING':
        new.leading = values[0]
    elif op == 'TEXTCOLOR':
        new.color = colors.toColor(values[0], colors.Color(0,0,0))
    elif op in ('ALIGN', 'ALIGNMENT'):
        new.alignment = values[0]
    elif op == 'VALIGN':
        new.valign = values[0]
    elif op == 'LEFTPADDING':
        new.leftPadding = values[0]
    elif op == 'RIGHTPADDING':
        new.rightPadding = values[0]
    elif op == 'TOPPADDING':
        new.topPadding = values[0]
    elif op == 'BOTTOMPADDING':
        new.bottomPadding = values[0]

GRID_STYLE = TableStyle(
    [('GRID', (0,0), (-1,-1), 0.25, colors.black),
     ('ALIGN', (1,1), (-1,-1), 'RIGHT')]
    )
BOX_STYLE = TableStyle(
    [('BOX', (0,0), (-1,-1), 0.50, colors.black),
     ('ALIGN', (1,1), (-1,-1), 'RIGHT')]
    )
LABELED_GRID_STYLE = TableStyle(
    [('INNERGRID', (0,0), (-1,-1), 0.25, colors.black),
     ('BOX', (0,0), (-1,-1), 2, colors.black),
     ('LINEBELOW', (0,0), (-1,0), 2, colors.black),
     ('LINEAFTER', (0,0), (0,-1), 2, colors.black),
     ('ALIGN', (1,1), (-1,-1), 'RIGHT')]
    )
COLORED_GRID_STYLE = TableStyle(
    [('INNERGRID', (0,0), (-1,-1), 0.25, colors.black),
     ('BOX', (0,0), (-1,-1), 2, colors.red),
     ('LINEBELOW', (0,0), (-1,0), 2, colors.black),
     ('LINEAFTER', (0,0), (0,-1), 2, colors.black),
     ('ALIGN', (1,1), (-1,-1), 'RIGHT')]
    )
LIST_STYLE = TableStyle(
    [('LINEABOVE', (0,0), (-1,0), 2, colors.green),
     ('LINEABOVE', (0,1), (-1,-1), 0.25, colors.black),
     ('LINEBELOW', (0,-1), (-1,-1), 2, colors.green),
     ('ALIGN', (1,1), (-1,-1), 'RIGHT')]
    )

def test():
    from reportlab.lib.units import inch
    rowheights = (24, 16, 16, 16, 16)
    rowheights2 = (24, 16, 16, 16, 30)
    colwidths = (50, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32)
    data = (
        ('', 'Jan', 'Feb', 'Mar','Apr','May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'),
        ('Mugs', 0, 4, 17, 3, 21, 47, 12, 33, 2, -2, 44, 89),
        ('T-Shirts', 0, 42, 9, -3, 16, 4, 72, 89, 3, 19, 32, 119),
        ('Key Ring', 0,0,0,0,0,0,1,0,0,0,2,13),
        ('Hats', 893, 912, '1,212', 643, 789, 159, 888, '1,298', 832, 453, '1,344','2,843')
        )
    data2 = (
        ('', 'Jan', 'Feb', 'Mar','Apr','May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'),
        ('Mugs', 0, 4, 17, 3, 21, 47, 12, 33, 2, -2, 44, 89),
        ('T-Shirts', 0, 42, 9, -3, 16, 4, 72, 89, 3, 19, 32, 119),
        ('Key Ring', 0,0,0,0,0,0,1,0,0,0,2,13),
        ('Hats\nLarge', 893, 912, '1,212', 643, 789, 159, 888, '1,298', 832, 453, '1,344','2,843')
        )
    styleSheet = getSampleStyleSheet()
    lst = []
    lst.append(Paragraph("Tables", styleSheet['Heading1']))
    lst.append(Paragraph(__doc__, styleSheet['BodyText']))
    lst.append(Paragraph("The Tables (shown in different styles below) were created using the following code:", styleSheet['BodyText']))
    lst.append(Preformatted("""
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
    t = Table(data, colwidths, rowheights)
    """, styleSheet['Code'], dedent=4))
    lst.append(Paragraph("""
    You can then give the Table a TableStyle object to control its format. The first TableStyle used was
    created as follows:
    """, styleSheet['BodyText']))
    lst.append(Preformatted("""
GRID_STYLE = TableStyle(
    [('GRID', (0,0), (-1,-1), 0.25, colors.black),
     ('ALIGN', (1,1), (-1,-1), 'RIGHT')]
    )
    """, styleSheet['Code']))
    lst.append(Paragraph("""
    TableStyles are created by passing in a list of commands. There are two types of commands - line commands
    and cell formatting commands. In all cases, the first three elements of a command are the command name,
    the starting cell and the ending cell.
    """, styleSheet['BodyText']))
    lst.append(Paragraph("""
    Line commands always follow this with the weight and color of the desired lines. Colors can be names,
    or they can be specified as a (R,G,B) tuple, where R, G and B are floats and (0,0,0) is black. The line
    command names are: GRID, BOX, OUTLINE, INNERGRID, LINEBELOW, LINEABOVE, LINEBEFORE
    and LINEAFTER. BOX and OUTLINE are equivalent, and GRID is the equivalent of applying both BOX and
    INNERGRID.
    """, styleSheet['BodyText']))
    lst.append(Paragraph("""
    Cell formatting commands are:
    """, styleSheet['BodyText']))
    lst.append(Paragraph("""
    FONT - takes fontname, fontsize and (optional) leading.
    """, styleSheet['Definition']))
    lst.append(Paragraph("""
    TEXTCOLOR - takes a color name or (R,G,B) tuple.
    """, styleSheet['Definition']))
    lst.append(Paragraph("""
    ALIGNMENT (or ALIGN) - takes one of LEFT, RIGHT and CENTRE (or CENTER).
    """, styleSheet['Definition']))
    lst.append(Paragraph("""
    LEFTPADDING - defaults to 6.
    """, styleSheet['Definition']))
    lst.append(Paragraph("""
    RIGHTPADDING - defaults to 6.
    """, styleSheet['Definition']))
    lst.append(Paragraph("""
    BOTTOMPADDING - defaults to 3.
    """, styleSheet['Definition']))
    lst.append(Paragraph("""
    A tablestyle is applied to a table by calling Table.setStyle(tablestyle).
    """, styleSheet['BodyText']))
    t = Table(data, colwidths, rowheights)
    t.setStyle(GRID_STYLE)
    lst.append(PageBreak())
    lst.append(Paragraph("This is GRID_STYLE\n", styleSheet['BodyText']))
    lst.append(t)

    t = Table(data, colwidths, rowheights)
    t.setStyle(BOX_STYLE)
    lst.append(Paragraph("This is BOX_STYLE\n", styleSheet['BodyText']))
    lst.append(t)
    lst.append(Paragraph("""
    It was created as follows:
    """, styleSheet['BodyText']))
    lst.append(Preformatted("""
BOX_STYLE = TableStyle(
    [('BOX', (0,0), (-1,-1), 0.50, colors.black),
     ('ALIGN', (1,1), (-1,-1), 'RIGHT')]
    )
    """, styleSheet['Code']))

    t = Table(data, colwidths, rowheights)
    t.setStyle(LABELED_GRID_STYLE)
    lst.append(Paragraph("This is LABELED_GRID_STYLE\n", styleSheet['BodyText']))
    lst.append(t)
    t = Table(data2, colwidths, rowheights2)
    t.setStyle(LABELED_GRID_STYLE)
    lst.append(Paragraph("This is LABELED_GRID_STYLE ILLUSTRATES EXPLICIT LINE SPLITTING WITH NEWLINE (different heights and data)\n", styleSheet['BodyText']))
    lst.append(t)
    lst.append(Paragraph("""
    It was created as follows:
    """, styleSheet['BodyText']))
    lst.append(Preformatted("""
LABELED_GRID_STYLE = TableStyle(
    [('INNERGRID', (0,0), (-1,-1), 0.25, colors.black),
     ('BOX', (0,0), (-1,-1), 2, colors.black),
     ('LINEBELOW', (0,0), (-1,0), 2, colors.black),
     ('LINEAFTER', (0,0), (0,-1), 2, colors.black),
     ('ALIGN', (1,1), (-1,-1), 'RIGHT')]
    )
    """, styleSheet['Code']))
    lst.append(PageBreak())

    t = Table(data, colwidths, rowheights)
    t.setStyle(COLORED_GRID_STYLE)
    lst.append(Paragraph("This is COLORED_GRID_STYLE\n", styleSheet['BodyText']))
    lst.append(t)
    lst.append(Paragraph("""
    It was created as follows:
    """, styleSheet['BodyText']))
    lst.append(Preformatted("""
COLORED_GRID_STYLE = TableStyle(
    [('INNERGRID', (0,0), (-1,-1), 0.25, colors.black),
     ('BOX', (0,0), (-1,-1), 2, colors.red),
     ('LINEBELOW', (0,0), (-1,0), 2, colors.black),
     ('LINEAFTER', (0,0), (0,-1), 2, colors.black),
     ('ALIGN', (1,1), (-1,-1), 'RIGHT')]
    )
    """, styleSheet['Code']))

    t = Table(data, colwidths, rowheights)
    t.setStyle(LIST_STYLE)
    lst.append(Paragraph("This is LIST_STYLE\n", styleSheet['BodyText']))
    lst.append(t)
    lst.append(Paragraph("""
    It was created as follows:
    """, styleSheet['BodyText']))
    lst.append(Preformatted("""
LIST_STYLE = TableStyle(
    [('LINEABOVE', (0,0), (-1,0), 2, colors.green),
     ('LINEABOVE', (0,1), (-1,-1), 0.25, colors.black),
     ('LINEBELOW', (0,-1), (-1,-1), 2, colors.green),
     ('ALIGN', (1,1), (-1,-1), 'RIGHT')]
    )
    """, styleSheet['Code']))

    t = Table(data, colwidths, rowheights)
    ts = TableStyle(
    [('LINEABOVE', (0,0), (-1,0), 2, colors.green),
     ('LINEABOVE', (0,1), (-1,-1), 0.25, colors.black),
     ('LINEBELOW', (0,-1), (-1,-1), 3, colors.green,'butt'),
     ('LINEBELOW', (0,-1), (-1,-1), 1, colors.white,'butt'),
     ('ALIGN', (1,1), (-1,-1), 'RIGHT'),
     ('TEXTCOLOR', (0,1), (0,-1), colors.red),
     ('BACKGROUND', (0,0), (-1,0), colors.Color(0,0.7,0.7))]
    )
    t.setStyle(ts)
    lst.append(Paragraph("This is a custom style\n", styleSheet['BodyText']))
    lst.append(t)
    lst.append(Paragraph("""
    It was created as follows:
    """, styleSheet['BodyText']))
    lst.append(Preformatted("""
   ts = TableStyle(
    [('LINEABOVE', (0,0), (-1,0), 2, colors.green),
     ('LINEABOVE', (0,1), (-1,-1), 0.25, colors.black),
     ('LINEBELOW', (0,-1), (-1,-1), 3, colors.green,'butt'),
     ('LINEBELOW', (0,-1), (-1,-1), 1, colors.white,'butt'),
     ('ALIGN', (1,1), (-1,-1), 'RIGHT'),
     ('TEXTCOLOR', (0,1), (0,-1), colors.red),
     ('BACKGROUND', (0,0), (-1,0), colors.Color(0,0.7,0.7))]
    )
    """, styleSheet['Code']))
    data = (
        ('', 'Jan\nCold', 'Feb\n', 'Mar\n','Apr\n','May\n', 'Jun\nHot', 'Jul\n', 'Aug\nThunder', 'Sep\n', 'Oct\n', 'Nov\n', 'Dec\n'),
        ('Mugs', 0, 4, 17, 3, 21, 47, 12, 33, 2, -2, 44, 89),
        ('T-Shirts', 0, 42, 9, -3, 16, 4, 72, 89, 3, 19, 32, 119),
        ('Key Ring', 0,0,0,0,0,0,1,0,0,0,2,13),
        ('Hats', 893, 912, '1,212', 643, 789, 159, 888, '1,298', 832, 453, '1,344','2,843')
        )
    c = list(colwidths)
    c[0] = None
    c[8] = None
    t = Table(data, c, [None]+list(rowheights[1:]))
    t.setStyle(LIST_STYLE)
    lst.append(Paragraph("""
        This is a LIST_STYLE table with the first rowheight set to None ie automatic.
        The top row cells are split at a newline '\\n' character. The first and August
        column widths were also set to None.
    """, styleSheet['BodyText']))
    lst.append(t)

    lst.append(Paragraph("""
        This demonstrates a number of features useful in financial statements. The first is decimal alignment;
        with ALIGN=DECIMAL the numbers align on the points; and the points are aligned based on
        the LEFTPADDING, which is usually 3 points so you should set it higher.  The second is multiple lines;
        one can specify double or triple lines and control the separation if desired. Finally, the coloured
        negative numbers were (we regret to say) done in the style; we don't have a way to conditionally
        format numbers based on value yet.
    """, styleSheet['BodyText']))


    t = Table([['Corporate Assets','Amount'],
               ['Fixed Assets','1,234,567.89'],
               ['Company Vehicle','1,234.8901'],
               ['Petty Cash','42'],
               ['Intellectual Property','(42,078,231.56)'],
               ['Net Position','Deep Sh*t.Really']
               ],
              [144,72])

    ts = TableStyle(
        [#first the top row
         ('ALIGN', (1,1), (-1,-1), 'CENTER'),
         ('LINEABOVE', (0,0), (-1,0), 1, colors.purple),
         ('LINEBELOW', (0,0), (-1,0), 1, colors.purple),
         ('FONT', (0,0), (-1,0), 'Times-Bold'),

        #bottom row has a line above, and two lines below
         ('LINEABOVE', (0,-1), (-1,-1), 1, colors.purple),  #last 2 are count, sep
         ('LINEBELOW', (0,-1), (-1,-1), 0.5, colors.purple, 1, None, None, 4,1),
         ('LINEBELOW', (0,-1), (-1,-1), 1, colors.red),
         ('FONT', (0,-1), (-1,-1), 'Times-Bold'),

        #numbers column
         ('ALIGN', (1,1), (-1,-1), 'DECIMAL'),
         ('RIGHTPADDING', (1,1), (-1,-1), 36),
         ('TEXTCOLOR', (1,4), (1,4), colors.red),

        #red cell         
        ]
        )

    t.setStyle(ts)
    lst.append(t)
    lst.append(Spacer(36,36))    
    lst.append(Paragraph("""
        The red numbers should be aligned LEFT &amp; BOTTOM, the blue RIGHT &amp; TOP
        and the green CENTER &amp; MIDDLE.
    """, styleSheet['BodyText']))
    XY  =   [['X00y', 'X01y', 'X02y', 'X03y', 'X04y'],
            ['X10y', 'X11y', 'X12y', 'X13y', 'X14y'],
            ['X20y', 'X21y', 'X22y', 'X23y', 'X24y'],
            ['X30y', 'X31y', 'X32y', 'X33y', 'X34y']]
    t=Table(XY, 5*[0.6*inch], 4*[0.6*inch])
    t.setStyle([('ALIGN',(1,1),(-2,-2),'LEFT'),
                ('TEXTCOLOR',(1,1),(-2,-2),colors.red),

                ('VALIGN',(0,0),(1,-1),'TOP'),
                ('ALIGN',(0,0),(1,-1),'RIGHT'),
                ('TEXTCOLOR',(0,0),(1,-1),colors.blue),

                ('ALIGN',(0,-1),(-1,-1),'CENTER'),
                ('VALIGN',(0,-1),(-1,-1),'MIDDLE'),
                ('TEXTCOLOR',(0,-1),(-1,-1),colors.green),
                ('INNERGRID', (0,0), (-1,-1), 0.25, colors.black),
                ('BOX', (0,0), (-1,-1), 0.25, colors.black),
                ])
    lst.append(t)
    data = [('alignment', 'align\012alignment'),
            ('bulletColor', 'bulletcolor\012bcolor'),
            ('bulletFontName', 'bfont\012bulletfontname'),
            ('bulletFontSize', 'bfontsize\012bulletfontsize'),
            ('bulletIndent', 'bindent\012bulletindent'),
            ('firstLineIndent', 'findent\012firstlineindent'),
            ('fontName', 'face\012fontname\012font'),
            ('fontSize', 'size\012fontsize'),
            ('leading', 'leading'),
            ('leftIndent', 'leftindent\012lindent'),
            ('rightIndent', 'rightindent\012rindent'),
            ('spaceAfter', 'spaceafter\012spacea'),
            ('spaceBefore', 'spacebefore\012spaceb'),
            ('textColor', 'fg\012textcolor\012color')]
    t = Table(data)
    t.setStyle([
            ('VALIGN',(0,0),(-1,-1),'TOP'),
            ('INNERGRID', (0,0), (-1,-1), 0.25, colors.black),
            ('BOX', (0,0), (-1,-1), 0.25, colors.black),
            ])
    lst.append(t)
    t = Table([ ('Attribute', 'Synonyms'),
                ('alignment', 'align, alignment'),
                ('bulletColor', 'bulletcolor, bcolor'),
                ('bulletFontName', 'bfont, bulletfontname'),
                ('bulletFontSize', 'bfontsize, bulletfontsize'),
                ('bulletIndent', 'bindent, bulletindent'),
                ('firstLineIndent', 'findent, firstlineindent'),
                ('fontName', 'face, fontname, font'),
                ('fontSize', 'size, fontsize'),
                ('leading', 'leading'),
                ('leftIndent', 'leftindent, lindent'),
                ('rightIndent', 'rightindent, rindent'),
                ('spaceAfter', 'spaceafter, spacea'),
                ('spaceBefore', 'spacebefore, spaceb'),
                ('textColor', 'fg, textcolor, color')])
    t.repeatRows = 1
    t.setStyle([
                ('FONT',(0,0),(-1,1),'Times-Bold',10,12),
                ('FONT',(0,1),(-1,-1),'Courier',8,8),
                ('VALIGN',(0,0),(-1,-1),'MIDDLE'),
                ('INNERGRID', (0,0), (-1,-1), 0.25, colors.black),
                ('BOX', (0,0), (-1,-1), 0.25, colors.black),
                ('BACKGROUND', (0, 0), (-1, 0), colors.green),
                ('BACKGROUND', (0, 1), (-1, -1), colors.pink),
                ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
                ('ALIGN', (0, 1), (0, -1), 'LEFT'),
                ('ALIGN', (-1, 1), (-1, -1), 'RIGHT'),
                ('FONT', (0, 0), (-1, 0), 'Times-Bold', 12),
                ('ALIGN', (1, 1), (1, -1), 'CENTER'),
                ])
    lst.append(t)
    lst.append(Table(XY,
            style=[ ('FONT',(0,0),(-1,-1),'Times-Roman', 5,6),
                    ('GRID', (0,0), (-1,-1), 0.25, colors.blue),]))
    lst.append(Table(XY,
            style=[ ('FONT',(0,0),(-1,-1),'Times-Roman', 10,12),
                    ('GRID', (0,0), (-1,-1), 0.25, colors.black),]))
    lst.append(Table(XY,
            style=[ ('FONT',(0,0),(-1,-1),'Times-Roman', 20,24),
                    ('GRID', (0,0), (-1,-1), 0.25, colors.red),]))
    lst.append(PageBreak())
    data=  [['00', '01', '02', '03', '04'],
            ['10', '11', '12', '13', '14'],
            ['20', '21', '22', '23', '24'],
            ['30', '31', '32', '33', '34']]
    t=Table(data,style=[
                    ('GRID',(0,0),(-1,-1),0.5,colors.grey),
                    ('GRID',(1,1),(-2,-2),1,colors.green),
                    ('BOX',(0,0),(1,-1),2,colors.red),
                    ('BOX',(0,0),(-1,-1),2,colors.black),
                    ('LINEABOVE',(1,2),(-2,2),1,colors.blue),
                    ('LINEBEFORE',(2,1),(2,-2),1,colors.pink),
                    ('BACKGROUND', (0, 0), (0, 1), colors.pink),
                    ('BACKGROUND', (1, 1), (1, 2), colors.lavender),
                    ('BACKGROUND', (2, 2), (2, 3), colors.orange),
                    ])
    lst.append(t)
    lst.append(Spacer(0,6))
    for s in t.split(4*inch,30):
        lst.append(s)
        lst.append(Spacer(0,6))
    lst.append(Spacer(0,6))
    for s in t.split(4*inch,36):
        lst.append(s)
        lst.append(Spacer(0,6))

    lst.append(Spacer(0,6))
    for s in t.split(4*inch,56):
        lst.append(s)
        lst.append(Spacer(0,6))

    import os, reportlab.platypus
    I = Image(os.path.join(os.path.dirname(reportlab.platypus.__file__),'..','tools','pythonpoint','demos','leftlogo.gif'))
    I.drawHeight = 1.25*inch*I.drawHeight / I.drawWidth
    I.drawWidth = 1.25*inch
    #I.drawWidth = 9.25*inch #uncomment to see better messaging
    P = Paragraph("<para align=center spaceb=3>The <b>ReportLab Left <font color=red>Logo</font></b> Image</para>", styleSheet["BodyText"])
    data=  [['A', 'B', 'C', Paragraph("<b>A pa<font color=red>r</font>a<i>graph</i></b><super><font color=yellow>1</font></super>",styleSheet["BodyText"]), 'D'],
            ['00', '01', '02', [I,P], '04'],
            ['10', '11', '12', [I,P], '14'],
            ['20', '21', '22', '23', '24'],
            ['30', '31', '32', '33', '34']]

    t=Table(data,style=[('GRID',(1,1),(-2,-2),1,colors.green),
                    ('BOX',(0,0),(1,-1),2,colors.red),
                    ('LINEABOVE',(1,2),(-2,2),1,colors.blue),
                    ('LINEBEFORE',(2,1),(2,-2),1,colors.pink),
                    ('BACKGROUND', (0, 0), (0, 1), colors.pink),
                    ('BACKGROUND', (1, 1), (1, 2), colors.lavender),
                    ('BACKGROUND', (2, 2), (2, 3), colors.orange),
                    ('BOX',(0,0),(-1,-1),2,colors.black),
                    ('GRID',(0,0),(-1,-1),0.5,colors.black),
                    ('VALIGN',(3,0),(3,0),'BOTTOM'),
                    ('BACKGROUND',(3,0),(3,0),colors.limegreen),
                    ('BACKGROUND',(3,1),(3,1),colors.khaki),
                    ('ALIGN',(3,1),(3,1),'CENTER'),
                    ('BACKGROUND',(3,2),(3,2),colors.beige),
                    ('ALIGN',(3,2),(3,2),'LEFT'),
                    ])

    t._argW[3]=1.5*inch
    lst.append(t)

    # now for an attempt at column spanning.
    lst.append(PageBreak())
    colWidths = [24] * 5
    rowHeight = [20] * 5
    data=  [['A', 'BBBBB', 'C', 'D', 'E'],
            ['00', '01', '02', '03', '04'],
            ['10', '11', '12', '13', '14'],
            ['20', '21', '22', '23', '24'],
            ['30', '31', '32', '33', '34']]
    sty = [
            ('ALIGN',(0,0),(-1,-1),'CENTER'),
            ('VALIGN',(0,0),(-1,-1),'TOP'),
            ('GRID',(0,0),(-1,-1),1,colors.green),
            ('BOX',(0,0),(-1,-1),2,colors.red),

            #span 'BBBB' across middle 3 cells in top row
            ('SPAN',(1,0),(3,0)),
            #now color the first cell in this range only,
            #i.e. the one we want to have spanned.  Hopefuly
            #the range of 3 will come out khaki.
            ('BACKGROUND',(1,0),(1,0),colors.khaki),

            ('SPAN',(0,2),(-1,2)),


            #span 'AAA'down entire left column
            ('SPAN',(0,0), (0, 1)),
            ('BACKGROUND',(0,0),(0,0),colors.cyan),
            ('LINEBELOW', (0,'splitlast'), (-1,'splitlast'), 1, colors.white,'butt'),
           ]
    t=Table(data,style=sty, colWidths = [20] * 5, rowHeights = [20]*5)
    lst.append(t)

    # und jetzt noch eine Tabelle mit 5000 Zeilen:
    sty = [ ('GRID',(0,0),(-1,-1),1,colors.green),
            ('BOX',(0,0),(-1,-1),2,colors.red),
           ]
    data = [[str(i), Paragraph("xx "* (i%10), styleSheet["BodyText"]), Paragraph("blah "*(i%40), styleSheet["BodyText"])] for i in xrange(500)]
    t=LongTable(data, style=sty, colWidths = [50,100,200])
    lst.append(t)


    SimpleDocTemplate('tables.pdf', showBoundary=1).build(lst)

if __name__ == '__main__':
    test()
