import time
from reportlab.pdfbase.pdfmetrics import _fonts, findFontAndRegister, getFont as _py_getFont
from sys import getrefcount as rc
import sys
#fn0 = 'Times-Bold'
#fn1 = 'Times-Roman'
N = 1000000
def tim(N,msg,func,*args):
    t0 = time.time()
    for i in xrange(N):
        x = func(*args)
    t1 = time.time()
    return "%s N=%d t=%.3f\n%r" % (msg,N,t1-t0,x)
for i in (0,1,2):
    for fn in 'Courier','Helvetica':
        print hex(id(_fonts)), hex(id(findFontAndRegister)), hex(id(fn)), rc(fn)
        from _rl_accel import getFontU
        print tim(N,'getFontU',getFontU,fn)
        print tim(N,'_py_getFont',_py_getFont,fn)
        print hex(id(_fonts)), hex(id(findFontAndRegister)), hex(id(fn)), rc(fn)
