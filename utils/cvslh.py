#copyright ReportLab Inc. 2000
#see license.txt for license details
#history http://cvs.sourceforge.net/cgi-bin/cvsweb.cgi/utils/cvslh.py?cvsroot=reportlab
#$Header: /tmp/reportlab/utils/cvslh.py,v 1.6 2002/01/21 13:19:27 rgbecker Exp $
#
#	python cvslh.py -d"2000/04/10 14:00:00" >\tmp\hacked_log
#
#	makes a reasonably formatted file of the log entries since the specified
#	date. Use -r to reverse the time order, -f to get just a list of the modified files.
#
import re, sys, os, getopt, string, tempfile
class logFileEntry:
	def __init__(self, version):
		self.version = version
		self.date = None
		self.author = None
		self.comment = None
	def __str__(self):
		if self.version:
			return "%10s %s %s %s" %(self.version, self.date, self.comment, self.author)
class logFile:
	def __init__(self,name):
		self.name  = name
		self.E = []
	def addEntry(self,E):
		self.E.append(E)

	def getChanges(self,L=None):
		if L is None: L = []
		for e in self.E:
			L.append(Change(self.name,e))

	def __str__(self):
		s = str(self.name)
		for e in self.E:
			s = s+'\n'+str(e)
		return s

class Change:
	def __init__(self,name,lFE):
		self.name = name
		self.version = lFE.version
		self.date = lFE.date
		self.comment = lFE.comment
		self.author = lFE.author

reWorking=re.compile('^Working +file: +(.*)$')
reVersion=re.compile('^revision +(.*)$')
reDate=re.compile('^date: +([^;]*); +author: +([^;]*)')
opt={'-d': '7 days ago'}
def findWorking():
	global i, lines
	while i<len(lines):
		m = reWorking.match(lines[i])
		i = i + 1
		if m:
			return m.group(1)
		
	return None

def findVersion(F):
	global i, lines, opt
	while i<len(lines):
		m = reVersion.match(lines[i])
		if m:
			E=logFileEntry(m.group(1))
			i = i + 1
			m = reDate.match(lines[i])
			if m:
				E.date = m.group(1)
				E.author = m.group(2)
				i = i + 1
				if re.match('^branches:',lines[i]): i = i + 1
				l = ''
				while i<len(lines) and re.match('^[-=]+$',lines[i]) is None:
					l = l + ' ' + lines[i][:-1]
					i = i + 1
				E.comment = l
				i = i + 1
			F.addEntry(E)
		else:
			if reWorking.search(lines[i]): return None
			i = i + 1
	return None

def sortFunc(a, b):
	if a.date<b.date: return -1
	elif a.date>b.date: return 1
	elif a.name<b.name: return -1
	elif a.name>b.name: return 1
	else: return 0

def sortFuncR(a,b):
	return -sortFunc(a,b)

if __name__=='__main__': #noruntests
	opts, argv= getopt.getopt(sys.argv[1:],'rfd:')
	for k,v in opts: opt[k]=v
	#cmd = 'cvs -z3 log -d"%s<now"%s' % (opt['-d'], ' '.join(argv))
	#sin, sout, serr = os.popen3(cmd,'t')
	#lines = sout.readlines()
	#err = serr.read()
	#print >>sys.stderr, err
	try:
		tmp = tempfile.mktemp("_cvslh_%d.tmp" % os.getpid())
		os.system('cvs -z3 log -d"%s<now"%s >"%s"' % (opt['-d'], ' '.join(argv),tmp))
		lines = open(tmp,'r').readlines()
	finally:
		if os.path.isfile(tmp): os.remove(tmp)
	i = 0
	cL = []
	reverseSort = opt.has_key('-r')
	filesOnly = opt.has_key('-f')
	while 1:
		f = findWorking()
		if f is None: break
		F = logFile(f)
		while findVersion(F):
			pass
		F.getChanges(cL)

	if not filesOnly:
		cL.sort(reverseSort and sortFuncR or sortFunc)
		d = ''
		for c in cL:
			if c.date[:10]!=d:
				d = c.date[:10]
				print '##### %s #####' % d
			print '\t%s %s %s %s' % (c.name, c.version, c.author, string.join(string.split(c.comment,'\n'),'\n\t\t'))
	else:
		L = []
		for c in cL:
			if c.name not in L: L.append(c.name)
		L.sort()
		print ' '.join(L)
