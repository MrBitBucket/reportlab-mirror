#!/usr/local/bin/python
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
#	$Log: daily.py,v $
#	Revision 1.36  2000/06/20 13:49:29  rgbecker
#	Added pyc_remove
#
#	Revision 1.35  2000/06/20 13:41:25  rgbecker
#	Fixed miss assign to opp
#	
#	Revision 1.34  2000/06/20 11:50:36  rgbecker
#	Fix htmldir moves (ie copy)
#	
#	Revision 1.33  2000/06/20 11:43:51  rgbecker
#	Chanded do_exec, added htmldir moves etc
#	
#	Revision 1.32  2000/06/20 09:15:50  rgbecker
#	Use python path in docs creation
#	
#	Revision 1.31  2000/06/19 15:55:41  rgbecker
#	Fixing up docs generation
#	
#	Revision 1.30  2000/05/17 15:39:10  rgbecker
#	Changes related to removal of SimpleFlowDocument
#	
#	Revision 1.29  2000/04/26 12:57:38  rgbecker
#	-py2pdf chmod commands added
#	
#	Revision 1.28  2000/04/21 13:22:17  rgbecker
#	Remove pdfgen/test in py2pdf mode
#	
#	Revision 1.27  2000/04/20 10:51:07  rgbecker
#	Added mv idle_print.py
#	
#	Revision 1.26  2000/04/20 08:39:59  rgbecker
#	Made cvsdir local everywhere
#	
#	Revision 1.25  2000/04/20 08:21:12  rgbecker
#	Fixes to projdir usage
#	
#	Revision 1.24  2000/04/19 15:16:13  rgbecker
#	os.path.isdir not os.isdir
#	
#	Revision 1.23  2000/04/19 15:14:33  rgbecker
#	os.path.split not os.split
#	
#	Revision 1.22  2000/04/19 15:11:58  rgbecker
#	Fixed do_exec call
#	
#	Revision 1.21  2000/04/19 15:07:34  rgbecker
#	Syntax error fix
#	
#	Revision 1.20  2000/04/19 15:06:28  rgbecker
#	Added py2pdf_dir
#	
#	Revision 1.19  2000/04/19 15:00:32  rgbecker
#	pyfontify-->PyFontify
#	
#	Revision 1.18  2000/04/19 14:56:07  rgbecker
#	Added CVS_remove
#	
#	Revision 1.17  2000/04/19 14:35:04  rgbecker
#	Used -D for py2pdf export
#	
#	Revision 1.16  2000/04/19 14:26:13  rgbecker
#	Added tagname
#	
#	Revision 1.15  2000/04/19 14:16:07  rgbecker
#	Got rid of userArgs
#	
#	Revision 1.14  2000/04/19 14:08:47  rgbecker
#	py2pdf additions
#	
#	Revision 1.13  2000/04/07 09:58:10  rgbecker
#	Fixed missing programs problems
#	
#	Revision 1.12  2000/04/06 14:10:10  rgbecker
#	Made anonymous
#	
#	Revision 1.11  2000/04/06 14:08:00  rgbecker
#	Changed release naming convention
#	
#	Revision 1.10  2000/04/06 13:01:58  rgbecker
#	Added import of time
#	
#	Revision 1.9  2000/04/06 12:59:48  rgbecker
#	ext-->pserver for release
#	
#	Revision 1.8  2000/04/06 12:57:38  rgbecker
#	Print user
#	
#	Revision 1.7  2000/04/06 12:54:29  rgbecker
#	Removed rtag again.
#	
#	Revision 1.6  2000/04/06 12:50:11  rgbecker
#	Fixed user and rtag
#	
#	Revision 1.5  2000/04/06 12:42:33  rgbecker
#	removed attempt at tagging
#	
#	Revision 1.4  2000/03/28 13:58:26  rgbecker
#	Add -r tag for release
#	
#	Revision 1.3  2000/03/28 13:40:32  rgbecker
#	Fix server for release
#	
#	Revision 1.2  2000/03/28 13:34:26  rgbecker
#	Fixed to release mechanism len()?
#	
#	Revision 1.1  2000/02/23 13:16:56  rgbecker
#	New infrastructure
#	
__version__=''' $Id: daily.py,v 1.36 2000/06/20 13:49:29 rgbecker Exp $ '''
'''
script for creating daily cvs archive dump
'''
import os, sys, string, traceback, re

#this is where we extract files etc
groupdir=os.path.normcase(os.path.normpath('%s/public_ftp'%os.environ['HOME']))
htmldir=os.path.normcase(os.path.normpath('%s/public_html'%os.environ['HOME']))
projdir = 'reportlab'
py2pdf_dir = 'py2pdf'
release=0		#1 if making a release
py2pdf=0		#1 if doing a special py2pdf zip/tgz
#USER=os.environ['USER']
USER='anonymous'

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

	print "Can't find %s anywhere on the path" % exe
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

def pyc_remove(d):
	'remove .pyc & .pyo files in d and subtree'
	if os.path.isdir(d):
		for p in os.listdir(d):
			fn = os.path.join(d,p)
			if os.path.isfile(fn) and fn[-4:] in ['.pyc','.pyo']:
				os.remove(fn)
			else:
				pyc_remove(fn)

def CVS_remove(d):
	'destroy CVS subdirs'
	if os.path.isdir(d):
		if os.path.split(d)[1]=='CVS':
			recursive_rmdir(d)
		for p in os.listdir(d):
			fn = os.path.join(d,p)
			if os.path.isdir(fn):
				if p=='CVS':
					recursive_rmdir(fn)
				else:
					CVS_remove(fn)

def safe_remove(p):
	if os.path.isfile(p): os.remove(p)

def do_exec(cmd, cmdname=None):
	i=os.popen(cmd,'r')
	print i.read()
	i = i.close()
	if i is not None:
		if cmdname is not None:
			print 'Error: %s '+ cmdname or cmd
		sys.exit(1)

def cvs_checkout(d):
	os.chdir(d)
	cvsdir = os.path.join(d,projdir)
	recursive_rmdir(cvsdir)
	recursive_rmdir('docs')

	cvs = find_exe('cvs')
	python = find_exe('python')
	if cvs is None:
		os.exit(1)

	os.environ['CVSROOT']=':pserver:%s@cvs.reportlab.sourceforge.net:/cvsroot/reportlab' % USER
	if release:
		do_exec(cvs+(' export -r %s %s' % (tagname,projdir)), 'the export phase')
	else:
		do_exec(cvs+' co %s' % projdir, 'the checkout phase')
		if py2pdf:
			# now we need to move the files & delete those we don't need
			dst = py2pdf_dir
			recursive_rmdir(dst)
			os.mkdir(dst)
			do_exec("mv reportlab/demos/py2pdf/py2pdf.py %s"%dst)
			do_exec("mv reportlab/demos/py2pdf/PyFontify.py %s" % dst)
			do_exec("mv reportlab/demos/py2pdf/idle_print.py %s" % dst)
			do_exec("rm -r reportlab/demos reportlab/platypus reportlab/lib/styles.py reportlab/README.pdfgen.txt reportlab/pdfgen/test", "reducing size")
			do_exec("mv %s %s" % (projdir,dst))
			do_exec("chmod a+x %s/py2pdf.py %s/idle_print.py" % (dst, dst))
			CVS_remove(dst)
		else:
			do_exec(cvs+' co docs')
			dst = os.path.join(d,"reportlab","docs")
			do_exec("mkdir %s" % dst)

			#add our reportlab parent to the path so we import from there
			if os.environ.has_key('PYTHONPATH'):
				opp = os.environ['PYTHONPATH']
				os.environ['PYTHONPATH']='%s:%s' % (d,opp)
			else:
				opp = None
				os.environ['PYTHONPATH']=d

			os.chdir('docs/reference')
			do_exec(python + ' ../tools/yaml2pdf.py reference.yml')
			os.chdir(d)
			do_exec('cp docs/reference/*.pdf %s' % htmldir)
			do_exec('mv docs/reference/*.pdf %s' % dst)
			os.chdir('docs/userguide')
			do_exec(python + ' genuserguide.py')
			os.chdir(d)
			do_exec('cp docs/userguide/*.pdf %s' % htmldir)
			do_exec('mv docs/userguide/*.pdf %s' % dst)
			recursive_rmdir('docs')
			pyc_remove(cvsdir)

			#restore the python path
			if opp is None:
				del os.environ['PYTHONPATH']
			else:
				os.environ['PYTHONPATH'] = opp

def do_zip(d):
	'create .tgz and .zip file archives of d/reportlab'

	os.chdir(d)
	if release:
		b = tagname
	else:
		b = py2pdf and "py2pdf" or "current"

	tarfile = '%s/%s.tgz' % (groupdir,b)
	zipfile = '%s/%s.zip' % (groupdir,b)

	if py2pdf:
		pdir = py2pdf_dir
	else:
		pdir = projdir

	cvsdir = os.path.join(groupdir,pdir)

	tar = find_exe('tar')
	if tar is not None:
		safe_remove(tarfile)
		do_exec('%s czvf %s %s' % (tar, tarfile, pdir))

	zip = find_exe('zip')
	if zip is not None:
		safe_remove(zipfile)
		do_exec('%s -ur %s %s' % (zip, zipfile, pdir))
	recursive_rmdir(cvsdir)

	if release:
		# make links to the latest outcome
		for b in ['reportlab','current']:
			ltarfile = '%s/%s.tgz' % (groupdir,b)
			lzipfile = '%s/%s.zip' % (groupdir,b)
			safe_remove(lzipfile)
			safe_remove(ltarfile)
			os.symlink(zipfile,lzipfile)
			os.symlink(tarfile,ltarfile)

if __name__=='__main__': #NORUNTESTS
	def Usage(msg=None):
		if msg is not None: print msg
		print 'Usage:\n    python daily.py [-release tag] | [-py2pdf]'
		sys.exit(1)
	release = '-release' in sys.argv[1:]
	py2pdf = '-py2pdf' in sys.argv[1:]
	if release:
		if py2pdf:
			Usage("Can't have -release and -py2pdf options")
		if len(sys.argv)!=3 or sys.argv[1] != '-release':
			Usage()
		tagname=sys.argv[2]
	cvs_checkout(groupdir)
	do_zip(groupdir)
	if release:
		release = None
		cvs_checkout(groupdir)
		do_zip(groupdir)
