#copyright ReportLab Inc. 2000-2001
#see license.txt for license details
#history http://cvs.sourceforge.net/cgi-bin/cvsweb.cgi/reportlab/rl_config.py?cvsroot=reportlab
#$Header: /tmp/reportlab/reportlab/rl_config.py,v 1.17 2001/08/22 12:14:55 rgbecker Exp $
import os, sys, string
from reportlab.lib import pagesizes

def _setOpt(name, value, conv=None):
	'''set a module level value from environ/default'''
	from os import environ
	ename = 'RL_'+name
	if environ.has_key(ename):
		value = environ[ename]
	if conv: value = conv(value)
	globals()[name] = value

sys_version = string.split(sys.version)[0]		#strip off the other garbage

def	_startUp():
	'''this function allows easy resetting to the global defaults'''
	############################################################
	# If the environment contains 'RL_xxx' then we use the value
	# else we use the given default
	_setOpt('shapeChecking', 1, int)
	_setOpt('defaultEncoding', 'WinAnsiEncoding')							# 'WinAnsi' or 'MacRoman'
	_setOpt('pageCompression',1,int)										#the default page compression mode
	_setOpt('defaultPageSize','A4',lambda v,M=pagesizes: getattr(M,v))		#check in reportlab/lib/pagesizes
	_setOpt('defaultImageCaching',0,int)			#set to zero to remove those annoying cached images
	_setOpt('PIL_WARNINGS',1,int)					#set to zero to remove those annoying warnings
	_setOpt('ZLIB_WARNINGS',1,int)
	_setOpt('warnOnMissingFontGlyphs',1,int)		# if 1, warns of each missing glyph
	_setOpt('_verbose',0,int)

	#places to search for Type 1 Font files
	if sys.platform=='win32':
		S = ['c:\\Program Files\\Adobe\\Acrobat 4.0\\Resource\\Font']
	elif sys.platform in ('linux2','freebsd4',):
		S = ['/usr/lib/Acrobat4/Resource/Font']
	elif sys.platform=='mac':	# we must be able to do better than this
		diskName = string.split(os.getcwd(), ':')[0]
		fontDir = diskName + ':Applications:Python %s:reportlab:fonts' % sys_version
		S = [fontDir]   # tba
		PIL_WARNINGS = 0 # PIL is not packagized in the Mac Python build
	else:
		S=[]
		#raise ValueError, 'Please add a proper T1SearchPath for your system to rl_config.py'
	S.append(os.path.abspath(os.path.join(os.path.dirname(__file__),'lib','fontDir')))
	P=[]
	for p in S:
		if os.path.isdir(p): P.append(p)
	_setOpt('T1SearchPath',P)

_startUp()
