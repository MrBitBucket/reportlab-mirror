import string
import types
import sys
import os
import copy

try:
	from xml.parsers import xmllib
	_xmllib_newStyle = 1
except ImportError:
	import xmllib
	_xmllib_newStyle = 0

from reportlab.lib.colors import stringToColor, white, black, red, Color
from reportlab.lib.fonts import tt2ps, ps2tt

sizeDelta = 2		# amount to reduce font size by for super and sub script
subFraction = 0.5	# fraction of font size that a sub script should be lowered
superFraction = 0.5	# fraction of font size that a super script should be raised

def _num(s):
	try:
		return int(s)
	except ValueError:
		return float(s)

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
	else:
		def start_greekLetter(self, attributes,letter):
			self._push(greek=1)
			self.handle_data(letter)

	def start_greek(self, attributes):
		self._push(greek=1)

	def end_greek(self):
		self._pop(greek=1)

	#things which are valid font attributes
	_fontAttrMap = {'size': ('fontSize',_num),
					'name': ('fontName', None),
					'color':('textColor',stringToColor)}
	def start_font(self,attr):
		A = {}
		for i, j in self._fontAttrMap.items():
			if attr.has_key(i):
				func = j[1]
				val  = attr[i]
				try:
					A[j[0]] = (func is None) and val or apply(func,(val,))
				except:
					self.syntax_error('%s: invalid value %s'%(i,val))
			apply(self._push,(),A)

	def end_font(self):
		self._pop()

	def _push(self,**kw):
		frag = copy.copy(self._stack[-1])
		for k, v in kw.items():
			setattr(frag,k,v)
		self._stack.append(frag)

	def _pop(self,**kw):
		frag = self._stack[-1]
		del self._stack[-1]
		for k, v in kw.items():
			assert getattr(frag,k)==v
		return frag

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
							'greek': (self.start_greek, self.end_greek)
							}

			# automatically add handlers for all of the greek characters
			for item in greeks.keys():
				self.elements[item] = (lambda attr,self=self,letter=greeks[item]:
					self.start_greekLetter(attr,letter), self.end_greek)

			# set up dictionary for greek characters, this is a class variable
			self.entitydefs = copy.copy(self.entitydefs)
			for item in greeks.keys():
				self.entitydefs[item] = '<%s/>' % item

	def _reset(self, style):
		'''reset the parser'''
		xmllib.XMLParser.reset(self)

		# initialize list of string segments to empty
		self.errors = []
		self.fragList = []

		# initialize frag values
		frag = ParaFrag()
		frag.sub = 0
		frag.super = 0
		frag.fontName, frag.bold, frag.italic = ps2tt(style.fontName)
		frag.fontSize = style.fontSize
		frag.underline = 0
		frag.greek = 0
		frag.textColor = style.textColor
		self._stack = [frag]

	def syntax_error(self,message):
		if message[:11]=="attribute `" and message[-18:]=="' value not quoted": return
		self.errors.append(message)

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

		if frag.greek: frag.fontName = 'symbol'
		# bold, italic, and underline
		frag.fontName = tt2ps(frag.fontName,frag.bold,frag.italic)

		self.fragList.append(frag)

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
		self.feed("<ReportLabParagraph>"+text+"</ReportLabParagraph>")
		self.close()	# force parsing to complete
		if len(self.errors)==0:
			fragList = self.fragList
			self.fragList = []
			return fragList
		else:
			return None

if __name__=='__main__':
	from reportlab.platypus.layout import cleanBlockQuotedText
	_parser=ParaParser()

	style=ParaFrag()
	style.fontName='Times-Roman'
	style.fontSize = 12
	style.textColor = black

	text='''
	<b><i><greek>a</greek>D</i></b>&beta;
	<font name="helvetica" size="15" color=green>
	Tell me, O muse, of that ingenious hero who travelled far and wide
	after he had sacked the famous town of Troy. Many cities did he visit,
	and many were the nations with whose manners and customs he was acquainted;
	moreover he suffered much by sea while trying to save his own life
	and bring his men safely home; but do what he might he could not save
	his men, for they perished through their own sheer folly in eating
	the cattle of the Sun-god Hyperion; so the god prevented them from
	ever reaching home. Tell me, too, about all these things, O daughter
	of Jove, from whatsoever source you may know them.</font>
	'''
	text = cleanBlockQuotedText(text)
	rv = _parser.parse(text,style)
	if rv is None:
		for l in _parser.errors:
			print l
	else:
		for l in rv:
			print l.fontName,l.fontSize,l.textColor,l.bold, l.text[:25]
