__version__=''' $Id'''
__doc__='''basic tests.'''

from reportlab.test import unittest
from reportlab.test.utils import makeSuiteForClasses

class RlAccelTestCase(unittest.TestCase):
    
    def testFpStr(self):
        # should give siz decimal places if less than 1.
        # if more, give up to seven sig figs
        from _rl_accel import fp_str
        assert fp_str(1,2,3)=='1 2 3'
        assert fp_str(1) == '1'

        assert fp_str(595.275574) == '595.2756'
        assert fp_str(59.5275574) == '59.52756'
        assert fp_str(5.95275574) == '5.952756'

    def test_AsciiBase85Encode(self):
        from _rl_accel import _AsciiBase85Encode
        assert _AsciiBase85Encode('Dragan Andric')=='6ul^K@;[2RDIdd%@f~>'

    def test_AsciiBase85Decode(self):
        from _rl_accel import _AsciiBase85Decode
        assert _AsciiBase85Decode('6ul^K@;[2RDIdd%@f~>')=='Dragan Andric'

    def testEscapePDF(self):
        from _rl_accel import escapePDF
        assert escapePDF('(test)')=='\\(test\\)'
        
    def test_instanceEscapePDF(self):
        from _rl_accel import _instanceEscapePDF
        assert _instanceEscapePDF('', '(test)')=='\\(test\\)'

    def testCalcChecksum(self):
        from _rl_accel import calcChecksum
        assert calcChecksum('test')==1952805748

    def testStringWidth(self):
        pass

    def test_instanceStringWidth(self):
        pass

    def test_sameFrag(self):
        pass

    def testGetFontInfo(self):
        pass

    def testSetFontInfo(self):
        pass

def makeSuite():
    # only run the tests if _rl_accel is present
    try:
        import _rl_accel
        return makeSuiteForClasses(RlAccelTestCase)
    except ImportError:
        return None

#noruntests
if __name__ == "__main__":
    unittest.TextTestRunner().run(makeSuite())