cdef extern from "math.h" nogil:
	double log10(double)
from cpython.unicode cimport PyUnicode_Check
_fp_fmts = "%.0f", "%.1f", "%.2f", "%.3f", "%.4f", "%.5f", "%.6f"
def fp_str(*a):
	'''convert separate arguments (or single sequence arg) into space separated numeric strings'''
	cdef int l, j
	cdef double i, sa
	s = []
	if len(a)==1 and isinstance(a[0],(tuple,list)):
		a = a[0]
	A = s.append
	for i in a:
		sa =abs(i)
		if sa<=1e-7: A('0')
		else:
			l = sa<=1 and 6 or min(max(0,(6-int(log10(sa)))),6)
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

def unicode2T1(utext,fonts,font0=None):
	'''return a list of (font,string) pairs representing the unicode text'''
	R = []
	font, fonts = fonts[0], fonts[1:]
	if font0 is None: font0 = font
	enc = font.encName
	if 'UCS-2' in enc:
		enc = 'UTF16'
	while utext:
		try:
			if PyUnicode_Check(utext):
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
				R.extend(unicode2T1(utext[i0:il],fonts,font0))
			else:
				R.append((font0._notdefFont,font0._notdefChar*(il-i0)))
			utext = utext[il:]
	return R

def _instanceStringWidthU(self, text, size, encoding='utf8'):
	"""This is the "purist" approach to width"""
	if not PyUnicode_Check(text): text = text.decode(encoding)
	#return sum([sum(f.widths.__getitem__(ord(c)) for c in t) for f, t in unicode2T1(text,[self]+self.substitutionFonts)])*0.001*size
	#return sum([sum(map(f.widths.__getitem__,list(map(ord,t)))) for f, t in unicode2T1(text,[self]+self.substitutionFonts)])*0.001*size
	#cdef int i, n
	cdef bytes t, c
	cdef double s=0
	cdef int i
	for f, t in unicode2T1(text,[self]+self.substitutionFonts):
		fwgi = f.widths.__getitem__
		for c in t:
			s += fwgi(ord(c))
	return s*0.001*size
