import sys, os, pyRXP, pprint, time

def test(fn):
	cwd = os.getcwd()
	try:
		print 'BEGIN'
		t0 = time.time()
		xml = open(fn,'r').read()
		os.chdir(os.path.dirname(fn))
		t1 = time.time()
		D = pyRXP.Parser().parse(xml)
		t2 = time.time()
		print 'END read took %7.2f" parse took %7.2f"' %(t1-t0,t2-t1)
		return D
	finally:
		os.chdir(cwd)
	

if __name__=='__main__':
	def Usage():
		print >>sys.stderr, 'Usage %s [-n] filename' % sys.argv[0]
		sys.exit()
	if len(sys.argv)<2: Usage()
	nopp = sys.argv[1]=='-n'
	if nopp: del sys.argv[1]
	if len(sys.argv)<2: Usage()
	fn = sys.argv[1]
	D = test(fn)
	if not nopp: pprint.pprint(D)
