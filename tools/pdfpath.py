#a class that will convert a pdfpath definition to our format
from reportlab.graphics.shapes import Path, definePath
__all__ = ('PDFPath',)
class PDFPath(Path):
    ops = dict(m='moveTo',l='lineTo',c='curveTo',h='closePath')

    def __init__(self,pdf='',**kw):
        self.__dict__.update(definePath(pathSegs=list(self._getSegs(pdf.strip().split())),**kw).__dict__)

    def _getSegs(self,L):
        n = len(L)
        i = 0
        ops = self.ops
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

