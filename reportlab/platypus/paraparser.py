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
#	$Log: paraparser.py,v $
#	Revision 1.18  2000/05/20 15:36:42  andy_robinson
#	Removed 1.5.2-style getattr call
#
#	Revision 1.17  2000/05/16 14:28:55  rgbecker
#	Fixes/Changes to get testplatypus to work with new framework
#	
#	Revision 1.16  2000/05/15 12:15:29  rgbecker
#	CDATA handler added
#	
#	Revision 1.15  2000/05/13 16:04:06  rgbecker
#	made size alias of fontsize for <para>
#	
#	Revision 1.14  2000/05/11 14:05:17  rgbecker
#	Use reportlab.lib.xmllib
#	
#	Revision 1.13  2000/04/25 13:07:57  rgbecker
#	Added license
#	
__version__=''' $Id: paraparser.py,v 1.18 2000/05/20 15:36:42 andy_robinson Exp $ '''
import string
import re
from types import TupleType
import sys
import os
import copy

#try:
#	from xml.parsers import xmllib
#	_xmllib_newStyle = 1
try:
	from reportlab.lib import xmllib
	_xmllib_newStyle = 1
except ImportError:
	import xmllib
	_xmllib_newStyle = 0


from reportlab.lib.colors import stringToColor, white, black, red, Color
from reportlab.lib.fonts import tt2ps, ps2tt
from reportlab.lib.enums import TA_LEFT, TA_RIGHT, TA_CENTER, TA_JUSTIFY

_re_para = re.compile('^\\s*<\\s*para(\\s+|>)')

sizeDelta = 2		# amount to reduce font size by for super and sub script
subFraction = 0.5	# fraction of font size that a sub script should be lowered
superFraction = 0.5	# fraction of font size that a super script should be raised

def _num(s):
	if s[0] in ['+','-']:
		try:
			return ('relative',int(s))
		except ValueError:
			return ('relative',float(s))
	else:
		try:
			return int(s)
		except ValueError:
			return float(s)

def _align(s):
	s = string.lower(s)
	if s=='left': return TA_LEFT
	elif s=='right': return TA_RIGHT
	elif s=='justify': return TA_JUSTIFY
	elif s in ('centre','center'): return TA_CENTER
	else: raise ValueError

_paraAttrMap = {'font': ('fontName', None),
				'fontsize': ('fontSize', _num),
				'size': ('fontSize', _num),
				'leading': ('leading', _num),
				'lindent': ('leftIndent', _num),
				'rindent': ('rightIndent', _num),
				'findent': ('firstLineIndent', _num),
				'align': ('alignment', _align),
				'spaceb': ('spaceBefore', _num),
				'spacea': ('spaceAfter', _num),
				'bfont': ('bulletFontName', None),
				'bfontsize': ('bulletFontIndent',_num),
				'bindent': ('bulletFontIndent',_num),
				'bcolor': ('bulletColor',stringToColor),
				'color':('textColor',stringToColor),
				'fg': ('textColor',stringToColor)}

#things which are valid font attributes
_fontAttrMap = {'size': ('fontSize', _num),
				'name': ('fontName', None),
				'fg': 	('textColor', stringToColor),
				'color':('textColor', stringToColor)}

def _addAttributeNames(m):
	K = m.keys()
	for k in K:
		n = string.lower(m[k][0])
		if not m.has_key(n):
			m[n] = m[k]

_addAttributeNames(_paraAttrMap)
_addAttributeNames(_fontAttrMap)

def _applyAttributes(obj, attr):
	for k, v in attr.items():
		if type(v) is TupleType and v[0]=='relative':
			#AR 20/5/2000 - remove 1.5.2-ism
			#v = v[1]+getattr(obj,k,0)
			if hasattr(obj, k):
				v = v[1]+getattr(obj,k)
			else:
				v = v[1]
		setattr(obj,k,v)

#characters not supported: epsi, Gammad, gammad, kappav, rhov, Upsi, upsi
greeks = {
	'alpha':'a',
	'beta':'b',
	'chi':'c',
	'Delta':'D',
	'delta':'d',
	'epsiv':'e',
	'eta':'h',
	'Gamma':'G',
	'gamma':'g',
	'iota':'i',
	'kappa':'k',
	'Lambda':'L',
	'lambda':'l',
	'mu':'m',
	'nu':'n',
	'Omega':'W',
	'omega':'w',
	'omicron':'x',
	'Phi':'F',
	'phi':'f',
	'phiv':'j',
	'Pi':'P',
	'pi':'p',
	'piv':'v',
	'Psi':'Y',
	'psi':'y',
	'rho':'r',
	'Sigma':'S',
	'sigma':'s',
	'sigmav':'V',
	'tau':'t',
	'Theta':'Q',
	'theta':'q',
	'thetav':'j',
	'Xi':'X',
	'xi':'x',
	'zeta':'z'
}

#------------------------------------------------------------------------
class ParaFrag:
	"""class ParaFrag contains the intermediate representation of string
	segments as they are being parsed by the XMLParser.
	"""
	def __init__(self,**attr):
		for k,v in attr.items():
			setattr(self,k,v)

	def clone(self,**attr):
		n = apply(ParaFrag,(),self.__dict__)
		if attr != {}: apply(ParaFrag.__init__,(n,),attr)
		return n

#------------------------------------------------------------------
# The ParaFormatter will be able to format the following xml
# tags:
#	   < b > < /b > - bold
#	   < i > < /i > - italics
#	   < u > < /u > - underline
#	   < super > < /super > - superscript
#	   < sub > < /sub > - subscript
#	   <font name=fontfamily/fontname color=colorname size=float>
#
#		The whole may be surrounded by <para> </para> tags
#
# It will also be able to handle any MathML specified Greek characters.
#------------------------------------------------------------------
class ParaParser(xmllib.XMLParser):

	#----------------------------------------------------------
	# First we will define all of the xml tag handler functions.
	#
	# start_<tag>(attributes)
	# end_<tag>()
	#
	# While parsing the xml ParaFormatter will call these
	# functions to handle the string formatting tags.
	# At the start of each tag the corresponding field will
	# be set to 1 and at the end tag the corresponding field will
	# be set to 0.	Then when handle_data is called the options
	# for that data will be aparent by the current settings.
	#----------------------------------------------------------

	#### bold
	def start_b( self, attributes ):
		self._push(bold=1)

	def end_b( self ):
		self._pop(bold=1)

	#### italics
	def start_i( self, attributes ):
		self._push(italic=1)

	def end_i( self ):
		self._pop(italic=1)

	#### underline
	def start_u( self, attributes ):
		self._push(underline=1)

	def end_u( self ):
		self._pop(underline=1)

	#### super script
	def start_super( self, attributes ):
		self._push(super=1)

	def end_super( self ):
		self._pop(super=1)

	#### sub script
	def start_sub( self, attributes ):
		self._push(sub=1)

	def end_sub( self ):
		self._pop(sub=1)

	#### greek script
	if _xmllib_newStyle:
		def handle_entityref(self,name):
			if greeks.has_key(name):
				self._push(greek=1)
				self.handle_data(greeks[name])
				self._pop(greek=1)
			else:
				xmllib.XMLParser.handle_entityref(self,name)

		def syntax_error(self,lineno,message):
			self._syntax_error(message)

	else:
		def start_greekLetter(self, attributes,letter):
			self._push(greek=1)
			self.handle_data(letter)

		def syntax_error(self,message):
			self._syntax_error(message)

	def _syntax_error(self,message):
		if message[:10]=="attribute " and message[-17:]==" value not quoted": return
		self.errors.append(message)

	def start_greek(self, attributes):
		self._push(greek=1)

	def end_greek(self):
		self._pop(greek=1)


	def start_font(self,attr):
		A = self.getAttributes(attr,_fontAttrMap)
		apply(self._push,(),A)

	def end_font(self):
		self._pop()

	def start_para(self,attr):
		style = self._style
		if attr!={}:
			style = copy.deepcopy(style)
			_applyAttributes(style,self.getAttributes(attr,_paraAttrMap))
			self._style = style

		# initialize semantic values
		frag = ParaFrag()
		frag.sub = 0
		frag.super = 0
		frag.rise = 0
		frag.fontName, frag.bold, frag.italic = ps2tt(style.fontName)
		frag.fontSize = style.fontSize
		frag.underline = 0
		frag.textColor = style.textColor
		frag.greek = 0
		self._stack = [frag]

	def end_para(self):
		self._pop()

	def _push(self,**attr):
		frag = copy.copy(self._stack[-1])
		_applyAttributes(frag,attr)
		self._stack.append(frag)

	def _pop(self,**kw):
		frag = self._stack[-1]
		del self._stack[-1]
		for k, v in kw.items():
			assert getattr(frag,k)==v
		return frag

	def getAttributes(self,attr,attrMap):
		A = {}
		for k, v in attr.items():
			k = string.lower(k)
			if k in attrMap.keys():
				j = attrMap[k]
				func = j[1]
				try:
					A[j[0]] = (func is None) and v or apply(func,(v,))
				except:
					self._syntax_error('%s: invalid value %s'%(k,v))
			else:
				self._syntax_error('invalid attribute name %s'%k)
		return A

	#----------------------------------------------------------------

	def __init__(self,verbose=0):
		if _xmllib_newStyle:
			xmllib.XMLParser.__init__(self,verbose=verbose)
		else:
			xmllib.XMLParser.__init__(self)
			# set up handlers for various tags
			self.elements = {	'b': (self.start_b, self.end_b),
							'u': (self.start_u, self.end_u),
							'i': (self.start_i, self.end_i),
							'super': (self.start_super, self.end_super),
							'sub': (self.start_sub, self.end_sub),
							'font': (self.start_font, self.end_font),
							'greek': (self.start_greek, self.end_greek),
							'para': (self.start_para, self.end_para)
							}


			# automatically add handlers for all of the greek characters
			for item in greeks.keys():
				self.elements[item] = (lambda attr,self=self,letter=greeks[item]:
					self.start_greekLetter(attr,letter), self.end_greek)

			# set up dictionary for greek characters, this is a class variable
			self.entitydefs = self.entitydefs.copy()
			for item in greeks.keys():
				self.entitydefs[item] = '<%s/>' % item

	def _reset(self, style):
		'''reset the parser'''
		xmllib.XMLParser.reset(self)

		# initialize list of string segments to empty
		self.errors = []
		self.fragList = []
		self._style = style

	#----------------------------------------------------------------
	def handle_data(self,data):
		"Creates an intermediate representation of string segments."

		frag = copy.copy(self._stack[-1])
		#save our data
		frag.text = data

		# if sub and super are both one they will cancel each other out
		if frag.sub == 1 and frag.super == 1:
			frag.sub = 0
			frag.super = 0

		if frag.sub:
			frag.rise = -frag.fontSize*subFraction
			frag.fontSize = max(frag.fontSize-sizeDelta,3)
		elif frag.super:
			frag.rise = frag.fontSize*superFraction
			frag.fontSize = max(frag.fontSize-sizeDelta,3)

		if frag.greek: frag.fontName = 'symbol'
		# bold, italic, and underline
		frag.fontName = tt2ps(frag.fontName,frag.bold,frag.italic)

		self.fragList.append(frag)

	def handle_cdata(self,data):
		self.handle_data(data)

	#----------------------------------------------------------------
	def parse(self, text, style):
		"""Given a formatted string will return a list of
		ParaFrag objects with their calculated widths.
		If errors occur None will be returned and the
		self.errors holds a list of the error messages.
		"""

		# the xmlparser requires that all text be surrounded by xml
		# tags, therefore we must throw some unused flags around the
		# given string
		self._reset(style)	# reinitialise the parser
		if not(len(text)>=6 and text[0]=='<' and _re_para.match(text)):
			text = "<para>"+text+"</para>"
		self.feed(text)
		self.close()	# force parsing to complete
		style = self._style
		del self._style
		if len(self.errors)==0:
			fragList = self.fragList
			self.fragList = []
			return style, fragList
		else:
			return style, None

if __name__=='__main__':
	from reportlab.platypus.paragraph import cleanBlockQuotedText
	_parser=ParaParser()
	def check_text(text,p=_parser):
		print '##########'
		text = cleanBlockQuotedText(text)
		l,rv = p.parse(text,style)
		if rv is None:
			for l in _parser.errors:
				print l
		else:
			print 'ParaStyle', l.fontName,l.fontSize,l.textColor
			for l in rv:
				print l.fontName,l.fontSize,l.textColor,l.bold, l.rise, l.text[:25]

	style=ParaFrag()
	style.fontName='Times-Roman'
	style.fontSize = 12
	style.textColor = black

	text='''
	<b><i><greek>a</greek>D</i></b>&beta;
	<font name="helvetica" size="15" color=green>
	Tell me, O muse, of that ingenious hero who travelled far and wide
	after</font> he had sacked the famous town of Troy. Many cities did he visit,
	and many were the nations with whose manners and customs he was acquainted;
	moreover he suffered much by sea while trying to save his own life
	and bring his men safely home; but do what he might he could not save
	his men, for they perished through their own sheer folly in eating
	the cattle of the Sun-god Hyperion; so the god prevented them from
	ever reaching home. Tell me, too, about all these things, O daughter
	of Jove, from whatsoever source you<super>1</super> may know them.
	'''
	check_text(text)
	check_text('<para> </para>')
	check_text('<para font="times-bold" size=24 leading=28.8 spaceAfter=72>ReportLab -- Reporting for the Internet Age</para>')
	check_text('''
	<font color=red>&tau;</font>Tell me, O muse, of that ingenious hero who travelled far and wide
	after he had sacked the famous town of Troy. Many cities did he visit,
	and many were the nations with whose manners and customs he was acquainted;
	moreover he suffered much by sea while trying to save his own life
	and bring his men safely home; but do what he might he could not save
	his men, for they perished through their own sheer folly in eating
	the cattle of the Sun-god Hyperion; so the god prevented them from
	ever reaching home. Tell me, too, about all these things, O daughter
	of Jove, from whatsoever source you may know them.''')
	check_text('''
	Telemachus took this speech as of good omen and rose at once, for
	he was bursting with what he had to say. He stood in the middle of
	the assembly and the good herald Pisenor brought him his staff. Then,
	turning to Aegyptius, "Sir," said he, "it is I, as you will shortly
	learn, who have convened you, for it is I who am the most aggrieved.
	I have not got wind of any host approaching about which I would warn
	you, nor is there any matter of public moment on which I would speak.
	My grieveance is purely personal, and turns on two great misfortunes
	which have fallen upon my house. The first of these is the loss of
	my excellent father, who was chief among all you here present, and
	was like a father to every one of you; the second is much more serious,
	and ere long will be the utter ruin of my estate. The sons of all
	the chief men among you are pestering my mother to marry them against
	her will. They are afraid to go to her father Icarius, asking him
	to choose the one he likes best, and to provide marriage gifts for
	his daughter, but day by day they keep hanging about my father's house,
	sacrificing our oxen, sheep, and fat goats for their banquets, and
	never giving so much as a thought to the quantity of wine they drink.
	No estate can stand such recklessness; we have now no Ulysses to ward
	off harm from our doors, and I cannot hold my own against them. I
	shall never all my days be as good a man as he was, still I would
	indeed defend myself if I had power to do so, for I cannot stand such
	treatment any longer; my house is being disgraced and ruined. Have
	respect, therefore, to your own consciences and to public opinion.
	Fear, too, the wrath of heaven, lest the gods should be displeased
	and turn upon you. I pray you by Jove and Themis, who is the beginning
	and the end of councils, [do not] hold back, my friends, and leave
	me singlehanded- unless it be that my brave father Ulysses did some
	wrong to the Achaeans which you would now avenge on me, by aiding
	and abetting these suitors. Moreover, if I am to be eaten out of house
	and home at all, I had rather you did the eating yourselves, for I
	could then take action against you to some purpose, and serve you
	with notices from house to house till I got paid in full, whereas
	now I have no remedy."''')

	check_text('''
But as the sun was rising from the fair sea into the firmament of
heaven to shed light on mortals and immortals, they reached Pylos
the city of Neleus. Now the people of Pylos were gathered on the sea
shore to offer sacrifice of black bulls to Neptune lord of the Earthquake.
There were nine guilds with five hundred men in each, and there were
nine bulls to each guild. As they were eating the inward meats and
burning the thigh bones [on the embers] in the name of Neptune, Telemachus
and his crew arrived, furled their sails, brought their ship to anchor,
and went ashore. ''')
	check_text('''
So the neighbours and kinsmen of Menelaus were feasting and making
merry in his house. There was a bard also to sing to them and play
his lyre, while two tumblers went about performing in the midst of
them when the man struck up with his tune.]''')
	check_text('''
"When we had passed the [Wandering] rocks, with Scylla and terrible
Charybdis, we reached the noble island of the sun-god, where were
the goodly cattle and sheep belonging to the sun Hyperion. While still
at sea in my ship I could bear the cattle lowing as they came home
to the yards, and the sheep bleating. Then I remembered what the blind
Theban prophet Teiresias had told me, and how carefully Aeaean Circe
had warned me to shun the island of the blessed sun-god. So being
much troubled I said to the men, 'My men, I know you are hard pressed,
but listen while I tell you the prophecy that Teiresias made me, and
how carefully Aeaean Circe warned me to shun the island of the blessed
sun-god, for it was here, she said, that our worst danger would lie.
Head the ship, therefore, away from the island.''')
	check_text('''&lt; &gt; &amp; &quot; &apos;''')
	check_text('''<![CDATA[<>&'"]]>''')
