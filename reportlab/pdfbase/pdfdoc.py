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
#	Revision 1.28  2000/10/18 16:37:22  aaron_watters
#	undid last checkin and added an option for a default outline (different fix)
#
#	Revision 1.27  2000/10/18 16:26:17  aaron_watters
#	moved the outline preprocessing step into the format method (fixes testing error)
#	
#	Revision 1.26  2000/10/18 05:03:21  aaron_watters
#	complete revision of pdfdoc.  Not finished (compression missing, testing needed)
#	I got Robin's last change in at the last moment :)
#	
#	Revision 1.24  2000/09/08 10:04:08  rgbecker
#	Paul Eddington's unix tell() returns a LongIntType bugfix
#	
#	Revision 1.23  2000/08/24 02:26:04  aaron_watters
#	change to PDFLiteral to support "lazy string conversions" (to support lazy crosslinks)
#	
#	Revision 1.22  2000/08/09 10:57:52  rgbecker
#	Andy's Symbol/Zapf font fix
#	
#	Revision 1.21  2000/06/26 15:58:22  rgbecker
#	Simple fix to widths problem
#	
#	Revision 1.20  2000/06/23 17:51:22  aaron_watters
#	/Producer (ReportLab http://www.reportlab.com) in document
#	
#	Revision 1.19  2000/06/01 09:44:26  rgbecker
#	SaveToFile: only close the file if we opened it.
#	Aggregated from types imports to module level.
#	
#	Revision 1.18  2000/04/28 17:33:44  andy_robinson
#	Added font encoding support and changed default encoding to WinAnsi
#	
#	Revision 1.17  2000/04/28 09:08:42  rgbecker
#	Fix typo in SaveToFile
#	
#	Revision 1.16  2000/04/27 18:11:56  rgbecker
#	Dinu's SaveFile patch
#	
#	Revision 1.15  2000/04/25 20:19:07  aaron_watters
#	added support for closed outline entries
#	
#	Revision 1.14  2000/04/18 19:50:30  aaron_watters
#	Minor support for inPage/inForm api elimination in canvas
#	
#	Revision 1.13  2000/04/15 15:00:09  aaron_watters
#	added support for addOutlineEntry0 api
#	
#	Revision 1.12  2000/04/06 09:52:02  andy_robinson
#	Removed some old comments; tweaks to experimental Outline methods.
#	
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
__version__=''' $Id: pdfdoc.py,v 1.28 2000/10/18 16:37:22 aaron_watters Exp $ '''
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
"""extremely anally  retentive structured version of pdfdoc"""

DEFAULT_ENCODING = 'WinAnsiEncoding' #hack here for a system wide change
ALLOWED_ENCODINGS = ('WinAnsiEncoding', 'MacRomanEncoding')

PDFError = 'PDFError'

StandardEnglishFonts = [
    'Courier', 'Courier-Bold', 'Courier-Oblique', 'Courier-BoldOblique',  
    'Helvetica', 'Helvetica-Bold', 'Helvetica-Oblique', 
    'Helvetica-BoldOblique',
    'Times-Roman', 'Times-Bold', 'Times-Italic', 'Times-BoldItalic',
    'Symbol','ZapfDingbats']

# set this flag to get more vertical whitespace (and larger files)
LongFormat = 1

# XXXX stream filters need to be added

# __InternalName__ is a special attribute that can only be set by the Document arbitrator
__InternalName__ = "__InternalName__"

# __RefOnly__ marks reference only elements that must be formatted on top level
__RefOnly__ = "__RefOnly__"

# __Comment__ provides a (one line) comment to inline with an object ref, if present
#   if it is more than one line then percentize it...
__Comment__ = "__Comment__"
DoComments = 1

# name for standard font dictionary
BasicFonts = "BasicFonts"

# name for the pages object
Pages = "Pages"

### generic utilities

import string, types
from reportlab.pdfbase import pdfutils
from reportlab.pdfbase.pdfutils import LINEEND   # this constant needed in both

# for % substitutions
LINEENDDICT = {"LINEEND": LINEEND, "PERCENT": "%"}

def markfilename(filename):
	# with the Mac, we need to tag the file in a special
	#way so the system knows it is a PDF file.
	#This supplied by Joe Strout
	import os
	if os.name == 'mac':
		import macfs
		try: 
			macfs.FSSpec(filename).SetCreatorType('CARO','PDF ')
		except:
			pass

def format(element, document, toplevel=0):
    """Indirection step for formatting.
       Ensures that document parameters alter behaviour
       of formatting for all elements.
    """
    from types import InstanceType
    if type(element) is InstanceType:
        if not toplevel and hasattr(element, __RefOnly__):
            # the object cannot be a component at non top level.
            # make a reference to it and return it's format
            R = document.Reference(element)
            return R.format(document)
        else:
            try:
                fmt = element.format
            except:
                raise AttributeError, "%s has no format operation" % element
            f = fmt(document)
            if DoComments and hasattr(element, __Comment__):
                f = "%s%s%s%s" % ("% ", element.__Comment__, LINEEND, f)
            return f
    else:
        return str(element)

def indent(s, IND=LINEEND+" "):
    return string.replace(s, LINEEND, IND)

### the global document structure manager

class PDFDocument:
    objectcounter = 0
    inObject = None
    # set this to define filters 
    defaultStreamFilters = None
    pageCounter = 1
    def __init__(self, encoding=DEFAULT_ENCODING, dummyoutline=0):
        self.encoding = encoding
        # mapping of internal identifier ("Page001") to PDF objectnumber and generation number (34, 0)
        self.idToObjectNumberAndVersion = {}
        # mapping of internal identifier ("Page001") to PDF object (PDFPage instance)
        self.idToObject = {}
        # internal id to file location
        self.idToOffset = {}
        # number to id
        self.numberToId = {}
        cat = self.Catalog = self._catalog = PDFCatalog()
        pages = self.Pages = PDFPages()
        cat.Pages = pages
        if dummyoutline:
            outlines = PDFOutlines0()
        else:
            outlines = PDFOutlines()
        self.Outlines = self.outline = outlines
        cat.Outlines = outlines
        self.info = self.Info = PDFInfo()
        self.Reference(self.Catalog)
        self.Reference(self.Info)
        # make std fonts (this could be made optional
        self.fontMapping = {}
        MakeStandardEnglishFontObjects(self, encoding)

    def SaveToFile(self, filename, canvas):
        # prepare outline
        outline = self.outline
        outline.prepare(self, canvas)
        from types import StringType
        if type(filename) is StringType:
            myfile = 1
            f = open(filename, "wb")
        else:
            myfile = 0
            f = filename # IT BETTER BE A FILE-LIKE OBJECT!
        txt = self.format()
        f.write(txt)
        if myfile:
            f.close()
            markfilename(filename) # do platform specific file junk
        
    def inPage(self):
        """specify the current object as a page (enables reference binding and other page features)"""
        if self.inObject is not None:
            if self.inObject=="page": return
            raise ValueError, "can't go in page already in object %s" % self.inObject
        self.inObject = "page"

    def inForm(self):
        """specify that we are in a form xobject (disable page features, etc)"""
        if self.inObject not in ["form", None]:
            raise ValueError, "can't go in form already in object %s" % self.inObject
        self.inObject = "form"
        # don't need to do anything else, I think...        

    def getInternalFontName(self, psfontname):
        fm = self.fontMapping
        if fm.has_key(psfontname):
            return fm[psfontname]
        else:
            raise PDFError, "Font %s not available in document" % repr(psfontname)

    def thisPageName(self):
        return "Page"+repr(self.pageCounter)

    def thisPageRef(self):
        return PDFObjectReference(self.thisPageName())

    def addPage(self, page):
        name = self.thisPageName()
        self.Reference(page, name)
        self.Pages.addPage(page)
        self.pageCounter = self.pageCounter+1
        self.inObject = None

    def formName(self, externalname):
        return "FormXob.%s" % externalname
    
    def addForm(self, name, form):
        """add a Form XObject."""
        # XXX should check that name is a legal PDF name
        if self.inObject != "form":
            self.inForm()
        self.Reference(form, self.formName(name))
        self.inObject = None

    def annotationName(self, externalname):
        return "Annot.%s"%externalname
    
    def addAnnotation(self, name, annotation):
        self.Reference(annotation, self.annotationName(name))
        
    def refAnnotation(self, name):
        internalname = self.annotationName(name)
        return PDFObjectReference(internalname)
        
    def setTitle(self, title):
        "embeds in PDF file"
        self.info.title = title
        
    def setAuthor(self, author):
        "embedded in PDF file"
        self.info.author = author
            
    def setSubject(self, subject):
        "embeds in PDF file"
        self.info.subject = subject

    def getAvailableFonts(self):
        fontnames = self.fontMapping.keys()
        fontnames.sort()
        return fontnames
    
    def format(self):
        # register the Catalog/INfo and then format the objects one by one until exhausted
        # (possible infinite loop if there is a bug that continually makes new objects/refs...)
        cat = self.Catalog
        info = self.Info
        self.Reference(self.Catalog)
        self.Reference(self.Info)
        # make std fonts (this could be made optional
        counter = 0 # start at first object (object 1 after preincrement)
        ids = [] # the collection of object ids in object number order
        numbertoid = self.numberToId
        idToNV = self.idToObjectNumberAndVersion
        idToOb = self.idToObject
        idToOf = self.idToOffset
        ### note that new entries may be "appended" DURING FORMATTING
        done = None
        File = PDFFile() # output collector
        while done is None:
            counter = counter+1 # do next object...
            if numbertoid.has_key(counter):
                id = numbertoid[counter]
                #printidToOb
                obj = idToOb[id]
                IO = PDFIndirectObject(id, obj)
                IOf = IO.format(self)
                # add a comment to the PDF output
                if DoComments:
                    File.add("%% %s %s %s" % (repr(id), repr(repr(obj)[:50]), LINEEND))
                offset = File.add(IOf)
                idToOf[id] = offset
                ids.append(id)
            else:
                done = 1
        # sanity checks (must happen AFTER formatting)
        lno = len(numbertoid)
        if counter-1!=lno:
            raise ValueError, "counter %s doesn't match number to id dictionary %s" %(counter, lno)
        # now add the xref
        xref = PDFCrossReferenceTable()
        xref.addsection(0, ids)
        xreff = xref.format(self)
        xrefoffset = File.add(xreff)
        # now add the trailer
        trailer = PDFTrailer(
            startxref = xrefoffset,
            Size = lno,
            Root = self.Reference(cat),
            Info = self.Reference(info)
            )
        trailerf = trailer.format(self)
        File.add(trailerf)
        # return string format for pdf file
        return File.format(self)
    
    def hasForm(self, name):
        """test for existence of named form"""
        internalname = self.formName(name)
        try:
            test = self.idToObject[internalname]          
        except:
            return 0
        else:
            return internalname

    def xobjDict(self, formnames):
        """construct an xobject dict (for inclusion in a resource dict, usually)
           from a list of form names (images not yet supported)"""
        D = {}
        for name in formnames:
            internalname = self.formName(name)
            reference = PDFObjectReference(internalname)
            D[internalname] = reference
        #print "xobjDict D", D
        return PDFDictionary(D)
        
    def Reference(self, object, name=None):
        ### note references may "grow" during the final formatting pass: don't use d.keys()!
        # don't make references to other references, or non instances
        from types import InstanceType
        #print"object type is ", type(object)
        tob = type(object)
        if (tob is not InstanceType) or (tob is InstanceType and object.__class__ is PDFObjectReference):
            return object
        idToObject = self.idToObject
        if hasattr(object, __InternalName__):
            # already registered
            intname = object.__InternalName__
            if name is not None and name!=intname:
                raise ValueError, "attempt to reregister object %s with new name %s" % (
                    repr(intname), repr(name))
            if not idToObject.has_key(intname):
                raise ValueError, "object named but not registered"
            return PDFObjectReference(intname)
        # otherwise register the new object
        objectcounter = self.objectcounter = self.objectcounter+1
        if name is None:
            name = "R"+repr(objectcounter)
        if idToObject.has_key(name):
            raise ValueError, "redefining named object: "+repr(name)
        object.__InternalName__ = name
        self.idToObjectNumberAndVersion[name] = (objectcounter, 0)
        self.numberToId[objectcounter] = name
        idToObject[name] = object
        return PDFObjectReference(name)

### chapter 4 Objects

PDFtrue = "true"
PDFfalse = "false"
PDFnull = "null"

def PDFnumber(n):
    return n

def PDFString(str):
    # might need to change this to class for encryption
    return "(%s)" % pdfutils._escape(str)
    
def PDFName(data):
    # first convert the name
    ldata = list(data)
    index = 0
    for thischar in data:
        if 0x21<=ord(thischar)<=0x7e and thischar not in "%()<>{}[]#":
            pass # no problemo
        else:
            hexord = hex(ord(thischar))[2:] # forget the 0x thing...
            ldata[index] = "#"+hexord
        index = index+1
    data = string.join(ldata, "")
    return "/%s" % data
    
class PDFDictionary:

    multiline = LongFormat
    def __init__(self, dict=None):
        """dict should be namestring to value eg "a": 122 NOT pdfname to value NOT "/a":122"""
        if dict is None:
            self.dict = {}
        else:
            self.dict = dict.copy()
    def __setitem__(self, name, value):
        self.dict[name] = value
    def Reference(name, document):
        ob = self.dict[name]
        self.dict[name] = document.Reference(ob)
    def format(self, document):
        dict = self.dict
        keys = dict.keys()
        keys.sort()
        L = []
        a = L.append
        for k in keys:
            v = dict[k]
            fv = format(v, document)
            fk = format(PDFName(k), document)
            a(fk)
            a(" "+fv)
        #L = map(str, L)
        if self.multiline:
            Lj = string.join(L, LINEEND)
            Lj = indent(Lj)
        else:
            Lj = L
            # break up every 6 elements anyway
            for i in range(6, len(Lj), 6):
                Lj.insert(i,LINEEND)
            Lj = string.join(L, " ")
        return "<< %s >>" % Lj

STREAMFMT = ("%(dictionary)s%(LINEEND)s" # dictionary
             "stream" # stream keyword
             "%(LINEEND)s" # a line end (could be just a \n)
             "%(content)s" # the content, with no lineend
             "endstream%(LINEEND)s" # the endstream keyword
             )
class PDFStream:
    '''set dictionary elements explicitly stream.dictionary[name]=value'''
    ### compression stuff not implemented yet
    __RefOnly__ = 1 # must be at top level
    def __init__(self, dictionary=None, content=None):
        if dictionary is None:
            dictionary = PDFDictionary()
        self.dictionary = dictionary
        self.content = content
        self.filters = None
    def format(self, document):
        dictionary = self.dictionary
        content = self.content
        filters = self.filters
        if self.content is None:
            raise ValueError, "stream content not set"
        if filters is None:
            filters = document.defaultStreamFilters
        if filters is not None:
            raise "oops", "filters for streams not yet implemented"
        fc = format(content, document)
        #print "type(content)", type(content)
        if fc!=content: burp
        # set dictionary length parameter
        dictionary["Length"] = len(content)
        fd = format(dictionary, document)
        sdict = LINEENDDICT.copy()
        sdict["dictionary"] = fd
        sdict["content"] = fc
        return STREAMFMT % sdict

def teststream(content=None):
    #content = "" # test
    if content is None:
        content = teststreamcontent
    content = string.strip(content)
    content = string.replace(content, "\n", LINEEND) + LINEEND
    S = PDFStream()
    S.content = content
    # nothing else needed...
    S.__Comment__ = "test stream"
    return S

teststreamcontent = """
1 0 0 1 0 0 cm BT /F9 12 Tf 14.4 TL ET
1.00 0.00 1.00 rg
n 72.00 72.00 432.00 648.00 re B*
"""       
class PDFArray:
    multiline = LongFormat
    def __init__(self, sequence):
        self.sequence = list(sequence)
    def References(self, document):
        """make all objects in sequence references"""
        self.sequence = map(document.Reference, self.sequence)
    def format(self, document):
        #ssequence = map(str, self.sequence)
        sequence = self.sequence
        fsequence = []
        for elt in sequence:
            felt = format(elt, document)
            fsequence.append(felt)
        if self.multiline:
            Lj = string.join(fsequence, LINEEND)
            Lj = indent(Lj)
        else:
            # break up every 10 elements anyway
            Lj = fsequence
            breakline = LINEEND+" "
            for i in range(10, len(Lj), 10):
                Lj.insert(i,breakline)
            Lj = string.join(Lj)
        return "[ %s ]" % Lj

INDIRECTOBFMT = ("%(n)s %(v)s obj%(LINEEND)s"
                 "%(content)s" "%(LINEEND)s"
                 "endobj" "%(LINEEND)s")

class PDFIndirectObject:
    __RefOnly__ = 1
    def __init__(self, name, content):
        self.name = name
        self.content = content
    def format(self, document):
        name = self.name
        (n, v) = document.idToObjectNumberAndVersion[name]
        content = self.content
        fcontent = format(content, document, toplevel=1) # yes this is at top level
        sdict = LINEENDDICT.copy()
        sdict["n"] = n
        sdict["v"] = v
        sdict["content"] = fcontent
        return INDIRECTOBFMT % sdict

class PDFObjectReference:
    def __init__(self, name):
        self.name = name
    def format(self, document):
        name = self.name
        (n, v) = document.idToObjectNumberAndVersion[name]
        return "%s %s R" % (n,v)

### chapter 5

PDFHeader = ("%PDF-1.3"+LINEEND+"%íì¶¾  "+LINEEND)

class PDFFile:
    ### just accumulates strings: keeps track of current offset
    def __init__(self):
        self.strings = []
        self.offset = 0
        self.add(PDFHeader)
    def add(self, s):
        """should be constructed as late as possible, return position where placed"""
        result = self.offset
        self.offset = result+len(s)
        self.strings.append(s)
        return result
    def format(self, document):
        return string.join(self.strings, "")

XREFFMT = '%0.10d %0.5d n'    

class PDFCrossReferenceSubsection:
    def __init__(self, firstentrynumber, idsequence):
        self.firstentrynumber = firstentrynumber
        self.idsequence = idsequence
    def format(self, document):
        """id sequence should represent contiguous object nums else error. free numbers not supported (yet)"""
        firstentrynumber = self.firstentrynumber
        idsequence = self.idsequence
        entries = list(idsequence)
        nentries = len(idsequence)
        # special case: object number 0 is always free
        taken = {}
        if firstentrynumber==0:
            taken[0] = "standard free entry"
            nentries = nentries+1
            entries.insert(0, "0000000000 65535 f")
        idToNV = document.idToObjectNumberAndVersion
        idToOffset = document.idToOffset
        lastentrynumber = firstentrynumber+nentries-1
        for id in idsequence:
            (num, version) = idToNV[id]
            if taken.has_key(num):
                raise ValueError, "object number collision %s %s %s" % (num, repr(id), repr(taken[id]))
            if num>lastentrynumber or num<firstentrynumber:
                raise ValueError, "object number %s not in range %s..%s" % (num, firstentrynumber, lastentrynumber)
            # compute position in list
            rnum = num-firstentrynumber
            taken[num] = id
            offset = idToOffset[id]
            entries[num] = XREFFMT % (offset, version)
        # now add the initial line
        firstline = "%s %s" % (firstentrynumber, nentries)
        entries.insert(0, firstline)
        # make sure it ends with a LINEEND
        entries.append("")
        if LINEEND=="\n" or LINEEND=="\r":
            reflineend = " "+LINEEND # as per spec
        elif LINEEND=="\r\n":
            reflineend = LINEEND
        else:
            raise ValueError, "bad end of line! %s" % repr(LINEEND)
        return string.join(entries, LINEEND)

class PDFCrossReferenceTable:

    def __init__(self):
        self.sections = []
    def addsection(self, firstentry, ids):
        section = PDFCrossReferenceSubsection(firstentry, ids)
        self.sections.append(section)
    def format(self, document):
        sections = self.sections
        if not sections:
            raise ValueError, "no crossref sections"
        L = ["xref"+LINEEND]
        for s in self.sections:
            fs = format(s, document)
            L.append(fs)
        return string.join(L, "")

TRAILERFMT = ("trailer%(LINEEND)s"
              "%(dict)s%(LINEEND)s"
              "startxref%(LINEEND)s"
              "%(startxref)s%(LINEEND)s"
              "%(PERCENT)s%(PERCENT)sEOF")

class PDFTrailer:

    def __init__(self, startxref, Size=None, Prev=None, Root=None, Info=None, ID=None, Encrypt=None):
        self.startxref = startxref
        if Size is None or Root is None:
            raise ValueError, "Size and Root keys required"
        dict = self.dict = PDFDictionary()
        for (n,v) in [("Size", Size), ("Prev", Prev), ("Root", Root),
                      ("Info", Info), ("Id", ID), ("Encrypt", Encrypt)]:
            if v is not None:
                dict[n] = v
    def format(self, document):
        fdict = format(self.dict, document)
        D = LINEENDDICT.copy()
        D["dict"] = fdict
        D["startxref"] = self.startxref
        return TRAILERFMT % D

#### XXXX skipping incremental update,
#### encryption

#### chapter 6, doc structure

class PDFCatalog:
    __Comment__ = "Document Root"
    __RefOnly__ = 1
    # to override, set as attributes
    __Defaults__ = {"Type": PDFName("Catalog"),
                "PageMode": PDFName("UseNone"),
                }
    __NoDefault__ = string.split("""
        Dests Outlines Pages Threads AcroForm Names OpenActions PageMode URI
        ViewerPreferences PageLabels PageLayout JavaScript StructTreeRoot SpiderInfo"""
                                 )
    __Refs__ = __NoDefault__ # make these all into references, if present
    
    def format(self, document):
        self.check_format(document)
        defaults = self.__Defaults__
        Refs = self.__Refs__
        D = {}
        for k in defaults.keys():
            default = defaults[k]
            v = None
            if hasattr(self, k) and getattr(self,k) is not None:
                v = getattr(self, k)
            elif default is not None:
                v = default
            if v is not None:
                D[k] = v
        for k in self.__NoDefault__:
            if hasattr(self, k):
                v = getattr(self,k)
                if v is not None:
                    D[k] = v
        # force objects to be references where required
        for k in Refs:
            if D.has_key(k):
                #print"k is", k, "value", D[k]
                D[k] = document.Reference(D[k])
        dict = PDFDictionary(D)
        return format(dict, document)

    def showOutline(self):
        self.PageMode = PDFName("UseOutlines")

    def showFullScreen(self):
        self.PageMode = PDFName("FullScreen")
        
    def check_format(self, document):
        """for use in subclasses"""
        pass

# not yet implementing
#  ViewerPreferences, PageLabelDictionaries,

class PDFPages(PDFCatalog):
    """PAGES TREE WITH ONE INTERNAL NODE, FOR "BALANCING" CHANGE IMPLEMENATION"""
    __Comment__ = "page tree"
    __RefOnly__ = 1
    # note: could implement page attribute inheritance...
    __Defaults__ = {"Type": PDFName("Pages"),
                    }
    __NoDefault__ = string.split("Kids Count Parent")
    __Refs__ = ["Parent"]
    def __init__(self):
        self.pages = []
    def __getitem__(self, item):
        return self.pages[item]
    def addPage(self, page):
        self.pages.append(page)
    def check_format(self, document):
        # convert all pages to page references
        pages = self.pages
        kids = PDFArray(self.pages)
        # make sure all pages are references
        kids.References(document)
        self.Kids = kids
        self.Count = len(pages)

class PDFPage(PDFCatalog):
    __Comment__ = "Page dictionary"
    # all PDF attributes can be set explicitly
    # if this flag is set, the "usual" behavior will be suppressed
    Override_default_compilation = 0
    __RefOnly__ = 1
    __Defaults__ = {"Type": PDFName("Page"),
                   # "Parent": PDFObjectReference(Pages),  # no! use document.Pages
                    }
    __NoDefault__ = string.split(""" Parent
        MediaBox Resources Contents CropBox Rotate Thumb Annots B Dur Hid Trans AA
        PieceInfo LastModified SeparationInfo ArtBox TrimBox BleedBox ID PZ
    """)
    __Refs__ = string.split("""
        Contents Parent ID
    """)
    pagewidth = 595
    pageheight = 842
    stream = None
    hasImages = 0
    compression = 0
    XObjects = None
    # transitionstring?
    # xobjects?
    # annotations
    def __init__(self):
        # set all nodefaults to None
        for name in self.__NoDefault__:
            setattr(self, name, None)
    def setCompression(self, onoff):
        self.compression = onoff
    def setStream(self, code):
        if self.Override_default_compilation:
            raise ValueError, "overridden! must set stream explicitly"
        from types import ListType
        if type(code) is ListType:
            code = string.join(code, LINEEND)+LINEEND
        self.stream = code
        
    def check_format(self, document):
        # set up parameters unless usual behaviour is suppressed
        if self.Override_default_compilation:
            return   
        self.MediaBox = self.MediaBox or PDFArray([0, 0, self.pagewidth, self.pageheight])
        if not self.Annots:
            self.Annots = None
        else:
            #print self.Annots
            #raise ValueError, "annotations not reimplemented yet"
            if type(self.Annots) is not types.InstanceType:
                self.Annots = PDFArray(self.Annots)
        if not self.Contents:
            stream = self.stream
            if not stream:
                self.Contents = teststream()
            else:
                S = PDFStream()
                S.content = stream
                # need to add filter stuff (?)
                S.__Comment__ = "page stream"
                self.Contents = S
        if not self.Resources:
            resources = PDFResourceDictionary()
            # fonts!
            resources.basicFonts()
            if self.hasImages:
                resources.allProcs()
            else:
                resources.basicProcs()
            if self.XObjects:
                #print "XObjects", self.XObjects.dict
                resources.XObject = self.XObjects
            self.Resources = resources
        if not self.Parent:
            pages = document.Pages
            self.Parent = document.Reference(pages)

def testpage(document):
    P = PDFPage()
    P.Contents = teststream()
    pages = document.Pages
    P.Parent = document.Reference(pages)
    P.MediaBox = PDFArray([0, 0, 595, 841])
    resources = PDFResourceDictionary()
    resources.allProcs() # enable all procsets
    resources.basicFonts()
    P.Resources = resources
    pages.addPage(P)

#### DUMMY OUTLINES IMPLEMENTATION FOR testing

DUMMYOUTLINE = """
<<
  /Count
      0
  /Type
      /Outlines
>>"""

class PDFOutlines0:
    __Comment__ = "TEST OUTLINE!"
    text = string.replace(DUMMYOUTLINE, "\n", LINEEND)
    __RefOnly__ = 1
    def format(self, document):
        return self.text
        

class OutlineEntryObject:
	"an entry in an outline"
	Title = Dest = Parent = Prev = Next = First = Last = Count = None
	def format(self, document):
		D = {}
		D["Title"] = PDFString(self.Title)
		D["Parent"] = self.Parent
		D["Dest"] = self.Dest
		for n in ("Prev", "Next", "First", "Last", "Count"):
			v = getattr(self, n)
			if v is not None:
				D[n] = v
		PD = PDFDictionary(D)
		return PD.format(document)


class PDFOutlines:
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
	currentlevel = -1 # ie, no levels yet
	
	def __init__(self):
		self.destinationnamestotitles = {}
		self.destinationstotitles = {}
		self.levelstack = []
		self.buildtree = []
		self.closedict = {} # dictionary of "closed" destinations in the outline

	def addOutlineEntry(self, destinationname, level=0, title=None, closed=None):
		"""destinationname of None means "close the tree" """
		from types import IntType, TupleType
		if destinationname is None and level!=0:
			raise ValueError, "close tree must have level of 0"
		if type(level) is not IntType: raise ValueError, "level must be integer, got %s" % type(level)
		if level<0: raise ValueError, "negative levels not allowed"
		if title is None: title = destinationname
		currentlevel = self.currentlevel
		stack = self.levelstack
		tree = self.buildtree
		# adjust currentlevel and stack to match level
		if level>currentlevel:
			if level>currentlevel+1:
				raise ValueError, "can't jump from outline level %s to level %s, need intermediates" %(currentlevel, level)
			level = currentlevel = currentlevel+1
			stack.append([])
		while level<currentlevel:
			# pop off levels to match
			current = stack[-1]
			del stack[-1]
			previous = stack[-1]
			lastinprevious = previous[-1]
			if type(lastinprevious) is TupleType:
				(name, sectionlist) = lastinprevious
				raise ValueError, "cannot reset existing sections: " + repr(lastinprevious)
			else:
				name = lastinprevious
				sectionlist = current
				previous[-1] = (name, sectionlist)
			#sectionlist.append(current)
			currentlevel = currentlevel-1
		if destinationname is None: return
		stack[-1].append(destinationname)
		self.destinationnamestotitles[destinationname] = title
		if closed: self.closedict[destinationname] = 1
		self.currentlevel = level
		
	def setDestinations(self, destinationtree):
		self.mydestinations = destinationtree
		
	def format(self, document):
		D = {}
		D["Type"] = PDFName("Outlines")
		c = self.count
		D["Count"] = c
		if c!=0:
		    D["First"] = self.first
		    D["Last"] = self.last
		PD = PDFDictionary(D)
		return PD.format(document)
		
	def setNames(self, canvas, *nametree):
		desttree = self.translateNames(canvas, nametree)
		self.setDestinations(desttree)
		
	def setNameList(self, canvas, nametree):
		"Explicit list so I don't need to do apply(...) in the caller"
		desttree = self.translateNames(canvas, nametree)
		self.setDestinations(desttree)
		
	def translateNames(self, canvas, object):
		"recursively translate tree of names into tree of destinations"
		from types import StringType, ListType, TupleType
		Ot = type(object)
		destinationnamestotitles = self.destinationnamestotitles
		destinationstotitles = self.destinationstotitles
		closedict = self.closedict
		if Ot is StringType:
			destination = canvas._bookmarkReference(object)
			title = object
			if destinationnamestotitles.has_key(object):
				title = destinationnamestotitles[object]
			else:
				destinationnamestotitles[title] = title
			destinationstotitles[destination] = title
			if closedict.has_key(object):
				closedict[destination] = 1 # mark destination closed
			return {object: canvas._bookmarkReference(object)} # name-->ref
		if Ot is ListType or Ot is TupleType:
			L = []
			for o in object:
				L.append(self.translateNames(canvas, o))
			if Ot is TupleType:
				return tuple(L)
			return L
		raise "in outline, destination name must be string: got a %s" % Ot

	def prepare(self, document, canvas):
		"""prepare all data structures required for save operation (create related objects)"""
		if self.mydestinations is None:
			if self.levelstack:
				self.addOutlineEntry(None) # close the tree
				destnames = self.levelstack[0]
				#from pprint import pprint; pprint(destnames); stop
				self.mydestinations = self.translateNames(canvas, destnames)
			else:
				self.first = self.last = None
				self.count = 0
				self.ready = 1
				return
		#self.first = document.objectReference("Outline.First")
		#self.last = document.objectReference("Outline.Last")
		# XXXX this needs to be generalized for closed entries!
		self.count = count(self.mydestinations, self.closedict)
		(self.first, self.last) = self.maketree(document, self.mydestinations, toplevel=1)
		self.ready = 1

	def maketree(self, document, destinationtree, Parent=None, toplevel=0):
		from types import ListType, TupleType, DictType
		tdestinationtree = type(destinationtree)
		if toplevel:
			levelname = "Outline"
			Parent = document.Reference(document.Outlines)
		else:
			self.count = self.count+1
			levelname = "Outline.%s" % self.count
			if Parent is None:
				raise ValueError, "non-top level outline elt parent must be specified"
		if tdestinationtree is not ListType and tdestinationtree is not TupleType:
			raise ValueError, "destinationtree must be list or tuple, got %s"
		nelts = len(destinationtree)
		lastindex = nelts-1
		lastelt = firstref = lastref = None
		destinationnamestotitles = self.destinationnamestotitles
		closedict = self.closedict
		for index in range(nelts):
			eltobj = OutlineEntryObject()
			eltobj.Parent = Parent
			eltname = "%s.%s" % (levelname, index)
			eltref = document.Reference(eltobj, eltname)
			#document.add(eltname, eltobj)
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
				# leaf with subsections: ({name: ref}, subsections) XXXX should clean up (see count(...))
				try:
					(leafdict, subsections) = elt
				except:
					raise ValueError, "destination tree elt tuple should have two elts, got %s" % len(elt)
				eltobj.Count = count(subsections, closedict)
				(eltobj.First, eltobj.Last) = self.maketree(document, subsections, eltref)
			else:
				raise ValueError, "destination tree elt should be dict or tuple, got %s" % te
			try:
				[(Title, Dest)] = leafdict.items()
			except:
				raise ValueError, "bad outline leaf dictionary, should have one entry "+str(elt)
			eltobj.Title = destinationnamestotitles[Title]
			eltobj.Dest = Dest
			if te is TupleType and closedict.has_key(Dest):
				# closed subsection, count should be negative
				eltobj.Count = -eltobj.Count
		return (firstref, lastref)
		
def count(tree, closedict=None): 
	"""utility for outline: recursively count leaves in a tuple/list tree"""
	from operator import add
	from types import TupleType, ListType
	tt = type(tree)
	if tt is TupleType:
		# leaf with subsections XXXX should clean up this structural usage
		(leafdict, subsections) = tree
		[(Title, Dest)] = leafdict.items()
		if closedict and closedict.has_key(Dest):
			return 1 # closed tree element
	if tt is TupleType or tt is ListType:
		#return reduce(add, map(count, tree))
		counts = []
		for e in tree:
			counts.append(count(e, closedict))
		return reduce(add, counts)
	return 1
	
	

#### dummy info
DUMMYINFO = """
<</Title (testing)
/Author (arw)
/CreationDate (D:20001012220652)
/Producer (ReportLab http://www.reportlab.com)
/Subject (this file generated by an alpha test module)
>>
"""
class PDFInfo0:
    __Comment__ = "TEST INFO STRUCTURE"
    text = string.replace(DUMMYINFO, "\n", LINEEND)
    __RefOnly__ = 1
    def format(self, document):
        return self.text

class PDFInfo:
    """PDF documents can have basic information embedded, viewable from
    File | Document Info in Acrobat Reader.  If this is wrong, you get
    Postscript errors while printing, even though it does not print."""
    def __init__(self):
        self.title = "untitled"
        self.author = "anonymous"
        self.subject = "unspecified"
        #now = time.localtime(time.time())
        #self.datestr = '%04d%02d%02d%02d%02d%02d' % tuple(now[0:6])
        
    def format(self, document):
        D = {}
        D["Title"] = PDFString(self.title)
        D["Author"] = PDFString(self.author)
        D["CreationDate"] = PDFDate()
        D["Producer"] = PDFString("ReporLab http://www.reportlab.com")
        D["Subject"] = PDFString(self.subject)
        PD = PDFDictionary(D)
        return PD.format(document)

# skipping thumbnails, etc


class Annotation:
    """superclass for all annotations."""
    defaults = [("Type", PDFName("Annot"),)]
    required = ("Type", "Rect", "Contents", "Subtype")
    permitted = required+(
      "Border", "C", "T", "M", "F", "H", "BS", "AA", "AS", "Popup", "P")
    def cvtdict(self, d):
        """transform dict args from python form to pdf string rep as needed"""
        Rect = d["Rect"]
        if type(Rect) is not types.StringType:
            d["Rect"] = PDFArray(Rect)
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
        return PDFDictionary(d)
    def Dict(self):
        raise ValueError, "DictString undefined for virtual superclass Annotation, must overload"
        # but usually
        #return self.AnnotationDict(self, Rect=(a,b,c,d)) or whatever
    def format(self, document):
        D = self.Dict()
        return D.format(document)

class TextAnnotation(Annotation):
    permitted = Annotation.permitted + (
        "Open", "Name", "AP")
    def __init__(self, Rect, Contents, **kw):
        self.Rect = Rect
        self.Contents = Contents
        self.otherkw = kw
    def Dict(self):
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
             
    def Dict(self):
        d = {}
        d.update(self.otherkw)
        d["Border"] = self.Border
        d["Rect"] = self.Rect
        d["Contents"] = self.Contents
        d["Subtype"] = "/Link"
        d["Dest"] = self.Destination
        return apply(self.AnnotationDict, (), d)
        

# skipping names tree

# skipping actions

# skipping names trees

# skipping to chapter 7

class PDFRectangle:
    def __init__(self, llx, lly, urx, ury):
        self.llx, self.lly, self.ulx, self.ury = llx, lly, urx, ury
    def format(self, document):
        A = PDFArray([self.llx, self.lly, self.ulx, self.ury])
        return format(A, document)

DATEFMT = '%04d%02d%02d%02d%02d%02d'
import time
(nowyyyy, nowmm, nowdd, nowhh, nowm, nows) = tuple(time.localtime(time.time())[:6])

class PDFDate:
    # gmt offset not yet suppported
    def __init__(self, yyyy=nowyyyy, mm=nowmm, dd=nowdd, hh=nowhh, m=nowm, s=nows):
        self.yyyy=yyyy; self.mm=mm; self.dd=dd; self.hh=hh; self.m=m; self.s=s
    def format(self, doc):
        S = PDFString(DATEFMT % (self.yyyy, self.mm, self.dd, self.hh, self.m, self.s))
        return format(S, doc)

  
class Destination:
    """not a pdfobject!  This is a placeholder that can delegates
       to a pdf object only after it has been defined by the methods
       below.  EG a Destination can refer to Appendix A before it has been
       defined, but only if Appendix A is explicitly noted as a destination
       and resolved before the document is generated...
       For example the following sequence causes resolution before doc generation.
          d = Destination()
          d.fit() # or other format defining method call
          d.setPage(p)
       (at present setPageRef is called on generation of the page).
    """
    representation = format = page = None
    def __init__(self,name):
        self.name = name
    def format(self, document):
        f = self.fmt
        if f is None: raise ValueError, "format not resolved %s" % self.name
        p = self.page
        if p is None: raise ValueError, "Page reference unbound %s" % self.name
        f.page = p
        return f.format(document)
    def xyz(self, left, top, zoom):  # see pdfspec mar 11 99 pp184+
        self.fmt = PDFDestinationXYZ(None, left, top, zoom)
    def fit(self):
        self.fmt = PDFDestinationFit(None)
    def fitb(self):
        self.fmt = PDFDestinationFitB(None)
    def fith(self, top):
        self.fmt = PDFDestinationFitH(None,top)
    def fitv(self, left):
        self.fmt = PDFDestinationFitV(None, left)
    def fitbh(self, top):
        self.fmt = PDFDestinationFitBH(None, top)
    def fitbv(self, left):
        self.fmt = PDFDestinationFitBV(None, left)
    def fitr(self, left, bottom, right, top):
        self.fmt = PDFDestinationFitR(None, left, bottom, right, top)
    def setPage(self, page):
        self.page = page
        #self.fmt.page = page # may not yet be defined!
            
class PDFDestinationXYZ:
    typename = "XYZ"
    def __init__(self, page, left, top, zoom):
        self.page = page; self.top=top; self.zoom=zoom
    def format(self, document):
        pageref = document.Reference(self.page)
        A = PDFArray( [ pageref, PDFName(self.typename), self.left, self.top, self.zoom ] )
        return format(A, document)
    
class PDFDestinationFit:
    typename = "Fit"
    def __init__(self, page):
        self.page = page
    def format(self, document):
        pageref = document.Reference(self.page)
        A = PDFArray( [ pageref, PDFName(self.typename) ] )
        return format(A, document)

class PDFDestinationFitB(PDFDestinationFit):
    typename = "FitB"
    
class PDFDestinationFitH:
    typename = "FitH"
    def __init__(self, page, top):
        self.page = page; self.top=top
    def format(self, document):
        pageref = document.Reference(self.page)
        A = PDFArray( [ pageref, PDFName(self.typename), self.top ] )
        return format(A, document)

class PDFDestinationFitBH(PDFDestinationFitH):
    typename = "FitBH"
    
class PDFDestinationFitV:
    typename = "FitV"
    def __init__(self, page, left):
        self.page = page; self.left=left
    def format(self, document):
        pageref = document.Reference(self.page)
        A = PDFArray( [ pageref, PDFName(self.typename), self.left ] )
        return format(A, document)

class PDFDestinationBV(PDFDestinationFitV):
    typename = "FitBV"

class PDFDestinationFitR:
    typename = "FitR"
    def __init__(self, page, left, bottom, right, top):
        self.page = page; self.left=left; self.bottom=bottom; self.right=right; self.top=top
    def format(self, document):
        pageref = document.Reference(self.page)
        A = PDFArray( [ pageref, PDFName(self.typename), self.left, self.bottom, self.right, self.top] )
        return format(A, document)

# named destinations need nothing

# skipping filespecs

class PDFResourceDictionary:
    """each element *could* be reset to a reference if desired"""
    def __init__(self):
        self.ColorSpace = {}
        self.XObject = {}
        self.ExtGState = {}
        self.Font = {}
        self.Pattern = {}
        self.ProcSet = []
        self.Properties = {}
        self.Shading = {}
        # ?by default define the basicprocs
        self.basicProcs()
    stdprocs = map(PDFName, string.split("PDF Text ImageB ImageC ImageI"))
    dict_attributes = ("ColorSpace", "XObject", "ExtGState", "Font", "Pattern", "Properties", "Shading")
    def allProcs(self):
        # define all standard procsets
        self.ProcSet = self.stdprocs
    def basicProcs(self):
        self.ProcSet = self.stdprocs[:2] # just PDF and Text
    def basicFonts(self):
        self.Font = PDFObjectReference(BasicFonts)
    def format(self, document):
        D = {}
        from types import ListType, DictType
        for dname in self.dict_attributes:
            v = getattr(self, dname)
            if type(v) is DictType:
                if v:
                    dv = PDFDictionary(v)
                    D[dname] = dv
            else:
                D[dname] = v
        v = self.ProcSet
        dname = "ProcSet"
        if type(v) is ListType:
            if v:
                dv = PDFArray(v)
                D[dname] = dv
        else:
            D[dname] = v
        DD = PDFDictionary(D)
        return format(DD, document)

class PDFType1Font:
    """no init: set attributes explicitly"""
    __RefOnly__ = 1
    # note! /Name appears to be an undocumented attribute....
    name_attributes = string.split("Type Subtype BaseFont ToUnicode Name")
    Type = "Font"
    Subtype = "Type1"
    # these attributes are assumed to already be of the right type
    local_attributes = string.split("FirstChar LastChar Widths Encoding FontDescriptor")
    def format(self, document):
        D = {}
        for name in self.name_attributes:
            if hasattr(self, name):
                value = getattr(self, name)
                D[name] = PDFName(value)
        for name in self.local_attributes:
            if hasattr(self, name):
                value = getattr(self, name)
                D[name] = value
        #print D
        PD = PDFDictionary(D)
        return PD.format(document)

def MakeStandardEnglishFontObjects(document, encoding=DEFAULT_ENCODING):
    # make the standard fonts and the standard font dictionary
    if encoding not in ALLOWED_ENCODINGS:
        raise ValueError, "bad encoding %s" % repr(encoding)
    D = {}
    count = 1
    fontmapping = document.fontMapping
    for name in StandardEnglishFonts:
        F = PDFType1Font()
        F.BaseFont = name
        F.Encoding = PDFName(DEFAULT_ENCODING)
        F.__Comment__ = "Standard English Font %s" % repr(name)
        fname = "F"+repr(count)
        F.Name = fname
        R = document.Reference(F, fname)
        D[fname] = R
        fontmapping[name] = "/"+fname # record the external to internal name map (NOT REALLY A PDFNAME: PAGE DESC)
        count = count+1
    DD = PDFDictionary(D)
    DD.__Comment__ = "The standard fonts dictionary"
    DDR = document.Reference(DD, BasicFonts)
    return DDR

class PDFTrueTypeFont(PDFType1Font):
    Subtype = "TrueType"
    #local_attributes = string.split("FirstChar LastChar Widths Encoding FontDescriptor") #same

class PDFMMType1Font(PDFType1Font):
    Subtype = "MMType1"

class PDFType3Font(PDFType1Font):
    Subtype = "Type3"
    local_attributes = string.split(
        "FirstChar LastChar Widths CharProcs FontBBox FontMatrix Resources Encoding")

class PDFType0Font(PDFType1Font):
    Subtype = "Type0"
    local_attributes = string.split(
        "DescendantFonts Encoding")

class PDFCIDFontType0(PDFType1Font):
    Subtype = "CIDFontType0"
    local_attributes = string.split(
        "CIDSystemInfo FontDescriptor DW W DW2 W2 Registry Ordering Supplement")

class PDFCIDFontType0(PDFType1Font):
    Subtype = "CIDFontType2"
    local_attributes = string.split(
        "BaseFont CIDToGIDMap CIDSystemInfo FontDescriptor DW W DW2 W2")

class PDFEncoding(PDFType1Font):
    Type = "Encoding"
    name_attributes = string.split("Type BaseEncoding")
    # these attributes are assumed to already be of the right type
    local_attributes = ["Differences"]

# skipping CMaps

class PDFFormXObject:
	# like page requires .info set by some higher level (doc)
	# XXXX any resource used in a form must be propagated up to the page that (recursively) uses
	#   the form!! (not implemented yet).
	XObjects = Annots = BBox = Matrix = Contents = stream = Resources = None
	hasImages = 1 # probably should change
	compression = 0
	def __init__(self, lowerx, lowery, upperx, uppery):
		#not done
		self.lowerx = lowerx; self.lowery=lowery; self.upperx=upperx; self.uppery=uppery
		
	def setStreamList(self, data):
		if type(data) is types.ListType:
			data = string.join(data, LINEEND)
		self.stream = data
		
	def format(self, document):
		self.BBox = self.BBox or PDFArray([self.lowerx, self.lowery, self.upperx, self.uppery])
		self.Matrix = self.Matrix or PDFArray([1, 0, 0, 1, 0, 0])
		if not self.Annots:
			self.Annots = None
		else:
			raise ValueError, "annotations not reimplemented yet"
		if not self.Contents:
			stream = self.stream
			if not stream:
				self.Contents = teststream()
			else:
				S = PDFStream()
				S.content = stream
				# need to add filter stuff (?)
				S.__Comment__ = "xobject form stream"
				self.Contents = S
		if not self.Resources:
			resources = PDFResourceDictionary()
			# fonts!
			resources.basicFonts()
			if self.hasImages:
				resources.allProcs()
			else:
				resources.basicProcs()
		sdict = self.Contents.dictionary
		sdict["Type"] = PDFName("XObject")
		sdict["Subtype"] = PDFName("Form")
		sdict["FormType"] = 1
		sdict["BBox"] = self.BBox
		sdict["Matrix"] = self.Matrix
		sdict["Resources"] = resources
		return self.Contents.format(document)

if __name__=="__main__":
    # first test
    print "line end is", repr(LINEEND)
    print "PDFName", PDFName("test")
    D = PDFDocument(dummyoutline=1)
    print "PDFDict", PDFDictionary({"this":1}).format(D)
    testpage(D)
    txt = D.format()
    fn = "test.pdf"
    f = open(fn, "wb")
    f.write(txt)
    print "wrote", fn

    
            