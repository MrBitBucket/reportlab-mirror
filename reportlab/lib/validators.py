"""
This module contains some standard verifying functions which can be
used in an attribute map.
"""

import string
from types import FloatType, IntType, ListType, TupleType, StringType

from reportlab.lib import colors
from reportlab.graphics.shapes import Auto

    
def isBoolean(x):
    return (x in (0, 1))


def isString(x):
    return (type(x) == StringType)

            
def isNumber(x):
    # Don't think we really want complex numbers for numbers!
    return (type(x) in (FloatType, IntType))


def isNumberOrNone(x):
    if x is None:
        return 1
    else:
        # Don't think we really want complex numbers for numbers!
        return (type(x) in (FloatType, IntType))


def isNumberOrAuto(x):
    if x == Auto:
        return 1
    else:
        # Don't think we really want complex numbers for numbers!
        return (type(x) in (FloatType, IntType))


def isTextAnchor(x):
    return (x in ('start', 'middle', 'end'))


def isListOfNumbers(x):
    # Don't think we really want complex numbers for numbers!
    if type(x) in (ListType, TupleType):
        for element in x:
            if not isNumber(element):
                return 0
        return 1
    else:
        return 0


def isListOfNumbersOrNone(x):
    if x is None:
        return 1
    else:
        return isListOfNumbers(x)

    
def isListOfShapes(x):
    if type(x) in (ListType, TupleType):
        answer = 1
        for element in x:
            if not isinstance(x, Shape):
                answer = 0
        return answer
    else:
        return 0


def isListOfStrings(x):
    if type(x) in (ListType, TupleType):
        answer = 1
        for element in x:
            if type(element) <> type(""):
                answer = 0
        return answer
    else:
        return 0


def isListOfStringsOrNone(x):
    if x is None:
        return 1
    else:
        return isListOfStrings(x)


def isTransform(x):
    if type(x) in (ListType, TupleType):
        if len(x) == 6:
            for element in x:
                if not isNumber(element):
                    return 0
            return 1
        else:
            return 0
    else:
        return 0
    

def isColor(x):
    return isinstance(x, colors.Color)


def isColorOrNone(x):
    if x is None:
        return 1
    else:
        return isinstance(x, colors.Color)


def isValidChild(x):
    """Is this child allowed in a drawing or group?

    I.e. does it descend from Shape or UserNode?
    """

    return isinstance(x, UserNode) or isinstance(x, Shape)


class OneOf:
    """Make validator functions for list of choices. Usage:
    >>> f = shapes.OneOf(('happy','sad'))
    >>> f('happy')
    1
    >>> f('grumpy')
    0
    >>> 
    """

    def __init__(self, choices):
        self._choices = choices

    def __call__(self, arg):
        return arg in self._choices


class SequenceOf:
    """Make validator functions for sequence of things:
    >>> isListOfColors = shapes.SequenceOf(isColor)    
    """
    
    def __init__(self, atomicFunc):
        self._atomicFunc = atomicFunc

    def __call__(self, seq):
        if type(seq) not in (ListType, TupleType):
            return 0
        else:
            for elem in seq:
                if not self._atomicFunc(elem):
                    return 0
            return 1
