"""
This module contains some standard verifying functions which can be
used in an attribute map.
"""

import string
from types import FloatType, IntType, ListType, TupleType, StringType
_SequenceTypes = (ListType,TupleType)
_NumberTypes = (FloatType,IntType)
from reportlab.lib import colors

class Validator:
	"base validator class"
	def __call__(self,x):
		return self.test(x)

	def __str__(self):
		return getattr(self,'_str',self.__class__.__name__)

	def normalize(self,x):
		return x

	def normalizeTest(self,x):
		try:
			self.normalize(x)
			return 1
		except:
			return 0

class _isAnything(Validator):
	def test(self,x):
		return 1

class _isNothing(Validator):
	def test(self,x):
		return 0

class _isBoolean(Validator):
	def test(self,x):
		if type(x) is IntType: return x in (0,1)
		return self.normalizeTest(x)

	def normalize(self,x):
		if x in (0,1): return x
		try:
			S = string.upper(x)
		except:
			raise ValueError, 'Must be boolean'
		if S in ('YES','TRUE'): return 1
		if S in ('NO','FALSE'): return 0
		raise ValueError, 'Must be boolean'

class _isString(Validator):
	def test(self,x):
		return type(x) is StringType

class _isNumber(Validator):
	def test(self,x):
		if type(x) in _NumberTypes: return 1
		return self.normalizeTest(x)

	def normalize(self,x):
		try:
			return float(x)
		except:
			return int(x)

class _isNumberOrNone(_isNumber):
	def test(self,x):
		return x is None or isNumber(x)

	def normalize(self,x):
		if x is None: return x
		return _isNumber.normalize(x)

class _isTextAnchor(Validator):
	"TextAnchor validator class."
	def test(self, x):
		return x in ('start', 'middle', 'end')

class _isListOfNumbersOrNone(Validator):
	"ListOfNumbersOrNone validator class."
	def test(self, x):
		if x is None: return 1
		return isListOfNumbers(x)

class _isListOfShapes(Validator):
	"ListOfShapes validator class."
	def test(self, x):
		from reportlab.graphics.shapes import Shape
		if type(x) in _SequenceTypes:
			answer = 1
			for element in x:
				if not isinstance(x, Shape):
					answer = 0
			return answer
		else:
			return 0

class _isListOfStringsOrNone(Validator):
	"ListOfStringsOrNone validator class."

	def test(self, x):
		if x is None: return 1
		return isListOfStrings(x)

class _isTransform(Validator):
	"Transform validator class."
	def test(self, x):
		if type(x) in _SequenceTypes:
			if len(x) == 6:
				for element in x:
					if not isNumber(element):
						return 0
				return 1
			else:
				return 0
		else:
			return 0

class _isColor(Validator):
	"Color validator class."
	def test(self, x):
		return isinstance(x, colors.Color)

class _isColorOrNone(Validator):
	"ColorOrNone validator class."
	def test(self, x):
		if x is None: return 1
		return isColor(x)

class _isValidChild(Validator):
	"ValidChild validator class."
	def test(self, x):
		"""Is this child allowed in a drawing or group?
		I.e. does it descend from Shape or UserNode?
		"""

		from reportlab.graphics.shapes import UserNode, Shape
		return isinstance(x, UserNode) or isinstance(x, Shape)

class OneOf(Validator):
	"""Make validator functions for list of choices.

	Usage:
	>>> f = reportlab.lib.validators.OneOf(('happy','sad'))
	>>> f('happy')
	1
	>>> f('grumpy')
	0
	>>> 
	"""
	def __init__(self, enum):
		self._enum = enum

	def test(self, x):
		return x in self._enum

class SequenceOf(Validator):
	def __init__(self,elemTest,name=None,emptyOK=1):
		self._elemTest = elemTest
		self._emptyOK = emptyOK
		if name: self._str = name

	def test(self, x):
		if type(x) not in _SequenceTypes: return 0
		if x==[] and not self._emptyOK: return 0
		for e in x:
			if not self._elemTest(e): return 0
		return 1

isBoolean = _isBoolean()
isString = _isString()
isNumber = _isNumber()
isNumberOrNone = _isNumberOrNone()
isTextAnchor = _isTextAnchor()
isListOfNumbers = SequenceOf(isNumber,'isListOfNumbers')
isListOfNumbersOrNone = _isListOfNumbersOrNone()
isListOfShapes = _isListOfShapes()
isListOfStrings = SequenceOf(isString,'isListOfStrings')
isListOfStringsOrNone = _isListOfStringsOrNone()
isTransform = _isTransform()
isColor = _isColor()
isColorOrNone = _isColorOrNone()
isValidChild = _isValidChild()
isAnything = _isAnything()
isNothing = _isNothing()
