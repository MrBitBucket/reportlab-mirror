"Some XML helper classes."
import os, string, sys
from types import StringType, ListType, TupleType
import pyRXP
assert pyRXP.version>='0.5', 'get the latest pyRXP!'
    

IGNOREWHITESPACE = 1

def ignoreWhitespace(list):
    newlist = []
    for elem in list:
        if type(elem) is StringType:
            short = string.strip(elem)
            if short == '':
                pass
            else:
                newlist.append(short)
        else:
            newlist.append(elem)
    return newlist


class TagWrapper:
    """Lazy utility for navigating XML.

    The following Python code works:

    tag.attribute      # returns given attribute
    tag.child          # returns first child with matching tag name
    for child in tag:  # iterates over them
    tag[3]             # returns fourth child
    len(tag)           # no of children
    """

    def __init__(self, node, returnEmptyTagContentAsString=1):
        tagName, attrs, children, spare = node
        self.tagName = tagName

        # this option affects tags with no content like <Surname></Surname>.
        # Can either return a None object, which is a pain in a prep file
        # as you have to  put if expressions around everything, or
        # an empty string so prep files can just do {{xml.wherever.Surname}}.
        self.returnEmptyTagContentAsString = returnEmptyTagContentAsString

        if attrs is None:
            self._attrs = {}
        else:
            self._attrs = attrs  # share the dictionary

        if children is None:
            self._children = []
        elif IGNOREWHITESPACE:
            self._children = ignoreWhitespace(children)
        else:
            self._children = children

    def __repr__(self):
        return 'TagWrapper<%s>' % self.tagName

    def __str__(self):
        if len(self):
            return str(self[0])
        else:
            if self.returnEmptyTagContentAsString:
                return ''
            else:
                return None

    def __len__(self):
        return len(self._children)

    def _value(self,name,default):
        try:
            return getattr(self,name)[0]
        except (AttributeError, IndexError):
            return default

    def __getattr__(self, attr):
        "Try various priorities"
        if self._attrs.has_key(attr):
            return self._attrs[attr]
        else:
            #first child tag whose name matches?
            for child in self._children:
                if type(child) is StringType:
                    pass
                else:
                    tagName, attrs, children, spare = child
                    if tagName == attr:
                        t = TagWrapper(child)
                        t.returnEmptyTagContentAsString = self.returnEmptyTagContentAsString
                        return t
            # not found, barf
            msg = '"%s" not found in attributes of tag <%s> or its children' % (attr, self.tagName)
            raise AttributeError, msg

    def keys(self):
        "return list of valid keys"
        result = self._attrs.keys()
        for child in self._children:
            if type(child) is StringType: pass
            else: result.append(child[0])
        return result

    def has_key(self,k):
        return k in self.keys()

    def __getitem__(self, idx):
        try:
            child = self._children[idx]
        except IndexError:
            raise IndexError, '%s no index %s' % (self.__repr__(), `idx`)
        if type(child) is StringType: return child
        else: return TagWrapper(child)

    def _namedChildren(self,name):
        R = []
        for c in self:
            if type(c) is StringType:
                if name is None: R.append(c)
            elif name == c.tagName: R.append(c)
        return R

def xml2doctree(xml):
    pyRXP_parse = pyRXP.Parser(
        ErrorOnValidityErrors=1,
        NoNoDTDWarning=1,
        ExpandCharacterEntities=0,
        ExpandGeneralEntities=0)
    return pyRXP_parse.parse(xml)


if __name__=='__main__':
    import os
    xml = open('rml_manual.xml','r').read()
    parsed = xml2doctree(xml)
