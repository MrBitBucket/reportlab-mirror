#!/usr/local/bin/python
#copyright ReportLab Inc. 2000
#see license.txt for license details
#history http://cvs.sourceforge.net/cgi-bin/cvsweb.cgi/utils/daily.py?cvsroot=reportlab
#$Header: /tmp/reportlab/utils/daily.py,v 1.50 2001/12/07 11:27:58 rgbecker Exp $
__version__=''' $Id: daily.py,v 1.50 2001/12/07 11:27:58 rgbecker Exp $ '''
'''
script for creating daily cvs archive dump
'''
import os, sys, string, traceback, re, glob, shutil

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
			rmdir(d)
		for p in os.listdir(d):
			fn = os.path.join(d,p)
			if os.path.isdir(fn):
				if p=='CVS':
					rmdir(fn)
				else:
					CVS_remove(fn)

def rmdir(d):
	'destroy directory d'
	if os.path.isdir(d):
		for p in os.listdir(d):
			fn = os.path.join(d,p)
			if os.path.isdir(fn):
				rmdir(fn)
			else:
				remove(fn)
		os.rmdir(d)

def remove(f):
	'remove an existing file'
	if os.path.isfile(f): os.remove(f)

def kill(f):
	'remove directory or file unconditionally'
	if os.path.isfile(f): os.remove(f)
	elif os.path.isdir(f): rmdir(f)
	elif '*' in f: map(kill,glob.glob(f))

def rename(src,dst):
	remove(dst)
	try:
		os.rename(src,dst)
	except:
		pass

def move(src,dst):
	if os.path.isdir(dst): dst = os.path.join(dst,os.path.basename(src))
	rename(src,dst)

def copy(src,dst):
	if os.path.isdir(dst): dst = os.path.join(dst,os.path.basename(src))
	if os.path.isfile(dst): kill(dst)
	if os.path.isfile(src): shutil.copy2(src,dst)
	elif os.path.isdir(src): shutil.copyTree(src,dst)
	elif '*' in src: map(lambda f,dst=dst: copy(f,dst),glob.glob(src))

def do_exec(cmd, cmdname=None):
	i=os.popen(cmd,'r')
	print i.read()
	i = i.close()
	if i is not None:
		if cmdname is not None:
			print 'Error: '+ (cmdname or cmd)
		sys.exit(1)

def genAll(f='genAll.py'):
	execfile(f,locals())
	return eval('_genAll')

def cvs_checkout(d):
	os.chdir(d)
	cvsdir = os.path.join(d,projdir)
	rmdir(cvsdir)
	rmdir('docs')

	cvs = find_exe('cvs')
	python = find_exe('python')
	if cvs is None:
		os.exit(1)

	os.environ['CVSROOT']=':pserver:%s@cvs.reportlab.sourceforge.net:/cvsroot/reportlab' % USER
	if release:
		do_exec(cvs+(' export -r %s %s' % (tagname,projdir)), 'the export phase')
	else:
		do_exec(cvs+' co -P %s' % projdir, 'the checkout phase')

	if py2pdf:
		# now we need to move the files & delete those we don't need
		dst = py2pdf_dir
		rmdir(dst)
		os.mkdir(dst)
		for f in ("py2pdf.py", "PyFontify.py", "idle_print.py"):
			move(os.path.join('reportlab/demos/py2pdf',f),dst)
		for f in ('reportlab/demos', 'reportlab/platypus', 'reportlab/lib/styles.py', 'reportlab/README.pdfgen.txt', 'reportlab/pdfgen/test', 'reportlab/tools','reportlab/test', 'reportlab/docs'):
			kill(f)
		move(projdir,dst)
		for f in ('py2pdf.py','idle_print.py'): os.chmod(os.path.join(dst,f),0775)	#rwxrwxr-x
		CVS_remove(dst)
	else:
		dst = os.path.join(d,"reportlab","docs")
		PP = "%s" % (d,)
		#add our reportlab parent to the path so we import from there
		if os.environ.has_key('PYTHONPATH'):
			opp = os.environ['PYTHONPATH']
			os.environ['PYTHONPATH']='%s:%s' % (PP,opp)
		else:
			opp = None
			os.environ['PYTHONPATH']=PP
		if '-pythonpath' in sys.argv:
			print 'PYTHONPATH=%s'%os.environ['PYTHONPATH']

		os.chdir(dst)
		try:
			# this creates PDFs in each manual's directory, and copies them to reportlab/docs
			genAll()(quiet='-s')
			# we copy them out to our html area
			copy(os.path.join(dst,'*.pdf'),htmldir)
			# and then delete them
			for f in ('*.pdf', 'userguide/*.pdf', 'graphguide/*.pdf' 'reference/*.pdf'): kill(f)
		except:
			print '????????????????????????????????'
			print 'Failed to run genAll.py, cwd=%s' % os.getcwd()
			do_exec('ls -l')
			print '????????????????????????????????'
		os.chdir(d)
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
		remove(tarfile)
		do_exec('%s czvf %s %s' % (tar, tarfile, pdir))

	zip = find_exe('zip')
	if zip is not None:
		remove(zipfile)
		do_exec('%s -ur %s %s' % (zip, zipfile, pdir))
	rmdir(cvsdir)

	if release:
		# make links to the latest outcome
		for b in ['reportlab','current']:
			ltarfile = '%s/%s.tgz' % (groupdir,b)
			lzipfile = '%s/%s.zip' % (groupdir,b)
			remove(lzipfile)
			remove(ltarfile)
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
