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
#	$Log: sequencer.py,v $
#	Revision 1.2  2000/06/09 16:18:19  andy_robinson
#	Doc strings, sequencer
#
#	Revision 1.1  2000/06/01 15:23:06  rgbecker
#	Platypus re-organisation
#	
__version__=''' $Id: sequencer.py,v 1.2 2000/06/09 16:18:19 andy_robinson Exp $ '''


def format_123(num):
	"""The simplest formatter"""
	return str(num)

def format_ABC(num):
	"""Uppercase.  Wraps around at 26."""
	n = (num -1) % 26
	return chr(n+65)

def format_abc(num):
	"""Lowercase.  Wraps around at 26."""
	n = (num -1) % 26
	return chr(n+97)


class Counter:
	"""Private class used by Sequencer.  Each counter
	knows its format, and the IDs of anything it
	resets, as well as its value. """
	def __init__(self):
		self._base = 1
		self._value = self.base
		self._formatter = format_123
		self._resets = []

	def reset(self, value=None):
		if value:
			self._value = value
		else:
			self._value = self._base

	def next(self):
		v = self._value
		self._value = self._value + 1
		return v

	def this(self):
		return self._value

		
class Sequencer:
	"""Something to make it easy to number paragraphs, sections,
	images and anything else.  It keeps track of a number of
	'counters'.
	Usage:
		>>> seq = layout.Sequencer()
		>>> seq.next('Bullets')
		1
		>>> seq.next('Bullets')
		2
		>>> seq.next('Bullets')
		3
		>>> seq.reset('Bullets')
		>>> seq.next('Bullets')
		1
		>>> seq.next('Figures')
		1
		>>>
	
	"""
	def __init__(self):
		self._counters = {}  #map key to current number
		self._defaultCounter = None

	def _getCounter(self, counter=None):
		"""Creates one if not present"""
		try:
			cnt = self._counters[counter]
		except KeyError:
			cnt = _Counter()
			self._counters[counter] = cnt
		return cnt
	

	def this(self, counter=None):
		"""Retrieves counter value but does not increment. For
		new counters, sets base value to 1."""
		if not counter:
			counter = self._defaultCounter
		return self._getCounter(counter).value
		
	def next(self, counter=None):
		"""Retrieves the numeric value for the given counter, then
		increments it by one.  New counters start at one."""
		if not counter:
			counter = self._defaultCounter
		cnt = self._getCounter(counter)
		n = cnt.value
		cnt.value = cnt.value + 1
		return n
	
	def setDefaultCounter(self, default=None):
		"""Changes the key used for the default"""
		self._defaultCounter = default
	
	def reset(self, counter=None, base=1):
		if not counter:
			counter = self._defaultCounter
		self._getCounter(counter).value = base

	def _format(self, number, formatCode):
		pass

	def chain(self, parent, child, base):
		
def test():
	s = Sequencer()
	print 'Counting using default sequence: %d %d %d' % (s.next(),s.next(), s.next())
	print 'Counting Figures: Figure %d, Figure %d, Figure %d' % (
		s.next('figure'), s.next('figure'), s.next('figure'))
	print 'Back to default again: %d' % s.next()
	s.setDefaultCounter('list1')
	print 'Set default to list1: %d %d %d' % (s.next(),s.next(), s.next())
	s.setDefaultCounter()
	print 'Set default to None again: %d %d %d' % (s.next(),s.next(), s.next())
	print
	
	
if __name__=='__main__':
	test()

	
	