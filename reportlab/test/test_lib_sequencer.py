#copyright ReportLab Inc. 2000-2001
#see license.txt for license details
#history http://cvs.sourceforge.net/cgi-bin/cvsweb.cgi/reportlab/test/test_lib_sequencer.py?cvsroot=reportlab
#$Header: /tmp/reportlab/reportlab/test/test_lib_sequencer.py,v 1.6 2002/07/24 19:56:38 andy_robinson Exp $
"""Tests for the reportlab.lib.sequencer module.
"""


import sys, random

from reportlab.test import unittest
from reportlab.test.utils import makeSuiteForClasses
from reportlab.lib.sequencer import Sequencer


class SequencerTestCase(unittest.TestCase):
    "Test Sequencer usage."

    def test0(self):
        "Test sequencer default counter."

        seq = Sequencer()
        msg = 'Initial value is not zero!'
        assert seq.this() == 0, msg


    def test1(self):
        "Test incrementing default counter."

        seq = Sequencer()

        for i in range(1, 101):
            n = seq.next()
            msg = 'Sequence value is not correct!'
            assert seq.this() == n, msg


    def test2(self):
        "Test resetting default counter."

        seq = Sequencer()
        start = seq.this()

        for i in range(1, 101):
            n = seq.next()

        seq.reset()

        msg = 'Sequence value not correctly reset!'
        assert seq.this() == start, msg


    def test3(self):
        "Test incrementing dedicated counter."

        seq = Sequencer()

        for i in range(1, 101):
            n = seq.next('myCounter1')
            msg = 'Sequence value is not correct!'
            assert seq.this('myCounter1') == n, msg


    def test4(self):
        "Test resetting dedicated counter."

        seq = Sequencer()
        start = seq.this('myCounter1')

        for i in range(1, 101):
            n = seq.next('myCounter1')

        seq.reset('myCounter1')

        msg = 'Sequence value not correctly reset!'
        assert seq.this('myCounter1') == start, msg


    def test5(self):
        "Test incrementing multiple dedicated counters."

        seq = Sequencer()
        startMyCounter0 = seq.this('myCounter0')
        startMyCounter1 = seq.this('myCounter1')

        for i in range(1, 101):
            n = seq.next('myCounter0')
            msg = 'Sequence value is not correct!'
            assert seq.this('myCounter0') == n, msg
            m = seq.next('myCounter1')
            msg = 'Sequence value is not correct!'
            assert seq.this('myCounter1') == m, msg


##    def testRandom(self):
##        "Test randomly manipulating multiple dedicated counters."
##
##        seq = Sequencer()
##        counterNames = ['c0', 'c1', 'c2', 'c3']
##
##        # Init.
##        for cn in counterNames:
##            setattr(self, cn, seq.this(cn))
##            msg = 'Counter start value is not correct!'
##            assert seq.this(cn) == 0, msg
##
##        # Increment/decrement.
##        for i in range(1, 101):
##            n = seq.next('myCounter0')
##            msg = 'Sequence value is not correct!'
##            assert seq.this('myCounter0') == n, msg
##            m = seq.next('myCounter1')
##            msg = 'Sequence value is not correct!'
##            assert seq.this('myCounter1') == m, msg


def makeSuite():
    return makeSuiteForClasses(SequencerTestCase)


#noruntests
if __name__ == "__main__":
    unittest.TextTestRunner().run(makeSuite())