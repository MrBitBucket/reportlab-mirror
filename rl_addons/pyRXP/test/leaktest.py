if __name__=='__main__': #noruntests
	import pyRXP, sys
	xml='<start><tag1>text here</tag1><tag1>more text</tag1></start>'
	n = 1
	P = i = tup = None
	if len(sys.argv)>1: n = int(sys.argv[1])
	for i in xrange(n):
		P=pyRXP.Parser()
		tup=P(xml)
	del n, pyRXP, sys, P, tup, xml
