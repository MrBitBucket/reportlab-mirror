"""Tests (incomplete) for the reportlab.lib.validators module.
"""
from reportlab.test import unittest
from reportlab.lib import colors
from reportlab.lib import validators

class ValidatorTestCase(unittest.TestCase):
	"Test validating functions."
	
	def test0(self):
		"Test isBoolean validator."

		msg = 'isBoolean Validation failed %s!'

		booleans = [0, 1, 'yes','no','true','false']
		badbooleans = ['a',3,-1,()]
		isBoolean = validators.isBoolean
		for b in booleans:
			assert isBoolean(b) == 1, msg % b
		for b in badbooleans:
			assert isBoolean(b) == 0, msg % b

	def test1(self):
		"Test isNumber validator."

		msg = 'Validation failed for number %s!'

		numbers = [0, 1, 2, -1, -2, 0.0, 0.1, -0.1]
		badNumbers = ['aaa',(1,1),(1+1j),colors]
		isNumber = validators.isNumber
		isListOfNumbers = validators.isListOfNumbers
		for n in numbers:
			assert isNumber(n) == 1, msg % str(n)
		for n in badNumbers:
			assert isNumber(n) == 0, msg % str(n)
		assert isListOfNumbers(numbers) == 1, msg % str(numbers)
		assert isListOfNumbers(badNumbers) == 0, msg % str(badNumbers)
		assert isListOfNumbers(numbers+[colors]) == 0, msg % str(numbers+[colors])

	def test2(self):
		"Test isNumberOrNone validator."

		msg = 'Validation failed for number %s!'

		numbers = [None, 0, 1, 2, -1, -2, 0.0, 0.1, -0.1] #, 2L, -2L]		 
		isNumberOrNone = validators.isNumberOrNone
		for n in numbers:
			assert isNumberOrNone(n) == 1, msg % str(n)


	def test4(self):
		"Test isString validator."

		msg = 'Validation failed for string %s!'

		strings = ['', '\n', '	', 'foo', '""']
		badStrings = [1,2.0,None,('a','b')]
		isString = validators.isString
		isListOfStrings = validators.isListOfStrings
		for s in strings:
			assert isString(s) == 1, msg % s
		for s in badStrings:
			assert isString(s) == 0, msg % s
		assert isListOfStrings(strings) == 1, msg % strings
		assert isListOfStrings(badStrings) == 0, msg % badStrings
		assert isListOfStrings(strings+[1]) == 0, msg % strings+[1]


	def test5(self):
		"Test isTextAnchor validator."

		msg = 'Validation failed for text anchor %s!'

		strings = ['start', 'middle', 'end']		
		isTextAnchor = validators.isTextAnchor
		for s in strings:
			assert isTextAnchor(s) == 1, msg % s

		"""
		def isListOfNumbersOrNone(x):
		def isListOfShapes(x):
		def isListOfStrings(x):
		def isListOfStringsOrNone(x):
		def isTransform(x):
		def isColor(x):
		def isColorOrNone(x):
		def isValidChild(x):
		class OneOf:
		class SequenceOf:
		"""


	def test6(self):
		"Test OneOf validator."

		msg = 'Validation failed for OneOf %s!'

		choices = ('clockwise', 'anticlockwise')		
		OneOf = validators.OneOf(choices)
		for c in choices:
			assert OneOf(c) == 1, msg % c
		for c in ('a', 'b', 'c'):
			assert OneOf(c) == 0, msg % c

		OneOf = validators.OneOf('clockwise', 'anticlockwise')
		for c in choices:
			assert OneOf(c) == 1, msg % c
		for c in ('a', 'b', 'c'):
			assert OneOf(c) == 0, msg % c

		try:
			validators.OneOf(choices,'bongo')
			raise AssertionError, "OneOf failed to detect bad arguments"
		except ValueError:
			pass

	def test7(self):
		"Test isInt validator"
		msg = 'Validation failed for isInt %s!'
		isInt = validators.isInt
		for c in (1,2,-3,0,'-4','4'):
			assert isInt(c), msg%c

		for c in (1.2,0.0,-3.0,'-4.0','4.4','AAAA'):
			assert not isInt(c), msg%c

	def test8(self):
		"test Sequence of validator"
		msg = 'Validation failed for SequenceOf %s!'
		v=validators.SequenceOf(validators.OneOf(('eps','pdf','png','gif','jpg','tif')),lo=1,hi=3,emptyOK=0)
		for c in (['png'],('eps',),('eps','pdf')):
			assert v(c), msg%c
		v._lo = 2
		for c in ([],(),('eps'),('eps','pdf','a'),['eps','pdf','png','gif']):
			assert not v(c), msg%c
		v._emptyOK=1
		for c in ([],(),('eps','pdf')):
			assert v(c), msg%c

def makeSuite():
	suite = unittest.TestSuite()
	
	suite.addTest(ValidatorTestCase('test0'))
	suite.addTest(ValidatorTestCase('test1'))
	suite.addTest(ValidatorTestCase('test2'))
	suite.addTest(ValidatorTestCase('test4'))
	suite.addTest(ValidatorTestCase('test5'))
	suite.addTest(ValidatorTestCase('test6'))
	suite.addTest(ValidatorTestCase('test7'))
	suite.addTest(ValidatorTestCase('test8'))

	return suite


#noruntests
if __name__ == "__main__":
	unittest.TextTestRunner().run(makeSuite())
	
