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
__version__=''' $Id: daily.py,v 1.16 2000/04/19 14:26:13 rgbecker Exp $ '''
'''
script for creating daily cvs archive dump
'''
import os, sys, string, traceback, re

#this is where we extract files etc
groupdir=os.path.normcase(os.path.normpath('%s/public_ftp'%os.environ['HOME']))
projdir = os.path.normcase(os.path.normpath('reportlab'))
cvsdir = os.path.join(groupdir,projdir)
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
	os.chdir(d)
	recursive_rmdir(cvsdir)

	cvs = find_exe('cvs')
	if cvs is None:
		os.exit(1)

	os.environ['CVSROOT']=':pserver:%s@cvs.reportlab.sourceforge.net:/cvsroot/reportlab' % USER
	if release:
		do_exec(cvs+(' export -r %s reportlab' % tagname), 'the export phase')
	else:
		if py2pdf:
			do_exec(cvs+(' export -r %s reportlab' % tagname), 'the checkout phase')
			# now we need to move the files & delete those we don't need
			os.mkdir("py2pdf")
			do_exec("mv reportlab/demos/py2pdf/py2pdf.py py2pdf", "mv py2pdf.py")
			do_exec("mv reportlab/demos/py2pdf/pyfontify.py reportlab", "mv pyfontify.py")
			do_exec("rm -r reportlab/demos reportlab/platypus reportlab/lib/styles.py reportlab/README.pdfgen.txt", "rm")
			do_exec("mv reportlab py2pdf")
		else:
			do_exec(cvs+' co reportlab', 'the checkout phase')

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
		projdir = 'py2pdf'
		cvsdir = os.path.join(groupdir,projdir)

	tar = find_exe('tar')
	if tar is not None:
		safe_remove(tarfile)
		do_exec('%s czvf %s %s' % (tar, tarfile, projdir), 'tar creation')

	zip = find_exe('zip')
	if zip is not None:
		safe_remove(zipfile)
		do_exec('%s -ur %s %s' % (zip, zipfile, projdir), 'zip creation')
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

if __name__=='__main__':
	def Usage(msg=None):
		if msg is not None:
			print msg
		print 'Usage:\n    python daily.py [-release tag] | [-py2pdf tag]'
		sys.exit(1)
	release = '-release' in sys.argv[1:]
	py2pdf = '-py2pdf' in sys.argv[1:]
	if release or py2pdf:
		if py2pdf and release:
			Usage("Can't have -release and -py2pdf options")
		if len(sys.argv)!=3 or sys.argv[1] not in ['-release','-py2pdf']:
			Usage()
		tagname=sys.argv[2]
	cvs_checkout(groupdir)
	do_zip(groupdir)
	if release:
		release = None
		cvs_checkout(groupdir)
		do_zip(groupdir)
