from reportlab.lib.utils import isUnicode, isSeq
from math import log
_log_10 = lambda x,log=log,_log_e_10=log(10.0): log(x)/_log_e_10
_fp_fmts = "%.0f", "%.1f", "%.2f", "%.3f", "%.4f", "%.5f", "%.6f"
def fp_str(*a):
    '''convert separate arguments (or single sequence arg) into space separated numeric strings'''
    if len(a)==1 and isSeq(a[0]): a = a[0]
    s = []
    A = s.append
    for i in a:
        sa =abs(i)
        if sa<=1e-7: A('0')
        else:
            l = sa<=1 and 6 or min(max(0,(6-int(_log_10(sa)))),6)
            n = _fp_fmts[l]%i
            if l:
                j = len(n)
                while j:
                    j -= 1
                    if n[j]!='0':
                        if n[j]!='.': j += 1
                        break
                n = n[:j]
            A((n[0]!='0' or len(n)==1) and n or n[1:])
    return ' '.join(s)

#hack test for comma users
if ',' in fp_str(0.25):
    _FP_STR = fp_str
    def fp_str(*a):
        return _FP_STR(*a).replace(',','.')

def unicode2T1(utext,fonts):
    '''return a list of (font,string) pairs representing the unicode text'''
    R = []
    font, fonts = fonts[0], fonts[1:]
    enc = font.encName
    if 'UCS-2' in enc:
        enc = 'UTF16'
    while utext:
        try:
            if isUnicode(utext):
                s = utext.encode(enc)
            else:
                s = utext
            R.append((font,s))
            break
        except UnicodeEncodeError as e:
            i0, il = e.args[2:4]
            if i0:
                R.append((font,utext[:i0].encode(enc)))
            if fonts:
                R.extend(unicode2T1(utext[i0:il],fonts))
            else:
                R.append((font._notdefFont,font._notdefChar*(il-i0)))
            utext = utext[il:]
    return R

def _instanceStringWidthU(self, text, size, encoding='utf8'):
    """This is the "purist" approach to width"""
    if not isUnicode(text): text = text.decode(encoding)
    return sum([sum(map(f.widths.__getitem__,list(map(ord,t)))) for f, t in unicode2T1(text,[self]+self.substitutionFonts)])*0.001*size

if __name__=='__main__':
    import sys, os
    for modname in 'reportlab.lib.rl_accel','reportlab.lib._rl_accel':
        for cmd  in (
            #"unicode2T1('abcde fghi . jkl ; mno',fonts)",
            #"unicode2T1(u'abcde fghi . jkl ; mno',fonts)",
            "_instanceStringWidthU(font,'abcde fghi . jkl ; mno',10)",
            "_instanceStringWidthU(font,u'abcde fghi . jkl ; mno',10)",
            ):
            print('%s %s' % (modname,cmd))
            s=';'.join((
                "from reportlab.pdfbase.pdfmetrics import getFont",
                "from %s import unicode2T1,_instanceStringWidthU" % modname,
                "fonts=[getFont('Helvetica')]+getFont('Helvetica').substitutionFonts""",
                "font=fonts[0]",
                ))
            os.system('%s -m timeit -s"%s" "%s"' % (sys.executable,s,cmd))
