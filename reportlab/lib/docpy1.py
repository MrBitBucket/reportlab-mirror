# more doc tools.  To be merged into docpy if the idea
# is a success.
"""This is an alternative route to making documentation. The idea
is a framework that lets you build both tutorial or user-guide
documentation and comprehensive package references.

Usage
-----
The script is invoked as follows:

  <base docpy0 handling plus "-t target" option>

package_or_module can be a fully qualified file or directory name like
C:\code\reportlab, or a string which evaluates to a package or module
on the standard Python path.  "-t" is used to specify more than one
document type; for example, you can define 'UserGuide' and 'Reference'
targets within a project and then build them with command like this:

    docpy -p c:\code\reportlab\graphics -t UserGuide -f PDF

If no target is given and you make no special provisions for docpy,
the script will traverse the package of module and build a reference
document with all the package, module, class and function names and
their docstrings.

Story Format
------------
The system works around the concept of a 'platform independent story'.
This is a list of tuples (or lists) in which the first item is a type
code.  For example:
    [('PARAGRAPH', 'H1', 'How DocPy Works'),
     ('IMAGE', 'wherever/mylogo.gif'),
     ('PARAGRAPH','Normal','Blah blah blah blah......')]

Some basic object types are provided - paragraphs, preformatted text
and images - and formatters are provided to render them as HTML or
PDF.

We also provide a simple 'story generator' called YAML - Yet Another
Markup Language - which lts you embed content in docstrings or files
with a minimum of typing.  YAML does a reasonable job of turning
plain docstrings into paragraphs.

Default Behaviour
-----------------
You may override the default behaviour at any point by providing a
function called getStory(target).  If you place such a function
in the __init__.py module of a package, it will be called in preference
to the default processing for a package.  It can do anything you want
including:
(1) processing an external file containing the whole manual
(2) process a small external file or embedded string which
provides an introduction, then continue with the default package
handling
(3) suppressing some subpackages or modules and changing the order
in which they are presented.


The default handling for a package is to display
- any doc string in __init__.py
- default handling for any modules in alphabetical order which do not begin
  with an underscore
- default handling for any subpackages in alphabetical order whose names
  do not begin with an underscore
This may be overridden by implementing a function getStory(target)
within the __init__.py file for the module.

The default handling for a module is to display
  - the doc string
  - default handling for any classes which are defined in the
    module, in alphabetical order, provided they do not begin
    with an underscore.
    (I think it only shows stuff defined locally, and not everything
    that is imported from elsewhere)
  - headers and docstrings for any functions defined in the module,
    provided they do not begin with an underscore
This may be overridden by implementing a function getStory(target)
within the the module.

The default handling for a class is to display
   - the doc string
   - header and docstring for any methods defined locally (not those
     inherited from elsewhere) , provided they do not begin with an
     underscore
This may be overridden by providing a method getStory(self, target)
in the class.

Multiple Targets
----------------
If any of the special getStory functions return None, docpy will
revert to the default processing. This lets you handle a single
target and 'give up' otherwise.  For example, this handler
will parse an external file if called with the target "UserGuide",
but otherwise docpy will detect the 'None' and handle the package
in the usual way.

def getStory(target):
    if target == 'UserGuide':
        # parse some local file
        import os
        myDir = os.path.split(__file__)[0]
        import yaml
        return yaml.parseFile(myDir + os.sep + 'my_user_guide.yaml')
    else:
        # this signals that it should revert to default processing
        return None




"""
import os
import sys
import glob
import imp
import string
import time

import yaml
from reportlab.lib import inspect


# this lot needed for PDF documentation only
from reportlab.pdfgen import canvas
from reportlab.lib import inspect
from reportlab.lib import colors
from reportlab.lib.units import inch, cm
from reportlab.lib.pagesizes import A4
from reportlab.lib import enums
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus.flowables import Flowable, Spacer
from reportlab.platypus.paragraph import Paragraph
from reportlab.platypus.flowables \
     import Flowable, Preformatted,Spacer, Image, KeepTogether, PageBreak
from reportlab.platypus.tableofcontents0 import TableOfContents0
from reportlab.platypus.xpreformatted import XPreformatted
from reportlab.platypus.frames import Frame
from reportlab.platypus.doctemplate \
     import PageTemplate, BaseDocTemplate
from reportlab.platypus.tables import TableStyle, Table

from types import StringType

class PackageDocumenter:
    """Generates a story about a package or module.

    This handles importing of packages.
    It starts off INSIDE the top level package; so if the 'reportlab'
    package lives under 'c:\\code', we get this:
        >>> c = docpy1.Context('c:\\code\\reportlab')
        >>> c.rootDir
        'c:\\code'
        >>> c.rootPackageName
        'reportlab'
        >>> c.getCurDir()
        'c:\\code\\reportlab'
        >>> c.getCurPrefix()
        'reportlab'
        >>> c.push('lib')
        >>> c.getCurDir()
        'c:\\code\\reportlab\\lib'
        >>> c.getCurPrefix()
        'reportlab.lib'
        >>> c.pop()
        'lib'
        >>> c.getCurDir()
        'c:\\code\\reportlab'
        >>> 
    """
    def __init__(self, package_or_module):
        if os.path.isdir(package_or_module):
            packageDir = package_or_module
            self.rootDir, self.rootPackageName = os.path.split(packageDir)
            self.isPackage = 1
            self.moduleName = None
        elif os.path.isfile(package_or_module):
            packageDir, fileName = os.path.split(package_or_module)
            self.rootDir = packageDir
            self.rootPackageName = ''
            self.moduleName = os.path.splitext(fileName)[0]
            self.isPackage = 0
        else:
            raise Exception("target is neither a package nor a module")

        if not self.rootDir in sys.path:
            sys.path.insert(0, self.rootDir)
        self._dirStack = []
        self._objStack = []
        self.target = None
        self.verbosity = 0
        self.showDocStrings = 1  
        self.parseDocStrings = 1 # use YAML on them?
        self.showUnderscores = 0   # do we show methods with an underscore in fron?
        self.showModuleAttributes = 1
        self.moduleCount = 0
        self.packageCount = 0
        if self.isPackage:
            self.pushDir(self.rootPackageName)

        
        
    def getCurDir(self):
        return self.rootDir + os.sep + string.join(self._dirStack, os.sep)

    def getCurPrefix(self):
        return string.join(self._dirStack, '.')
    
    def pushDir(self, dirname):
        self._dirStack.append(dirname)
        # import and get hold of the module 
        __import__(self.getCurPrefix(), globals(), locals())
        pkg = sys.modules[self.getCurPrefix()]
        self._objStack.append(pkg)
        if self.verbosity > 0:
            print 'documenting package %s' % self.getCurPrefix()
        
    def popDir(self):
        "back up one level"
        self._objStack.pop()
        return self._dirStack.pop()

    def getCurPackage(self):
        return self._objStack[-1]

    def findModulesInCurrentDirectory(self):
        "returns all .py module names in the given directory"""
        filenames = os.listdir(self.getCurDir())
        found = []
        for filename in filenames:
            root, ext = os.path.splitext(filename)
            if ext == '.py':
                found.append(root)
        found.sort()
        return found

    def findPackagesInCurrentDirectory(self):
        "finds all valid subpackages"
        packageDir = self.getCurDir()
        filenames = os.listdir(packageDir)
        found = []
        for filename in filenames:
            if os.path.isdir(packageDir + os.sep + filename):
                initFileName = packageDir + os.sep + filename + os.sep + '__init__.py'
                if os.path.isfile(initFileName):
                    found.append(filename)
        found.sort()
        return found

    def appendDocToStory(self, object, story):
        doc = inspect.getdoc(object)
        if doc is None:
            doc = '(no docstring)'
        elif len(string.strip(doc)) == 0:
            doc = '(no docstring)'

        if self.parseDocStrings:
            for item in yaml.parseText(doc):
                story.append(item)
        else: #single preformatted chunk
            story.append(('PREFORMATTED','Code',doc))
            
    def getStory(self):
        started = time.time()
        story = []
        if self.isPackage:
            self.processDirectory(story)
        else:
            self.processModule(self.moduleName, story)
        finished = time.time()
        if self.verbosity > 0:
            print 'processed %d packages and %d modules in %0.2f seconds' % (
                self.packageCount, self.moduleCount, finished-started)
        return story
    
    def processDirectory(self, story):
        """The main handler.  Recurses down, finding modules and appending to the story."""
        if self.verbosity > 1:
            print 'processPackage(%s)' % self.getCurPrefix()
        story.append(('PACKAGE',self.getCurPrefix()))
        #story.append(('PARAGRAPH','H1','Package ' + self.getCurPrefix()))
        
        #if self.showDocStrings:
        #    story.append(in
        moduleNames = self.findModulesInCurrentDirectory()
        for moduleName in moduleNames:
            self.processModule(moduleName, story)
            
        packageNames = self.findPackagesInCurrentDirectory()
        for packageName in packageNames:
            self.pushDir(packageName)
            self.processDirectory(story)
            self.popDir()
        self.packageCount = self.packageCount + 1
        
    def processModule(self, moduleName, story):
        """documents a module"""
        # YUK - refactor to something which gets the
        # story from an alreadt-loaded module and
        # two things which call it.
        if self.verbosity > 1:
            print 'processModule(%s)' % moduleName
        if self.isPackage:
            name = self.getCurPrefix() + '.' + moduleName
        else:
            if not self.rootDir in sys.path:
                sys.path.insert(0, self.rootDir)
            name = moduleName
        __import__(name, globals(), locals())
        self.module = sys.modules[name]
        self.moduleName = moduleName

        story.append(('MODULE', name))
        if self.isPackage:
            name = self.getCurPrefix() + '.' + moduleName
        else:
            name = moduleName
        story.append(('PARAGRAPH','H1','Module ' + name))
            
        self.moduleCount = self.moduleCount + 1

        # first, the doc string
        if self.showDocStrings:
            self.appendDocToStory(self.module, story)

        # now the objects
        for (name, object) in inspect.getmembers(self.module):
            if inspect.isclass(object):
                self.processClass(object, story)
            elif inspect.isfunction(object):
                self.processFunction(object, story)

    def processClass(self, klass, story):

        # was it defined here?
        definedIn = klass.__module__
        if self.isPackage:
            currentlyIn = self.getCurPrefix() + '.' + self.moduleName
        else:
            currentlyIn = self.moduleName
        #print klass.__module__, currentlyIn
        if definedIn == currentlyIn:
            story.append(('CLASS', klass.__name__))
            story.append(('PARAGRAPH','H2', 'class ' + klass.__name__))
            if self.showDocStrings:
                self.appendDocToStory(klass, story)
        
            for (name, member) in inspect.getmembers(klass):
                if inspect.ismethod(member):
                    # was it defined in this class or a parent?
                    if member.im_class == klass:
                        story.append(('METHOD',name))
                        story.append(('PARAGRAPH','H3','method ' + name))
                        if self.showDocStrings:
                            self.appendDocToStory(member, story)                            

    def processFunction(self, func, story):
        # was it defined here? Want to compare .py and .pyc
        # so split off the extension
        funcDefinedIn = os.path.splitext(func.func_code.co_filename)[0]
        currentlyIn = os.path.splitext(self.module.__file__)[0]
        if funcDefinedIn == currentlyIn:
            story.append(('FUNCTION', func.__name__))
            story.append(('PARAGRAPH','H3','method ' + func.__name__))
            if self.showDocStrings:
                self.appendDocToStory(func, story)                
        



class DocBuilder:
    """Base class for things to process the story and make a document.

    For a story element ('SPAM',EGGS) it tries to find a method
    processSpam (capitalizing only the first letter) and calls it
    with the argument EGGS.  Arguments needs not be strings,
    although they usually are for default use of docpy."""
    def __init__(self, story):
        self._story = story
        self.ignoreUnknowns = 0

    def go(self):
        for tup in self._story:
            try:
                first = tup[0]
                rest = tup[1:]
                methodName = 'process' + first[0:1] + string.lower(first[1:])
                if self.ignoreUnknowns:
                    if hasattr(self, methodName):
                        method = getattr(self, methodName)
                        apply(method, rest)
                else: #just do it and raise an error if not found
                    method = getattr(self, methodName)
                    apply(method, rest)
            except:
                print 'DocBuilder error on story element:', tup
                raise
        self.finished()
        
    def finished(self):
        print 'StoryBuilder.finished()'

    def processPackage(self, packageName):
        print "StoryBuilder.processPackage('%s')" % packageName

    def processModule(self, moduleName):
        print "StoryBuilder.processModule('%s')" % moduleName
        
    def processClass(self, className):
        print "StoryBuilder.processClass('%s')" % className

    def processMethod(self, methodName):
        print "StoryBuilder.processMethod('%s')" % methodName

    def processFunction(self, functionName):
        print "StoryBuilder.processFunction('%s')" % functionName
        

class HTMLDocBuilder(DocBuilder):
    """Makes a directory of files, one per module documented.

    Package documentation is named as "reportlab_lib_docpy.html"
    so as to keep it in one place; the alternative would be to
    spray GIFs and HTML files all over somebody's Python hierarchy.

    You can provide your own HTML template, which should have
    the strings "%(title)s" and "%(body)s".
    """

    
    template = "<html><head><title>%(title)s</title></head><body>%(body)s</body></html>"
    def __init__(self, story, output='.', createDir=0):
        DocBuilder.__init__(self, story)
        # build up a list of strings for the HTML
        # for HTML, 'output' means a directory
        directory = output
        self.directory = directory
        
        self.pageTitle = None
        self.outFileName = None
        self.moduleName = None
        self.className = None
        self.content = []

        # this maintains (name ->  list_of_content)
        # tree so one can properly index the HTML on a single pass.
        self.packages = {}
        self.currentPackageName = None
        
        if not os.path.isdir(directory):
            if createDir:
                os.makedirs(directory)
                print 'created output directory %s' % directory
            else:
                raise Exception("Output Directory %s does not exist!")

   
    def writeModuleFile(self):
        "Write out the pending module file to disk, if present"
        if len(self.content) > 0:
            # package documentation goes to package content
##            if self.outFileName is None:
##                packageContent =  self.packages[self.currentPackageName]
##                for elem in self.content:
##                    packageContent.append(elem)
##                self.content = []
##            else:
            self.content.append('<hr><address>%s</address>' % self.getByLine())
            dict = {'title':self.pageTitle, 'body': string.join(self.content, '\n')}
            data = self.template % dict
            open(self.outFileName, 'w').write(data)
            print 'wrote',self.outFileName
            self.content = []
            self.outFileName = None

    def writePackageFile(self, name, contents):
        "Write out the package file to disk"
        contents.append('<hr><address>%s</address>' % self.getByLine())
        dict = {'title':'Package Index for ' + name, 'body': string.join(contents, '\n')}
        data = self.template % dict
        filename = self.directory + os.sep + self.getModuleFileName(name)
        open(filename, 'w').write(data)
        print 'wrote package index',filename

    def getByLine(self):
        return 'generated by docpy1.py at %s' % (time.ctime(time.time()))

    def getModuleFileName(self, moduleName):
        "For link-making.  Returns the HTML file name to use for the module (or package)"
        return string.replace(moduleName, '.', '_') + '.html'
    
    def getLink(self, name, destfile):
        return '<a href="%s">%s</a>' % (destfile, name)        

    def finished(self):
        "close any open file"
        self.writeModuleFile()
        #now write out all packages
        for (name, contents) in self.packages.items():
            self.writePackageFile(name, contents)

    # utilities to make package processing and linking a bit more readable
    
    def getParentPackage(self, packageName):
        "returns parent package name; empty string if no parent"
        bits = string.split(packageName, '.')
        return string.join(bits[0:-1],'.')

    def packageIsSibling(self, name1, name2):
        "returns true if they have same parent"
        return (self.getParentPackage(name1) == self.getParentPackage(name2))

    
    def processPackage(self, packageName):
        """Start processing a package index page"""
        assert not self.packages.has_key(packageName), "HTMLDocBuilder already has a package level '%s'" % packageName
        self.currentPackageName = packageName
        # TODO: make up a high-tech URL whereby you can click on any part of the package
        # hierarchy and jump to it.
        bits = string.split(packageName, '.')
        title = '<h1>Package '
        print 'processPackage(%s)' % packageName
        for i in range(1,len(bits)):
            pkgName = string.join(bits[0:i],'.')
            print '    link',pkgName
            pkgFile = self.getModuleFileName(pkgName)
            title = title + '<a href="%s">%s</a>' % (pkgFile, bits[i-1]) + '.'
        
        title = title + bits[-1] + '</h1>'        
        content = ['<!--Package Index for %s-->' % packageName,
                   title,
                   ]
        self.packages[packageName] = content

        # add package link to any parents
        pkgName = self.getParentPackage(self.currentPackageName)
        while pkgName:
            # add module name and link to all parents
            pkg = self.packages[pkgName]
            pkg.append('<p>package %s</p>' % self.getLink(
                packageName, self.getModuleFileName(packageName))
                       )
            pkgName = self.getParentPackage(pkgName)
        

    def processModule(self, moduleName):
        """"Write any pending pages, and start a new page for the module"""
        self.writeModuleFile()
        self.outFileName = self.directory + os.sep + self.getModuleFileName(moduleName)
        self.content.append('<!--Module:%s-->' % moduleName)
        self.pageTitle = 'docpy: module %s' % moduleName
        self.moduleName = moduleName

        pkgName = self.currentPackageName
        while pkgName:
            # add module name and link to all parents
            pkg = self.packages[pkgName]
            pkg.append('&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;module %s<br>' % self.getLink(
                moduleName, self.getModuleFileName(moduleName))
                       )
            pkgName = self.getParentPackage(pkgName)
            

        
    def processClass(self, className):
        self.className = className
        self.content.append('<!--Class:%s-->' % className)

    def processMethod(self, methodName):
        self.content.append('<!--method: %s.%s -->' % (self.className, methodName))

    def processFunction(self, functionName):
        self.content.append('<!--function %s -->' % functionName)


    def processParagraph(self, style, text):
        if style == 'H1':
            self.content.append('<h1>%s</h1>' % text)
        elif style == 'H2':
            self.content.append('<h2>%s</h2>' % text)
        elif style == 'H3':
            self.content.append('<h3>%s</h3>' % text)
        elif style == 'Normal':
            self.content.append('<p>%s</p>' % text)

    def processPreformatted(self, style, text):
        self.content.append('<pre>%s</pre>' % text)



####################################################################
# 
# Stuff needed for building PDF docs.
# 
####################################################################


def mainPageFrame(canvas, doc):
    "The page frame used for all PDF documents."
    
    canvas.saveState()

    pageNumber = canvas.getPageNumber()
    canvas.line(2*cm, A4[1]-2*cm, A4[0]-2*cm, A4[1]-2*cm)
    canvas.line(2*cm, 2*cm, A4[0]-2*cm, 2*cm)
    if pageNumber > 1:
        canvas.setFont('Times-Roman', 12)
        canvas.drawString(4 * inch, cm, "%d" % pageNumber)
        if hasattr(canvas, 'headerLine'): # hackish
            headerline = string.join(canvas.headerLine, ' \215 ')
            canvas.drawString(2*cm, A4[1]-1.75*cm, headerline)

    canvas.setFont('Times-Roman', 8)
    msg = "Generated with reportlab.lib.docpy0. See http://www.reportlab.com!"
    canvas.drawString(2*cm, 1.65*cm, msg)

    canvas.restoreState()
    

class MyTemplate(BaseDocTemplate):
    "The document template used for all PDF documents."
    
    _invalidInitArgs = ('pageTemplates',)
    
    def __init__(self, filename, **kw):
        frame1 = Frame(2.5*cm, 2.5*cm, 15*cm, 25*cm, id='F1')
        self.allowSplitting = 0
        apply(BaseDocTemplate.__init__, (self, filename), kw)
        self.addPageTemplates(PageTemplate('normal', [frame1], mainPageFrame))


    def afterFlowable(self, flowable):
        "Takes care of header line, TOC and outline entries."
        
        if flowable.__class__.__name__ == 'Paragraph':
            f = flowable

            # Build a list of heading parts.
            # So far, this is the *last* item on the *previous* page...
            if f.style.name[:8] == 'Heading1':
                self.canv.headerLine = [f.text] # hackish
            elif f.style.name[:8] == 'Heading2':
                if len(self.canv.headerLine) == 2:
                    del self.canv.headerLine[-1]
                elif len(self.canv.headerLine) == 3:
                    del self.canv.headerLine[-1]
                    del self.canv.headerLine[-1]
                self.canv.headerLine.append(f.text)
            elif f.style.name[:8] == 'Heading3':
                if len(self.canv.headerLine) == 3:
                    del self.canv.headerLine[-1]
                self.canv.headerLine.append(f.text)

            if f.style.name[:7] == 'Heading':
                # Register TOC entries.
                headLevel = int(f.style.name[7:])-1
                self.notify0('TOCEntry', (headLevel, flowable.getPlainText(), self.page))

                # Add PDF outline entries.
                c = self.canv
                title = f.text
                key = str(hash(f))
                lev = int(f.style.name[7:])
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



class PDFDocBuilder(DocBuilder):
    """Creates a single PDF document for the package.  TO BE COMPLETED!"""
    def __init__(self, story, output=None, createDir=0):
        DocBuilder.__init__(self, story)
        # find the package or module name to use in the filename
        for elem in self._story:
            if elem[0] == 'PACKAGE':
                self.name = elem[1]
                self.typ = 'package'
                break
            elif elem[0] == 'module':
                self.name = elem[1]
                self.typ = 'module'
                break
        assert self.name, "Story does not contain a package or module name!"
        print 'Package or module name ="%s"' % self.name
        if output:
            assert string.lower(output)[-4:] == '.pdf', "output filename must end with .pdf, you provided '%s'" % output
            self.filename = output
        else:
            self.filename = string.replace(self.name, '.', '_') + '.pdf'
    
        self.styleMap = { #maps para styles to those in our style sheet
            'H1':'Heading1',
            'H2':'Heading2',
            'H3':'Heading3',
            'Normal':'BodyText'
            }
        
    def makeHeadingStyle(self, level, typ=None, doc=''):
        "Make a heading style for different types of module content."

        if typ in ('package', 'module', 'class'):
            style = ParagraphStyle(name='Heading'+str(level),
                                      fontName = 'Courier-Bold',
                                      fontSize=14,
                                      leading=18,
                                      spaceBefore=12,
                                      spaceAfter=6)
        elif typ in ('method', 'function'):
            if doc:
                style = ParagraphStyle(name='Heading'+str(level),
                                          fontName = 'Courier-Bold',
                                          fontSize=12,
                                          leading=18,
                                          firstLineIndent=-18,
                                          leftIndent=36,
                                          spaceBefore=0,
                                          spaceAfter=-3)
            else:
                style = ParagraphStyle(name='Heading'+str(level),
                                          fontName = 'Courier-Bold',
                                          fontSize=12,
                                          leading=18,
                                          firstLineIndent=-18,
                                          leftIndent=36,
                                          spaceBefore=0,
                                          spaceAfter=0)

        else:
            style = ParagraphStyle(name='Heading'+str(level),
                                      fontName = 'Times-Bold',
                                      fontSize=14,
                                      leading=18,
                                      spaceBefore=12,
                                      spaceAfter=6)
            
        return style

    def go(self):
        self.styleSheet = getSampleStyleSheet()
        self.styleCode = self.styleSheet['Code']
        self.styleBody = self.styleSheet['BodyText']
        self.story = []

        # Cover page
        # need to know if package or module
        typ = 'Package'
        
        t = time.gmtime(time.time())
        timeString = time.strftime("%Y-%m-%d %H:%M", t)
        self.story.append(Paragraph('<font size=18>Documentation for %s "%s"</font>' % (self.typ, self.name), self.styleBody))
        self.story.append(Paragraph('<font size=18>Generated by: docpy1.py </font>',  self.styleBody))
        self.story.append(Paragraph('<font size=18>Date generated: %s</font>' % timeString, self.styleBody))
        self.story.append(Paragraph('<font size=18>Format: PDF</font>', self.styleBody))
        self.story.append(PageBreak())

        # Table of contents
        #toc = TableOfContents0()
        #self.story.append(toc)
        self.story.append(PageBreak())

        DocBuilder.go(self)

    def processPackage(self, className):
        pass

    def processModule(self, moduleName):
        pass

    def processClass(self, className):
        pass

    def processMethod(self, methodName):
        pass
    
    def processFunction(self, functionName):
        pass

    def processParagraph(self, style, text):
        pdfStyleName = self.styleMap[style]
        pdfStyle = self.styleSheet[pdfStyleName]
        para = Paragraph(text, pdfStyle)
        self.story.append(para)

    def processPreformatted(self, style, text):
        pdfStyle = self.styleSheet['Code']
        pre = Preformatted(text, pdfStyle)
        self.story.append(pre)
        
    def finished(self):
        doc = MyTemplate(self.filename)
        #doc.build(self.story)
        doc.multiBuild0(self.story)

            
def document(something, format, output, silent=1, createDir=1):
    print 'document %s, format=%s, output=%s, silent=%d, createDir=%d' % (
        something, format, output, silent, createDir)
    if os.path.isdir(something):
        assert os.path.isfile(something + os.sep + '__init__.py'), \
               "%s is not a valid Python package!  __init__.py not found."

    elif os.path.isfile(something):
        #it's a file, it exists, cool
        pass
        D = PackageDocumenter(something)
        story = D.getStory()
        #make a subdirectory called doc
        B = HTMLDocBuilder(story, directory='doc', createDir=1)
        B.go()
    else:
        raise Exception("%s is not a Python package or module" % something)

    D = PackageDocumenter(something)
    story = D.getStory()
    if not silent:
        print 'built %d-element story from source' % len(story)

    if format == 'PDF':
        B = PDFDocBuilder(story, createDir=1)
    elif format == 'HTML':
        B = HTMLDocBuilder(story, output='doc', createDir=1)
    B.go()
    if not silent:
        print 'finished documenting', something
    
def main():
    "Handle command-line options and trigger corresponding action."
    usage = """Usage:
    Show help:
        docpy -h
    docpy modulefile [-f [PDF|HTML] [-d output_directory] [-s]

    Example 1: silently generate PDF documentation for reportlab package,
    writing to current directory:
        docpy c:\wherever\reportlab -f PDF

    Example 2: generate HTML documentation for reportlab package
        docpy c:\wherever\reportlab -f HTML
    """

    #tried getopt but it seems to make things more complex
    # as we want exactly one non-keyword option
    args = map(string.lower, sys.argv[1:])
    
    #defaults, may be overridden by arguments
    target = None
    silent = 0
    format = 'PDF'
    
    for arg in args:
        if arg == 'silent':
            silent = 1
        elif arg == 'verbose':
            silent = 0
        elif arg == 'pdf':
            format = 'PDF'
        elif arg == 'html':
            format = 'HTML'
        elif arg == 'help':
            print usage
            sys.exit(0)
        else:
            target = arg

    document(target, format, silent)
    
if __name__ == '__main__':
    main()
    
        
        
        
        