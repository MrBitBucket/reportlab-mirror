#copyright ReportLab Inc. 2000-2001
#see license.txt for license details
#history http://cvs.sourceforge.net/cgi-bin/cvsweb.cgi/reportlab/rl_config.py?cvsroot=reportlab
#$Header: /tmp/reportlab/reportlab/rl_config.py,v 1.18 2001/08/28 17:59:37 rgbecker Exp $

shapeChecking =				1
defaultEncoding =			'WinAnsiEncoding'		# 'WinAnsi' or 'MacRoman'
pageCompression =			1						# default page compression mode
defaultPageSize =			'A4'					#default page size
defaultImageCaching =		0						#set to zero to remove those annoying cached images
PIL_WARNINGS =				1						#set to zero to remove those annoying warnings
ZLIB_WARNINGS =				1						
warnOnMissingFontGlyphs =	1						#if 1, warns of each missing glyph
_verbose =					0
T1SearchPath =				('c:\\Program Files\\Adobe\\Acrobat 4.0\\Resource\\Font',
							)

#### Normally don't need to edit below here ####
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
	'''This function allows easy resetting to the global defaults
	If the environment contains 'RL_xxx' then we use the value
	else we use the given default'''

	#places to search for Type 1 Font files
	if sys.platform=='win32':
		S = ['c:\\Program Files\\Adobe\\Acrobat 4.0\\Resource\\Font']
	elif sys.platform in ('linux2','freebsd4',):
		S = ['/usr/lib/Acrobat4/Resource/Font']
	elif sys.platform=='mac':	# we must be able to do better than this
		diskName = string.split(os.getcwd(), ':')[0]
		fontDir = diskName + ':Applications:Python %s:reportlab:fonts' % sys_version
		S = [fontDir]					# tba
		globals()['PIL_warnings'] = 0	# PIL is not packagized in the Mac Python build
	else:
		S=[]
		#raise ValueError, 'Please add a proper T1SearchPath for your system to rl_config.py'
	S.append(os.path.abspath(os.path.join(os.path.dirname(__file__),'lib','fontDir')))
	P=[]
	for p in S:
		if os.path.isdir(p): P.append(p)
	_setOpt('T1SearchPath',P)

	for k in ('shapeChecking', 'defaultEncoding', 'pageCompression',
				'defaultPageSize', 'defaultImageCaching', 'PIL_WARNINGS',
				'ZLIB_WARNINGS', 'warnOnMissingFontGlyphs', '_verbose',
				):
		v = globals()[k]
		if type(v)==type(1): conv = int
		elif k=='defaultPageSize': conv = lambda v,M=pagesizes: getattr(M,v)
		else: conv = None
		_setOpt(k,v,conv)

_startUp()
