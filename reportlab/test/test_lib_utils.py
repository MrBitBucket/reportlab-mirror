"""Tests for reportlab.lib.utils
"""
import os
import reportlab
from reportlab.test import unittest
from reportlab.test.utils import makeSuiteForClasses
from reportlab.lib import colors
from reportlab.lib.utils import recursiveImport, \
                                 recursiveGetAttr, \
                                recursiveSetAttr



class ImporterTestCase(unittest.TestCase):
    "Test import utilities"

    def test1(self):
        "try stuff known to be in the path"
        m1 = recursiveImport('reportlab.pdfgen.canvas')
        import reportlab.pdfgen.canvas
        assert m1 == reportlab.pdfgen.canvas

    def test2(self):
        "try under a directory NOT on the path"
        D = os.path.join(os.path.dirname(reportlab.__file__), 'tools','pythonpoint')
        fn = os.path.join(D,'stdparser.py')
        if os.path.isfile(fn) or os.path.isfile(fn+'c') or os.path.isfile(fn+'o'):
            m1 = recursiveImport('stdparser', baseDir=D)
        
    def test3(self):
        "ensure CWD is on the path"
        rlDir = os.path.dirname(reportlab.__file__)
        testDir = os.path.join(rlDir, 'test')
        cwd = os.getcwd()
        os.chdir(testDir)
        m1 = recursiveImport('test_lib_colors')

    def test4(self):
        "ensure noCWD removes current dir from path"
        rlDir = os.path.dirname(reportlab.__file__)
        testDir = os.path.join(rlDir, 'test')
        cwd = os.getcwd()
        os.chdir(testDir)
        self.assertRaises(ImportError,
                          recursiveImport,
                          'test_lib_colors',
                          noCWD=1)

    def test5(self):
        "recursive attribute setting/getting on modules"
        import reportlab.lib.units
        inch = recursiveGetAttr(reportlab, 'lib.units.inch')
        assert inch == 72

        recursiveSetAttr(reportlab, 'lib.units.cubit', 18*inch)        
        cubit = recursiveGetAttr(reportlab, 'lib.units.cubit')
        assert cubit == 18*inch

    def test6(self):
        "recursive attribute setting/getting on drawings"
        from reportlab.graphics.charts.barcharts import sampleH1
        drawing = sampleH1()
        recursiveSetAttr(drawing, 'barchart.valueAxis.valueMax', 72)
        theMax = recursiveGetAttr(drawing, 'barchart.valueAxis.valueMax')
        assert theMax == 72
        

        
        
        
        


def makeSuite():
    return makeSuiteForClasses(ImporterTestCase)


#noruntests
if __name__ == "__main__":
    unittest.TextTestRunner().run(makeSuite())
