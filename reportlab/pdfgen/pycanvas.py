# a Pythonesque Canvas v0.3
# Author : Jerome Alet - <alet@librelogiciel.com>
# License : ReportLab's license
#

__doc__ = """pycanvas.Canvas : a Canvas class which can also output Python source code.

pycanvas.Canvas class works exactly like canvas.Canvas, but you can call str() on
pycanvas.Canvas instances. Doing so will return the Python source code equivalent
to your own program, which would, when run, produce the same PDF document as
your original program.

Generated Python source code defines a doIt() function which accepts a filename
or file-like object as its single parameter. The doIt() function will generate
a PDF document and save it in the file you specified in this argument, and will
also return you the Generated Python source code, which you can run again
to produce the very same PDF document and the Python source code, which...
ad nauseam !

the reportlab/test/test_pdfgen_pycanvas.py program is the test suite for
pycanvas, you can do the following :

    $ cd reportlab/test
    $ python test_pdfgen_pycanvas.py >n1.py
    
    this will produce both n1.py and test_pdfgen_pycanvas.pdf
    
    then :
    
    $ python n1.py n1.pdf >n2.py
    $ python n2.py n2.pdf >n3.py
    $ ...
    
    n1.py, n2.py, n3.py and so on will be identical files.
    
    n1.pdf, n2.pdf, n3.pdf and so on will be PDF files
    similar to test_pdfgen_pycanvas.pdf.
    
Alternatively you can import n1.py (or n3.py, or n16384.py if you prefer)
in your own program, and then call its doIt function :

    import n1
    pythonsource = n1.doIt("myfile.pdf")
    
Why would you want to use such a beast ?
    
    - To linearize a program : optimizing some complex parts for example.
    
    - To debug : reading the generated Python source code may help you.
    
    - To create standalone scripts : say your program uses a high level
      environment to generate its output (databases, RML, etc...), using 
      this class would give you an equivalent program but with complete 
      independance from the high level environment (e.g. if you don't 
      have Oracle)
    
    - ... Insert your own ideas here ...
    
    - For fun because you can do it !
"""

import cStringIO
from reportlab.pdfgen import canvas
from reportlab.pdfgen import pathobject
from reportlab.pdfgen import textobject

PyHeader = """#! /usr/bin/env python

import sys
from reportlab.pdfgen import pycanvas
from reportlab.pdfgen import pathobject
from reportlab.pdfgen import textobject
from reportlab.lib.colors import Color

def doIt(file) :"""

PyFooter = """    return str(c)

if __name__ == "__main__" :
    if len(sys.argv) != 2 :
        sys.stderr.write("%s needs one and only one argument\\n" % sys.argv[0])
        sys.exit(-1)
    else :
        print doIt(sys.argv[1])    
        sys.exit(0)
"""
    
def buildargs(*args, **kwargs) :
    arguments = ""
    for arg in args :
        arguments += "%s, " % repr(arg)
    for (kw, val) in kwargs.items() :
        arguments += "%s=%s, " % (kw, repr(val))
    if arguments[-2:] == ", " :
        arguments = arguments[:-2]
    return arguments    

_in = 0

class Canvas :
    class TextObject :
        class Action :
            def __init__(self, parent, action) :
                self._parent = parent
                self._action = action
        
            def __getattr__(self, name) :
                return getattr(getattr(self._parent._text, self._action), name)
                
            def __call__(self, *args, **kwargs) :
                global _in
                # print "text [%s] : %i" % (self._action, _in)
                if not _in :
                    self._parent._parent._PyWrite("    t.%s(%s)" % (self._action, apply(buildargs, args, kwargs)))
                _in += 1
                retcode = apply(getattr(self._parent._text, self._action), args, kwargs)
                _in -= 1
                return retcode
        
        def __init__(self, parent) :
            self._parent = parent
            self._initdone = 0
        
        def __repr__(self) :
            return "t"
            
        def __getattr__(self, name) :
            return self.Action(self, name)
            
        def __call__(self, *args, **kwargs) :
            if not self._initdone :
                self._text = apply(textobject.PDFTextObject, (self._parent, ) + args, kwargs)
                self._parent._PyWrite("    t = c.beginText(%s)" % apply(buildargs, args, kwargs))
                self._initdone = 1
            return self
        
    class PathObject :
        class Action :
            def __init__(self, parent, action) :
                self._parent = parent
                self._action = action
                
            def __getattr__(self, name) :
                return getattr(getattr(self._parent._path, self._action), name)
        
            def __call__(self, *args, **kwargs) :
                global _in
                # print "path [%s] : %i" % (self._action, _in)
                if not _in :
                    self._parent._parent._PyWrite("    p.%s(%s)" % (self._action, apply(buildargs, args, kwargs)))
                _in += 1    
                retcode = apply(getattr(self._parent._path, self._action), args, kwargs)
                _in -= 1
                return retcode
        
        def __init__(self, parent) :
            self._parent = parent
            self._initdone = 0
        
        def __repr__(self) :
            return "p"
            
        def __getattr__(self, name) :
            return self.Action(self, name)
            
        def __call__(self, *args, **kwargs) :
            if not self._initdone :
                self._path = apply(pathobject.PDFPathObject, args, kwargs)
                self._parent._PyWrite("    p = c.beginPath(%s)" % apply(buildargs, args, kwargs))
                self._initdone = 1
            return self
        
    class Action :
        def __init__(self, parent, action) :
            self._parent = parent
            self._action = action

        def __getattr__(self, name) :
            return getattr(getattr(self._parent._canvas, self._action), name)
        
        def __call__(self, *args, **kwargs) :
            global _in
            try :
                # print "canvas [%s] : %i" % (self._action, _in)
                if (not _in) and (self._action != "__nonzero__") :
                    self._parent._PyWrite("    c.%s(%s)" % (self._action, apply(buildargs, args, kwargs)))
                _in += 1    
                retcode = apply(getattr(self._parent._canvas, self._action), args, kwargs)
                _in -= 1    
                return retcode
            except AttributeError :    # __nonzero__, but I don't know why
                _in -= 1
                return 1

    def __init__(self, *args, **kwargs) :
        self._footerpresent = 0
        self._canvas = apply(canvas.Canvas, args, kwargs)
        self._pyfile = cStringIO.StringIO()
        self._PyWrite(PyHeader)
        try :
            del kwargs["filename"]
        except KeyError :    
            pass
        self._PyWrite("    c = pycanvas.Canvas(file, %s)" % apply(buildargs, args[1:], kwargs))

    def __str__(self) :
        if not self._footerpresent :
            self._PyWrite(PyFooter)
            self._footerpresent = 1
        return self._pyfile.getvalue()

    def __getattr__(self, name) :
        if name == "beginPath" :
            return self.PathObject(self)
        elif name == "beginText" :
            return self.TextObject(self)
        else :    
            return self.Action(self, name)

    def _PyWrite(self, pycode) :
        self._pyfile.write("%s\n" % pycode)

if __name__ == '__main__':
    print 'For test scripts, look in reportlab/test'
