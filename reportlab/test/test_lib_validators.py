"""Tests (incomplete) for the reportlab.lib.validators module.
"""


from reportlab.test import unittest
from reportlab.lib import colors
from reportlab.lib import validators
from reportlab.graphics.shapes import Auto


class ValidatorTestCase(unittest.TestCase):
    "Test validating functions."
    
    def test0(self):
        "Test isBoolean validator."

        msg = 'Validation failed for Boolean %s!'

        booleans = [0, 1]
        isBoolean = validators.isBoolean()
        for b in booleans:
            assert isBoolean(b) == 1, msg % b


    def test1(self):
        "Test isNumber validator."

        msg = 'Validation failed for number %s!'

        numbers = [0, 1, 2, -1, -2, 0.0, 0.1, -0.1] #, 2L, -2L]        
        isNumber = validators.isNumber()
        for n in numbers:
            assert isNumber(n) == 1, msg % str(n)


    def test2(self):
        "Test isNumberOrNone validator."

        msg = 'Validation failed for number %s!'

        numbers = [None, 0, 1, 2, -1, -2, 0.0, 0.1, -0.1] #, 2L, -2L]        
        isNumberOrNone = validators.isNumberOrNone()
        for n in numbers:
            assert isNumberOrNone(n) == 1, msg % str(n)


    def test4(self):
        "Test isString validator."

        msg = 'Validation failed for string %s!'

        strings = ['', '\n', '  ', 'foo', '""']        
        isString = validators.isString()
        for s in strings:
            assert isString(s) == 1, msg % s


    def test5(self):
        "Test isTextAnchor validator."

        msg = 'Validation failed for text anchor %s!'

        strings = ['start', 'middle', 'end']        
        isTextAnchor = validators.isTextAnchor()
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


def makeSuite():
    suite = unittest.TestSuite()
    
    suite.addTest(ValidatorTestCase('test0'))
    suite.addTest(ValidatorTestCase('test1'))
    suite.addTest(ValidatorTestCase('test2'))
    suite.addTest(ValidatorTestCase('test4'))
    suite.addTest(ValidatorTestCase('test5'))
    suite.addTest(ValidatorTestCase('test6'))

    return suite


#noruntests
if __name__ == "__main__":
    unittest.TextTestRunner().run(makeSuite())
    