#!/bin/env python
#copyright ReportLab Inc. 2000
#see license.txt for license details
#history http://cvs.sourceforge.net/cgi-bin/cvsweb.cgi/reportlab/lib/formatters.py?cvsroot=reportlab
#$Header: /tmp/reportlab/reportlab/lib/formatters.py,v 1.4 2002/03/22 14:43:43 rgbecker Exp $
__version__=''' $Id: formatters.py,v 1.4 2002/03/22 14:43:43 rgbecker Exp $ '''
__doc__="""
These help format numbers and dates in a user friendly way.

Used by the graphics framework.
"""
import string, sys, os

class Formatter:
	"Base formatter - simply applies python format strings"
	def __init__(self, pattern):
		self.pattern = pattern
	def format(self, obj):
		return self.pattern % obj
	def __repr__(self):
		return "%s('%s')" % (self.__class__.__name__, self.pattern)
	def __call__(self, x):
		return self.format(x)


class DecimalFormatter(Formatter):
	"""lets you specify how to build a decimal.

	A future NumberFormatter class will take Microsoft-style patterns
	instead - "$#,##0.00" is WAY easier than this."""
	def __init__(self, places=2, decimalSep='.', thousandSep=None, prefix=None, suffix=None):
		self.decimalPlaces = places
		self.decimalSeparator = decimalSep
		self.thousandSeparator = thousandSep
		self.prefix = prefix
		self.suffix = suffix

	def format(self, num):
		# positivize the numbers
		sign=num<0
		if sign:
			num = -num
		places, sep = self.decimalPlaces, self.decimalSeparator
		strip = places<=0
		if places and strip: places = -places
		strInt, strFrac = (('%.' + str(places) + 'f') % num).split('.')

		if self.thousandSeparator is not None:
			strNew = ''
			while strInt:
				left, right = strInt[0:-3], strInt[-3:]
				if left == '':
					#strNew = self.thousandSeparator + right + strNew
					strNew = right + strNew
				else:
					strNew = self.thousandSeparator + right + strNew
				strInt = left
			strInt = strNew
		strFrac = sep + strFrac
		if strip:
			while strFrac and strFrac[-1] in ['0',sep]: strFrac = strFrac[:-1]
		strBody = strInt + strFrac
		if sign: strBody = '-' + strBody
		if self.prefix:
			strBody = self.prefix + strBody
		if self.suffix:
			strBody = strBody + self.suffix
		return strBody
	
	def __repr__(self):
		return "%s(places=%d, decimalSep=%s, thousandSep=%s, prefix=%s, suffix=%s)" % (
					self.__class__.__name__,
					self.decimalPlaces,
					repr(self.decimalSeparator),
					repr(self.thousandSeparator),
					repr(self.prefix),
					repr(self.suffix)
					)
