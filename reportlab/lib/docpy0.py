#!/usr/bin/env python

"""Generate documentation from live Python objects.

This is an evolving module that allows to generated documentation
for python modules in an automated fashion. The idea is to take
live Python objects and inspect them in order to use as much mean-
ingful information as possible to write in some formatted way into
different types of documents.

In principle a skeleton captures the gathered information and
makes it available via a certain API to formatters that use it
in whatever way they like to produce something of interest. The
API allows for adding behaviour in subclasses of these formatters,
such that, e.g. for certain classes it is possible to trigger
special actions like displaying a sample image of a class that
represents some graphical widget, say.

Type the following for usage info:

  python docpy0.py -h
"""

# Much inspired by Ka-Ping Yee's htmldoc.py.
# Needs his inspect module.

# Dinu Gherman

import sys, os, re, types, string, getopt
from string import find, join, split, replace, expandtabs, rstrip

from reportlab.pdfgen import canvas
from reportlab.lib import inspect
from reportlab.lib.units import inch, cm
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus.flowables import Flowable, Spacer
from reportlab.platypus.paragraph import Paragraph
from reportlab.platypus.flowables \
     import Flowable, Preformatted,Spacer, Image, KeepTogether
from reportlab.platypus.xpreformatted import XPreformatted
from reportlab.platypus.frames import Frame
from reportlab.platypus.doctemplate \
     import PageTemplate, BaseDocTemplate
from reportlab.platypus.tables import TableStyle, Table

# Needed to draw widget demos.

from reportlab.graphics import shapes
from reportlab.graphics.widgetbase import Widget
from reportlab.graphics import renderPDF

# Ignore if no GD rendering available.

try:
    from rlextra.graphics import renderGD
except ImportError:
    pass


####################################################################
# 
# Stuff needed for building PDF docs.
# 
####################################################################

def mainPageFrame(canvas, doc):
    "The page frame used for all PDF documents."
    
    canvas.saveState()
    canvas.setFont('Times-Roman', 12)
    canvas.drawString(4 * inch, cm, "%d" % canvas.getPageNumber())
    canvas.restoreState()
    

class MyTemplate(BaseDocTemplate):
    "The document template used for all PDF documents."
    
    _invalidInitArgs = ('pageTemplates',)
    
    def __init__(self, filename, **kw):
        frame1 = Frame(inch, inch, 6*inch, 9.7*inch, id='F1')
        self.allowSplitting = 0
        apply(BaseDocTemplate.__init__, (self, filename), kw)
        self.addPageTemplates(PageTemplate('normal', [frame1], mainPageFrame))

    def afterFlowable(self, flowable):
        if flowable.__class__.__name__ == 'Paragraph':
            f = flowable
            if f.style.name[:7] == 'Heading':
                # Add line height to current vert. position.
                c = self.canv
                title = f.text
                key = str(hash(f))
                lev = int(f.style.name[7:]) #- 1
                try:
                    if lev == 0:
                        isClosed = 0
                    else:
                        isClosed = 1

                    c.bookmarkPage(key)
                    c.addOutlineEntry(title, key, level=lev,
                                      closed=isClosed)
                except:
                    pass


####################################################################
# 
# Utility functions (Ka-Ping Yee).
# 
####################################################################

def _htmlescape(text):
    "Escape special HTML characters, namely &, <, >."
    return replace(replace(replace(text, '&', '&amp;'),
                                         '<', '&lt;'),
                                         '>', '&gt;')

def _htmlrepr(object):
    return _htmlescape(repr(object))


def _defaultformat(object):
    return '=' + _htmlrepr(object)


def _getdoc(object):
    result = inspect.getdoc(object)
    if not result:
        try:
            result = inspect.getcomments(object)
        except:
            pass
    return result and rstrip(result) + '\n' or ''


def _reduceDocStringLength(docStr):
    "Return first line of a multiline string."
    
    return split(docStr, '\n')[0]


####################################################################
# 
# More utility functions (Andy Robinson & Dinu Gherman).
# 
####################################################################

def makeHtmlSection(text, bgcolor='#FFA0FF'):
    """Create HTML code for a section.

    This is usually a header for all classes or functions.
    """
    text = _htmlescape(expandtabs(text))
    result = []
    result.append("""<TABLE WIDTH="100\%" BORDER="0">""")
    result.append("""<TR><TD BGCOLOR="%s" VALIGN="CENTER">""" % bgcolor)
    result.append("""<H2>%s</H2>""" % text)
    result.append("""</TD></TR></TABLE>""")
    result.append('')

    return join(result, '\n')


def makeHtmlSubSection(text, bgcolor='#AAA0FF'):
    """Create HTML code for a subsection.

    This is usually a class or function name.
    """
    text = _htmlescape(expandtabs(text))
    result = []
    result.append("""<TABLE WIDTH="100\%" BORDER="0">""")
    result.append("""<TR><TD BGCOLOR="%s" VALIGN="CENTER">""" % bgcolor)
    result.append("""<H3><TT><FONT SIZE="+2">%s</FONT></TT></H3>""" % text)
    result.append("""</TD></TR></TABLE>""")
    result.append('')

    return join(result, '\n')


def makeHtmlInlineImage(text):
    """Create HTML code for an inline image.
    """

    return """<IMG SRC="%s" ALT="%s">""" % (text, text)


def indentLevel(line, spacesPerTab=4):
    """Counts the indent levels on the front

    It is assumed that one tab equals 4 spaces.
    """
    x = 0
    nextTab = 4
    for ch in line:
        if ch == ' ':
            x = x + 1
        elif ch == '\t':
            x = nextTab
            nextTab = x + spacesPerTab
        else:
            return x


assert indentLevel('hello') == 0, 'error in indentLevel'
assert indentLevel(' hello') == 1, 'error in indentLevel'
assert indentLevel('  hello') == 2, 'error in indentLevel'
assert indentLevel('   hello') == 3, 'error in indentLevel'
assert indentLevel('\thello') == 4, 'error in indentLevel'
assert indentLevel(' \thello') == 4, 'error in indentLevel'
assert indentLevel('\t hello') == 5, 'error in indentLevel'


# This may well be replaceable by something in the inspect module.
def getFunctionBody(f, linesInFile):
    """Pass in the function object and the lines in the file.

    Since we will typically grab several things out of
    the same file.  it extracts a multiline text block.
    Works with methods too."""

    if hasattr(f, 'im_func'):
        #it's a method, drill down and get its function
        f = f.im_func

    extracted = []    
    firstLineNo = f.func_code.co_firstlineno - 1
    startingIndent = indentLevel(linesInFile[firstLineNo])
    extracted.append(linesInFile[firstLineNo])
    #brackets = 0
    for line in linesInFile[firstLineNo+1:]:
        ind = indentLevel(line)
        if ind <= startingIndent:
            break
        else:
            extracted.append(line)
         # we are not indented
    return string.join(extracted, '\n')

    # ???
    usefulLines = lines[firstLineNo:lineNo+1]
    return string.join(usefulLines, '\n')


####################################################################
# 
# Core "standard" docpy classes
# 
####################################################################

class Skeleton0:
    """A class collecting 'interesting' information about a module."""

    def __init__(self):
        # This is an ad-hoc, somewhat questionable 'data structure',
        # but for the time being it serves its purpose...
        self.module = {}
        self.functions = {}
        self.classes = {}


    # Might need more like this, later.
    def getModuleName(self):
        """Return the name of the module being treated."""

        return self.module['name']


    # These inspect methods all rely on the inspect module.
    def inspect(self, object):
        """Collect information about a given object."""

        self.moduleSpace = object

        # Very non-OO, left for later...        
        if inspect.ismodule(object):
            self._inspectModule(object)
        elif inspect.isclass(object):
            self._inspectClass(object)
        elif inspect.ismethod(object):
            self._inspectMethod(object)
        elif inspect.isfunction(object):
            self._inspectFunction(object)
        elif inspect.isbuiltin(object):
            self._inspectBuiltin(object)
        else:
            msg = "Don't know how to document this kind of object."
            raise TypeError, msg


    def _inspectModule(self, object):
        """Collect information about a given module object."""

        name = object.__name__

        self.module['name'] = name
        if hasattr(object, '__version__'):
            self.module['version'] = object.__version__

        cadr = lambda list: list[1]
        modules = map(cadr, inspect.getmembers(object, inspect.ismodule))

        classes, cdict = [], {}
        for key, value in inspect.getmembers(object, inspect.isclass):
            if (inspect.getmodule(value) or object) is object:
                classes.append(value)
                cdict[key] = cdict[value] = '#' + key

        functions, fdict = [], {}
        for key, value in inspect.getmembers(object, inspect.isroutine):
            if inspect.isbuiltin(value) or inspect.getmodule(value) is object:
                functions.append(value)
                fdict[key] = '#-' + key
                if inspect.isfunction(value): fdict[value] = fdict[key]

        for c in classes:
            for base in c.__bases__:
                key, modname = base.__name__, base.__module__
                if modname != name and sys.modules.has_key(modname):
                    module = sys.modules[modname]
                    if hasattr(module, key) and getattr(module, key) is base:
                        if not cdict.has_key(key):
                            cdict[key] = cdict[base] = modname + '.txt#' + key

        doc = _getdoc(object) or 'No doc string.'
        self.module['doc'] = doc

        if modules:
            self.module['importedModules'] = map(lambda m:m.__name__, modules)

        if classes:
            for item in classes:
                self._inspectClass(item, fdict, cdict)

        if functions:
            for item in functions:
                self._inspectFunction(item, fdict, cdict)


    def _inspectClass(self, object, functions={}, classes={}):
        """Collect information about a given class object."""

        name = object.__name__
        bases = object.__bases__
        results = []
        
        if bases:
            parents = []
            for base in bases:
                parents.append(base)

        self.classes[name] = {}
        if bases:
            self.classes[name]['bases'] = parents

        methods, mdict = [], {}
        for key, value in inspect.getmembers(object, inspect.ismethod):
            methods.append(value)
            mdict[key] = mdict[value] = '#' + name + '-' + key

        if methods:
            if not self.classes[name].has_key('methods'):
                self.classes[name]['methods'] = {}
            for item in methods:
                self._inspectMethod(item, functions, classes, mdict, name)

        doc = _getdoc(object) or 'No doc string.'
        self.classes[name]['doc'] = doc


    def _inspectMethod(self, object, functions={}, classes={}, methods={}, clname=''):
        """Collect information about a given method object."""

        self._inspectFunction(object.im_func, functions, classes, methods, clname)


    def _inspectFunction(self, object, functions={}, classes={}, methods={}, clname=''):
        """Collect information about a given function object."""

        try:
            args, varargs, varkw, defaults = inspect.getargspec(object)
            argspec = inspect.formatargspec(
                args, varargs, varkw, defaults,
                defaultformat=_defaultformat)
        except TypeError:
            argspec = '( ... )'
        
        doc = _getdoc(object) or 'No doc string.'

        if object.__name__ == '<lambda>':
            decl = [' lambda  ', argspec[1:-1]]
            # print '  %s' % decl
            # Do something with lambda functions as well...
            # ...
        else:
            decl = object.__name__
            if not clname:
                self.functions[object.__name__] = {'signature':argspec, 'doc':doc}
            else:
                theMethods = self.classes[clname]['methods']
                if not theMethods.has_key(object.__name__):
                    theMethods[object.__name__] = {}

                theMethod = theMethods[object.__name__]                
                theMethod['signature'] = argspec
                theMethod['doc'] = doc


    # Not used/tested.
    def _inspectBuiltin(self, object):
        """Collect information about a given built-in."""

        print object.__name__ + '( ... )'


    def walk(self, formatter):
        """Call event methods in a visiting formatter."""

        s = self
        f = formatter

        # The order is fixed, but could be made flexible
        # with one more template method...
        
        # Module
        modName = s.module['name'] 
        modDoc = s.module['doc']
        imported = s.module.get('importedModules', [])
        imported.sort()
        # f.indentLevel = f.indentLevel + 1
        f.beginModule(modName, modDoc, imported)

        # Classes
        f.indentLevel = f.indentLevel + 1
        f.beginClasses(s.classes.keys())
        items = s.classes.items()
        items.sort()
        for k, v in items:
            cDoc = s.classes[k]['doc']
            bases = s.classes[k].get('bases', [])
            f.indentLevel = f.indentLevel + 1
            f.beginClass(k, cDoc, bases)

            # This if should move out of this method. 
            if not s.classes[k].has_key('methods'):
                s.classes[k]['methods'] = {}

            # Methods
            #f.indentLevel = f.indentLevel + 1
            f.beginMethods(s.classes[k]['methods'].keys())
            #if s.classes[k].has_key('methods'):
            items = s.classes[k]['methods'].items()
            items.sort()
            for m, v in items:
                mDoc = v['doc']
                sig = v['signature']
                f.indentLevel = f.indentLevel + 1
                f.beginMethod(m, mDoc, sig)
                f.indentLevel = f.indentLevel - 1
                f.endMethod(m, mDoc, sig)

            #f.indentLevel = f.indentLevel - 1
            f.endMethods(s.classes[k]['methods'].keys())

            f.indentLevel = f.indentLevel - 1
            f.endClass(k, cDoc, bases)

            # And what about attributes?!

        f.indentLevel = f.indentLevel - 1
        f.endClasses(s.classes.keys())

        # Functions
        f.indentLevel = f.indentLevel + 1
        f.beginFunctions(s.functions.keys())
        items = s.functions.items()
        items.sort()
        for k, v in items:
            doc = v['doc']
            sig = v['signature']
            f.indentLevel = f.indentLevel + 1
            f.beginFunction(k, doc, sig)
            f.indentLevel = f.indentLevel - 1
            f.endFunction(k, doc, sig)
        f.indentLevel = f.indentLevel - 1
        f.endFunctions(s.functions.keys())
        
        #f.indentLevel = f.indentLevel - 1
        f.endModule(modName, modDoc, imported)

        # Constants?!


####################################################################
# 
# Core "standard" docpy document builders
# 
####################################################################

class DocBuilder0:
    """An abstract class to document the skeleton of a Python module.

    Instances take a skeleton instance s and call their s.walk()
    method. The skeleton, in turn, will walk over its tree structure
    while generating events and calling equivalent methods from a
    specific interface (begin/end methods).
    """

    fileSuffix = None
    
    def __init__(self, skeleton=None):
        self.skeleton = skeleton
        self.packageName = None
        self.indentLevel = 0
        

    def write(self, skeleton=None):
        if skeleton:
            self.skeleton = skeleton
        self.skeleton.walk(self)


    # Event-method API, called by associated skeleton instances.

    # The following four methods are *not* called by skeletons!
    def begin(self): pass
    def end(self): pass

    def beginPackage(self, name):
        self.packageName = name
        
    def endPackage(self, name):
        pass

    # Only this subset is really called by associated skeleton instances.

    def beginModule(self, name, doc, imported): pass
    def endModule(self, name, doc, imported): pass

    def beginClasses(self, names): pass
    def endClasses(self, names): pass
    
    def beginClass(self, name, doc, bases): pass
    def endClass(self, name, doc, bases): pass
    
    def beginMethods(self, names): pass
    def endMethods(self, names): pass

    def beginMethod(self, name, doc, sig): pass
    def endMethod(self, name, doc, sig): pass

    def beginFunctions(self, names): pass
    def endFunctions(self, names): pass
    
    def beginFunction(self, name, doc, sig): pass
    def endFunction(self, name, doc, sig): pass


class AsciiDocBuilder0(DocBuilder0):
    """Document the skeleton of a Python module in ASCII format.

    The output will be an ASCII file with nested lines representing
    the hiearchical module structure.

    Currently, no doc strings are listed."""

    fileSuffix = '.txt'
    outLines = []
    indentLabel = '  '
    
    def end(self):
        if self.packageName:
            path = self.packageName + self.fileSuffix
        elif self.skeleton:
            path = self.skeleton.getModuleName() + self.fileSuffix
        else:
            path = ''
            
        if path:
            file = open(path, 'w')
            for line in self.outLines:
                file.write(line + '\n')
            file.close()


    def beginPackage(self, name):
        DocBuilder0.beginPackage(self, name)
        lev, label = self.indentLevel, self.indentLabel
        self.outLines.append('%sPackage: %s' % (lev*label, name))
        self.outLines.append('')


    def beginModule(self, name, doc, imported):
        append = self.outLines.append
        lev, label = self.indentLevel, self.indentLabel
        self.outLines.append('%sModule: %s' % (lev*label, name))
##        self.outLines.append('%s%s' % ((lev+1)*label, _reduceDocStringLength(doc)))
        append('')

        if imported:
            self.outLines.append('%sImported' % ((lev+1)*label))
            append('')
            for m in imported:
                self.outLines.append('%s%s' % ((lev+2)*label, m))
            append('')


    def beginClasses(self, names):
        if names:
            lev, label = self.indentLevel, self.indentLabel
            self.outLines.append('%sClasses' % (lev*label))
            self.outLines.append('')


    def beginClass(self, name, doc, bases):
        append = self.outLines.append
        lev, label = self.indentLevel, self.indentLabel

        if bases:
            bases = map(lambda b:b.__name__, bases) # hack
            append('%s%s(%s)' % (lev*label, name, join(bases, ', ')))
        else:
            append('%s%s' % (lev*label, name))
        return

##        append('%s%s' % ((lev+1)*label, _reduceDocStringLength(doc)))
        self.outLines.append('')


    def endClass(self, name, doc, bases):
        self.outLines.append('')


    def beginMethod(self, name, doc, sig):
        append = self.outLines.append
        lev, label = self.indentLevel, self.indentLabel
        append('%s%s%s' % (lev*label, name, sig))
##        append('%s%s' % ((lev+1)*label, _reduceDocStringLength(doc)))
##        append('')


    def beginFunctions(self, names):
        if names:
            lev, label = self.indentLevel, self.indentLabel
            self.outLines.append('%sFunctions' % (lev*label))
            self.outLines.append('')


    def endFunctions(self, names):
        self.outLines.append('')


    def beginFunction(self, name, doc, sig):
        append = self.outLines.append
        lev, label = self.indentLevel, self.indentLabel
        self.outLines.append('%s%s%s' % (lev*label, name, sig))
##        append('%s%s' % ((lev+1)*label, _reduceDocStringLength(doc)))
##        append('')


class HtmlDocBuilder0(DocBuilder0):
    "A class to write the skeleton of a Python source in HTML format."

    fileSuffix = '.html'
    outLines = []

    def begin(self):
        self.outLines.append("""<!doctype html public "-//W3C//DTD HTML 4.0 Transitional//EN">""")
        self.outLines.append("""<html>""")
    

    def end(self):
        if self.packageName:
            path = self.packageName + self.fileSuffix
        elif self.skeleton:
            path = self.skeleton.getModuleName() + self.fileSuffix
        else:
            path = ''
            
        if path:
            file = open(path, 'w')
            self.outLines.append('</body></html>')
            for line in self.outLines:
                file.write(line + '\n')
            file.close()

    
    def beginPackage(self, name):
        DocBuilder0.beginPackage(self, name)

        self.outLines.append("""<title>%s</title>""" % name)
        self.outLines.append("""<body bgcolor="#ffffff">""")
        self.outLines.append("""<H1>%s</H1>""" % name)
        self.outLines.append('')


    def beginModule(self, name, doc, imported):
        if not self.packageName:
            self.outLines.append("""<title>%s</title>""" % name)
            self.outLines.append("""<body bgcolor="#ffffff">""")

        self.outLines.append("""<H1>%s</H1>""" % name)
        self.outLines.append('')
        for line in split(doc, '\n'):
            self.outLines.append("""<FONT SIZE="-1">%s</FONT>""" % _htmlescape(line))
            self.outLines.append('<BR>')
        self.outLines.append('')

        if imported:
            self.outLines.append(makeHtmlSection('Imported Modules'))
            self.outLines.append("""<ul>""")
            for m in imported:
                self.outLines.append("""<li>%s</li>""" % m)
            self.outLines.append("""</ul>""")


    def beginClasses(self, names):
        self.outLines.append(makeHtmlSection('Classes'))


    def beginClass(self, name, doc, bases):
        DocBuilder0.beginClass(self, name, doc, bases)

        # Keep an eye on the base classes.
        self.currentBaseClasses = bases

        if bases:
            self.outLines.append(makeHtmlSubSection('%s(%s)' % (name, join(bases, ', '))))
        else:
            self.outLines.append(makeHtmlSubSection('%s' % name))
        for line in split(doc, '\n'):
            self.outLines.append("""<FONT SIZE="-1">%s</FONT>""" % _htmlescape(line))
            self.outLines.append('<BR>')

        self.outLines.append('')


    def beginMethods(self, names):
        if names:
            self.outLines.append('<H3>Method Interface</H3>')
            self.outLines.append('')


    def beginMethod(self, name, doc, sig):
        self.beginFunction(name, doc, sig)


    def beginFunctions(self, names):
        self.outLines.append(makeHtmlSection('Functions'))


    def beginFunction(self, name, doc, sig):
        append = self.outLines.append
        append("""<DL><DL><DT><TT><STRONG>%s</STRONG>%s</TT></DT>""" % (name, sig))
        append('')
        for line in split(doc, '\n'):
            append("""<DD><FONT SIZE="-1">%s</FONT></DD>""" % _htmlescape(line))
            append('<BR>')
        append('</DL></DL>')
        append('')


class PdfDocBuilder0(DocBuilder0):
    "Document the skeleton of a Python module in PDF format."

    fileSuffix = '.pdf'

    def makeHeadingStyle(self, level, typ=None):
        "Make a heading style for different types of module content."

        if typ in ('package', 'module', 'class'):
            style = ParagraphStyle(name='Heading'+str(level),
                                      fontName = 'Courier-Bold',
                                      fontSize=14,
                                      leading=18,
                                      spaceBefore=12,
                                      spaceAfter=6)
        elif typ in ('method', 'function'):
            style = ParagraphStyle(name='Heading'+str(level),
                                      fontName = 'Courier-Bold',
                                      fontSize=12,
                                      leading=18,
                                      firstLineIndent=18,
                                      spaceBefore=12,
                                      spaceAfter=6)
        else:
            style = ParagraphStyle(name='Heading'+str(level),
                                      fontName = 'Times-Bold',
                                      fontSize=14,
                                      leading=18,
                                      spaceBefore=12,
                                      spaceAfter=6)
            
        return style
    
    
    def begin(self):
        styleSheet = getSampleStyleSheet()
        self.code = styleSheet['Code']
        self.bt = styleSheet['BodyText']
        self.story = []

        
    def end(self):
        if self.packageName:
            path = self.packageName + self.fileSuffix
        elif self.skeleton:
            path = self.skeleton.getModuleName() + self.fileSuffix
        else:
            path = ''
        
        if path:
            doc = MyTemplate(path)
            doc.build(self.story)


    def beginPackage(self, name):
        DocBuilder0.beginPackage(self, name)
        story = self.story
        story.append(Paragraph(name, self.makeHeadingStyle(self.indentLevel, 'package')))


    def beginModule(self, name, doc, imported):
        story = self.story
        bt = self.bt
        story.append(Paragraph(name, self.makeHeadingStyle(self.indentLevel, 'module')))

        story.append(XPreformatted(doc, bt))

        if imported:
            story.append(Paragraph('Imported modules', self.makeHeadingStyle(self.indentLevel + 1)))
            for m in imported:
                p = Paragraph('<bullet>\201</bullet> %s' % m, bt)
                p.style.bulletIndent = 10
                p.style.leftIndent = 18
                story.append(p)


    def beginClasses(self, names):
        self.story.append(Paragraph('Classes', self.makeHeadingStyle(self.indentLevel)))


    def beginClass(self, name, doc, bases):
        bt = self.bt
        story = self.story
        if bases:
            story.append(Paragraph('%s(%s)' % (name, join(bases, ', ')), self.makeHeadingStyle(self.indentLevel, 'class')))
        else:
            story.append(Paragraph(name, self.makeHeadingStyle(self.indentLevel, 'class')))

        story.append(XPreformatted(doc, bt))


    def beginMethod(self, name, doc, sig):
        bt = self.bt
        story = self.story
##        story.append(Paragraph(name+sig, h3))
        story.append(Paragraph(name+sig, self.makeHeadingStyle(self.indentLevel, 'method')))
        story.append(XPreformatted(doc, bt))


    def beginFunctions(self, names):
        if names:
            self.story.append(Paragraph('Functions', self.makeHeadingStyle(self.indentLevel)))


    def beginFunction(self, name, doc, sig):
        bt = self.bt
        story = self.story
        story.append(Paragraph(name+sig, self.makeHeadingStyle(self.indentLevel, 'function')))
        story.append(XPreformatted(doc, bt))


####################################################################
# 
# Special-purpose document builders
# (This will later be placed in a dedicated file.)
# 
####################################################################

class GraphPdfDocBuilder0(PdfDocBuilder0):
    "A PDF document builder displaying widget drawings and other info."

    fileSuffix = '-graph.pdf'

    def beginClass(self, name, doc, bases):
        PdfDocBuilder0.beginClass(self, name, doc, bases)
        # Keep an eye on the base classes.
        self.currentBaseClasses = bases
        
    
    def endClass(self, name, doc, bases):
        "Append a graphic demo of a widget at the end of a class."
        
        PdfDocBuilder0.endClass(self, name, doc, bases)

        # Find out if that was a Widget.
        widgetFound = 0
        for b in self.currentBaseClasses:
            if b.__name__ == 'Widget':
                widgetFound = 1
                break

        if widgetFound:
            widget = eval('self.skeleton.moduleSpace.' + name + '()')
            self.showWidgetDemo(widget)
            self.showWidgetDemoCode(widget)
            self.showWidgetProperties(widget)
            

    def showWidgetDemo(self, widget):
        """Show a graphical demo of the widget."""

        # Get a demo drawing from the widget and add it to the story.
        # Ignored if no GD rendering available
        # or the demo method does not returna drawing.
        try:
            drawing = widget.demo()
            widget.verify()
            flo = renderPDF.GraphicsFlowable(drawing)
            self.story.append(Spacer(6,6))
            self.story.append(flo)
            self.story.append(Spacer(6,6))
        except IndexError:
            pass


    def showWidgetDemoCode(self, widget):
        """Show a demo code of the widget."""

        widgetClass = widget.__class__
        demoMethod = widgetClass.demo
        srcFileName = demoMethod.im_func.func_code.co_filename
        (dirname, fileNameOnly) = os.path.split(srcFileName)

        # Heading
        className = widgetClass.__name__
        self.story.append(Paragraph("<i>Example</i>", self.bt))

        # Sample code
        lines = open(srcFileName, 'r').readlines()
        lines = map(string.rstrip, lines)
        codeSample = getFunctionBody(demoMethod, lines)
        self.story.append(Preformatted(codeSample, self.code))



    def showWidgetProperties(self, widget):
        """Dump all properties of a widget."""
        
        props = widget.getProperties()
        keys = props.keys()
        keys.sort()
        lines = []
        for key in keys:
            value = props[key]
            lines.append('%s = %s' % (key, value))
        text = join(lines, '\n')
        self.story.append(Paragraph("<i>Properties of Example Widget</i>", self.bt))
        self.story.append(XPreformatted(text, self.code))


class GraphHtmlDocBuilder0(HtmlDocBuilder0):
    "A class to write the skeleton of a Python source."

    fileSuffix = '-graph.html'

    def endClass(self, name, doc, bases):
        "Append a graphic demo of a widget at the end of a class."
        
        HtmlDocBuilder0.endClass(self, name, doc, bases)

        # Find out if that was a Widget.
        widgetFound = 0
        for b in self.currentBaseClasses:
            if b.__name__ == 'Widget':
                #print "RING: Widget '%s' found!!" % name
                widgetFound = 1
                break

        if widgetFound:
            widget = eval('self.skeleton.moduleSpace.' + name + '()')
            self.showWidgetDemo(widget)
            self.showWidgetDemoCode(widget)
            self.showWidgetProperties(widget)


    def showWidgetDemo(self, widget):
        """Show a graphical demo of the widget."""

        # Get a demo drawing from the widget and add it to the story.
        # Ignored if no GD rendering available
        # or the demo method does not returna drawing.
        try:
            drawing = widget.demo()
            widget.verify()
            modName = self.skeleton.getModuleName()
            path = '%s-%s.jpg' % (modName, widget.__class__.__name__)
            #print path
            renderGD.drawToFile(drawing, path, kind='JPG')
            self.outLines.append('<H3>Demo</H3>')
            self.outLines.append(makeHtmlInlineImage(path))
        except:
            pass


    def showWidgetDemoCode(self, widget):
        """Show a demo code of the widget."""

        widgetClass = widget.__class__
        demoMethod = widgetClass.demo
        srcFileName = demoMethod.im_func.func_code.co_filename
        (dirname, fileNameOnly) = os.path.split(srcFileName)

        # Heading
        className = widgetClass.__name__
        self.outLines.append('<H3>Example Code</H3>')

        # Sample code
        lines = open(srcFileName, 'r').readlines()
        lines = map(string.rstrip, lines)
        codeSample = getFunctionBody(demoMethod, lines)
        self.outLines.append('<PRE>%s</PRE>' % codeSample)
        self.outLines.append('')


    def showWidgetProperties(self, widget):
        """Dump all properties of a widget."""
        
        props = widget.getProperties()
        keys = props.keys()
        keys.sort()
        lines = []
        for key in keys:
            value = props[key]
            lines.append('%s = %s' % (key, value))
        text = join(lines, '\n')
        self.outLines.append('<H3>Properties of Example Widget</H3>')
        self.outLines.append('<PRE>%s</PRE>' % text)
        self.outLines.append('')


####################################################################
# 
# Main
# 
####################################################################

def printUsage():
    """docpy0.py - Automated documentation for Python source code.
    
Usage: python docpy0.py [options]

    [options]
        -h          Print this help message.
        -f name     Use the document builder indicated by 'name',
                    e.g. Ascii, Html, Pdf, GraphHtml, GraphPdf.
        -m module   Generate doc for module named 'module'.
        -p package  Generate doc for package named 'package'.

Examples:

    python docpy0.py -h
    python docpy0.py -m docpy0.py -f Ascii
    python docpy0.py -m string -f Html
    python docpy0.py -m signsandsymbols.py -f Pdf
    python docpy0.py -p pingo -f Html
    python docpy0.py -m signsandsymbols.py -f GraphPdf
    python docpy0.py -m signsandsymbols.py -f GraphHtml
"""


def documentModule0(path, builder=DocBuilder0()):
    """Generate documentation for one Python file in some format.

    This handles Python standard modules like string, custom modules
    on the Python search path like e.g. docpy as well as modules
    specified with their full path like C:/tmp/junk.py.

    The doc file will always be saved in the current directory
    with a basename equal to the module's name.
    """

    cwd = os.getcwd()

    # Append directory to Python search path if we get one.
    dirName = os.path.dirname(path)
    if dirName:
        sys.path.append(dirName)

    # Remove .py extension from module name.
    if path[-3:] == '.py':
        modname = path[:-3]
    else:
        modname = path

    # Remove directory paths from module name.
    if dirName:
        modname = os.path.basename(modname)

    # Load the module.    
    try:
        module = __import__(modname)
    except:
        print 'Failed to import %s.' % modname
        os.chdir(cwd)
        return
    
    # Do the real documentation work.
    s = Skeleton0()
    s.inspect(module)
    builder.write(s)
    
    # Remove appended directory from Python search path if we got one.
    if dirName:
        del sys.path[-1]

    os.chdir(cwd)


def _packageWalkCallback(builder, dirPath, files):
    """A callback function used when waking over a package tree."""
    
    files = filter(lambda f:f != '__init__.py', files)
    files = filter(lambda f:f[-3:] == '.py', files)
    if files:
        for f in files:
            path = os.path.join(dirPath, f)
            print path
            builder.indentLevel = builder.indentLevel + 1
            documentModule0(path, builder)
            builder.indentLevel = builder.indentLevel - 1

    
def documentPackage0(path, builder=DocBuilder0()):
    """Generate documentation for one Python package in some format.

    Rigiht now, 'path' must be a filesystem path, later it will
    also be a package name whose path will be resolved by importing
    the top-level module.
    
    The doc file will always be saved in the current directory.
    """

    name = path
    if string.find(path, os.sep) > -1:
        name = os.path.splitext(os.path.basename(path))[0]
    else:
        package = __import__(name)
        name = path
        path = os.path.dirname(package.__file__)

    cwd = os.getcwd()
    builder.beginPackage(name)
    os.path.walk(path, _packageWalkCallback, builder)
    builder.endPackage(name)
    os.chdir(cwd)


def main():
    """Handle command-line options and trigger corresponding action.
    """
    
    opts, args = getopt.getopt(sys.argv[1:], 'hf:m:p:')

##    # Without options run the previous main() generating lots of files.
##    if opts == []:
##        previousMain()
##        sys.exit(0)
##
    # On -h print usage and exit immediately.
    for o, a in opts:
        if o == '-h':
            print printUsage.__doc__
            #printUsage()
            sys.exit(0)

    # On -f set the DocBuilder to use or a default one.
    builder = DocBuilder0()
    for o, a in opts:
        if o == '-f':
            builder = eval("%sDocBuilder0()" % a)
            break

    # Now call the real documentation functions.
    for o, a in opts:
        if o == '-m':
            builder.begin()
            documentModule0(a, builder)
            builder.end()
            sys.exit(0)
        elif o == '-p':
            builder.begin()
            documentPackage0(a, builder)
            builder.end()
            sys.exit(0)


if __name__ == '__main__':
    main()
