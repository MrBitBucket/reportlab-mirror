#!/bin/env python
###############################################################################
#
#	ReportLab Public License Version 1.0
#
#   Except for the change of names the spirit and intention of this
#   license is the same as that of Python
#
#	(C) Copyright ReportLab Inc. 1998-2000.
#
#
# All Rights Reserved
#
# Permission to use, copy, modify, and distribute this software and its
# documentation for any purpose and without fee is hereby granted, provided
# that the above copyright notice appear in all copies and that both that
# copyright notice and this permission notice appear in supporting
# documentation, and that the name of ReportLab not be used
# in advertising or publicity pertaining to distribution of the software
# without specific, written prior permission. 
# 
#
# Disclaimer
#
# ReportLab Inc. DISCLAIMS ALL WARRANTIES WITH REGARD TO THIS
# SOFTWARE, INCLUDING ALL IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS,
# IN NO EVENT SHALL ReportLab BE LIABLE FOR ANY SPECIAL, INDIRECT
# OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES WHATSOEVER RESULTING FROM LOSS
# OF USE, DATA OR PROFITS, WHETHER IN AN ACTION OF CONTRACT, NEGLIGENCE OR
# OTHER TORTIOUS ACTION, ARISING OUT OF OR IN CONNECTION WITH THE USE OR
# PERFORMANCE OF THIS SOFTWARE. 
#
###############################################################################
#	$Log: cvs_check.py,v $
#	Revision 1.2  2000/02/15 17:57:39  rgbecker
#	License files added
#
__version__=''' $Id: cvs_check.py,v 1.2 2000/02/15 17:57:39 rgbecker Exp $ '''
'''
script for testing ReportLab anonymous cvs download and test
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

def cvs_checkout(d,u):
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
	i=os.popen(cvs+' -z7 -d:pserver:anonymous@cvs.reportlab.sourceforge.net:/cvsroot/reportlab co reportlab','r')
	print i.read()
	i = i.close()
	if i is not None:
		print 'there was an error during the download phase'
		sys.exit(1)

def do_tests(d):
	global _ecount

	def find_test_files(L,d,N):
		n = os.path.basename(d)
		if n!='test' and n!='tests': return
		for n in filter(lambda n: n[-3:]=='.py',N):
			L.append(os.path.normcase(os.path.normpath(os.path.join(d,n))))

	fn = os.path.normcase(os.path.normpath(os.path.join(d,'reportlab')))
	if fn not in sys.path: sys.path.insert(0,fn)
	test_files = []
	os.path.walk(fn,find_test_files,test_files)
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

if __name__=='__main__':
	legal_options = ['-dir', '-help','-nocvs','-notest','-clean', '-fclean']
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

	if '-notest' not in options:
		do_tests(dir)

	if dir is _testdir and ((_ecount==0 and '-clean' in options) or '-fclean' in options):
		recursive_rmdir(dir)
