# Simple script to check the #history line in cvs files
# single argument mode an or of 
INDICATE_MISSING=1
CHK_HISTORY_REF=2
FIX_HISTORY_REF=4
# We descend the working copy from here down looking for files
# referred to in CVS/Entries. These are checked for the following
# lines. And the #history line is fixed up so that it points to the
# relevant http:// thing; currently knows about cvs on SF and reportlab.co.uk
#copyright ReportLab Inc. 2000
#see license.txt for license details
#history http://cvs.sourceforge.net/cgi-bin/cvsweb.cgi/utils/copyrite.py?cvsroot=reportlab
#$Header: /tmp/reportlab/utils/copyrite.py,v 1.1 2000/10/24 13:56:02 rgbecker Exp $
import string, os, sys
INDICATE_MISSING=1
CHK_HISTORY_REF=2
FIX_HISTORY_REF=4

def fileEntries(E):
	R = []
	for e in E:
		if e[0]!='/': continue
		i = string.find(e[1:],'/')
		if i>=0: R.append(e[1:i+1])
	return R

def visit( arg, dirname, names):
	if 'CVS' in names:
		del names[names.index('CVS')]
		Repository = string.strip(open(os.path.join(dirname,'CVS','Repository'),'r').readlines()[0])
		for e in fileEntries(open(os.path.join(dirname,'CVS','Entries'),'r').readlines()):
			if e in names:
				arg.append((Repository,dirname,e))

def findCopyright(r,d,e, mode=0):
	fn = os.path.join(d,e)
	L = open(fn,'r').readlines()
	i = 0
	j = None
	while i<len(L)-2:
		l = L[i]
		if string.find(l,'#copyright ReportLab Inc.')==0 and string.find(L[i+2],'#history')==0:
			j = i + 2
			break
		i = i+1

	if not j:
		if mode & INDICATE_MISSING:
			print "Can't find licence marker in %s" % fn
		return

	if e=='copyr.txt' or not (mode & (CHK_HISTORY_REF|FIX_HISTORY_REF)): return

	if string.find(r,'/cvsroot/reportlab')==0:
		refn = '#history http://cvs.sourceforge.net/cgi-bin/cvsweb.cgi/%s/%s?cvsroot=reportlab'%(string.join(string.split(r,'/')[3:],'/'),e)
	elif string.find(r,'/rl_home/repository')==0:
		refn = '#history www.reportlab.co.uk/rl-cgi/viewcvs.cgi/%s/%s'%(string.join(string.split(r,'/')[3:],'/'),e)
	else:
		print "Don't know about repository:%s"%r
		return
	refnn = refn+'\n'

	if (mode & FIX_HISTORY_REF) and L[j]!=refnn:
		print "Fix %s" % refn
		L[j] = refnn
		f = open(fn,'w')
		for l in L:
			f.write(l)
	elif (mode & CHK_HISTORY_REF) and L[j]!=refnn:
		print "Bad %s" % refn

if __name__=='__main__':
	mode = 1
	if len(sys.argv)>1: mode = int(sys.argv[1])
	L = []
	os.path.walk('.',visit,L)
	for r,d,e in L:
		findCopyright(r,d,e,mode)
