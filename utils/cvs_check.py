#!/bin/env python
#copyright ReportLab Inc. 2000
#see license.txt for license details
#history http://cvs.sourceforge.net/cgi-bin/cvsweb.cgi/utils/cvs_check.py?cvsroot=reportlab
#$Header: /tmp/reportlab/utils/cvs_check.py,v 1.7 2000/10/25 08:57:46 rgbecker Exp $
__version__=''' $Id: cvs_check.py,v 1.7 2000/10/25 08:57:46 rgbecker Exp $ '''
'''
script for testing ReportLab anonymous cvs download and test
'''

_globals=globals().copy()			#make a copy of out globals
_globals['__name__'] = "__main__"	#for passing to execfile

import os, sys, string, traceback, re

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

def safe_remove(p):
	if os.path.isfile(p): os.remove(p)

def do_exec(cmd, cmdname):
	i=os.popen(cmd,'r')
	print i.read()
	i = i.close()
	if i is not None:
		print 'there was an error executing '+cmdname
		sys.exit(1)

def cvs_checkout(d):
	recursive_rmdir(d)

	cvs = find_exe('cvs')
	if cvs is None:
		print "Can't find cvs anywhere on the path"
		os.exit(1)

	have_tmp = os.path.isdir(_tmp)
	os.makedirs(d)
	os.environ['HOME']=d
	os.environ['CVSROOT']=':pserver:anonymous@cvs.reportlab.sourceforge.net:/cvsroot/reportlab'
	os.chdir(d)
	f = open(os.path.join(d,'.cvspass'),'w')
	f.write(_cvspass+'\n')
	f.close()
	do_exec(cvs+' -z7 -d:pserver:anonymous@cvs.reportlab.sourceforge.net:/cvsroot/reportlab co reportlab',
		'the download phase')

def do_zip(d):
	'create .tgz and .zip file archives of d/reportlab'
	def find_src_files(L,d,N):
		if os.path.basename(d)=='CVS': return	#ignore all CVS
		for n in N:
			fn = os.path.normcase(os.path.normpath(os.path.join(d,n)))
			if os.path.isfile(fn): L.append(fn)

	os.chdir(d)
	src_files = []
	fn = os.path.normcase(os.path.normpath('reportlab'))
	os.path.walk(fn,find_src_files,src_files)
	tarfile = 'replab'
	safe_remove(tarfile)
	safe_remove('replab.tgz')
	zipfile = 'replab.zip'
	safe_remove(zipfile)
	if src_files==[]: return
	src_files = string.replace(string.join(src_files),'\\','/')

	tar = find_exe('tar')
	do_exec('%s cvf %s %s' % (tar, tarfile, src_files), 'tar creation')
	do_exec('%s -S .tgz %s' % (find_exe('gzip'), tarfile), 'gzip')

	zip = find_exe('zip')
	do_exec('%s -u %s %s' % (zip, zipfile, src_files), 'zip creation' )

def find_py_files(d):
	def _py_files(L,d,N):
 		for n in filter(lambda x: x[-3:]=='.py', N):
			fn = os.path.normcase(os.path.normpath(os.path.join(d,n)))
			if os.path.isfile(fn): L.append(fn)
	L=[]
	os.path.walk(d,_py_files,L)
	return L

def find_executable_py_files(d):
	prog=re.compile('^( |\t)*if( |\t)+__name__( |\t)*==( |\t)*(\'|\")__main__(\'|\")( |\t)*:')
	L=[]
	for n in find_py_files(d):
		for l in open(n,'r').readlines():
			if prog.match(l) is not None:
				L.append(n)
				break
	return L

def do_tests(d):
	global _ecount

	def find_test_files(L,d,N):
		n = os.path.basename(d)
		if n!='test' : return
		for n in filter(lambda n: n[-3:]=='.py',N):
			fn = os.path.normcase(os.path.normpath(os.path.join(d,n)))
			if os.path.isfile(fn): L.append(fn)

	fn = os.path.normcase(os.path.normpath(os.path.join(d,'reportlab')))		
	d = os.path.normcase(os.path.normpath(d))
	if d not in sys.path: sys.path.insert(0,d)
	test_files = []
	os.path.walk(fn,find_test_files,test_files)
	for t in find_executable_py_files(fn):
		if t not in test_files:
			test_files.append(t)

	for t in test_files:
		fn =os.path.normcase(os.path.normpath(os.path.join(d,t)))
		bn = os.path.basename(fn)
		print '##### Test %s starting' % bn
		try:
			os.chdir(os.path.dirname(fn))
			execfile(fn,_globals.copy())
			print '##### Test %s finished ok' % bn
		except:
			traceback.print_exc(None,sys.stdout)
			_ecount = _ecount + 1

if __name__=='__main__': #NORUNTESTS
	legal_options = ['-dir', '-help','-nocvs','-notest','-clean', '-fclean', '-zip' ]
	def usage(code=0, msg=''):
		f = code and sys.stderr or sys.stdout
		if msg is not None: f.write(msg+'\n')
		f.write(\
'''
Usage
	python reportlab_cvs_check.py [options]

	option
	-help		print this message and exit
	-dir path	specify directory to test implies -nocvs
	-nocvs		don't do cvs checkout
	-notest 	don't carry out tests
	-clean		cleanup if no errors
	-fclean		cleanup even if some errors occur
	-zip		create tgz and zip files after cvs stage
''')
		sys.exit(code)

	dir=_testdir
	dflag = 0
	options = sys.argv[1:]
	sys.argv[1:]=[]
	for k in options:
		if k not in legal_options:
			if dflag:
				dir = k
				dflag = 0
			else:
				usage(code=1,msg="unknown option '%s'" % k)
		else:
			dflag = k=='-dir'

	if '-help' in options: usage()

	if '-nocvs' not in options and dir is _testdir:
		cvs_checkout(dir)

	if '-zip' in options:
		do_zip(dir)

	if '-notest' not in options:
		do_tests(dir)

	if dir is _testdir and ((_ecount==0 and '-clean' in options) or '-fclean' in options):
		recursive_rmdir(dir)
