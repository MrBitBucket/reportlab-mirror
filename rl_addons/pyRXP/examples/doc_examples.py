if __name__=='__main__':
	import pyRXP, traceback, os, sys, pprint
	sys.stderr=sys.stdout
	p=pyRXP.Parser()
	print '''import pyRXP'''
	print '''p=pyRXP.Parser()'''
	
	code = ['''pyRXP.version''',
			'''pyRXP.RXPVersion''',
			'''p('<tag>content</tag>')''',
			'''p('<tag1><tag2>content</tag2></tag1>')''',
			-1,'''pprint.pprint(p('<tag1><tag2>content</tag2></tag1>'))''',
			'''p('<tag>my contents</tag>')''',
			'''p('<tag></tag>')''',
			'''p('<tag/>')''',
			'''p('<outerTag><innerTag>bb</innerTag>aaa<singleTag/></outerTag>')''',
			-1,'''pprint.pprint(p('<outerTag><innerTag>bb</innerTag>aaa<singleTag/></outerTag>'))''',
			'''p('<tag/><!-- this is a comment about the tag -->')''',
			'''p('<!-- this is a comment -->')''',
			'''p('<a>aaa</a') # note the missing ‘>’''',
			'''p('<a></a><b></b>')''',
			'''p('<outer><a></a><b></b></outer>')''',
			'''os.getcwd()''',
			'''os.listdir('.')''',
			-1,'''dtd = open('tinydtd.dtd', 'r').read()''',
			'''dtd''',
			-1,'''fn=open('sample1.xml', 'r').read()''',
			'''fn''',
			'''p(fn)''',
			-1,'''fn=open('sample2.xml', 'r').read()''',
			'''fn''',
			'''p(fn)''',
			-1,'''fn=open('sample4.xml', 'r').read()''',
			'''fn''',
			'''p(fn,NoNoDTDWarning=0)''',
			-1,'''fn=open('sample3.xml', 'r').read()''',
			'''fn''',
			'''p(fn)''',
			'''p('<a></a><b></b>',AllowMultipleElements = 0)''',
			'''p('<a></a><b></b>',AllowMultipleElements=1)''',
			'''p('<a></A>',CaseInsensitive=1)''',
			'''p('<a></A>',CaseInsensitive=0)''',
			'''p('<a>&#999;</a>',ErrorOnBadCharacterEntities=0)''',
			'''p('<a>&#999;</a>',ErrorOnBadCharacterEntities=1)''',
			'''p('<a>&dud;</a>',ErrorOnUndefinedEntities=0)''',
			'''p('<a>&dud;</a>',ErrorOnUndefinedEntities=1)''',
			'''p('<a>&#109;</a>',ExpandCharacterEntities=1)''',
			'''p('<a>&#109;</a>',ExpandCharacterEntities=0)''',
			'''p('<a>&amp;</a>',ExpandGeneralEntities=0)''',
			'''p('<a>&amp;</a>',ExpandGeneralEntities=1)''',
			'''p('<a>&amp;</a>',IgnoreEntities=0)''',
			'''p('<a>&amp;</a>',IgnoreEntities=1)''',
			'''p('<a><!-- this is a comment --></a>',ReturnComments=1)''',
			'''p('<a><!-- this is a comment --></a>',ReturnComments=0)''',
			'''p('<a>causes an error</b>',SimpleErrorFormat=0)''',
			'''p('<a>causes an error</b>',SimpleErrorFormat=1)''',
			'''p('<a>&amp;</a>',XMLPredefinedEntities=1)''',
			'''p('<a>&amp;</a>',XMLPredefinedEntities=0)''',
			]
	po = 0
	i = 0
	for c in code:
		if type(c) is type(1):
			po=1
		else:
			i += 1
			print '>>> '+c
			if po:
				po = 0
				exec c in globals(), locals()
			else:
				try:
					__x = eval(c)
					print __x
				except:
					traceback.print_exc()
