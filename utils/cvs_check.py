#! /usr/bin/env python
'''
script for testing ReportLab anonymous cvs download and test

12/Feb/2000	RGB Initial Version tested on Win95
'''

_globals=globals().copy()			#make a copy of out globals
_globals['__name__'] = "__main__"	#for passing to execfile

import os, sys, string, traceback

#this is what we need to write to .cvspass for anonymous access
_cvspass=':pserver:anonymous@cvs.reportlab.sourceforge.net:/cvsroot/reportlab A'
_tmp=os.path.normcase(os.path.normpath('/tmp'))
_testdir=os.path.normcase(os.path.normpath('/tmp/reportlab_test'))
_ecount = 0

def get_path():
	for i in os.environ.keys():
		if string.upper(i)=='PATH':
			return string.split(os.environ[i],os.pathsep)
	return []

def find_exe(exe):
	if sys.platform=='win32':
		exe='%s.exe'%exe

	for p in get_path():
		f = os.path.join(p,exe)
		if os.path.isfile(f): return f

	return None

def recursive_rmdir(d):
	'destroy directory d'
	if os.path.isdir(d):
		for p in os.listdir(d):
			fn = os.path.join(d,p)
			if os.path.isfile(fn):
				os.remove(fn)
			else:
				recursive_rmdir(fn)
		os.rmdir(d)

def cvs_checkout():
	recursive_rmdir(_testdir)

	cvs = find_exe('cvs')
	if cvs is None:
		print "Can't find cvs anywhere on the path"
		os.exit(1)

	have_tmp = os.path.isdir(_tmp)
	os.makedirs(_testdir)
	os.environ['HOME']=_testdir
	os.environ['CVSROOT']=':pserver:anonymous@cvs.reportlab.sourceforge.net:/cvsroot/reportlab'
	os.chdir(_testdir)
	f = open(os.path.join(_testdir,'.cvspass'),'w')
	f.write(_cvspass+'\n')
	f.close()
	i=os.popen(cvs+' -z7 -d:pserver:anonymous@cvs.reportlab.sourceforge.net:/cvsroot/reportlab co reportlab','r')
	print i.read()
	i = i.close()
	if i is not None:
		print 'there was an error during the download phase'
		sys.exit(1)

def do_tests():
	global _ecount

	def find_test_files(L,d,N):
		n = os.path.basename(d)
		if n!='test' and n!='tests': return
		for n in filter(lambda n: n[-3:]=='.py',N):
			L.append(os.path.normcase(os.path.normpath(os.path.join(d,n))))

	fn = os.path.normcase(os.path.normpath(os.path.join(_testdir,'reportlab')))
	if fn not in sys.path: sys.path.insert(0,fn)
	test_files = []
	os.path.walk(fn,find_test_files,test_files)
	for t in test_files:
		fn =os.path.normcase(os.path.normpath(os.path.join(_testdir,t)))
		bn = os.path.basename(fn)
		print '##### Test %s starting' % bn
		try:
			os.chdir(os.path.dirname(fn))
			execfile(fn,_globals.copy())
			print '##### Test %s finished ok' % bn
		except:
			traceback.print_exc(None,sys.stdout)
			_ecount = _ecount + 1

if __name__=='__main__':
	legal_options = ['-help','-nocvs','-notest','-clean', '-fclean']
	def usage(code=0, msg=''):
		f = code and sys.stderr or sys.stdout
		if msg is not None: f.write(msg+'\n')
		f.write(\
'''
Usage
	python reportlab_cvs_check.py [options]

	option
	-help	print this message and exit
	-nocvs	don't do cvs checkout
	-notest don't carry out tests
	-clean	cleanup if no errors
	-fclean	cleanup even if some errors occur
''')
		sys.exit(code)

	options = sys.argv[1:]
	for k in options:
		if k not in legal_options:
			usage(code=1,msg="unknown option '%s'" % k)

	if '-help' in options: usage()

	if '-nocvs' not in options:
		cvs_checkout()

	if '-notest' not in options:
		do_tests()

	if (_ecount==0 and '-clean' in options) or '-fclean' in options:
		recursive_rmdir(_testdir)
