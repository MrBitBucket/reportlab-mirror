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
#	Revision 1.1  2000/06/01 15:23:06  rgbecker
#	Platypus re-organisation
#
__version__=''' $Id: sequencer.py,v 1.1 2000/06/01 15:23:06 rgbecker Exp $ '''
class Sequencer:
	"""Something to make it easy to number paragraphs, sections,
	images and anything else. Usage:
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
	I plan to add multi-level linkages, so that Head2 could be reet
	"""
	def __init__(self):
		self.dict = {}

	def next(self, category):
		if self.dict.has_key(category):
			self.dict[category] = self.dict[category] + 1
		else:
			self.dict[category] = 1
		return self.dict[category]

	def reset(self, category):
		self.dict[category] = 0
