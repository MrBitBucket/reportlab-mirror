import pyRXP, traceback, sys
def goodTest(x,t,tb=0,**kw):
	try:
		P=pyRXP.Parser(**kw)
		r = P(x)
		rb = 0
	except:
		et, ev, None = sys.exc_info()
		r = '%s %s' % (et.__name__, str(ev))
		rb = 1

	s = ''
	for k,v in kw.items():
		s = s+', %s=%s' % (k,str(v))
	if type(t) is type(''):
		t = t.replace('\r','\\r')
		t = t.replace('\n','\\n')
	if type(r) is type(''):
		r = r.replace('\r','\\r')
		r = r.replace('\n','\\n')
	print 'Parser(%s)(%s)-->'%(s[2:],repr(x)),r,
	if r==t and rb==tb:
		print 'OK'
	else:
		print '!!!!!BAD!!!!! should --> ', t

def failTest(x,t,tb=1,**kw):
	goodTest(x,t,tb,**kw)

if __name__=='__main__': #noruntests
	if '__doc__' in sys.argv: print pyRXP.__doc__
	else:
		try:
			for k,v in pyRXP.parser_flags.items(): eval('pyRXP.Parser(%s=%d)' % (k,v))
			print 'Parser keywords OK'
		except:
			traceback.print_exc()
			print 'Parser keywords BAD'
		try:
			for k,v in pyRXP.parser_flags.items(): eval('pyRXP.Parser()("<a/>",%s=%d)' % (k,v))
			print 'Parser().parse keywords OK'
		except:
			traceback.print_exc()
			print 'Parser().parse keywords BAD'
		goodTest('<a></a>',('a', None, [], None))
		goodTest('<a></a>',('a', {}, [], None),ExpandEmpty=1)
		goodTest('<a></a>',['a', None, [], None],MakeMutableTree=1)
		goodTest('<a/>',('a', None, None, None))
		goodTest('<a/>',('a', {}, [], None),ExpandEmpty=1)
		goodTest('<a/>',['a', None, None, None],MakeMutableTree=1)
		goodTest('<a/>',['a', {}, [], None],ExpandEmpty=1,MakeMutableTree=1)
		failTest('</a>',"Error Error: End tag </a> outside of any element\n in unnamed entity at line 1 char 4 of [unknown]\n")
		goodTest('<a>A<!--comment--></a>',('a', None, ['A'], None))
		goodTest('<a>A<!--comment--></a>',('a', {}, ['A'], None),ExpandEmpty=1)
		goodTest('<a>A<!--comment--></a>', ('a', None, ['A', '<!--comment-->'], None), ReturnComments=1)
		goodTest('<a>A&lt;&amp;&gt;</a>',('a', None, ['A<&>'], None))
		goodTest('<a>A&lt;&amp;&gt;</a>',('a', None, ['A', '<', '&', '>'], None), MergePCData=0)
		goodTest('<!--comment--><a/>',('a', None, None, None),ReturnComments=1)
		goodTest('<!--comment--><a/>',['<!--comment-->',('a', None, None, None)],ReturnComments=1,ReturnList=1)
		goodTest('<!--comment--><a/>',('a', None, None, None),ReturnComments=1)
		failTest('<?xml version="1.0" encoding="LATIN-1"?></a>',"Error Unknown declared encoding LATIN-1\nInternal error, ParserPush failed!\n")
