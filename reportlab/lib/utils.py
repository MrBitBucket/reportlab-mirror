#copyright ReportLab Inc. 2000
#see license.txt for license details
#history http://cvs.sourceforge.net/cgi-bin/cvsweb.cgi/reportlab/lib/utils.py?cvsroot=reportlab
#$Header: /tmp/reportlab/reportlab/lib/utils.py,v 1.18 2001/08/22 19:30:03 aaron_watters Exp $
__version__=''' $Id: utils.py,v 1.18 2001/08/22 19:30:03 aaron_watters Exp $ '''

import string, os
from types import *
from reportlab.lib.logger import warnOnce
SeqTypes = (ListType,TupleType)

def _checkImportError(errMsg):
	if string.lower(string.strip(str(errMsg)[0:16]))!='no module named': raise

try:
	#raise ImportError
	### NOTE!  FP_STR SHOULD PROBABLY ALWAYS DO A PYTHON STR() CONVERSION ON ARGS
	### IN CASE THEY ARE "LAZY OBJECTS".  ACCELLERATOR DOESN'T DO THIS (YET)
	try:
		from _rl_accel import fp_str				# in case of builtin version
	except ImportError, errMsg:
		_checkImportError(errMsg)
		from reportlab.lib._rl_accel import fp_str	# specific
except ImportError, errMsg:
	#_checkImportError(errMsg) # this effectively requires _rl_accel... should not be required
	def fp_str(*a):
		if len(a)==1 and type(a[0]) in SeqTypes: a = a[0]
		s = []
		for i in a:
			s.append('%0.2f' % i)
		return string.join(s)

#hack test for comma users
if ',' in fp_str(0.25):
	_FP_STR = fp_str
	def fp_str(*a):
		return string.replace(apply(_FP_STR,a),',','.')

def import_zlib():
	try:
		import zlib
	except ImportError, errMsg:
		_checkImportError(errMsg)
		zlib = None
		if ZLIB_WARNINGS: warnOnce('zlib not available')
	return zlib

try:
	from PIL import Image
except ImportError, errMsg:
	_checkImportError(errMsg)
	from reportlab.rl_config import PIL_WARNINGS
	try:
		import Image
		if PIL_WARNINGS: warnOnce('Python Imaging Library not available as package; upgrade your installation!')
	except ImportError, errMsg:
		_checkImportError(errMsg)
		Image = None
		if PIL_WARNINGS: warnOnce('Python Imaging Library not available')
PIL_Image = Image
del Image

def getHyphenater(hDict=None):
	try:
		from reportlab.lib.pyHnj import Hyphen
		if hDict is None: hDict=os.path.join(os.path.dirname(__file__),'hyphen.mashed')
		return Hyphen(hDict)
	except ImportError, errMsg:
		if str(errMsg)!='No module named pyHnj': raise
		return None

def _className(self):
	'''Return a shortened class name'''
	try:
		name = self.__class__.__name__
		i=string.rfind(name,'.')
		if i>=0: return name[i+1:]
		return name
	except AttributeError:
		return str(self)
