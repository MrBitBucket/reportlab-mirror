# uses pyexpat to build the tree. Yuk, globals,
# but want a quick speed comparison with pyRXP

import xml.parsers.expat

class ExpatTreeParser:
    """Crude and incomplete tree-builder based on expat.

    Need to add a few more handlers before it accurately
    deals with all relevant elements; but close enough
    for benchmark comparisons.  It (like expat) returns
    Unicode strings; we don't want to penalize it for
    this so leave them as Unicode."""
    def __init__(self):
        # fake top node makes it easy to initialize
        self.curNode = ('_FAKE_ROOT_',{},[],None)
        self.nodestack = [self.curNode]
        
    def handleStartElement(self, name, attrs):
        #print 'start element %s' % name
        newNode = (name, attrs, [], None)
        self.nodestack.append(newNode)
        self.curNode[2].append(newNode)
        self.curNode = newNode

    def handleCharData(self, data):
        #print 'char data %s' % data
        self.curNode[2].append(data)

    def handleEndElement(self, name):
        #print 'end element %s' % name
        self.nodestack.pop()
        self.curNode = self.nodestack[-1]

    def parse(self, data):
        p = xml.parsers.expat.ParserCreate()
        p.StartElementHandler = self.handleStartElement
        p.EndElementHandler = self.handleEndElement
        p.CharacterDataHandler = self.handleCharData
        p.Parse(data)
        # will be the first child of our fake top node
        return self.curNode[2][0]

def expattree(data):
    return ExpatTreeParser().parse(data)    

    
