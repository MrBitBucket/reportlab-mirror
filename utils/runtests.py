#!/usr/bin/env python
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
#	$Log: runtests.py,v $
#	Revision 1.12  2000/07/19 13:44:54  rgbecker
#	Added -prof option
#
#	Revision 1.11  2000/05/17 15:39:10  rgbecker
#	Changes related to removal of SimpleFlowDocument
#	
#	Revision 1.10  2000/05/11 09:54:43  rgbecker
#	Fixed dir argument handling
#	
#	Revision 1.9  2000/04/12 13:34:33  rgbecker
#	Fixes to exception handling
#	
#	Revision 1.8  2000/04/11 10:45:56  rgbecker
#	CLEAN_EXCEPTIONS & sys.argv[0] setting
#	
#	Revision 1.7  2000/04/07 09:21:29  rgbecker
#	Fixed import bug
#	
#	Revision 1.6  2000/04/06 15:08:53  rgbecker
#	Changes to way dir is handled
#	
#	Revision 1.5  2000/04/03 09:29:36  rgbecker
#	Eliminated -dir option
#	
#	Revision 1.4  2000/03/02 12:22:28  rgbecker
#	Added recognition comment checks
#	
#	Revision 1.3  2000/03/02 10:43:37  rgbecker
#	Fixed problem with -dir relativepath
#	
#	Revision 1.2  2000/02/23 15:08:23  rgbecker
#	Fixed clean_files
#	
#	Revision 1.1  2000/02/23 13:16:56  rgbecker
#	New infrastructure
#	
#	
__version__=''' $Id: runtests.py,v 1.12 2000/07/19 13:44:54 rgbecker Exp $ '''
'''
script for testing ReportLab
'''

_globals=globals().copy()				#make a copy of out globals
_globals['__name__'] = "__main__"	#for passing to execfile

import os, sys, string, traceback, re, copy

#if a file matches this it won't be cleaned
CLEAN_EXCEPTIONS=['demos/pythonpoint/leftlogo.a85', 'demos/pythonpoint/spectrum.png']

_ecount = 0	# count of errors

def makeabs(dir):
	if not os.path.isabs(dir): #abspath not available under 1.5.1
		dir = os.path.join(os.getcwd(),dir)
	return os.path.normcase(os.path.normpath(dir))

def find_py_files(d):
	def _py_files(L,d,N):
		for n in filter(lambda x: x[-3:]=='.py', N):
			fn = os.path.normcase(os.path.normpath(os.path.join(d,n)))
			if os.path.isfile(fn): L.append(fn)
	L=[]
	os.path.walk(d,_py_files,L)
	return L

def find_executable_py_files(d):
	prog=re.compile('^((( |\t)*if( |\t)+__name__( |\t)*==( |\t)*(\'|\")__main__(\'|\")( |\t)*:)|#REPORTLAB_TEST_SCRIPT)( |\t)*$')
	L=[]
	for n in find_py_files(d):
		for l in open(n,'r').readlines():
			if prog.match(l) is not None:
				L.append(n)
				break
	return L

def do_tests(d,cyc,prof):
	global _ecount

	def find_test_files(L,d,N):
		n = os.path.basename(d)
		if n!='test' : return
		for n in filter(lambda n: n[-3:]=='.py',N):
			fn = os.path.normcase(os.path.normpath(os.path.join(d,n)))
			if os.path.isfile(fn): L.append(fn)

	if cyc is not None: import Cyclops
	elif prof is not None:
		import profile, pstats
	os.chdir(d)
	test_files = []
	os.path.walk('.',find_test_files,test_files)
	for t in find_executable_py_files('.'):
		if t not in test_files:
			test_files.append(t)

	oldArgv0 =sys.argv[0]
	for t in test_files:
		fn =os.path.normcase(os.path.normpath(os.path.join(d,t)))
		bn = os.path.basename(fn)
		print '##### Test %s starting' % bn
		dn = os.path.dirname(fn)
		sys.path.insert(0,dn)
		sys.argv[0] = fn
		os.chdir(os.path.dirname(fn))
		g = copy.copy(_globals)
		try:
			if cyc is not None:
				z = Cyclops.CycleFinder()
				z.run(execfile,(fn,g))
				if z.find_cycles():
					print '!!!!!! CYCLES WERE FOUND !!!!!!'
					if 's' in cyc: z.show_stats()
					if 'c' in cyc: z.show_cycles()
					if 'o' in cyc: z.show_cycleobjs()
					if 'C' in cyc: z.show_sccs()
					if 'a' in cyc: z.show_arcs()
				else:
					print '!!!!!! NO CYCLES WERE FOUND !!!!!!'
					if 's' in cyc: z.show_stats()
			elif prof is not None:
				p = profile.Profile()
				p.runctx("execfile(\"%s\")" % bn, g, g)
				s = pstats.Stats(p)
				if 't' in prof[0]: s.sort_stats('time').print_stats(prof[1])
				if 'c' in prof[0]: s.sort_stats('cumulative').print_stats(prof[1])
			else:
				execfile(fn,g)
			print '##### Test %s finished ok' % bn
		except:
			traceback.print_exc(None,sys.stdout)
			_ecount = _ecount + 1
		del sys.path[0]
	sys.argv[0] = oldArgv0

def is_exceptional(fn,exceptions):
	for x in exceptions:
		xfn = os.path.normcase(os.path.normpath(x))
		if makeabs(fn)[-len(xfn):]==xfn: return 1
	return 0

def clean_files(d):
	def find_cleanable_files(L,d,N):
		n = os.path.basename(d)
		for n in filter(lambda n: n[-4:] in ['.PYC','.PDF','.A85','.PNG','.IMG'],map(string.upper,N)):
			fn = os.path.normcase(os.path.normpath(os.path.join(d,n)))
			if os.path.isfile(fn) and not is_exceptional(fn,CLEAN_EXCEPTIONS):
				os.remove(fn)
	os.chdir(d)
	os.path.walk('.',find_cleanable_files,None)

if __name__=='__main__': #NORUNTESTS
	legal_options = ['-cycles', '-dir', '-help','-notest','-clean', '-fclean', '-prof']
	def usage(code=0, msg=''):
		f = code and sys.stderr or sys.stdout
		if msg is not None: f.write(msg+'\n')
		f.write(\
'''
Usage
    python runtests.py [dir] [options]

    option
    dir             directory to test default .
    -help           print this message and exit
    -cycles[=flags] check for cycles using Tim Peter's Cyclops cycle finder
                    flags=s(tats), a(rcs), C(omponents), c(ycles), o(bjects)
	-prof[=flags]	do profiling flags=c(umulative), t(ime)
    -notest         don't carry out tests
    -clean          cleanup if no errors
    -fclean         cleanup even if some errors occur
''')
		sys.exit(code)

	dir='.'
	cyc = prof = None
	options = sys.argv[1:]
	sys.argv[1:]=[]

	if options!=[] and options[0][0]!='-':
		dir = options[0]
		del options[0]

	for k in options:
		if '=' in k:
			i, cyc = string.split(k,'=')
			if i=='-cycles':
				k = i
				for i in cyc:
					if i not in 'scCao':
						usage(code=1,msg="Bad cycles option '%s'"%i)
			elif i=='-prof':
				k = i
				if ':' in cyc:
					prof=string.split(cyc,':')
				else:
					try:
						prof = ['t',int(cyc)]
					except:
						prof = [cyc,10]
				try:
					prof[1] = int(prof[1])
					if prof[1]<=0: raise ValueError
				except:
					usage(code=1,msg="Bad profile count '%s'"%prof[1])
				cyc = None
				if prof[0]=='':
					prof[0]='t'
				else:
					for i in prof[0]:
						if i not in 'ct':
							usage(code=1,msg="Bad profile option '%s'"%i)
		elif k=='-cycles': cyc = 'sc'
		elif k=='-prof': prof = ['t', 10]
		if k not in legal_options:
			usage(code=1,msg="unknown option '%s'" % k)

	dir = makeabs(dir)
	if not os.path.isdir(dir):
		usage(code=1,msg="Invalid directory '%s'"%dir)

	if '-help' in options: usage()

	if '-notest' not in options:
		do_tests(dir, cyc, prof)

	if ((_ecount==0 and '-clean' in options) or '-fclean' in options):
		clean_files(dir)
