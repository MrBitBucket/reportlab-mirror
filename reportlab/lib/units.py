#!/bin/env python
#copyright ReportLab Inc. 2000
#see license.txt for license details
#history http://cvs.sourceforge.net/cgi-bin/cvsweb.cgi/reportlab/lib/units.py?cvsroot=reportlab
#$Header: /tmp/reportlab/reportlab/lib/units.py,v 1.3 2001/05/02 17:51:09 rgbecker Exp $
__version__=''' $Id: units.py,v 1.3 2001/05/02 17:51:09 rgbecker Exp $ '''

inch = 72.0
cm = inch / 2.54

def toLength(s):
	'''convert a string to  a length'''
	try:
		if s[-2:]=='cm': return float(s[:-2])*cm
		if s[-2:]=='in': return float(s[:-2])*inch
		if s[-2:]=='pt': return float(s[:-2])
		if s[-1:]=='i': return float(s[:-1])*inch
		return float(s)
	except:
		raise ValueError, "Can't convert '%s' to length" % s
