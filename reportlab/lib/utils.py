###############################################################################
#
#	ReportLab Public License Version 1.0
#
#   Except for the change of names the spirit and intention of this
#   license is the same as that of Python
#
#	(C) Copyright ReportLab Inc. 1998-2000.
#
#
# All Rights Reserved
#
# Permission to use, copy, modify, and distribute this software and its
# documentation for any purpose and without fee is hereby granted, provided
# that the above copyright notice appear in all copies and that both that
# copyright notice and this permission notice appear in supporting
# documentation, and that the name of ReportLab not be used
# in advertising or publicity pertaining to distribution of the software
# without specific, written prior permission. 
# 
#
# Disclaimer
#
# ReportLab Inc. DISCLAIMS ALL WARRANTIES WITH REGARD TO THIS
# SOFTWARE, INCLUDING ALL IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS,
# IN NO EVENT SHALL ReportLab BE LIABLE FOR ANY SPECIAL, INDIRECT
# OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES WHATSOEVER RESULTING FROM LOSS
# OF USE, DATA OR PROFITS, WHETHER IN AN ACTION OF CONTRACT, NEGLIGENCE OR
# OTHER TORTIOUS ACTION, ARISING OUT OF OR IN CONNECTION WITH THE USE OR
# PERFORMANCE OF THIS SOFTWARE. 
#
###############################################################################
#	$Log: utils.py,v $
#	Revision 1.3  2000/08/29 09:19:31  rgbecker
#	Initial version of D Yoo's pyHnj
#
#	Revision 1.2  2000/08/24 18:19:47  rgbecker
#	Added _className func
#	
#	Revision 1.1  2000/08/01 10:50:20  rgbecker
#	Initial version
#	
__version__=''' $Id: utils.py,v 1.3 2000/08/29 09:19:31 rgbecker Exp $ '''
from types import *
SeqTypes = (ListType,TupleType)
import string, os
try:
	#raise ImportError
	from reportlab.lib._rl_accel import fp_str
except ImportError:
	def fp_str(*a):
		if len(a)==1 and type(a[0]) in SeqTypes: a = a[0]
		s = []
		for i in a:
			s.append('%0.2f' % i)
		return string.join(s)

def getHyphenater(hDict=None):
	try:
		from reportlab.lib.pyHnj import Hyphen
		if hDict is None: hDict=os.path.join(os.path.dirname(__file__),'hyphen.mashed')
		return Hyphen(hDict)
	except ImportError:
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
