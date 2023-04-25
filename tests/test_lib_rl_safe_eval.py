#Copyright ReportLab Europe Ltd. 2000-2017
#see license.txt for license details
"""Tests for reportlab.lib.rl_safe_eval
"""
__version__='3.5.33'
from reportlab.lib.testutils import setOutDir,makeSuiteForClasses, printLocation
setOutDir(__name__)
import os, time, sys
import reportlab
from reportlab import rl_config
import unittest
from reportlab.lib import colors
from reportlab.lib.utils import rl_safe_eval, rl_safe_exec, annotateException, rl_extended_literal_eval
from reportlab.lib.rl_safe_eval import BadCode

testObj = [1,('a','b',2),{'A':1,'B':2.0},"32"]
class TestClass:
    a = 1
    format = 3
testInst = TestClass()
def testFunc(bad=False):
    return open('/tmp/myfile','r') if bad else testObj

class SafeEvalTestSequenceMeta(type):
    def __new__(cls, name, bases, cdict):
        def genTest(kind, expr,**kwds):
            def test(self):
                getattr(self,kind+'s')(expr,**kwds)
            return test

        for kind, _data in (
                (
                'work',
                (
                '[i for i in range(10)]',
                '3**4',
                '3*"A"',
                '3+4',
                '(3,4)',
                'SafeEvalTestCase',
                ("testObj",dict(g=dict(testObj=testObj))),
                "(lambda x,y:[x,y])('a',2)",
                "(lambda x:[x])(2)",
                "(lambda *args:[args])(2)",
                "(lambda y: (lambda f:f(y))(lambda x: x+1))(2)",
                "(lambda f: lambda n: (1,(1,(1,(1,f(n-1))))) if n else 1)(lambda x:x)(5)",
                "((lambda f: (lambda x: x(x))(lambda y: f(lambda *args: y(y)(*args)))) (lambda f: lambda n: (1,(1,(1,(1,f(n-1))))) if n else 1)(30))",
                'list(range(1000))[1:1000:100]',
                'tuple(range(1000))[1:1000:100]',
                'dict(a=1)["a"]',
                'dict(a=1).setdefault("a",2)',
                'dict(a=1).get("a",2)',
                'dict(a=1).pop("a",2)',
                '{"_":1+_ for _ in (1,2)}.pop(1,None)',
                '1 if True else "a"',
                '1 if False else "a"',
                'testFunc(bad=False)',
                '(min([1]),min(1,2),max([1]),max(1,2))',
                '(sum((1,2,3)),sum((1,2,3),-1))',
                'list(enumerate((1,2,3)))',
                'list(zip((1,2,3),("a","b","c")))',
                '(hasattr(testInst,"b"),hasattr(testInst,"a"))',
                'list(map(lambda x: (x+13,chr(x)),(1,2,3,4)))',
                '(any([1]),any([]),all([]),all([1,None]),all([1,2]))',
                '(getattr(testInst,"a"),getattr(testInst,"a",12),getattr(testInst,"xxx",13))',
                'list(sorted([3,4,1,2,0],reverse=True))',
                'list(reversed([3,4,1,2,0]))',
                'list(range(1,10,3))',
                '({1,2,3},set([4,5,6]),frozenset([7,8,9]),{i for i in range(1,10,3)})',
                '"%s%s" % (1,2)',
                )
                ),
                (
                'fail',
                (
                'vars()',
                '(type(1),type(str),type(testObj),type(TestClass))',
                'open("/tmp/myfile")',
                'SafeEvalTestCase.__module__',
                ("testInst.__class__.__bases__[0].__subclasses__()",dict(g=dict(testInst=testInst))),
                "10**200**200",
                "pow(10,200)",
                '__import__("reportlab")',
                ('(lambda i: [i for i in ((i, 1) for j in range(1000000))][-1])(1)',dict(timeout=0.1)),
                ('[i for i in ((j, 1) for j in range(1000000))][-1]',dict(timeout=0.1)),
                ('''((lambda f: (lambda x: x(x))(lambda y: f(lambda *args: y(y)(*args)))) (lambda f: lambda n: (1,(1,(1,(1,f(n-1))))) if n else 1)(300))''',
                        dict(timeout=0.1,exception=RuntimeError)),
                'dict(__class__=1)["__class__"]',
                'dict(a=1).setdefault("__class__",2)',
                'dict(a=1).get("__class__",2)',
                'dict(a=1).pop("__class__",2)',
                '{"__class__":1}["__class__"]',
                '{"__class__":1}.setdefault("__class__",2)',
                '{"__class__":1}.get("__class__",2)',
                '{"__class__":1}.pop("__class__",2)',
                '{"_":1 for _ in (1,2)}.pop("__class__",2)',
                'type("Devil",[dict],{__init__:lambda self:self.__class__})',
                'testFunc(bad=True)',
                'getattr(testInst,"__class__",14)',
                '"{1}{2}".format(1,2)',
                'builtins',
                '[ [ [ [ ftype(ctype(0, 0, 0, 0, 3, 67, b"t\\x00d\\x01\\x83\\x01\\xa0\\x01d\\x02\\xa1\\x01\\x01\\x00d\\x00S\\x00", (None, "os", "touch /tmp/exploited"), ("__import__", "system"), (), "<stdin>", "", 1, b"\\x12\\x01"), {})() for ftype in [type(lambda: None)] ] for ctype in [type(getattr(lambda: {None}, Word("__code__")))] ] for Word in [orgTypeFun("Word", (str,), { "mutated": 1, "startswith": lambda self, x: False, "__eq__": lambda self,x: self.mutate() and self.mutated < 0 and str(self) == x, "mutate": lambda self: {setattr(self, "mutated", self.mutated - 1)}, "__hash__": lambda self: hash(str(self)) })] ] for orgTypeFun in [type(type(1))]] and "red"',
                )
                ),
                ):
            tfmt = 'test_ExpectedTo%s_%%02d' % kind.capitalize()
            for i, expr in enumerate(_data):
                if expr is None:
                    continue #test = genTest('skip','')
                else:
                    expr, kwds = expr if isinstance(expr,tuple) else (expr,{})
                    test = genTest(kind, expr,**kwds)
                cdict[tfmt%i] = test
        return type.__new__(cls, name, bases, cdict)

def addMeta(mcs):
    def wrap(cls):
        ov = cls.__dict__.copy()
        sl = ov.get('__slots__')
        if sl is not None:
            if isinstance(sl, str):
                sl = [sl]
            for slv in sl:
                ov.pop(slv)
        ov.pop('__dict__', None)
        ov.pop('__weakref__', None)
        if hasattr(cls, '__qualname__'):
            ov['__qualname__'] = cls.__qualname__
        return mcs(cls.__name__, cls.__bases__, ov)
    return wrap

@addMeta(SafeEvalTestSequenceMeta)
class SafeEvalTestCase(unittest.TestCase):
    def works(self, expr, g=None, l=None):
        try:
            answer = eval(expr,g,l)
            result = rl_safe_eval(expr,g,l)
        except:
            print('expr=%r' % expr)
            annotateException('\nexpr=%r\n' % expr)
        self.assertEqual(answer,result,"rl_safe_eval(%r) = %r not expected %r" % (expr,result,answer))
    def skips(self,*args,**kwds):
        raise unittest.SkipTest
    def fails(self, expr, g=None, l=None, timeout=None, exception=BadCode):
        try:
            result = rl_safe_eval(expr,g,l,timeout=timeout)
            self.assertEqual(True,False,"rl_safe_eval(%r)=%r did not raise %s" % (expr,result,exception.__name__))
        except exception:
            return
        except:
            self.assertEqual(True,False,"rl_safe_eval(%r) raised %s: %s instead of %s" % (expr,sys.exc_info()[0].__name__,str(sys.exc_info()[1]),exception.__name__))

GA = 'ga'
class SafeEvalTestBasics(unittest.TestCase):
    def test_001(self):
        A=3
        self.assertTrue(rl_safe_eval("A==3"))
    def test_002(self):
        self.assertTrue(rl_safe_eval("GA=='ga'"))

class ExtendedLiteralEval(unittest.TestCase):
    def test_001(self):
        S = colors.getAllNamedColors().copy()
        C = {s:getattr(colors,s) for s in '''Blacker CMYKColor CMYKColorSep Color ColorType HexColor PCMYKColor PCMYKColorSep Whiter
                        _chooseEnforceColorSpace _enforceCMYK _enforceError _enforceRGB _enforceSEP _enforceSEP_BLACK
                        _enforceSEP_CMYK _namedColors _re_css asNative cmyk2rgb cmykDistance color2bw colorDistance
                        cssParse describe fade fp_str getAllNamedColors hsl2rgb hue2rgb linearlyInterpolatedColor
                        obj_R_G_B opaqueColor rgb2cmyk setColors toColor toColorOrNone'''.split()
                        if callable(getattr(colors,s,None))}
        def showVal(s):
            try:
                r = rl_extended_literal_eval(s,C,S)
            except:
                r = str(sys.exc_info()[1])
            return r

        for expr, expected in (
                ('1.0', 1.0),
                ('1', 1),
                ('red', colors.red),
                ('True', True),
                ('False', False),
                ('None', None),
                ('Blacker(red,0.5)', colors.Color(.5,0,0,1)),
                ('PCMYKColor(21,10,30,5,spotName="ABCD")', colors.PCMYKColor(21,10,30,5,spotName='ABCD',alpha=100)),
                ('HexColor("#ffffff")', colors.Color(1,1,1,1)),
                ('linearlyInterpolatedColor(red, blue, 0, 1, 0.5)', colors.Color(.5,0,.5,1)),
                ('red.rgb()', 'Bad expression'),
                ('__import__("sys")', 'Bad expression'),
                ('globals()', 'Bad expression'),
                ('locals()', 'Bad expression'),
                ('vars()', 'Bad expression'),
                ('builtins', 'Bad expression'),
                ('__file__', 'Bad expression'),
                ('__name__', 'Bad expression'),
                ):
            self.assertEqual(showVal(expr),expected,f"rl_extended_literal_eval({expr!r}) is not equal to expected {expected}")

def makeSuite():
    return makeSuiteForClasses(SafeEvalTestCase,SafeEvalTestBasics,ExtendedLiteralEval)

if __name__ == "__main__": #noruntests
    unittest.TextTestRunner().run(makeSuite())
    printLocation()
