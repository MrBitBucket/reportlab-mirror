#!/bin/env python
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
#	$Log: logger.py,v $
#	Revision 1.1  2000/07/26 11:58:31  rgbecker
#	Initial version
#
__version__=''' $Id: logger.py,v 1.1 2000/07/26 11:58:31 rgbecker Exp $ '''

from sys import stderr
class Logger:
	'''
	An extended file type thing initially equivalent to sys.stderr
	You can add/remove file type things; it has a write method
	'''
	def __init__(self):
		self._fps = [stderr]
		self._fns = {}

	def add(self,fp):
		'''add the file/string fp to the destinations'''
		if type(fp) is StringType:
			if fp in self._fns: return
			fp = open(fn,'wb')
			self._fns[fn] = fp
		self._fps.append(fp)

	def remove(self,fp):
		'''remove the file/string fp from the destinations'''
		if type(fp) is StringType:
			if fp not in self._fns: return
			fn = fp
			fp = self._fns[fn]
			del self.fns[fn]
		if fp in self._fps:
			del self._fps[self._fps.index(fp)]

	def write(self,text):
		'''write text to all the destinations'''
		if text[-1]!='\n': text=text+'\n'
		map(lambda fp,t=text: fp.write(t),self._fps)

	def __call__(self,text):
		self.write(text)

logger=Logger()

class WarnOnce:

	def __init__(self,kind='Warn'):
		self.uttered = {}
		self.pfx = '%s: '%kind

	def once(self,warning):
		if not self.uttered.has_key(warning):
			logger.write(self.pfx + warning)
			self.uttered[warning] = 1

	def __call__(self,warning):
		self.once(warning)

warnOnce=WarnOnce()
infoOnce=WarnOnce('Info')
