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
#	$Log: propertyset.py,v $
#	Revision 1.1  2000/04/14 10:38:13  rgbecker
#	Moved out of layout.py
#
__version__=''' $Id: propertyset.py,v 1.1 2000/04/14 10:38:13 rgbecker Exp $ '''
###########################################################
# This class provides an 'instance inheritance'
# mechanism for its descendants, simpler than acquisition
# but not as far-reaching
###########################################################
class PropertySet:
	defaults = {}

	def __init__(self, name, parent=None):
		self.name = name
		self.parent = parent
		self.attributes = {}

	def __setattr__(self, key, value):
		if self.defaults.has_key(key):
			self.attributes[key] = value
		else:
			self.__dict__[key] = value

	def __getattr__(self, key):
		if self.defaults.has_key(key):
			if self.attributes.has_key(key):
				found = self.attributes[key]
			elif self.parent:
				found = getattr(self.parent, key)
			else:  #take the class default
				found = self.defaults[key]
		else:
			found = self.__dict__[key]
		return found

	def __repr__(self):
		return "<%s '%s'>" % (self.__class__.__name__, self.name)

	def listAttrs(self):
		print 'name =', self.name
		print 'parent =', self.parent
		keylist = self.defaults.keys()
		keylist.sort()
		for key in keylist:
			value = self.attributes.get(key, None)
			if value:
				print '%s = %s (direct)' % (key, value)
			else: #try for inherited
				value = getattr(self.parent, key, None)
				if value:
					print '%s = %s (inherited)' % (key, value)
				else:
					value = self.defaults[key]
					print '%s = %s (class default)' % (key, value)
