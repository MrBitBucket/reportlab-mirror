#copyright ReportLab Inc. 2000-2001
#see license.txt for license details
#history http://cvs.sourceforge.net/cgi-bin/cvsweb.cgi/reportlab/rl_config.py?cvsroot=reportlab
#$Header: /tmp/reportlab/reportlab/rl_config.py,v 1.20 2001/08/30 08:37:38 rgbecker Exp $

shapeChecking =				1
defaultEncoding =			'WinAnsiEncoding'		# 'WinAnsi' or 'MacRoman'
pageCompression =			1						# default page compression mode
defaultPageSize =			'A4'					#default page size
defaultImageCaching =		0						#set to zero to remove those annoying cached images
PIL_WARNINGS =				1						#set to zero to remove those annoying warnings
ZLIB_WARNINGS =				1						
warnOnMissingFontGlyphs =	1						#if 1, warns of each missing glyph
_verbose =					0

# places to look for T1Font information
T1SearchPath =	('c:/Program Files/Adobe/Acrobat 4.0/Resource/Font', #Win32
				'%(disk)s/Applications/Python %(sys_version)s/reportlab/fonts', #Mac?
				'/usr/lib/Acrobat4/Resource/Font', #Linux
				'%(REPORTLAB_DIR)s/lib/fontDir', #special
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
	import reportlab
	D = {'REPORTLAB_DIR': os.path.dirname(reportlab.__file__),
		'disk': string.split(os.getcwd(), ':')[0],
		'sys_version': sys_version,
		}

	P=[]
	for p in T1SearchPath:
		d = string.replace(p % D,'/',os.sep)
		print d
		if os.path.isdir(d): P.append(d)
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
