#!/bin/env python
#copyright ReportLab Inc. 2000
#see license.txt for license details
#history http://cvs.sourceforge.net/cgi-bin/cvsweb.cgi/reportlab/lib/fonts.py?cvsroot=reportlab
#$Header: /tmp/reportlab/reportlab/lib/fonts.py,v 1.3 2001/03/02 15:34:21 rgbecker Exp $
__version__=''' $Id: fonts.py,v 1.3 2001/03/02 15:34:21 rgbecker Exp $ '''
import string, sys, os
###############################################################################
#	A place to put useful font stuff
###############################################################################
#
#	   Font Mappings
# The brute force approach to finding the correct postscript font name;
# much safer than the rule-based ones we tried.
# preprocessor to reduce font face names to the shortest list
# possible.  Add any aliases you wish; it keeps looking up
# until it finds no more translations to do.  Any input
# will be lowercased before checking.
_family_alias = {
			'serif':'times',
			'sansserif':'helvetica',
			'monospaced':'courier',
			'arial':'helvetica'
			}
#maps a piddle font to a postscript one.
_tt2ps_map = {
			#face, bold, italic -> ps name
			('times', 0, 0) :'Times-Roman',
			('times', 1, 0) :'Times-Bold',
			('times', 0, 1) :'Times-Italic',
			('times', 1, 1) :'Times-BoldItalic',

			('courier', 0, 0) :'Courier',
			('courier', 1, 0) :'Courier-Bold',
			('courier', 0, 1) :'Courier-Oblique',
			('courier', 1, 1) :'Courier-BoldOblique',
			
			('helvetica', 0, 0) :'Helvetica',
			('helvetica', 1, 0) :'Helvetica-Bold',
			('helvetica', 0, 1) :'Helvetica-Oblique',
			('helvetica', 1, 1) :'Helvetica-BoldOblique',

			# there is only one Symbol font			
			('symbol', 0, 0) :'Symbol',
			('symbol', 1, 0) :'Symbol',
			('symbol', 0, 1) :'Symbol',
			('symbol', 1, 1) :'Symbol',

			# ditto for dingbats
			('zapfdingbats', 0, 0) :'ZapfDingbats',
			('zapfdingbats', 1, 0) :'ZapfDingbats',
			('zapfdingbats', 0, 1) :'ZapfDingbats',
			('zapfdingbats', 1, 1) :'ZapfDingbats',
	  }

_ps2tt_map={}
for k,v in _tt2ps_map.items():
	if not _ps2tt_map.has_key(k):
		_ps2tt_map[string.lower(v)] = k

def ps2tt(psfn):
	'ps fontname to family name, bold, italic'
	psfn = string.lower(psfn)
	if _ps2tt_map.has_key(psfn):
		return _ps2tt_map[psfn]
	raise "Can't map PS font", psfn

def tt2ps(fn,b,i):
	'family name + bold & italic to ps font name'
	K = (string.lower(fn),b,i)
	if _tt2ps_map.has_key(K):
		return _tt2ps_map[K]
	raise "Can't map PS font", fn

#this maps fontnames to the equivalent filename root.
_font2fnrMap={
	'symbol': 'Sy______',
	'zapfdingbats': 'Zd______',
	'helvetica': '_a______',
	'helvetica-bold': '_ab_____',
	'helvetica-boldoblique': '_abi____',
	'helvetica-oblique': '_ai_____',
	'times-bold': '_eb_____',
	'times-bolditalic': '_ebi____',
	'times-italic': '_ei_____',
	'times-roman': '_er_____',
	'courier-bold': 'cob_____',
	'courier-boldoblique': 'cobo____',
	'courier': 'com_____',
	'courier-oblique': 'coo_____',
	}

import sys, os
if sys.platform=='win32':
	_T1Path=['c:\\program Files\\Adobe\\Acrobat 4.0\\Resource\\Font']
else:
	_T1Path=[]

def _findFNR(fontName):
	return _font2fnrMap[string.lower(fontName)]

def findPFB(fontName):
	n = _findFNR(fontName)+'.pfb'
	for d in _T1Path:
		f = os.path.join(d,n)
		if os.path.isfile(f): return f
	return None
