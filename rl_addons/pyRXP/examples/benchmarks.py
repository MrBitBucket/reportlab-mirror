# benchmark
# MSXML:  This can be downloaded from many places.  You need 3.0
# which is NOT in most newly installed Windows boxes. (650kb)
# http://download.microsoft.com/download/xml/Install/3.0/WIN98Me/EN-US/msxml3.exe
#    for a quick tutorial on MSXML 3.0, see
# http://www.perfectxml.com/articles/xml/msxml30.asp

# you should then run the COM MakePY utility on the Pythonwin menu.
# to get it going as fast as possible.


import sys
import glob
import time
import string
from types import TupleType
import cStringIO
    
def tupleTreeStats(node):
    # counts tags and attributes recursively
    # use for all reportlab parsers
    if node[1] is None:
        attrCount = 0
    else:
        attrCount = len(node[1])
    nodeCount = 1
    if node[2] is not None:
        for child in node[2]:
            if type(child) is TupleType:
                a, n = tupleTreeStats(child)
                attrCount = attrCount + a
                nodeCount = nodeCount + n
    return attrCount, nodeCount

###  pyRXP - our wrapper around Univ of Edinburgh

def getPyRXPParser():
    import pyRXP
    p = pyRXP.Parser()
    return p

def getNonValidatingPyRXPParser():
    import pyRXP
    p = pyRXP.Parser(Validate=0)
    return p

def parseWithPyRXP(parser, rawdata):
    return parser.parse(rawdata)

###  rparsexml - Aaron's very fast pure python parser

def loadRparseXML():
    #it's a module, what the heck
    from rlextra.radxml import rparsexml
    return rparsexml

def parseWithRParseXML(rparsexml, rawdata):
    #first argument is a dummy holding none
    return rparsexml.parsexml0(rawdata)[0] 

###  expattree - tree-building wrapper around pyexpat
def getExpatParser():
    import expattree
    return expattree.ExpatTreeParser()
    
def parseWithExpat(expatParser, rawdata):
    #first argument is a dummy holding none
    return expatParser.parse(rawdata)

####### minidom - non-validating DOM parser in the Python distro

def loadMiniDOM():
    import xml.dom.minidom
    return xml.dom.minidom

def parseWithMiniDOM(dom_module, rawdata):
    #parser is None
    return dom_module.parseString(rawdata)
    
def statsWithMiniDOM(node):
    return (1, 0)

#########  Microsoft XML Parser via COM ######################


def loadMSXML30():
    from win32com.client import Dispatch
    msx = Dispatch('Microsoft.XMLDOM')
    return msx

def parseWithMSXML30(msx, rawdata):
    msx.loadXML(rawdata)
    return msx

def statsWithMSXML30(node):
    #not done
    return (1,0)    

###########4DOM ###############
def load4DOM():
    from xml.dom.ext.reader import PyExpat
    from xml.dom import Node
    reader = PyExpat.Reader()
    return reader

def parseWith4DOM(reader, rawdata):
    return reader.fromString(rawdata)


def statsWith4DOM(node):
    #node
    return (1,0)

def loadCDomlette():
    from Ft.Lib import cDomlettec
    return cDomlettec

def parseWithCDomlette(modul, rawdata):
    io = cStringIO.StringIO(rawdata)
    return modul.parse(io, '')

def statsWithCDomlette(node):
    #node
    return (1,0)

##########put them all together################

TESTMAP = [
    # name of parser; function to initialize if needed;
    # function to parse; function to do stats
    ('pyRXP', getPyRXPParser, parseWithPyRXP, tupleTreeStats),
    ('pyRXP_nonvalidating', getNonValidatingPyRXPParser, parseWithPyRXP, tupleTreeStats),
    ('rparsexml', loadRparseXML, parseWithRParseXML, tupleTreeStats),
    ('expat', getExpatParser, parseWithExpat, tupleTreeStats),
    ('minidom', loadMiniDOM, parseWithMiniDOM, statsWithMiniDOM),
    ('msxml30', loadMSXML30, parseWithMSXML30, statsWithMSXML30),
    ('4dom', load4DOM, parseWith4DOM, statsWith4DOM),
    ('cdomlette', loadCDomlette, parseWithCDomlette, statsWithCDomlette)
    ]    

def interact(testName=None, dtd=1, pause='unknown'):

    # if no DTD requested, trim off first 2 lines; the lack of
    # a DTD reference will put validating parsers into non-
    # validating mode
    if dtd:
        sampleText = open('rml_a.xml').read()
    else:
        print 'DTD declaration removed, non-validating'
        lines = open('rml_a.xml').readlines()[2:]
        sampleText = string.join(lines,'')
        
    if testName:
        found = 0
        for row in TESTMAP:
            if row[0] == testName:
                found = 1
                (name, loadFunc, parseFunc, statFunc) = row
                break
        if not found:
            print 'parser %s not found, please select' % testName

    if not testName:            
    # interactive, show stuff
        print "Interactive benchmark suite for Python XML tree-parsers."
        print 'Using sample XML file %d bytes long' % len(sampleText)
        print "Parsers available:"
        i = 1
        for (name, a, b, c) in TESTMAP:
            print '\t%d.  %s' % (i, name)
            i = i + 1
        print
        inp = raw_input('Parser number (or x to exit) > ')
        if inp == 'x':
            print 'bye'
            return
        else:
            num = int(inp)
            (name, loadFunc, parseFunc, statFunc) = TESTMAP[num-1]

    # force pause to 1 or 0 by asking
    if pause == 'unknown': 
        inp = raw_input("Shall we do memory tests?  i.e. you look at Task Manager? y/n > ")
        assert inp in 'yn', 'enter "y" or "n".  Please run again!'
        pause = (inp == 'y')



    print 'testing %s' % testName
    #load the parser
    t0 = time.clock()
    parser = loadFunc()
    loadTime = time.clock() - t0
    if pause:
        baseMem = float(raw_input("Pre-parsing: please input python process memory in kb > "))
    t1 = time.clock()
    parsedOutput = parseFunc(parser, sampleText)
    t2 = time.clock()
    parseTime = t2 - t1
    
    if pause:
        totalMem = float(raw_input('Post-parsing: please input python process memory in kb > '))
        usedMem = totalMem - baseMem
        memFactor = usedMem * 1024.0 / len(sampleText)
    t3 = time.clock()
    n, a = statFunc(parsedOutput)
    t4 = time.clock()
    traverseTime = t4 - t3
    print 'counted %d tags, %d attributes' % (n, a)
    if pause:
        print '%s: init %0.4f, parse %0.4f, traverse %0.4f, mem used %dkb, mem factor %0.2f' % (
            name, loadTime, parseTime, traverseTime, usedMem, memFactor)
    else:
        print '%s: init %0.4f, parse %0.4f, traverse %0.4f' % (
            name, loadTime, parseTime, traverseTime)
    print

    
if __name__=='__main__':
    import sys
    args = sys.argv[:]
    if '-nodtd' in args:
        dtd=0
        args.remove('-nodtd')
    else:
        dtd=1
        
    if '-pause' in args:
        pause = 1
        args.remove('-pause')
    elif '-nopause' in args:
        pause = 0
        args.remove('-nopause')
    else:
        pause = 'unknown'  # it will ask
    if len(args) > 1:
        testName = args[1]
    else:
        testName = None
    interact(testName, dtd, pause=pause)
    
        
