
###############################################################################
#
#	ReportLab Public License Version 1.0
#
#   Except for the change of names the spirit and intention of this
#   license is the same as that of Python
#
#	(C) Copyright ReportLab Inc. 1998-2000.
#
#
# All Rights Reserved
#
# Permission to use, copy, modify, and distribute this software and its
# documentation for any purpose and without fee is hereby granted, provided
# that the above copyright notice appear in all copies and that both that
# copyright notice and this permission notice appear in supporting
# documentation, and that the name of ReportLab not be used
# in advertising or publicity pertaining to distribution of the software
# without specific, written prior permission. 
# 
#
# Disclaimer
#
# ReportLab Inc. DISCLAIMS ALL WARRANTIES WITH REGARD TO THIS
# SOFTWARE, INCLUDING ALL IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS,
# IN NO EVENT SHALL ReportLab BE LIABLE FOR ANY SPECIAL, INDIRECT
# OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES WHATSOEVER RESULTING FROM LOSS
# OF USE, DATA OR PROFITS, WHETHER IN AN ACTION OF CONTRACT, NEGLIGENCE OR
# OTHER TORTIOUS ACTION, ARISING OUT OF OR IN CONNECTION WITH THE USE OR
# PERFORMANCE OF THIS SOFTWARE. 
#
###############################################################################
#	$Log: pdfdoc.py,v $
#	Revision 1.11  2000/04/02 02:52:39  aaron_watters
#	added support for outline trees
#
#	Revision 1.10  2000/03/24 21:03:51  aaron_watters
#	Added forms, destinations, linkages and other features
#	
#	Revision 1.7  2000/02/23 15:09:23  rgbecker
#	Memory leak fixes
#	
#	Revision 1.6  2000/02/17 12:36:25  rgbecker
#	added _HAVE_ZLIB to stop compression being set without zlib
#	
#	Revision 1.5  2000/02/17 02:07:23  rgbecker
#	Docstring & other fixes
#	
#	Revision 1.4  2000/02/16 09:42:50  rgbecker
#	Conversion to reportlab package
#	
#	Revision 1.3  2000/02/15 17:55:59  rgbecker
#	License text fixes
#	
#	Revision 1.2  2000/02/15 15:47:09  rgbecker
#	Added license, __version__ and Logi comment
#	
__version__=''' $Id: pdfdoc.py,v 1.11 2000/04/02 02:52:39 aaron_watters Exp $ '''
__doc__=""" 
PDFgen is a library to generate PDF files containing text and graphics.  It is the 
foundation for a complete reporting solution in Python.  

The module pdfdoc.py handles the 'outer structure' of PDF documents, ensuring that
all objects are properly cross-referenced and indexed to the nearest byte.  The 
'inner structure' - the page descriptions - are presumed to be generated before 
each page is saved.
pdfgen.py calls this and provides a 'canvas' object to handle page marking operators.
piddlePDF calls pdfgen and offers a high-level interface.

2000-10-13 gmcm Packagize
"""

import os
import sys
import string
import time
import tempfile
import cStringIO
from types import *
from math import sin, cos, pi, ceil

try:
    import zlib
    _HAVE_ZLIB = 1
except:
    print "zlib not available, page compression not available"
    _HAVE_ZLIB = 0


from reportlab.pdfgen.pdfgeom import bezierArc

from reportlab.pdfbase import pdfutils
from reportlab.pdfbase.pdfutils import LINEEND   # this constant needed in both
from reportlab.pdfbase import pdfmetrics
##############################################################
#
#            Constants and declarations
#
##############################################################



StandardEnglishFonts = [
    'Courier', 'Courier-Bold', 'Courier-Oblique', 'Courier-BoldOblique',  
    'Helvetica', 'Helvetica-Bold', 'Helvetica-Oblique', 
    'Helvetica-BoldOblique',
    'Times-Roman', 'Times-Bold', 'Times-Italic', 'Times-BoldItalic',
    'Symbol','ZapfDingbats']

PDFError = 'PDFError'
AFMDIR = '.'

A4 = (595.27,841.89)   #default page size

class PDFDocument:
    """Responsible for linking and writing out the whole document.
    Builds up a list of objects using add(key, object).  Each of these
    must inherit from PDFObject and be able to write itself into the file.
    For cross-linking, it provides getPosition(key) which tells you where
    another object is, or raises a KeyError if not found.  The rule is that
    objects should only refer ones previously written to file.
    """
    def __init__(self):
        self.objects = []
        self.objectPositions = {}
        # named object references (may be unbound)
        self.objectReferences = {}
        self.inObject = None # mark for whether in page or form or possibly others...
        self.thispageposition = None # record if in page
        self.thisformposition = None # record if in form
        
        self.fonts = MakeType1Fonts()

        #mapping of Postscriptfont names to internal ones;
        #needs to be dynamically built once we start adding
        #fonts in.
        self.fontMapping = {}
        for i in range(len(StandardEnglishFonts)):
            psname = StandardEnglishFonts[i]
            pdfname = '/F%d' % (i+1)
            self.fontMapping[psname] = pdfname
        
            
        self.pages = []
        self.pagepositions = []
        
        # position 1
        cat = PDFCatalog()
        self._catalog = cat
        cat.RefPages = 3
        cat.RefOutlines = 2
        self.add('Catalog', cat)
    
        # position 2 - outlines
        outl = PDFOutline()
        self.outline = outl
        self.add('Outline', outl)
    
        # position 3 - pages collection
        self.PageCol = PDFPageCollection()
        self.add('PagesTreeRoot',self.PageCol)
    
        # positions 4-16 - fonts
        fontstartpos = len(self.objects) + 1
        for font in self.fonts:
            self.add('Font.'+font.keyname, font)
        # make font dict as a shared indirect object reference
        #self.fontdict = MakeFontDictionary(fontstartpos, len(self.fonts))
        fontdicttext = MakeFontDictionary(fontstartpos, len(self.fonts))
        fontdictob = PDFLiteral(fontdicttext)
        self.add("FontDictionary", fontdictob)
        self.fontdict = self.objectReference("FontDictionary")
        
        # position 17 - Info
        self.info = PDFInfo()  #hang onto it!
        self.add('Info', self.info)
        self.infopos = len(self.objects)  #1-based, this gives its position
    
    
    def add(self, key, obj):
        #self.objectPositions[key] = len(self.objects)  # its position
        self.objectPositions[key] = p = len(self.objects)+1 # its position
        self.setObjectReference(key, p)
        self.objects.append(obj)
        #obj.doc = self
        #return len(self.objects) - 1  # give its position
        return self.getPosition(key)
        
    def replace(self, key, obj):
        """replace an object (but you better know what you are doing)"""
        position = self.getPosition(key)
        #self.setObjectReference(key, position)
        self.objects[position-1] = obj
        return position
        
    def reserve(self, key):
        """reserve an object position later to be replaced (no replace == error)"""
        return self.add(key, key)

    def getPosition(self, key):
        """Tell you where the given object is in the file - used for
        cross-linking; an object can call self.doc.getPosition("Page001")
        to find out where the object keyed under "Page001" is stored."""
        return self.objectPositions[key]
        
    def setObjectReference(self, key, position):
        ref = self.objectReference(key)
        ref.bind("%s 0 R" % position)
        
    def objectReference(self, key):
        "get a (lazy) object ref"
        #return "%s 0 R" % self.getPosition(key)
        refs = self.objectReferences
        try:
            test = refs[key]
        except:
            refs[key] = test = BindableStr(key)
        return test
        
    
    def setTitle(self, title):
        "embeds in PDF file"
        self.info.title = title
        
    def setAuthor(self, author):
        "embedded in PDF file"
        self.info.author = author
            
    def setSubject(self, subject):
        "embeds in PDF file"
        self.info.subject = subject
            
    
    def printXref(self):
        self.startxref = sys.stdout.tell()
        print 'xref'
        print 0,len(self.objects) + 1
        print '0000000000 65535 f'
        for pos in self.xref:
            print '%0.10d 00000 n' % pos

    def writeXref(self, f):
        self.startxref = f.tell()
        f.write('xref' + LINEEND)
        f.write('0 %d' % (len(self.objects) + 1) + LINEEND)
        f.write('0000000000 65535 f' + LINEEND)
        for pos in self.xref:
            f.write('%0.10d 00000 n' % pos + LINEEND)

    
    def printTrailer(self):
        print 'trailer'
        print '<< /Size %d /Root %d 0 R /Info %d 0 R>>' % (len(self.objects) + 1, 1, self.infopos)
        print 'startxref'
        print self.startxref

    def writeTrailer(self, f):
        f.write('trailer' + LINEEND)
        f.write('<< /Size %d /Root %d 0 R /Info %d 0 R>>' % (len(self.objects) + 1, 1, self.infopos)  + LINEEND)
        f.write('startxref' + LINEEND)
        f.write(str(self.startxref)  + LINEEND)

    def SaveToFile(self, filename):
        """Open a file, and ask each object in turn to write itself to
        the file.  Keep track of the file position at each point for
        use in the index at the end"""
        f = open(filename, 'wb')
        i = 1
        self.xref = []
        f.write("%PDF-1.2" + LINEEND)  # for CID support
        f.write("%\355\354\266\276" + LINEEND)
        # do preprocessing as needed
        # prepare outline
        outline = self.outline
        outline.prepare(self)
        for obj in self.objects:
            pos = f.tell()
            self.xref.append(pos)
            f.write(str(i) + ' 0 obj' + LINEEND)
            obj.save(f)
            f.write('endobj' + LINEEND)
            i = i + 1
        self.writeXref(f)
        self.writeTrailer(f)
        f.write('%%EOF')  # no lineend needed on this one!
        f.close()
        # with the Mac, we need to tag the file in a special
        #way so the system knows it is a PDF file.
        #This supplied by Joe Strout
        if os.name == 'mac':
            import macfs
            try: 
                macfs.FSSpec(filename).SetCreatorType('CARO','PDF ')
            except:
                pass


    def printPDF(self):
        "prints it to standard output.  Logs positions for doing trailer"
        print "%PDF-1.0"
        print "%\355\354\266\276"
        i = 1
        self.xref = []
        for obj in self.objects:
            pos = sys.stdout.tell()
            self.xref.append(pos)
            print i, '0 obj'
            obj.printPDF()
            print 'endobj'
            i = i + 1
        self.printXref()
        self.printTrailer()
        print "%%EOF",
        
    def inPage(self):
        """specify the current object as a page (enables reference binding and other page features)"""
        if self.inObject is not None:
            raise ValueError, "can't go in page already in object %s" % self.inObject
        self.inObject = "page"
        pagenum = len(self.PageCol.PageList)+1
        pagename = "Page%06d" % pagenum
        streamname = "PageStream%06d" % pagenum
        pageposition = self.reserve(pagename)
        streamposition = self.reserve(streamname)
        self.pageposition = (pagenum, pagename, streamname, pageposition, streamposition)
        
    def thisPageRef(self):
        if self.inObject!="page":
            raise ValueError, "can't get thisPageRef -- not declared inPage"
        (pagenum, pagename, streamname, pageposition, streamposition) = self.pageposition
        return self.objectReference(pagename)
        
    def inForm(self):
        """specify that we are in a form xobject (disable page features, etc)"""
        if self.inObject not in ["form", None]:
            raise ValueError, "can't go in form already in object %s" % self.inObject
        self.inObject = "form"
        # don't need to do anything else, I think...

    def addPage(self, page):
        """adds page and stream at end.  Maintains pages list"""
        #page.buildstream()
        if self.inObject != "page":
            self.inPage()
        (pagenum, pagename, streamname, pageposition, streamposition) = self.pageposition
        pos = len(self.objects) # work out where added
        
        parentpos = page.ParentPos = self.getPosition("PagesTreeRoot")   #pages collection
        page.info = {
            'parentpos': parentpos,
            'fontdict':self.fontdict,
            'contentspos':streamposition,
            }
        
        self.PageCol.PageList.append(pageposition)  
        #pagenum = len(self.PageCol.PageList)
        #self.add('Page%06d'% pagenum, page)
        self.replace(pagename, page)
        #self.objects.append(page)
        #self.add('PageStream%06d'% pagenum, page.stream)
        self.replace(streamname, page.stream)
        #self.objects.append(page.stream)
        # clear inObject
        self.inObject = None
        
    def addForm(self, name, form):
        """add a Form XObject."""
        # XXX should check that name is a legal PDF name
        if self.inObject != "form":
            self.inForm()
        form.info = {"fontdict": self.fontdict}
        self.add("FormXob.%s" % name, form)
        self.inObject = None
        
    def hasForm(self, name):
        """test for existence of named form"""
        internalname = "FormXob.%s" % name
        try:
            test = self.objectReference(internalname)            
        except:
            return 0
        else:
            return internalname
        
    def xobjDict(self, formnames):
        """construct an xobject dict (for inclusion in a resource dict, usually)
           from a list of form names (images not yet supported)"""
        L = []
        a = L.append
        a("        <<")
        for name in formnames:
            internalname = "FormXob.%s" % name
            reference = self.objectReference(internalname)
            a("           /%s %s" % (internalname, reference))
        a(">>")
        a("")
        return string.join(L, LINEEND)
        
    def addAnnotation(self, name, annotation):
        self.add("Annot.%s"%name, annotation)
        
    def refAnnotation(self, name):
        internalname = "Annot.%s" % name
        return self.objectReference(internalname)

    def hasFont(self, psfontname):
        return self.fontMapping.has_key(psfontname)

    def getInternalFontName(self, psfontname):
        try:
            return self.fontMapping[psfontname]
        except:
            raise PDFError, "Font %s not available in document" % psfontname

    def getAvailableFonts(self):
        fontnames = self.fontMapping.keys()
        fontnames.sort()
        return fontnames
    
##############################################################
#
#            Utilities
#
##############################################################

class OutputGrabber:
    """At times we need to put something in the place of standard
    output.  This grabs stdout, keeps the data, and releases stdout
    when done.
    
    NOT working well enough!"""
    def __init__(self):
        self.oldoutput = sys.stdout
        sys.stdout = self
        self.closed = 0
        self.data = []
    def write(self, x):
        if not self.closed:
            self.data.append(x)
    
    def getData(self):
        return string.join(self.data)

    def close(self):
        sys.stdout = self.oldoutput
        self.closed = 1
        
    def __del__(self):
        if not self.closed:
            self.close()
    
                
def testOutputGrabber():
    gr = OutputGrabber()
    for i in range(10):
        print 'line',i
    data = gr.getData()
    gr.close()
    print 'Data...',data
    

##############################################################
#
#            PDF Object Hierarchy
#
##############################################################



class PDFObject:
    """Base class for all PDF objects.  In PDF, precise measurement
    of file offsets is essential, so the usual trick of just printing
    and redirecting output has proved to give different behaviour on
    Mac and Windows.  While it might be soluble, I'm taking charge
    of line ends at the binary level and explicitly writing to a file.
    The LINEEND constant lets me try CR, LF and CRLF easily to help
    pin down the problem."""
    def save(self, file):
        "Save its content to an open file"
        file.write('% base PDF object' + LINEEND)
    def printPDF(self):
        self.save(sys.stdout)
    

class PDFLiteral(PDFObject):
    " a ready-made one you wish to quote"
    def __init__(self, text):
        self.text = text
    def save(self, file):
        file.write(self.text + LINEEND)



class PDFCatalog(PDFObject):
    "requires RefPages and RefOutlines set"
    PageMode = "/UseNone"
    def __init__(self):
        self.template = string.join([
                        '<<',
                        '/Type /Catalog',
                        '/Pages %d 0 R',
                        '/Outlines %d 0 R',
                        '/PageMode %s',
                        '>>'
                        ],LINEEND
                        )
    def showOutline(self):
        self.PageMode = "/UseOutlines"
    def save(self, file):
        file.write(self.template % (self.RefPages, self.RefOutlines, self.PageMode) + LINEEND)


class PDFInfo(PDFObject):
    """PDF documents can have basic information embedded, viewable from
    File | Document Info in Acrobat Reader.  If this is wrong, you get
    Postscript errors while printing, even though it does not print."""
    def __init__(self):
        self.title = "untitled"
        self.author = "anonymous"
        self.subject = "unspecified"

        now = time.localtime(time.time())
        self.datestr = '%04d%02d%02d%02d%02d%02d' % tuple(now[0:6])

    def save(self, file):
        file.write(string.join([
                "<</Title (%s)",
                "/Author (%s)",
                "/CreationDate (D:%s)",
                "/Producer (PDFgen)",
                "/Subject (%s)",
                ">>"
                ], LINEEND
            ) % ( 
    pdfutils._escape(self.title), 
    pdfutils._escape(self.author), 
    self.datestr, 
    pdfutils._escape(self.subject)
    ) + LINEEND)
    


class PDFOutline0(PDFObject):
    "null outline, does nothing yet"
    def __init__(self):
        self.template = string.join([
                '<<',
                '/Type /Outlines',
                '/Count 0',
                '>>'],
                LINEEND)
    def save(self, file):
        file.write(self.template + LINEEND)
        
class PDFOutline(PDFObject):
    """takes a recursive list of outline destinations
       like
           out = PDFOutline1()
           out.setNames(canvas, # requires canvas for name resolution
             "chapter1dest",
             ("chapter2dest",
              ["chapter2section1dest",
               "chapter2section2dest",
               "chapter2conclusiondest"]
             ), # end of chapter2 description
             "chapter3dest",
             ("chapter4dest", ["c4s1", "c4s2"])
             )
       Higher layers may build this structure incrementally. KISS at base level.
    """
    # first attempt, many possible features missing.
    #no init for now
    mydestinations = ready = None
    counter = 0
    def setDestinations(self, destinationtree):
        self.mydestinations = destinationtree
    def save(self, file):
        c = self.count
        if c==0:
           file.write(BasicPDFDictString(Type="/Outlines", Count=c))
           return
        first = self.first
        last = self.last
        file.write(BasicPDFDictString(Type="/Outlines", Count=c, First=first, Last=last))
    def setNames(self, canvas, *nametree):
        desttree = self.translateNames(canvas, nametree)
        self.setDestinations(desttree)
    def translateNames(self, canvas, object):
        "recursively translate tree of names into tree of destinations"
        from types import ListType, TupleType, StringType
        Ot = type(object)
        if Ot is StringType:
            return {object: canvas._bookmarkReference(object)} # name-->ref
        if Ot is ListType or Ot is TupleType:
            L = []
            for o in object:
                L.append(self.translateNames(canvas, o))
            if Ot is TupleType:
                return tuple(L)
            return L
        raise "in outline, destination name must be string: got a %s" % Ot
    def prepare(self, document):
        """prepare all data structures required for save operation (create related objects)"""
        if self.mydestinations is None:
            self.first = self.last = None
            self.count = 0
            self.ready = 1
            return
        #self.first = document.objectReference("Outline.First")
        #self.last = document.objectReference("Outline.Last")
        self.count = count(self.mydestinations)
        (self.first, self.last) = self.maketree(document, self.mydestinations, toplevel=1)
        self.ready = 1
    def maketree(self, document, destinationtree, Parent=None, toplevel=0):
        from types import ListType, TupleType, DictType
        if toplevel:
            levelname = "Outline"
            Parent = document.objectReference("Outline")
        else:
            self.count = self.count+1
            levelname = "Outline.%s" % self.count
            if Parent is None:
                raise ValueError, "non-top level outline elt parent must be specified"
        if type(destinationtree) is not ListType and type(destinationtree) is not TupleType:
            raise ValueError, "destinationtree must be list or tuple, got %s"
        nelts = len(destinationtree)
        lastindex = nelts-1
        lastelt = firstref = lastref = None
        for index in range(nelts):
            eltobj = OutlineEntryObject()
            eltobj.Parent = Parent
            eltname = "%s.%s" % (levelname, index)
            eltref = document.objectReference(eltname)
            document.add(eltname, eltobj)
            if lastelt is not None:
                lastelt.Next = eltref
                eltobj.Prev = lastref
            if firstref is None:
                firstref = eltref
            lastref = eltref
            lastelt = eltobj # advance eltobj
            lastref = eltref
            elt = destinationtree[index]
            te = type(elt)
            if te is DictType:
                # simple leaf {name: dest}
                leafdict = elt
            elif te is TupleType:
                # leaf with subsections: ({name: ref}, subsections)
                try:
                    (leafdict, subsections) = elt
                except:
                    raise ValueError, "destination tree elt tuple should have two elts, got %s" % len(elt)
                eltobj.Count = count(subsections)
                (eltobj.First, eltobj.Last) = self.maketree(document, subsections, eltref)
            else:
                raise ValueError, "destination tree elt should be dict or tuple, got %s" % te
            try:
                [(Title, Dest)] = leafdict.items()
            except:
                raise ValueError, "bad outline leaf dictionary, should have one entry "+str(elt)
            eltobj.Title = Title
            eltobj.Dest = Dest
        return (firstref, lastref)
def count(tree): 
    """utility for outline: recursively count leaves in a tuple/list tree"""
    from types import TupleType, ListType
    from operator import add
    tt = type(tree)
    if tt is TupleType or tt is ListType:
        return reduce(add, map(count, tree))
    return 1
    
class OutlineEntryObject(PDFObject):
    "an entry in an outline"
    Title = Dest = Parent = Prev = Next = First = Last = Count = None
    def save(self, file):
        D = {}
        D["Title"] = PDFString(self.Title)
        D["Parent"] = self.Parent
        D["Dest"] = self.Dest
        for n in ("Prev", "Next", "First", "Last", "Count"):
            v = getattr(self, n)
            if v is not None:
                D[n] = v
        file.write(apply(BasicPDFDictString, (), D))
    

class PDFPageCollection(PDFObject):
    "presumes PageList attribute set (list of integers)"
    def __init__(self):
        self.PageList = []

    def save(self, file):
        lines = [ '<<',
                '/Type /Pages',
                '/Count %d' % len(self.PageList),
                '/Kids ['
                ]
        for page in self.PageList:
            lines.append(str(page) + ' 0 R ')
        lines.append(']')
        lines.append('>>')
        text = string.join(lines, LINEEND)
        file.write(text + LINEEND)


class ResourceDictUserMixin:
    """common functionality for PDFObjects that have resource dictionaries"""
    #override
    info = None

    def resourceDict(self, **kw):
        info = {}
        if self.info:
            info.update(self.info)
        info.update(kw)
        #info = self.info
        L = []
        a = L.append
        a("<<")
        a("    /Font %(fontdict)s" % info)
        a("    /ProcSet %(procsettext)s" % info)
        #if self.XObjects:
        #    a("    /XObject "+self.XObjects)
        if info.has_key("XObjects") and info["XObjects"]:
             a("    /XObject "+info["XObjects"])
        a(">>")
        #a("")
        return string.join(L, LINEEND)
        
class PDFPage(PDFObject, ResourceDictUserMixin):
    """The Bastard.  Needs list of Resources etc. Use a standard one for now.
    It manages a PDFStream object which must be added to the document's list
    of objects as well."""
    def __init__(self):
        self.drawables = []
        self.pagewidth = 595  #these are overridden by piddlePDF
        self.pageheight = 842
        self.stream = PDFStream()
        self.hasImages = 0
        # when set this should be a python string containing a PDF XObject dictionary
        self.XObjects = ""
        # when full, should contain a list of pdfgen annotation names
        #self.AnnotationNames = [] (not used)
        # when set, should contain a list of object references equivalent to names above
        self.Annots = []
        self.pageTransitionString = ''  # presentation effects
        # editors on different systems may put different things in the line end
        # without me noticing.  No triple-quoted strings allowed!
        self.template = string.join([
                '<<',
                '/Type /Page',
                '/Parent %(parentpos)d 0 R',
                '/Resources',
                #'   <<',
                #'   /Font %(fontdict)s',
                #'   /ProcSet %(procsettext)s',
                #'   >>',
                "%(resourcedict)s",
                '/MediaBox [0 0 %(pagewidth)d %(pageheight)d]',  #A4 by default
                '/Contents %(contentspos)d 0 R',
                '%(transitionString)s',
                '%(Annots)s',
                '>>'],
            LINEEND)
            
    #def addXObjectDictString(XObjectDictString): set directly (also for form)
    #    self.XObjects = XObjectDictString
        
    def setCompression(self, onoff=0):
        "Turns page compression on or off"
        assert onoff in [0,1], "Page compression options are 1=on, 2=off"
        self.stream.compression = onoff 
        
    def save(self, file):
        info = self.info
        info['pagewidth'] = self.pagewidth
        info['pageheight'] = self.pageheight
        # check for image support
        if self.hasImages:
            info['procsettext'] = '[/PDF /Text /ImageC]'
        else:
            info['procsettext'] = '[/PDF /Text]'
        info['transitionString'] = self.pageTransitionString
        info['resourcedict'] = self.resourceDict(XObjects=self.XObjects)
        Annots = self.Annots
        if Annots:
            info['Annots'] = "/Annots %s" % apply(BasicPDFArrayString,Annots)
        else:
            info['Annots'] = ""

        #print self.template
        #print info
        file.write(self.template % info + LINEEND)

    def clear(self):
        self.drawables = []
    
    def setStream(self, data):
        if type(data) is ListType:
            data = string.join(data, LINEEND)
        self.stream.setStream(data)

TestStream = "BT /F6 24 Tf 80 672 Td 24 TL (   ) Tj T* ET"


class PDFStream(PDFObject):
    "Used for the contents of a page"
    def __init__(self):
        self.data = None
        self.compression = 0

    def setStream(self, data):
        self.data = data
        
    def streamDict(self, **kw):
        if self.compression:
            return '<< /Length %(length)d /Filter [/ASCII85Decode /FlateDecode]>>' % kw + LINEEND
        else:
            return '<< /Length %(length)d >>' % kw + LINEEND

    def save(self, file):
        #avoid crashes if they wrote nothing in the page
        if self.data == None:
             self.data = TestStream

        if self.compression == 1:
            comp = zlib.compress(self.data)   #this bit is very fast...
            base85 = pdfutils._AsciiBase85Encode(comp) #...sadly this isn't
            wrapped = pdfutils._wrap(base85)
            data_to_write = wrapped
        else:
            data_to_write = self.data
        # the PDF length key should contain the length including
        # any extra LF pairs added by Print on DOS.
        
        #lines = len(string.split(self.data,'\n'))
        #length = len(self.data) + lines   # one extra LF each
        length = len(data_to_write) + len(LINEEND)    #AR 19980202
        #arw: mar16 2000: make more general for subclassing
        #if self.compression:
        #    file.write('<< /Length %d /Filter [/ASCII85Decode /FlateDecode]>>' % length + LINEEND)
        #else:
        #    file.write('<< /Length %d >>' % length + LINEEND)
        file.write(self.streamDict(length=length))
        file.write('stream' + LINEEND)
        file.write(data_to_write + LINEEND)
        file.write('endstream' + LINEEND)
        
PDFFormDictTemplate = string.join([ # from pdf spec mar 11 1999 p 257 (arw)
  "<< /Type /XObject /Subtype /Form /FormType 1",
  "/BBox [%(lowerx)d %(lowery)d %(upperx)d %(uppery)d]",
  "/Matrix [1 0 0 1 0 0]", # constant matrix for now
  "/Length %(length)d",
  "%(filter)s",
  "/Resources",
  "%(resourcedict)s",
  "%(Annots)s",
  ">>",
  ""], LINEEND) 
        
class PDFFormXObject(PDFStream, ResourceDictUserMixin):
    # like page requires .info set by some higher level (doc)
    # XXXX any resource used in a form must be propagated up to the page that (recursively) uses
    #   the form!! (not implemented yet).
    XObjects = Annots = None
    compression = 0
    def __init__(self, lowerx, lowery, upperx, uppery):
        self.lowerx = lowerx; self.lowery=lowery; self.upperx=upperx; self.uppery=uppery
    def streamDict(self, **kw):
        D = {"lowerx":self.lowerx, "lowery": self.lowery, "upperx":self.upperx, "uppery":self.uppery, "filter":""}
        if self.compression: D["filter"] = "/Filter [/ASCII85Decode /FlateDecode]"
        D["resourcedict"] = self.resourceDict(procsettext="[/PDF /Text /ImageC]", XObjects=self.XObjects)
        Annots = self.Annots
        if Annots:
            D['Annots'] = "/Annots %s" % apply(BasicPDFArrayString,Annots)
        else:
            D['Annots'] = ""
        D.update(kw)
        return PDFFormDictTemplate % D
    def setStreamList(self, data):
        if type(data) is ListType:
            data = string.join(data, LINEEND)
        self.setStream(data)
        
class Annotation(PDFObject):
    """superclass for all annotations."""
    defaults = (("Type", "/Annot"),)
    required = ("Type", "Rect", "Contents", "Subtype")
    permitted = required+(
      "Border", "C", "T", "M", "F", "H", "BS", "AA", "AS", "Popup", "P")
    def cvtdict(self, d):
        """transform dict args from python form to pdf string rep as needed"""
        Rect = d["Rect"]
        from types import StringType
        if type(Rect) is not StringType:
            d["Rect"] = apply(BasicPDFArrayString, tuple(Rect))
        d["Contents"] = PDFString(d["Contents"])
        return d
    def AnnotationDict(self, **kw):
        d = {}
        for (name,val) in self.defaults:
            d[name] = val
        d.update(kw)
        for name in self.required:
            if not d.has_key(name):
                raise ValueError, "keyword argument %s missing" % name
        d = self.cvtdict(d)
        permitted = self.permitted
        for name in d.keys():
            if name not in permitted:
                raise ValueError, "bad annotation dictionary name %s" % name
        return apply(BasicPDFDictString, (), d)
    def DictString(self):
        raise ValueError, "DictString undefined for virtual superclass Annotation, must overload"
        # but usually
        #return self.AnnotationDict(self, Rect=(a,b,c,d)) or whatever
    def save(self, file):
        file.write(self.DictString())

class TextAnnotation(Annotation):
    permitted = Annotation.permitted + (
        "Open", "Name", "AP")
    def __init__(self, Rect, Contents, **kw):
        self.Rect = Rect
        self.Contents = Contents
        self.otherkw = kw
    def DictString(self):
        d = {}
        d.update(self.otherkw)
        d["Rect"] = self.Rect
        d["Contents"] = self.Contents
        d["Subtype"] = "/Text"
        return apply(self.AnnotationDict, (), d)
        
class LinkAnnotation(Annotation):
    
    permitted = Annotation.permitted + (
        "Dest", "A", "PA")
    def __init__(self, Rect, Contents, Destination, Border="[0 0 1]", **kw):
        self.Border = Border
        self.Rect = Rect
        self.Contents = Contents
        self.Destination = Destination
        self.otherkw = kw
        
    def dummyDictString(self): # old, testing
        return """
          << /Type /Annot /Subtype /Link /Rect [71 717 190 734] /Border [16 16 1]
             /Dest [23 0 R /Fit] >>
             """
             
    def DictString(self):
        d = {}
        d.update(self.otherkw)
        d["Border"] = self.Border
        d["Rect"] = self.Rect
        d["Contents"] = self.Contents
        d["Subtype"] = "/Link"
        d["Dest"] = self.Destination
        return apply(self.AnnotationDict, (), d)
        
class Destination:
    """not a pdfobject!  This is a placeholder that can convert itself
       to a string only after it has been defined by the methods
       below.  EG a Destination can refer to Appendix A before it has been
       defined, but only if Appendix A is explicitly noted as a destination
       and resolved before the document is generated...
       For example the following sequence causes resolution before doc generation.
          d = Destination()
          d.fit() # or other format defining method call
          d.setPageRef("20 0 R")
       (at present setPageRef is called on generation of the page).
    """
    representation = format = pageref = None
    def __init__(self,name):
        self.name = name
    def __str__(self):
        f = self.format
        if f is None: raise ValueError, "format not resolved %s" % self.name
        p = self.pageref
        if p is None: raise ValueError, "Page reference unbound %s" % self.name
        return f % p
    def xyz(self, left, top, zoom):  # see pdfspec mar 11 99 pp184+
        self.format = "[ %%s /XYZ %s %s %s ]" % (left, top, zoom)
    def fit(self):
        self.format = "[ %s /Fit ]"
    def fitb(self):
        self.format = "[ %s /FitB ]"
    def fith(self, top):
        self.format = "[ %%s /FitH %s ]" % top
    def fitv(self, left):
        self.format = "[ %%s /FitV %s ]" % left
    def fitbh(self, top):
        self.format = "[ %%s /FitBH %s ]" % top
    def fitbv(self, left):
        self.format = "[ %%s /FitBV %s ]" % left
    def setPageRef(self, pageref):
        self.pageref = pageref
        
class BindableStr:
    """trick to make an object whose str() operation may be defined later."""
    strValue = None
    def __init__(self, name):
        self.name = name
    def __str__(self):
        v = self.value
        if v is None: raise ValueError, "str value unbound for name %s" % self.name
        return v
    def bind(self, v):
        self.value = v

# this one doesn't seem to work (but I'm not sure :( ).
class InkAnnotation(Annotation):
    permitted = Annotation.permitted + (
        "InkList", "BS", "AP")
    def __init__(self, Rect, Contents, InkList, **kw):
        # inklist should be a list of tuples representing a path (in default user space)
        self.Rect = Rect
        self.Contents = Contents
        self.InkList = InkList
        self.otherkw = kw
    def DictString(self):
        InkList = self.InkList
        # convert the inklist seq of seq into pdf string rep
        #InkList = map(BasicPDFArrayString, InkList)
        L = []
        for e in InkList:
            L.append(apply(BasicPDFArrayString, e))
        InkList = apply(BasicPDFArrayString, tuple(L))
        d = {}
        d["InkList"] = InkList
        d["Rect"] = self.Rect
        d["Contents"] = self.Contents
        d.update(self.otherkw)
        d["Subtype"] = "Ink"
        return apply(self.AnnotationDict, (), d)
###### more helpers ###### (maybe these should be in utils or in a separate file?)
def BasicPDFDictString(**kw):
    """from a set of keyword arguments (with string values)
       make a PDF dictionary."""
    L = []
    a = L.append
    a("<<")
    for name in kw.keys():
        val = kw[name]
        # XXXX should check name and val for valid data!!!
        a("  /%s" % name)
        a("      %s" % val)
    a(">>")
    a("")
    return string.join(L, LINEEND)
   
def BasicPDFArrayString(*args):
    """from a list of positional arguments (with string or int values)
       make a PDF array"""
    # XXXX should check elts for valid data
    L = ["["]
    a = L.append
    for arg in args:
        a(" %s" % arg)
    a("]")
    return string.join(L, "")
    
def PDFString(str):
    return "(%s)" % pdfutils._escape(str)
    
##### end helpers #####


class PDFImage(PDFObject):
    # sample one while developing.  Currently, images go in a literals
    def save(self, file):
        file.write(string.join([
                '<<',
                '/Type /XObject',
                '/Subtype /Image',
                '/Name /Im0',
                '/Width 24',
                '/Height 23',
                '/BitsPerComponent 1',
                '/ColorSpace /DeviceGray',
                '/Filter /ASCIIHexDecode',
                '/Length 174',
                '>>',
                'stream',
                '003B00 002700 002480 0E4940 114920 14B220 3CB650',
                '75FE88 17FF8C 175F14 1C07E2 3803C4 703182 F8EDFC',
                'B2BBC2 BB6F84 31BFC2 18EA3C 0E3E00 07FC00 03F800',
                '1E1800 1FF800>',
                'endstream',
                'endobj'
                ], LINEEND) + LINEEND)

class PDFType1Font(PDFObject):
    def __init__(self, key, font):
        self.fontname = font
        self.keyname = key
        self.template = string.join([
                    '<<',
                    '/Type /Font',
                    '/Subtype /Type1',
                    '/Name /%s',
                    '/BaseFont /%s',
                    '/Encoding /MacRomanEncoding',
                    '>>'],
                    LINEEND)
    def save(self, file):
        file.write(self.template % (self.keyname, self.fontname) + LINEEND)


       





##############################################################
#
#            some helpers
#
##############################################################

def MakeType1Fonts():
    "returns a list of all the standard font objects"
    fonts = []
    pos = 1
    for fontname in StandardEnglishFonts:
        font = PDFType1Font('F'+str(pos), fontname)
        fonts.append(font)
        pos = pos + 1
    return fonts

def MakeFontDictionary(startpos, count):
    "returns a font dictionary assuming they are all in the file from startpos"    
    dict = "  <<" + LINEEND
    pos = startpos
    for i in range(count):
        dict = dict + '\t\t/F%d %d 0 R ' % (i + 1, startpos + i) + LINEEND
    dict = dict + "\t\t>>" + LINEEND
    return dict
        
if __name__ == '__main__':
	#these tests are for memory leaks only
	doc = PDFDocument()
