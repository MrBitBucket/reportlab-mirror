import os, time, shutil, gc
from reportlab.pdfbase.pdfmetrics import _py_getFont, _py_unicode2T1
from _rl_accel import unicode2T1
utext = 'This is the end of the \xce\x91\xce\xb2 world. This is the end of the \xce\x91\xce\xb2 world jap=\xe3\x83\x9b\xe3\x83\x86. This is the end of the \xce\x91\xce\xb2 world. This is the end of the \xce\x91\xce\xb2 world jap=\xe3\x83\x9b\xe3\x83\x86'.decode('utf8')
fontName = 'Times-Roman'
fontSize=12
N = 10000
def tim(msg,func,*args):
    t0 = time.time()
    for i in xrange(N):
        x = func(*args)
    t1 = time.time()
    return "%s N=%d t=%.3f\n%r" % (msg,N,t1-t0,x)

#print tim('_py_stringWidth', _py_stringWidth, utext, fontName, fontSize)
#print tim('stringWidth2', stringWidth2, utext, fontName, fontSize)

font = _py_getFont(fontName)
print unicode2T1(utext,[font]+font.substitutionFonts)==_py_unicode2T1(utext,[font]+font.substitutionFonts)
print unicode2T1(u'ABCDEF',[font]+font.substitutionFonts)
print _py_unicode2T1(u'ABCDEF',[font]+font.substitutionFonts)
for i in (0,1,2):
    print gc.collect(),len(gc.get_objects())
    print tim('unicode2T1',unicode2T1,utext,[font]+font.substitutionFonts)
    print gc.collect(),len(gc.get_objects())
    print tim('_py_unicode2T1',_py_unicode2T1,utext,[font]+font.substitutionFonts)
    print gc.collect(),len(gc.get_objects())
