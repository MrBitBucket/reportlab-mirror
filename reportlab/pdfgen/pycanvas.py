# a Pythonesque Canvas v0.5
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
pycanvas, you can do the following to run it :

    First set verbose=1 in reportlab/rl_config.py
    
    then from the command interpreter :
    
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
    
    - To debug : reading the generated Python source code may help you or
      the ReportLab team to diagnose problems. The generated code is now
      clearly commented and shows nesting levels, page numbers, and so
      on. You can use the generated script when asking for support : we
      can see the results you obtain without needing your datas or complete
      application.
    
    - To create standalone scripts : say your program uses a high level
      environment to generate its output (databases, RML, etc...), using 
      this class would give you an equivalent program but with complete 
      independance from the high level environment (e.g. if you don't 
      have Oracle).
    
    - To contribute some nice looking PDF documents to the ReportLab website
      without having to send a complete application you don't want to
      distribute.
      
    - ... Insert your own ideas here ...
    
    - For fun because you can do it !
"""

import cStringIO
from reportlab.pdfgen import canvas
from reportlab.pdfgen import pathobject
from reportlab.pdfgen import textobject

PyHeader = '''#! /usr/bin/env python

import sys
from reportlab.pdfgen import pycanvas
from reportlab.pdfgen import pathobject
from reportlab.pdfgen import textobject
from reportlab.lib.colors import Color

def doIt(file) :
    """Generates a PDF document, save it into file, and returns Python source code.
    
       file : either a filename or a file-like object.
       
       returns : the equivalent Python source code as a string of text.
    """'''

PyFooter = '''
    # sends back the equivalent Python source code
    return str(c)

if __name__ == "__main__" :
    if len(sys.argv) != 2 :
        # second argument must be the name of the PDF file to create
        sys.stderr.write("%s needs one and only one argument\\n" % sys.argv[0])
        sys.exit(-1)
    else :
        # we've got a filename, we can proceed.
        print doIt(sys.argv[1])    
        sys.exit(0)
'''
    
def buildargs(*args, **kwargs) :
    arguments = ""
    for arg in args :
        arguments += "%s, " % repr(arg)
    for (kw, val) in kwargs.items() :
        arguments += "%s=%s, " % (kw, repr(val))
    if arguments[-2:] == ", " :
        arguments = arguments[:-2]
    return arguments    

# global nesting level
_in = 0

class PDFAction :
    def __init__(self, parent, action) :
        self._parent = parent
        self._action = action
    
    def __getattr__(self, name) :
        return getattr(getattr(self._parent._object, self._action), name)
        
    def __call__(self, *args, **kwargs) :
        global _in
        if not _in :
            self._parent._parent._PyWrite("    %s.%s(%s)" % (self._parent._name, self._action, apply(buildargs, args, kwargs)))
        _in += 1
        retcode = apply(getattr(self._parent._object, self._action), args, kwargs)
        _in -= 1
        return retcode
        
class PDFObject :
    _number = 0
    def __init__(self, parent) :
        self._parent = parent
        self._initdone = 0
    
    def __getattr__(self, name) :
        return PDFAction(self, name)
        
    def __repr__(self) :
        return self._name
        
    def __call__(self, *args, **kwargs) :
        if not self._initdone :
            self.__class__._number += 1
            methodname = apply(self._postinit, args, kwargs)
            self._parent._PyWrite("\n    # create PDF%sObject number %i\n    %s = %s.%s(%s)" % (methodname[5:], self.__class__._number, self._name, self._parent._name, methodname, apply(buildargs, args, kwargs)))
            self._initdone = 1
        return self
    
class Canvas :
    class TextObject(PDFObject) :
        _name = "t"
        def _postinit(self, *args, **kwargs) :
            self._object = apply(textobject.PDFTextObject, (self._parent, ) + args, kwargs)
            return "beginText"
        
    class PathObject(PDFObject) :
        _name = "p"
        def _postinit(self, *args, **kwargs) :
            self._object = apply(pathobject.PDFPathObject, args, kwargs)
            return "beginPath"
        
    class Action(PDFAction) :
        def __call__(self, *args, **kwargs) :
            global _in
            try :
                if (not _in) and (self._action != "__nonzero__") :
                    if self._action == "showPage" :
                        self._parent._PyWrite("\n    # Ends page %i" % self._parent._pagenumber)
                    elif self._action == "saveState" :    
                        state = {}
                        d = self._parent._object.__dict__
                        for name in self._parent._object.STATE_ATTRIBUTES:
                            state[name] = d[name] 
                        self._parent._PyWrite("\n    # Saves context level %i %s" % (self._parent._contextlevel, state))
                        self._parent._contextlevel += 1
                    elif self._action == "restoreState" :    
                        self._parent._contextlevel -= 1
                        self._parent._PyWrite("\n    # Restores context level %i %s" % (self._parent._contextlevel, self._parent._object.state_stack[-1]))
                    elif self._action == "beginForm" :    
                        self._parent._formnumber += 1
                        self._parent._PyWrite("\n    # Begins form %i" % self._parent._formnumber)
                    elif self._action == "endForm" :    
                        self._parent._PyWrite("\n    # Ends form %i" % self._parent._formnumber)
                    elif self._action == "save" :    
                        self._parent._PyWrite("\n    # Saves the PDF document to disk")
                        
                    self._parent._PyWrite("    %s.%s(%s)" % (self._parent._name, self._action, apply(buildargs, args, kwargs)))
                    
                    if self._action == "showPage" :
                        self._parent._pagenumber += 1
                        self._parent._PyWrite("\n    # Begins page %i" % self._parent._pagenumber)
                    elif self._action == "endForm" :    
                        self._parent._PyWrite("")
                _in += 1    
                retcode = apply(getattr(self._parent._object, self._action), args, kwargs)
                _in -= 1    
                return retcode
            except AttributeError :    # __nonzero__, but I don't know why
                _in -= 1
                return 1

    _name = "c"
    def __init__(self, *args, **kwargs) :
        self._contextlevel = 0
        self._pagenumber = 1
        self._formnumber = 0
        self._footerpresent = 0
        self._object = apply(canvas.Canvas, args, kwargs)
        self._pyfile = cStringIO.StringIO()
        self._PyWrite(PyHeader)
        try :
            del kwargs["filename"]
        except KeyError :    
            pass
        self._PyWrite("    # create the PDF document\n    %s = pycanvas.Canvas(file, %s)\n\n    # Begins page 1" % (self._name, apply(buildargs, args[1:], kwargs)))

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
