#a class that will convert a pdfpath definition to our format
from reportlab.graphics.shapes import Path, definePath, _PATH_OP_ARG_COUNT, _PATH_OP_NAMES
__all__ = ('PDFPath',)

def _getSegs(L):
    n = len(L)
    i = 0
    ops = dict(m='moveTo',l='lineTo',c='curveTo',h='closePath')
    while i < n:
        for j in i, i+2, i+6:
            op = L[j]
            if op in ops:
                try:
                    opName = ops[op]
                    nargs = _PATH_OP_ARG_COUNT[_PATH_OP_NAMES.index(opName)]
                    yield tuple([opName]+[float(L[i+k]) for k in range(nargs)])
                    i = j+1
                    break
                except:
                    raise ValueError('Error converting PDFPath at %s' % ' '.join(L[i:i+6]))
        else:
            raise ValueError('Error converting PDFPath at %s' % ' '.join(L[i:i+6]))

def pdfpath(pdf='',**kwds):
    if pdf:
        pdf = pdf.strip()
    if pdf:
        p = definePath(pathSegs=list(_getSegs(pdf.split())),**kwds)
    else:
        p = Path(**kwds)
    return p
