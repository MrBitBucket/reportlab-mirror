#!/bin/env python
#Copyright ReportLab Europe Ltd. 2000-2004
#see license.txt for license details
__version__='''$Id$'''
__doc__="""Test reportlab.lib.util module"""

from reportlab.test import unittest
from reportlab.test.utils import makeSuiteForClasses, outputfile


class FmtTestCase(unittest.TestCase):

    def testFmt(self):
        from reportlab.lib.utils import FmtSelfDict
        class MixedIn(FmtSelfDict):
            def __init__(self):
                self.a = 'AA'
                self._b = '_BB'
                self.d = '(overridden)'
        obj = MixedIn()
        self.assertEqual('blah', obj._fmt('blah'))
        self.assertEqual('blah %', obj._fmt('blah %%'))
        self.assertRaises(ValueError, obj._fmt, 'blah %')
        self.assertEqual(
            'moon AA june_BB spoon %(a)sCC ni',
            obj._fmt('moon %(a)s june%(_b)s spoon %%(a)s%(c)s %(d)s', c='CC', C='boon', d='ni'))
        self.assertRaises(AttributeError, obj._fmt, '%(c)s')  # XXX bit weird, can this be changed?


def makeSuite():
    return makeSuiteForClasses(FmtTestCase)


#noruntests
if __name__ == "__main__":
    unittest.TextTestRunner().run(makeSuite())
