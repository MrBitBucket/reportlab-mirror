"""
Tests for TypedPropertyCollection class.
"""

import os, sys, copy, tempfile
from os.path import join, basename, splitext

from reportlab.graphics.widgetbase import PropHolder, TypedPropertyCollection
from reportlab.lib.attrmap import AttrMap, AttrMapValue
from reportlab.lib.validators import isNumber
from reportlab.test import unittest


TPC = TypedPropertyCollection


class PH(PropHolder):
    _attrMap = AttrMap(
        a = AttrMapValue(isNumber),
        b = AttrMapValue(isNumber)
        )


class TPCTestCase(unittest.TestCase):
    "Test TypedPropertyCollection class."

    def test1(self):
        "Test setting an invalid collective attribute."

        t = TPC(PH)
        try:
            t.c = 42
        except AttributeError:
            pass
        

    def test2(self):
        "Test setting a valid collective attribute."

        t = TPC(PH)
        t.a = 42
        assert t.a == 42


    def test3(self):
        "Test setting a valid collective attribute with an invalid value."

        t = TPC(PH)
        try:
            t.a = 'fourty-two'
        except AttributeError:
            pass


    def test4(self):
        "Test setting a valid collective attribute with a convertible invalid value."

        t = TPC(PH)
        t.a = '42'
        assert t.a == '42' # Or should it rather be an integer?
        

    def test5(self):
        "Test accessing an unset collective attribute."

        t = TPC(PH)
        try:
            t.a
        except AttributeError:
            pass


    def test6(self):
        "Test overwriting a collective attribute in one slot."

        t = TPC(PH)
        t.a = 42
        t[0].a = 4242
        assert t[0].a == 4242


    def test7(self):
        "Test overwriting a one slot attribute with a collective one."

        t = TPC(PH)
        t[0].a = 4242
        t.a = 42
        assert t[0].a == 4242


def makeSuite():
    suite = unittest.TestSuite()

    suite.addTest(TPCTestCase('test1'))
    suite.addTest(TPCTestCase('test2'))
    suite.addTest(TPCTestCase('test3'))
    suite.addTest(TPCTestCase('test4'))
    suite.addTest(TPCTestCase('test5'))
    suite.addTest(TPCTestCase('test6'))
    suite.addTest(TPCTestCase('test7'))

    return suite


#noruntests
if __name__ == "__main__":
    unittest.TextTestRunner().run(makeSuite())
