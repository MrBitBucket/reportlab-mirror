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
#	$Log: daily.py,v $
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
__version__=''' $Id: daily.py,v 1.8 2000/04/06 12:57:38 rgbecker Exp $ '''
'''
script for creating daily cvs archive dump
'''
import os, sys, string, traceback, re

#this is where we extract files etc
groupdir=os.path.normcase(os.path.normpath('/home/groups/ftp/pub/reportlab'))
projdir = os.path.normcase(os.path.normpath('reportlab'))
cvsdir = os.path.join(groupdir,projdir)
release=0		#1 if making a release
USER=os.environ['USER']

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
	os.chdir(d)
	recursive_rmdir(cvsdir)

	cvs = find_exe('cvs')
	if cvs is None:
		print "Can't find cvs anywhere on the path"
		os.exit(1)

	if release:
		print release, USER
		os.environ['CVSROOT']=':ext:%s@cvs1:/cvsroot/reportlab' % USER
		#do_exec(cvs+(' rtag %s' % release), 'the tag phase')
		do_exec(cvs+(' co -r %s reportlab'%release), 'the download phase')
	else:
		os.environ['CVSROOT']=':pserver:%s@cvs1:/cvsroot/reportlab' % USER
		do_exec(cvs+' co reportlab', 'the download phase')

def do_zip(d):
	'create .tgz and .zip file archives of d/reportlab'
	def find_src_files(L,d,N):
		if string.upper(os.path.basename(d))=='CVS': return	#ignore all CVS
		for n in N:
			fn = os.path.normcase(os.path.normpath(os.path.join(d,n)))
			if os.path.isfile(fn): L.append(fn)

	os.chdir(d)
	src_files = []
	os.path.walk(projdir,find_src_files,src_files)
	if release:
		b = "reportlab_%4d%02d%02d" %time.gmtime(time.time())[:3]
	else:
		b = "current"

	tarfile = '%s/%s.tgz' % (groupdir,b)
	zipfile = '%s/%s.zip' % (groupdir,b)
	safe_remove(zipfile)
	safe_remove(tarfile)
	if src_files==[]: return
	src_files = string.join(src_files)

	tar = find_exe('tar')
	do_exec('%s czvf %s %s' % (tar, tarfile, src_files), 'tar creation')

	zip = find_exe('zip')
	do_exec('%s -u %s %s' % (zip, zipfile, src_files), 'zip creation')
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
	release = '-release' in sys.argv[1:]
	if release:
		if len(sys.argv)!=3 or sys.argv[1]!='-release':
			print 'Usage:\n    python daily.py [-release tag]'
			sys.exit(1)
		release=sys.argv[2]
	cvs_checkout(groupdir)
	do_zip(groupdir)
