import re, sys, getopt
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
	def __str__(self):
		s = str(self.name)
		for e in self.E:
			s = s+'\n'+str(e)
		return s

reWorking=re.compile('^Working +file: +(.*)$')
reVersion=re.compile('^revision +(.*)$')
reDate=re.compile('^date: +([^;]*); +author: +([^;]*)')
opt={'-d': None}
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
			if opt['-d']:
				ok = opt['-d']<=E.date
			else:
				ok = 1
			if ok: F.addEntry(E)
		else:
			if reWorking.search(lines[i]): return None
			i = i + 1
	return None

opts, argv= getopt.getopt(sys.argv[1:],'d:')
for k,v in opts: opt[k]=v
if len(argv):
	lines = open(argv[0],'r').readlines()
else:
	lines = sys.stdin.readlines()
i = 0
while 1:
	f = findWorking()
	if f is None: break
	F = logFile(f)
	while findVersion(F):
		pass
	if F.E != []:
		print str(F)
