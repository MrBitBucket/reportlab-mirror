#copyright ReportLab Inc. 2000-2001
#see license.txt for license details
#history http://cvs.sourceforge.net/cgi-bin/cvsweb.cgi/reportlab/rl_config.py?cvsroot=reportlab
#$Header: /tmp/reportlab/reportlab/rl_config.py,v 1.24 2001/09/28 10:31:10 rgbecker Exp $

allowTableBoundsErrors = 1 # set to 0 to die on too large elements in tables in debug (recommend 1 for production use)
shapeChecking =				1
defaultEncoding =			'WinAnsiEncoding'		# 'WinAnsi' or 'MacRoman'
pageCompression =			1						# default page compression mode
defaultPageSize =			'A4'					#default page size
defaultImageCaching =		0						#set to zero to remove those annoying cached images
PIL_WARNINGS =				1						#set to zero to remove those annoying warnings
ZLIB_WARNINGS =				1						
warnOnMissingFontGlyphs =	1						#if 1, warns of each missing glyph
_verbose =					0
showBoundary =				0						# turns on and off boundary behaviour in Drawing

# places to look for T1Font information
T1SearchPath =	('c:/Program Files/Adobe/Acrobat 4.0/Resource/Font', #Win32
				'%(disk)s/Applications/Python %(sys_version)s/reportlab/fonts', #Mac?
				'/usr/lib/Acrobat4/Resource/Font', #Linux
				'%(REPORTLAB_DIR)s/lib/fontDir', #special
				)

# places to look for CMap files - should ideally merge with above
CMapSearchPath = ('/usr/local/Acrobat4/Resource/CMap',
				'C:\\Program Files\\Adobe\\Acrobat\\Resource\\CMap',
				'C:\\Program Files\\Adobe\\Acrobat 5.0\\Resource\\CMap',
				'C:\\Program Files\\Adobe\\Acrobat 4.0\\Resource\\CMap'
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
_SAVED = {}

def	_startUp():
	'''This function allows easy resetting to the global defaults
	If the environment contains 'RL_xxx' then we use the value
	else we use the given default'''
	V = ('T1SearchPath','CMapSearchPath','shapeChecking', 'defaultEncoding', 'pageCompression',
				'defaultPageSize', 'defaultImageCaching', 'PIL_WARNINGS',
				'ZLIB_WARNINGS', 'warnOnMissingFontGlyphs', '_verbose',
				)

	if _SAVED=={}:
		for k in V:
			_SAVED[k] = globals()[k]

	#places to search for Type 1 Font files
	import reportlab
	D = {'REPORTLAB_DIR': os.path.dirname(reportlab.__file__),
		'disk': string.split(os.getcwd(), ':')[0],
		'sys_version': sys_version,
		}

	P=[]
	for p in _SAVED['T1SearchPath']:
		d = string.replace(p % D,'/',os.sep)
		if os.path.isdir(d): P.append(d)
	_setOpt('T1SearchPath',P)

	P=[]
	for p in _SAVED['CMapSearchPath']:
		d = string.replace(p % D,'/',os.sep)
		if os.path.isdir(d): P.append(d)
	_setOpt('CMapSearchPath',P)

	for k in V[1:]:
		v = _SAVED[k]
		if type(v)==type(1): conv = int
		elif k=='defaultPageSize': conv = lambda v,M=pagesizes: getattr(M,v)
		else: conv = None
		_setOpt(k,v,conv)

_startUp()
