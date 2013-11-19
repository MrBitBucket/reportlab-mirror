__doc__="""helper for importing pdf structures into a ReportLab generated document
"""
from reportlab.pdfbase.pdfdoc import format
class PDFPattern:
    __PDFObject__ = True
    __RefOnly__ = 1
    def __init__(self, pattern_sequence, **keywordargs):
        """
        Description of a kind of PDF object using a pattern.

        Pattern sequence should contain strings or singletons of form [string].
        Strings are literal strings to be used in the object.
        Singletons are names of keyword arguments to include.
        Keyword arguments can be non-instances which are substituted directly in string conversion,
        or they can be object instances in which case they should be pdfdoc.* style
        objects with a x.format(doc) method.
        Keyword arguments may be set on initialization or subsequently using __setitem__, before format.
        "constant object" instances can also be inserted in the patterns.
        """
        self.pattern = pattern_sequence
        self.arguments = keywordargs
        for x in pattern_sequence:
            if not isinstance(x,str) and not hasattr(x,'format'):
                if len(x)!=1:
                    raise ValueError("sequence elts must be strings or singletons containing strings: "+ascii(x))
                if not isinstance(x[0],str):
                    raise ValueError("Singletons must contain strings or instances only: "+ascii(x[0]))
    def __setitem__(self, item, value):
        self.arguments[item] = value
    def __getitem__(self, item):
        return self.arguments[item]
    def format(self, document):
        L = []
        arguments = self.arguments
        for x in self.pattern:
            if isinstance(x,str):
                L.append(x)
            elif hasattr(x,'format'):
                L.append(x.format(document) )
            else:
                name = x[0]
                value = arguments.get(name, None)
                if value is None:
                    raise ValueError("%s value not defined" % ascii(name))
                if isinstance(value,str):
                    L.append(value)
                else:
                    L.append(value.formatformat(document))
        return "".join(L)


