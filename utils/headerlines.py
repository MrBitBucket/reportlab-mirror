# Simple script to check the #$Header lines in cvs files
#copyright ReportLab Inc. 2000
#see license.txt for license details
#history http://cvs.sourceforge.net/cgi-bin/cvsweb.cgi/utils/copyrite.py?cvsroot=reportlab
#$Header: /tmp/reportlab/utils/headerlines.py,v 1.1 2002/03/21 19:29:05 rgbecker Exp $
__version__='''$Header:'''
import string, os, sys, time, re
hl_re=re.compile(r'^\s*#\s*\$Header\s*:\s*')
v_re=re.compile(r'^__version__\s*=\s*')

class HList:
	def __init__(self):
		self.H = []
		self.V = []
		self.M = []
		self.N = []

def getHeader(f):
	h = None
	v = None
	for l in open(f,'r').readlines():
		if not h:
			h = hl_re.search(l)
			if h:
				h = tuple(l[len(h.group(0)):].split(' ')[0:4]+[f.replace('\\','/')])
				if v: break
		if not v:
			v = v_re.search(l)
			if v and h: break
	return h, v

def visit(L, dirname, names):
	for n in names:
		if n[-3:]=='.py':
			f = os.path.join(dirname,n)
			if os.path.isfile(f):
				h, v = getHeader(f)
				if h:
					L.H.append(h)
				else:
					L.M.append(f)
				if v:
					L.V.append(f)
				else:
					L.N.append(f)

if __name__=='__main__':
	L = HList()
	D = len(sys.argv)<2 and ['.'] or sys.argv[1:]
	print 'Directories Searched %s' % time.asctime(time.gmtime())
	for d in D:
		n, m, v, w = len(L.H),len(L.M),len(L.V),len(L.N)
		os.path.walk(d,visit,L)
		print '  "%s" #headers=%d #missing=%d #versioned=%d #unversioned=%d' % (d,len(L.H)-n,len(L.M)-m,len(L.V)-v,len(L.N)-w)

	L.H.sort()
	L.M.sort()
	L.V.sort()
	L.N.sort()

	if len(L.H):
		print '\nHeaders:'
		for h in L.H:
			print '  %s %s %s %s "%s"' % h

	if len(L.M):
		print '\nFiles without headers:'
		for m in L.M:
			print '  "%s"' % m

	if len(L.V):
		print '\nVersioned:'
		for v in L.V:
			print '  "%s"' % v

	if len(L.N):
		print '\nUnversioned:'
		for n in L.N:
			print '  "%s"' % n
