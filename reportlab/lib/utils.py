#copyright ReportLab Inc. 2000
#see license.txt for license details
#history http://cvs.sourceforge.net/cgi-bin/cvsweb.cgi/reportlab/lib/utils.py?cvsroot=reportlab
#$Header: /tmp/reportlab/reportlab/lib/utils.py,v 1.23 2001/12/12 11:42:43 rgbecker Exp $
__version__=''' $Id: utils.py,v 1.23 2001/12/12 11:42:43 rgbecker Exp $ '''

import string, os, sys
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

def recursiveImport(modulename, baseDir=None):
	"""Dynamically imports possible packagized module, or raises ImportError"""
	import imp
	parts = string.split(modulename, '.')
	part = parts[0]
	if baseDir:
		path = [baseDir]
	else:
		path = None

	#make import errors a bit more informative
	try:
		(file, pathname, description) = imp.find_module(part, path)
		childModule = parentModule = imp.load_module(part, file, pathname, description)
		for name in parts[1:]:
			(file, pathname, description) = imp.find_module(name, parentModule.__path__)
			childModule = imp.load_module(name, file, pathname, description)
			setattr(parentModule, name, childModule)
			parentModule = childModule
	except ImportError:
		msg = "cannot import '%s' while attempting recursive import of '%s'" % (part, modulename)
		if baseDir:
			msg = msg + " under directory '%s'" % baseDir
		raise ImportError, msg

	return childModule


	
		


def import_zlib():
	try:
		import zlib
	except ImportError, errMsg:
		_checkImportError(errMsg)
		zlib = None
		from reportlab.rl_config import ZLIB_WARNINGS
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

class ArgvDictValue:
	'''A type to allow clients of getArgvDict to specify a conversion function'''
	def __init__(self,value,func):
		self.value = value
		self.func = func

def getArgvDict(**kw):
	'''	Builds a dictionary from its keyword arguments with overrides from sys.argv.
		Attempts to be smart about conversions, but the value can be an instance
		of ArgDictValue to allow specifying a conversion function.
	'''
	def handleValue(v,av,func):
		if func:
			v = func(av)
		else:
			t = type(v)
			if t is StringType:
				v = av
			elif t is FloatType:
				v = float(av)
			elif t is IntType:
				v = int(av)
			elif t is ListType:
				v = list(eval(av))
			elif t is TupleType:
				v = tuple(eval(av))
			else:
				raise TypeError, "Can't convert string '%s' to %s" % (av,str(t))
		return v

	A = sys.argv[1:]
	R = {}
	for k, v in kw.items():
		if isinstance(v,ArgvDictValue):
			v, func = v.value, v.func
		else:
			func = None
		handled = 0
		ke = k+'='
		for a in A:
			if string.find(a,ke)==0:
				av = a[len(ke):]
				A.remove(a)
				R[k] = handleValue(v,av,func)
				handled = 1
				break

		if not handled: R[k] = handleValue(v,v,func)

	return R

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
