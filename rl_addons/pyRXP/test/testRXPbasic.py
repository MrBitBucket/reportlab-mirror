import traceback, sys
_pyRXP = None
_logf = open('pyRXP_test.log','w')
_bad = 0
_total = 0
def _dot(c,write=sys.stdout.write):
	global _total, _bad
	write(c)
	if c=='E': _bad = _bad + 1
	if _total%40 == 39: write('\n')
	_total = _total + 1

def goodTest(x,t,tb=0,**kw):
	try:
		P=_pyRXP.Parser(**kw)
		r = P(x)
		rb = 0
	except:
		et, ev, _unused = sys.exc_info()
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
	print >>_logf, '%s.Parser(%s)(%s)'%(_pyRXP.__name__,s[2:],repr(x)),
	if r==t and rb==tb:
		print >>_logf, 'OK'
		_dot('.')
	else:
		_dot('E')
		print >>_logf,'\nBAD got ', r
		print >>_logf,'Expected', t

def failTest(x,t,tb=1,**kw):
	goodTest(x,t,tb,**kw)

def _runTests(pyRXP):
	global _pyRXP
	_pyRXP = pyRXP
	print >>_logf, '############# Testing',pyRXP.__name__
	try:
		for k,v in pyRXP.parser_flags.items(): eval('pyRXP.Parser(%s=%d)' % (k,v))
		print >>_logf,'Parser keywords OK'
		_dot('.')
	except:
		traceback.print_exc()
		print >>_logf,'Parser keywords BAD'
		_dot('E')
	try:
		for k,v in pyRXP.parser_flags.items(): eval('pyRXP.Parser()("<a/>",%s=%d)' % (k,v))
		print >>_logf,'Parser().parse keywords OK'
		_dot('.')
	except:
		traceback.print_exc()
		print >>_logf,'Parser().parse keywords BAD'
		_dot('E')

	goodTest('<a></a>',('a', None, [], None))
	goodTest('<a></a>',('a', {}, [], None),ExpandEmpty=1)
	goodTest('<a></a>',['a', None, [], None],MakeMutableTree=1)
	goodTest('<a/>',('a', None, None, None))
	goodTest('<a/>',('a', {}, [], None),ExpandEmpty=1)
	goodTest('<a/>',['a', None, None, None],MakeMutableTree=1)
	goodTest('<a/>',['a', {}, [], None],ExpandEmpty=1,MakeMutableTree=1)
	failTest('</a>',"Error Error: End tag </a> outside of any element\n in unnamed entity at line 1 char 4 of [unknown]\nEnd tag </a> outside of any element\nParse Failed!\n")
	goodTest('<a>A<!--comment--></a>',('a', None, ['A'], None))
	goodTest('<a>A<!--comment--></a>',('a', {}, ['A'], None),ExpandEmpty=1)
	goodTest('<a>A<!--comment--></a>', ('a', None, ['A', ('<!--', None, ['comment'], None)], None), ReturnComments=1)
	goodTest('<a>A&lt;&amp;&gt;</a>',('a', None, ['A<&>'], None))
	goodTest('<a>A&lt;&amp;&gt;</a>',('a', None, ['A', '<', '&', '>'], None), MergePCData=0)
	goodTest('<!--comment--><a/>',('a', None, None, None),ReturnComments=1)
	goodTest('<!--comment--><a/>',[('<!--',None,['comment'],None),('a', None, None, None)],ReturnComments=1,ReturnList=1)
	goodTest('<!--comment--><a/>',('a', None, None, None),ReturnComments=1)
	failTest('<?xml version="1.0" encoding="LATIN-1"?></a>',"Error Unknown declared encoding LATIN-1\nInternal error, ParserPush failed!\n")
	goodTest('<?work version="1.0" encoding="utf-8"?><a/>',[('<?',{'name':'work'}, ['version="1.0" encoding="utf-8"'],None), ('a', None, None, None)],IgnorePlacementErrors=1,ReturnList=1,ReturnProcessingInstructions=1,ReturnComments=1)
	goodTest('<a>\nHello\n<b>cruel\n</b>\nWorld\n</a>',('a', None, ['\nHello\n', ('b', None, ['cruel\n'], (('aaa', 2, 3), ('aaa', 3, 4))), '\nWorld\n'], (('aaa', 0, 3), ('aaa', 5, 4))),fourth=pyRXP.recordLocation,srcName='aaa')
	goodTest('<a aname="ANAME" aother="AOTHER">\nHello\n<b bname="BNAME" bother="BOTHER">cruel\n</b>\nWorld\n</a>',('a', {"aname": "ANAME", "aother": "AOTHER"}, ['\nHello\n', ('b', {"bname": "BNAME", "bother": "BOTHER"}, ['cruel\n'], (('aaa', 2, 33), ('aaa', 3, 4))), '\nWorld\n'], (('aaa', 0, 33), ('aaa', 5, 4))),fourth=pyRXP.recordLocation,srcName='aaa')
	goodTest('<a><![CDATA[<a>]]></a>',('a', None, ['<a>'], None))
	goodTest('<a><![CDATA[<a>]]></a>',('a', None, [('<![CDATA[', None, ['<a>'], None)], None),ReturnCDATASectionsAsTuples=1)
	goodTest('''<foo:A xmlns:foo="http://www.foo.org/"><foo:B><foo:C xmlns:foo="http://www.bar.org/"><foo:D>abcd</foo:D></foo:C></foo:B><foo:B/><A>bare A<C>bare C</C><B>bare B</B></A><A xmlns="http://default.reportlab.com/" xmlns:bongo="http://bongo.reportlab.com/">default ns A<bongo:A>bongo A</bongo:A><B>default NS B</B></A></foo:A>''',('{http://www.foo.org/}A', {'xmlns:foo': 'http://www.foo.org/'}, [('{http://www.foo.org/}B', None, [('{http://www.bar.org/}C', {'xmlns:foo': 'http://www.bar.org/'}, [('{http://www.bar.org/}D', None, ['abcd'], None)], None)], None), ('{http://www.foo.org/}B', None, None, None), ('A', None, ['bare A', ('C', None, ['bare C'], None), ('B', None, ['bare B'], None)], None), ('{http://default.reportlab.com/}A', {'xmlns': 'http://default.reportlab.com/', 'xmlns:bongo': 'http://bongo.reportlab.com/'}, ['default ns A', ('{http://bongo.reportlab.com/}A', None, ['bongo A'], None), ('{http://default.reportlab.com/}B', None, ['default NS B'], None)], None)], None),XMLNamespaces=1,ReturnNamespaceAttributes=1)


def run():
	import pyRXP
	try:
		import pyRXPU
	except ImportError:
		pyRXPU = None
	if '__doc__' in sys.argv:
		print pyRXP.__doc__
	else:
		for p in (pyRXP, pyRXPU):
			if p: _runTests(p)
		msg = "\n%d tests, %s failures!" % (_total,_bad and `_bad` or 'no')
		print msg
		print >> _logf, msg

if __name__=='__main__': #noruntests
	run()
