import _renderPM
from reportlab.pdfbase.pdfmetrics import getFont
f=getFont('Times-Roman'); print 'getFont'
_renderPM.makeT1Font('Times-Roman',f.face.findT1File(),f.encoding.vector); print 'makeFont'
f=getFont('Times-Bold'); print 'getFont'
_renderPM.makeT1Font('Times-Bold',f.face.findT1File(),f.encoding.vector); print 'makeFont'
_renderPM.delCache(); print 'delCache'
f=getFont('Times-Roman'); print 'getFont'
_renderPM.makeT1Font('Times-Roman',f.face.findT1File(),f.encoding.vector); print 'makeFont'
f=getFont('Times-Bold'); print 'getFont'
_renderPM.makeT1Font('Times-Bold',f.face.findT1File(),f.encoding.vector); print 'makeFont'
_renderPM.delCache(); print 'delCache'
