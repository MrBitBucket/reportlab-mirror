#Copyright ReportLab Europe Ltd. 2000-2012
#see license.txt for license details
#history http://www.reportlab.co.uk/cgi-bin/viewcvs.cgi/public/reportlab/trunk/reportlab/platypus/paraparser.py
__version__=''' $Id$ '''
__doc__='''The parser used to process markup within paragraphs'''
import string
import re
import sys
import os
import copy
import base64
from pprint import pprint as pp

try:
    import pickle as pickle
except:
    import pickle
import unicodedata
import reportlab.lib.sequencer

from reportlab.lib.abag import ABag
from reportlab.lib.utils import ImageReader, isPy3, annotateException, encode_label, asUnicode, UniChr
from reportlab.lib.colors import toColor, white, black, red, Color
from reportlab.lib.fonts import tt2ps, ps2tt
from reportlab.lib.enums import TA_LEFT, TA_RIGHT, TA_CENTER, TA_JUSTIFY
from reportlab.lib.units import inch,mm,cm,pica
if isPy3:
    from html.parser import HTMLParser
    from html.entities import name2codepoint
else:
    from HTMLParser import HTMLParser
    from htmlentitydefs import name2codepoint

_re_para = re.compile(r'^\s*<\s*para(?:\s+|>|/>)')

sizeDelta = 2       # amount to reduce font size by for super and sub script
subFraction = 0.5   # fraction of font size that a sub script should be lowered
superFraction = 0.5 # fraction of font size that a super script should be raised

DEFAULT_INDEX_NAME='_indexAdd'


def _convnum(s, unit=1, allowRelative=True):
    if s[0] in ('+','-') and allowRelative:
        try:
            return ('relative',int(s)*unit)
        except ValueError:
            return ('relative',float(s)*unit)
    else:
        try:
            return int(s)*unit
        except ValueError:
            return float(s)*unit

def _num(s, unit=1, allowRelative=True):
    """Convert a string like '10cm' to an int or float (in points).
       The default unit is point, but optionally you can use other
       default units like mm.
    """
    if s.endswith('cm'):
        unit=cm
        s = s[:-2]
    if s.endswith('in'):
        unit=inch
        s = s[:-2]
    if s.endswith('pt'):
        unit=1
        s = s[:-2]
    if s.endswith('i'):
        unit=inch
        s = s[:-1]
    if s.endswith('mm'):
        unit=mm
        s = s[:-2]
    if s.endswith('pica'):
        unit=pica
        s = s[:-4]
    return _convnum(s,unit,allowRelative)

def _numpct(s,unit=1,allowRelative=False):
    if s.endswith('%'):
        return _PCT(_convnum(s[:-1],allowRelative=allowRelative))
    else:
        return _num(s,unit,allowRelative)

class _PCT:
    def __init__(self,v):
        self._value = v*0.01

    def normalizedValue(self,normalizer):
        normalizer = normalizer or getattr(self,'_normalizer')
        return normalizer*self._value

def _valignpc(s):
    s = s.lower()
    if s in ('baseline','sub','super','top','text-top','middle','bottom','text-bottom'):
        return s
    if s.endswith('%'):
        n = _convnum(s[:-1])
        if isinstance(n,tuple):
            n = n[1]
        return _PCT(n)
    n = _num(s)
    if isinstance(n,tuple):
        n = n[1]
    return n

def _autoLeading(x):
    x = x.lower()
    if x in ('','min','max','off'):
        return x
    raise ValueError('Invalid autoLeading=%r' % x )

def _align(s):
    s = s.lower()
    if s=='left': return TA_LEFT
    elif s=='right': return TA_RIGHT
    elif s=='justify': return TA_JUSTIFY
    elif s in ('centre','center'): return TA_CENTER
    else: raise ValueError

_paraAttrMap = {'font': ('fontName', None),
                'face': ('fontName', None),
                'fontsize': ('fontSize', _num),
                'size': ('fontSize', _num),
                'leading': ('leading', _num),
                'autoleading': ('autoLeading', _autoLeading),
                'lindent': ('leftIndent', _num),
                'rindent': ('rightIndent', _num),
                'findent': ('firstLineIndent', _num),
                'align': ('alignment', _align),
                'spaceb': ('spaceBefore', _num),
                'spacea': ('spaceAfter', _num),
                'bfont': ('bulletFontName', None),
                'bfontsize': ('bulletFontSize',_num),
                'boffsety': ('bulletOffsetY',_num),
                'bindent': ('bulletIndent',_num),
                'bcolor': ('bulletColor',toColor),
                'color':('textColor',toColor),
                'backcolor':('backColor',toColor),
                'bgcolor':('backColor',toColor),
                'bg':('backColor',toColor),
                'fg': ('textColor',toColor),
                }

_bulletAttrMap = {
                'font': ('bulletFontName', None),
                'face': ('bulletFontName', None),
                'size': ('bulletFontSize',_num),
                'fontsize': ('bulletFontSize',_num),
                'offsety': ('bulletOffsetY',_num),
                'indent': ('bulletIndent',_num),
                'color': ('bulletColor',toColor),
                'fg': ('bulletColor',toColor),
                }

#things which are valid font attributes
_fontAttrMap = {'size': ('fontSize', _num),
                'face': ('fontName', None),
                'name': ('fontName', None),
                'fg':   ('textColor', toColor),
                'color':('textColor', toColor),
                'backcolor':('backColor',toColor),
                'bgcolor':('backColor',toColor),
                }
#things which are valid span attributes
_spanAttrMap = {'size': ('fontSize', _num),
                'face': ('fontName', None),
                'name': ('fontName', None),
                'fg':   ('textColor', toColor),
                'color':('textColor', toColor),
                'backcolor':('backColor',toColor),
                'bgcolor':('backColor',toColor),
                'style': ('style',None),
                }
#things which are valid font attributes
_linkAttrMap = {'size': ('fontSize', _num),
                'face': ('fontName', None),
                'name': ('fontName', None),
                'fg':   ('textColor', toColor),
                'color':('textColor', toColor),
                'backcolor':('backColor',toColor),
                'bgcolor':('backColor',toColor),
                'dest': ('link', None),
                'destination': ('link', None),
                'target': ('link', None),
                'href': ('link', None),
                }
_anchorAttrMap = {'fontSize': ('fontSize', _num),
                'fontName': ('fontName', None),
                'name': ('name', None),
                'fg':   ('textColor', toColor),
                'color':('textColor', toColor),
                'backcolor':('backColor',toColor),
                'bgcolor':('backColor',toColor),
                'href': ('href', None),
                }
_imgAttrMap = {
                'src': ('src', None),
                'width': ('width',_numpct),
                'height':('height',_numpct),
                'valign':('valign',_valignpc),
                }
_indexAttrMap = {
                'name': ('name',None),
                'item': ('item',None),
                'offset': ('offset',None),
                'format': ('format',None),
                }

def _addAttributeNames(m):
    K = list(m.keys())
    for k in K:
        n = m[k][0]
        if n not in m: m[n] = m[k]
        n = n.lower()
        if n not in m: m[n] = m[k]

_addAttributeNames(_paraAttrMap)
_addAttributeNames(_fontAttrMap)
_addAttributeNames(_spanAttrMap)
_addAttributeNames(_bulletAttrMap)
_addAttributeNames(_anchorAttrMap)
_addAttributeNames(_linkAttrMap)

def _applyAttributes(obj, attr):
    for k, v in attr.items():
        if isinstance(v,(list,tuple)) and v[0]=='relative':
            if hasattr(obj, k):
                v = v[1]+getattr(obj,k)
            else:
                v = v[1]
        setattr(obj,k,v)

#Named character entities intended to be supported from the special font
#with additions suggested by Christoph Zwerschke who also suggested the
#numeric entity names that follow.
greeks = {
    'Aacute': b'\xc3\x81',
    'aacute': b'\xc3\xa1',
    'Acirc': b'\xc3\x82',
    'acirc': b'\xc3\xa2',
    'acute': b'\xc2\xb4',
    'AElig': b'\xc3\x86',
    'aelig': b'\xc3\xa6',
    'Agrave': b'\xc3\x80',
    'agrave': b'\xc3\xa0',
    'alefsym': b'\xe2\x84\xb5',
    'Alpha': b'\xce\x91',
    'alpha': b'\xce\xb1',
    'and': b'\xe2\x88\xa7',
    'ang': b'\xe2\x88\xa0',
    'Aring': b'\xc3\x85',
    'aring': b'\xc3\xa5',
    'asymp': b'\xe2\x89\x88',
    'Atilde': b'\xc3\x83',
    'atilde': b'\xc3\xa3',
    'Auml': b'\xc3\x84',
    'auml': b'\xc3\xa4',
    'bdquo': b'\xe2\x80\x9e',
    'Beta': b'\xce\x92',
    'beta': b'\xce\xb2',
    'brvbar': b'\xc2\xa6',
    'bull': b'\xe2\x80\xa2',
    'cap': b'\xe2\x88\xa9',
    'Ccedil': b'\xc3\x87',
    'ccedil': b'\xc3\xa7',
    'cedil': b'\xc2\xb8',
    'cent': b'\xc2\xa2',
    'Chi': b'\xce\xa7',
    'chi': b'\xcf\x87',
    'circ': b'\xcb\x86',
    'clubs': b'\xe2\x99\xa3',
    'cong': b'\xe2\x89\x85',
    'copy': b'\xc2\xa9',
    'crarr': b'\xe2\x86\xb5',
    'cup': b'\xe2\x88\xaa',
    'curren': b'\xc2\xa4',
    'dagger': b'\xe2\x80\xa0',
    'Dagger': b'\xe2\x80\xa1',
    'darr': b'\xe2\x86\x93',
    'dArr': b'\xe2\x87\x93',
    'deg': b'\xc2\xb0',
    'delta': b'\xce\xb4',
    'Delta': b'\xe2\x88\x86',
    'diams': b'\xe2\x99\xa6',
    'divide': b'\xc3\xb7',
    'Eacute': b'\xc3\x89',
    'eacute': b'\xc3\xa9',
    'Ecirc': b'\xc3\x8a',
    'ecirc': b'\xc3\xaa',
    'Egrave': b'\xc3\x88',
    'egrave': b'\xc3\xa8',
    'empty': b'\xe2\x88\x85',
    'emsp': b'\xe2\x80\x83',
    'ensp': b'\xe2\x80\x82',
    'Epsilon': b'\xce\x95',
    'epsilon': b'\xce\xb5',
    'epsiv': b'\xce\xb5',
    'equiv': b'\xe2\x89\xa1',
    'Eta': b'\xce\x97',
    'eta': b'\xce\xb7',
    'ETH': b'\xc3\x90',
    'eth': b'\xc3\xb0',
    'Euml': b'\xc3\x8b',
    'euml': b'\xc3\xab',
    'euro': b'\xe2\x82\xac',
    'exist': b'\xe2\x88\x83',
    'fnof': b'\xc6\x92',
    'forall': b'\xe2\x88\x80',
    'frac12': b'\xc2\xbd',
    'frac14': b'\xc2\xbc',
    'frac34': b'\xc2\xbe',
    'frasl': b'\xe2\x81\x84',
    'Gamma': b'\xce\x93',
    'gamma': b'\xce\xb3',
    'ge': b'\xe2\x89\xa5',
    'harr': b'\xe2\x86\x94',
    'hArr': b'\xe2\x87\x94',
    'hearts': b'\xe2\x99\xa5',
    'hellip': b'\xe2\x80\xa6',
    'Iacute': b'\xc3\x8d',
    'iacute': b'\xc3\xad',
    'Icirc': b'\xc3\x8e',
    'icirc': b'\xc3\xae',
    'iexcl': b'\xc2\xa1',
    'Igrave': b'\xc3\x8c',
    'igrave': b'\xc3\xac',
    'image': b'\xe2\x84\x91',
    'infin': b'\xe2\x88\x9e',
    'int': b'\xe2\x88\xab',
    'Iota': b'\xce\x99',
    'iota': b'\xce\xb9',
    'iquest': b'\xc2\xbf',
    'isin': b'\xe2\x88\x88',
    'Iuml': b'\xc3\x8f',
    'iuml': b'\xc3\xaf',
    'Kappa': b'\xce\x9a',
    'kappa': b'\xce\xba',
    'Lambda': b'\xce\x9b',
    'lambda': b'\xce\xbb',
    'lang': b'\xe2\x8c\xa9',
    'laquo': b'\xc2\xab',
    'larr': b'\xe2\x86\x90',
    'lArr': b'\xe2\x87\x90',
    'lceil': b'\xef\xa3\xae',
    'ldquo': b'\xe2\x80\x9c',
    'le': b'\xe2\x89\xa4',
    'lfloor': b'\xef\xa3\xb0',
    'lowast': b'\xe2\x88\x97',
    'loz': b'\xe2\x97\x8a',
    'lrm': b'\xe2\x80\x8e',
    'lsaquo': b'\xe2\x80\xb9',
    'lsquo': b'\xe2\x80\x98',
    'macr': b'\xc2\xaf',
    'mdash': b'\xe2\x80\x94',
    'micro': b'\xc2\xb5',
    'middot': b'\xc2\xb7',
    'minus': b'\xe2\x88\x92',
    'mu': b'\xc2\xb5',
    'Mu': b'\xce\x9c',
    'nabla': b'\xe2\x88\x87',
    'nbsp': b'\xc2\xa0',
    'ndash': b'\xe2\x80\x93',
    'ne': b'\xe2\x89\xa0',
    'ni': b'\xe2\x88\x8b',
    'notin': b'\xe2\x88\x89',
    'not': b'\xc2\xac',
    'nsub': b'\xe2\x8a\x84',
    'Ntilde': b'\xc3\x91',
    'ntilde': b'\xc3\xb1',
    'Nu': b'\xce\x9d',
    'nu': b'\xce\xbd',
    'Oacute': b'\xc3\x93',
    'oacute': b'\xc3\xb3',
    'Ocirc': b'\xc3\x94',
    'ocirc': b'\xc3\xb4',
    'OElig': b'\xc5\x92',
    'oelig': b'\xc5\x93',
    'Ograve': b'\xc3\x92',
    'ograve': b'\xc3\xb2',
    'oline': b'\xef\xa3\xa5',
    'omega': b'\xcf\x89',
    'Omega': b'\xe2\x84\xa6',
    'Omicron': b'\xce\x9f',
    'omicron': b'\xce\xbf',
    'oplus': b'\xe2\x8a\x95',
    'ordf': b'\xc2\xaa',
    'ordm': b'\xc2\xba',
    'or': b'\xe2\x88\xa8',
    'Oslash': b'\xc3\x98',
    'oslash': b'\xc3\xb8',
    'Otilde': b'\xc3\x95',
    'otilde': b'\xc3\xb5',
    'otimes': b'\xe2\x8a\x97',
    'Ouml': b'\xc3\x96',
    'ouml': b'\xc3\xb6',
    'para': b'\xc2\xb6',
    'part': b'\xe2\x88\x82',
    'permil': b'\xe2\x80\xb0',
    'perp': b'\xe2\x8a\xa5',
    'phis': b'\xcf\x86',
    'Phi': b'\xce\xa6',
    'phi': b'\xcf\x95',
    'piv': b'\xcf\x96',
    'Pi': b'\xce\xa0',
    'pi': b'\xcf\x80',
    'plusmn': b'\xc2\xb1',
    'pound': b'\xc2\xa3',
    'prime': b'\xe2\x80\xb2',
    'Prime': b'\xe2\x80\xb3',
    'prod': b'\xe2\x88\x8f',
    'prop': b'\xe2\x88\x9d',
    'Psi': b'\xce\xa8',
    'psi': b'\xcf\x88',
    'radic': b'\xe2\x88\x9a',
    'rang': b'\xe2\x8c\xaa',
    'raquo': b'\xc2\xbb',
    'rarr': b'\xe2\x86\x92',
    'rArr': b'\xe2\x87\x92',
    'rceil': b'\xef\xa3\xb9',
    'rdquo': b'\xe2\x80\x9d',
    'real': b'\xe2\x84\x9c',
    'reg': b'\xc2\xae',
    'rfloor': b'\xef\xa3\xbb',
    'Rho': b'\xce\xa1',
    'rho': b'\xcf\x81',
    'rlm': b'\xe2\x80\x8f',
    'rsaquo': b'\xe2\x80\xba',
    'rsquo': b'\xe2\x80\x99',
    'sbquo': b'\xe2\x80\x9a',
    'Scaron': b'\xc5\xa0',
    'scaron': b'\xc5\xa1',
    'sdot': b'\xe2\x8b\x85',
    'sect': b'\xc2\xa7',
    'shy': b'\xc2\xad',
    'sigmaf': b'\xcf\x82',
    'sigmav': b'\xcf\x82',
    'Sigma': b'\xce\xa3',
    'sigma': b'\xcf\x83',
    'sim': b'\xe2\x88\xbc',
    'spades': b'\xe2\x99\xa0',
    'sube': b'\xe2\x8a\x86',
    'sub': b'\xe2\x8a\x82',
    'sum': b'\xe2\x88\x91',
    'sup1': b'\xc2\xb9',
    'sup2': b'\xc2\xb2',
    'sup3': b'\xc2\xb3',
    'supe': b'\xe2\x8a\x87',
    'sup': b'\xe2\x8a\x83',
    'szlig': b'\xc3\x9f',
    'Tau': b'\xce\xa4',
    'tau': b'\xcf\x84',
    'there4': b'\xe2\x88\xb4',
    'thetasym': b'\xcf\x91',
    'thetav': b'\xcf\x91',
    'Theta': b'\xce\x98',
    'theta': b'\xce\xb8',
    'thinsp': b'\xe2\x80\x89',
    'THORN': b'\xc3\x9e',
    'thorn': b'\xc3\xbe',
    'tilde': b'\xcb\x9c',
    'times': b'\xc3\x97',
    'trade': b'\xef\xa3\xaa',
    'Uacute': b'\xc3\x9a',
    'uacute': b'\xc3\xba',
    'uarr': b'\xe2\x86\x91',
    'uArr': b'\xe2\x87\x91',
    'Ucirc': b'\xc3\x9b',
    'ucirc': b'\xc3\xbb',
    'Ugrave': b'\xc3\x99',
    'ugrave': b'\xc3\xb9',
    'uml': b'\xc2\xa8',
    'upsih': b'\xcf\x92',
    'Upsilon': b'\xce\xa5',
    'upsilon': b'\xcf\x85',
    'Uuml': b'\xc3\x9c',
    'uuml': b'\xc3\xbc',
    'weierp': b'\xe2\x84\x98',
    'Xi': b'\xce\x9e',
    'xi': b'\xce\xbe',
    'Yacute': b'\xc3\x9d',
    'yacute': b'\xc3\xbd',
    'yen': b'\xc2\xa5',
    'yuml': b'\xc3\xbf',
    'Yuml': b'\xc5\xb8',
    'Zeta': b'\xce\x96',
    'zeta': b'\xce\xb6',
    'zwj': b'\xe2\x80\x8d',
    'zwnj': b'\xe2\x80\x8c',
    }

#------------------------------------------------------------------------
class ParaFrag(ABag):
    """class ParaFrag contains the intermediate representation of string
    segments as they are being parsed by the XMLParser.
    fontname, fontSize, rise, textColor, cbDefn
    """


_greek2Utf8=None
def _greekConvert(data):
    global _greek2Utf8
    if not _greek2Utf8:
        from reportlab.pdfbase.rl_codecs import RL_Codecs
        import codecs
        #our decoding map
        dm = codecs.make_identity_dict(range(32,256))
        for k in range(0,32):
            dm[k] = None
        dm.update(RL_Codecs._RL_Codecs__rl_codecs_data['symbol'][0])
        _greek2Utf8 = {}
        for k,v in dm.items():
            if not v:
                u = '\0'
            else:
                if isPy3:
                    u = chr(v)
                else:
                    u = unichr(v).encode('utf8')
            _greek2Utf8[chr(k)] = u
    return ''.join(map(_greek2Utf8.__getitem__,data))


def ugeCB(name):
    '''undefined general entity handler'''
    try:
        return greeks[name]
    except:
        return ('&#38;'+name+';').encode('utf8')

try:
    import pyRXPU
    _TRMAP = dict(
            caseInsensitive='CaseInsensitive',
            )
    def makeParser(**kwds):
        d = dict(ErrorOnUnquotedAttributeValues=0,
                Validate=0,srcName='Paragraph text',
                ugeCB = ugeCB,
                )
        for k in kwds:
            if k in _TRMAP:
                d[_TRMAP[k]] = kwds[k]
        return pyRXPU.Parser(**d)
except ImportError:
    raise ImportError("pyRXPU not importable Alternate parser not yet implemented")

#------------------------------------------------------------------
# !!! NOTE !!! THIS TEXT IS NOW REPLICATED IN PARAGRAPH.PY !!!
# The ParaFormatter will be able to format the following
# tags:
#       < /b > - bold
#       < /i > - italics
#       < u > < /u > - underline
#       < strike > < /strike > - strike through
#       < super > < /super > - superscript
#       < sup > < /sup > - superscript
#       < sub > < /sub > - subscript
#       <font name=fontfamily/fontname color=colorname size=float>
#        <span name=fontfamily/fontname color=colorname backcolor=colorname size=float style=stylename>
#       < bullet > </bullet> - bullet text (at head of para only)
#       <onDraw name=callable label="a label"/>
#       <index [name="callablecanvasattribute"] label="a label"/>
#       <link>link text</link>
#           attributes of links 
#               size/fontSize=num
#               name/face/fontName=name
#               fg/textColor/color=color
#               backcolor/backColor/bgcolor=color
#               dest/destination/target/href/link=target
#       <a>anchor text</a>
#           attributes of anchors 
#               fontSize=num
#               fontName=name
#               fg/textColor/color=color
#               backcolor/backColor/bgcolor=color
#               href=href
#       <a name="anchorpoint"/>
#       <unichar name="unicode character name"/>
#       <unichar value="unicode code point"/>
#       <img src="path" width="1in" height="1in" valign="bottom"/>
#               width="w%" --> fontSize*w/100   idea from Roberto Alsina
#               height="h%" --> linewidth*h/100 <ralsina@netmanagers.com.ar>
#       <greek> - </greek>
#
#       The whole may be surrounded by <para> </para> tags
#
# It will also be able to handle any MathML specified Greek characters.
#------------------------------------------------------------------
class ParaParser(HTMLParser):

    #----------------------------------------------------------
    # First we will define all of the xml tag handler functions.
    #
    # start_<tag>(attributes)
    # end_<tag>()
    #
    # While parsing the xml ParaFormatter will call these
    # functions to handle the string formatting tags.
    # At the start of each tag the corresponding field will
    # be set to 1 and at the end tag the corresponding field will
    # be set to 0.  Then when handle_data is called the options
    # for that data will be aparent by the current settings.
    #----------------------------------------------------------

    def __getattr__( self, attrName ):
        """This way we can handle <TAG> the same way as <tag> (ignoring case)."""
        if attrName!=attrName.lower() and attrName!="caseSensitive" and not self.caseSensitive and \
            (attrName.startswith("start_") or attrName.startswith("end_")):
                return getattr(self,attrName.lower())
        raise AttributeError(attrName)

    #### bold
    def start_b( self, attributes ):
        self._push(bold=1)

    def end_b( self ):
        self._pop(bold=1)

    def start_strong( self, attributes ):
        self._push(bold=1)

    def end_strong( self ):
        self._pop(bold=1)

    #### italics
    def start_i( self, attributes ):
        self._push(italic=1)

    def end_i( self ):
        self._pop(italic=1)

    def start_em( self, attributes ):
        self._push(italic=1)

    def end_em( self ):
        self._pop(italic=1)

    #### underline
    def start_u( self, attributes ):
        self._push(underline=1)

    def end_u( self ):
        self._pop(underline=1)

    #### strike
    def start_strike( self, attributes ):
        self._push(strike=1)

    def end_strike( self ):
        self._pop(strike=1)

    #### link
    def start_link(self, attributes):
        self._push(**self.getAttributes(attributes,_linkAttrMap))

    def end_link(self):
        frag = self._stack[-1]
        del self._stack[-1]
        assert frag.link!=None

    #### anchor
    def start_a(self, attributes):
        A = self.getAttributes(attributes,_anchorAttrMap)
        name = A.get('name',None)
        if name is not None:
            name = name.strip()
            if not name:
                self._syntax_error('<a name="..."/> anchor variant requires non-blank name')
            if len(A)>1:
                self._syntax_error('<a name="..."/> anchor variant only allows name attribute')
                A = dict(name=A['name'])
            A['_selfClosingTag'] = 'anchor'
        else:
            href = A.get('href','').strip()
            A['link'] = href    #convert to our link form
            A.pop('href',None)
        self._push(**A)

    def end_a(self):
        frag = self._stack[-1]
        sct = getattr(frag,'_selfClosingTag','')
        if sct:
            assert sct=='anchor' and frag.name,'Parser failure in <a/>'
            defn = frag.cbDefn = ABag()
            defn.label = defn.kind = 'anchor'
            defn.name = frag.name
            del frag.name, frag._selfClosingTag
            self.handle_data('')
            self._pop()
        else:
            del self._stack[-1]
            assert frag.link!=None

    def start_img(self,attributes):
        A = self.getAttributes(attributes,_imgAttrMap)
        if not A.get('src'):
            self._syntax_error('<img> needs src attribute')
        A['_selfClosingTag'] = 'img'
        self._push(**A)

    def end_img(self):
        frag = self._stack[-1]
        assert getattr(frag,'_selfClosingTag',''),'Parser failure in <img/>'
        defn = frag.cbDefn = ABag()
        defn.kind = 'img'
        defn.src = getattr(frag,'src',None)
        defn.image = ImageReader(defn.src)
        size = defn.image.getSize()
        defn.width = getattr(frag,'width',size[0])
        defn.height = getattr(frag,'height',size[1])
        defn.valign = getattr(frag,'valign','bottom')
        del frag._selfClosingTag
        self.handle_data('')
        self._pop()

    #### super script
    def start_super( self, attributes ):
        self._push(super=1)

    def end_super( self ):
        self._pop(super=1)

    start_sup = start_super
    end_sup = end_super

    #### sub script
    def start_sub( self, attributes ):
        self._push(sub=1)

    def end_sub( self ):
        self._pop(sub=1)

    #### greek script
    #### add symbol encoding
    def handle_charref(self, name):
        try:
            if name[0]=='x':
                n = int(name[1:],16)
            else:
                n = int(name)
        except ValueError:
            self.unknown_charref(name)
            return
        self.handle_data(UniChr(n))   #.encode('utf8'))

    def syntax_error(self,lineno,message):
        self._syntax_error(message)

    def _syntax_error(self,message):
        if message[:10]=="attribute " and message[-17:]==" value not quoted": return
        self.errors.append(message)

    def start_greek(self, attr):
        self._push(greek=1)

    def end_greek(self):
        self._pop(greek=1)

    def start_unichar(self, attr):
        if 'name' in attr:
            if 'code' in attr:
                self._syntax_error('<unichar/> invalid with both name and code attributes')
            try:
                v = unicodedata.lookup(attr['name'])
            except KeyError:
                self._syntax_error('<unichar/> invalid name attribute\n"%s"' % ascii(name))
                v = '\0'
        elif 'code' in attr:
            try:
                v = int(eval(attr['code']))
                v = chr(v) if isPy3 else unichr(v)
            except:
                self._syntax_error('<unichar/> invalid code attribute %s' % ascii(attr['code']))
                v = '\0'
        else:
            v = None
            if attr:
                self._syntax_error('<unichar/> invalid attribute %s' % list(attr.keys())[0])

        if v is not None:
            self.handle_data(v)
        self._push(_selfClosingTag='unichar')

    def end_unichar(self):
        self._pop()

    def start_font(self,attr):
        self._push(**self.getAttributes(attr,_fontAttrMap))

    def end_font(self):
        self._pop()

    def start_span(self,attr):
        A = self.getAttributes(attr,_spanAttrMap)
        if 'style' in A:
            style = self.findSpanStyle(A.pop('style'))
            D = {}
            for k in 'fontName fontSize textColor backColor'.split():
                v = getattr(style,k,self)
                if v is self: continue
                D[k] = v
            D.update(A)
            A = D
        self._push(**A)

    end_span = end_font

    def start_br(self, attr):
        self._push(_selfClosingTag='br',lineBreak=True,text='')
        
    def end_br(self):
        #print('\nend_br called, %d frags in list' % len(self.fragList))
        frag = self._stack[-1]
        assert frag._selfClosingTag=='br' and frag.lineBreak,'Parser failure in <br/>'
        del frag._selfClosingTag
        self._handled_text = False
        self.handle_data('')
        self._pop()
        


    def _initial_frag(self,attr,attrMap,bullet=0):
        style = self._style
        if attr!={}:
            style = copy.deepcopy(style)
            _applyAttributes(style,self.getAttributes(attr,attrMap))
            self._style = style

        # initialize semantic values
        frag = ParaFrag()
        frag.sub = 0
        frag.super = 0
        frag.rise = 0
        frag.underline = 0
        frag.strike = 0
        frag.greek = 0
        frag.link = None
        if bullet:
            frag.fontName, frag.bold, frag.italic = ps2tt(style.bulletFontName)
            frag.fontSize = style.bulletFontSize
            frag.textColor = hasattr(style,'bulletColor') and style.bulletColor or style.textColor
        else:
            frag.fontName, frag.bold, frag.italic = ps2tt(style.fontName)
            frag.fontSize = style.fontSize
            frag.textColor = style.textColor
        return frag

    def start_para(self,attr):
        self._stack = [self._initial_frag(attr,_paraAttrMap)]

    def end_para(self):
        self._pop()

    def start_bullet(self,attr):
        if hasattr(self,'bFragList'):
            self._syntax_error('only one <bullet> tag allowed')
        self.bFragList = []
        frag = self._initial_frag(attr,_bulletAttrMap,1)
        frag.isBullet = 1
        self._stack.append(frag)

    def end_bullet(self):
        self._pop()

    #---------------------------------------------------------------
    def start_seqdefault(self, attr):
        try:
            default = attr['id']
        except KeyError:
            default = None
        self._seq.setDefaultCounter(default)

    def end_seqdefault(self):
        pass

    def start_seqreset(self, attr):
        try:
            id = attr['id']
        except KeyError:
            id = None
        try:
            base = int(attr['base'])
        except:
            base=0
        self._seq.reset(id, base)

    def end_seqreset(self):
        pass

    def start_seqchain(self, attr):
        try:
            order = attr['order']
        except KeyError:
            order = ''
        order = order.split()
        seq = self._seq
        for p,c in zip(order[:-1],order[1:]):
            seq.chain(p, c)
    end_seqchain = end_seqreset

    def start_seqformat(self, attr):
        try:
            id = attr['id']
        except KeyError:
            id = None
        try:
            value = attr['value']
        except KeyError:
            value = '1'
        self._seq.setFormat(id,value)
    end_seqformat = end_seqreset

    # AR hacking in aliases to allow the proper casing for RML.
    # the above ones should be deprecated over time. 2001-03-22
    start_seqDefault = start_seqdefault
    end_seqDefault = end_seqdefault
    start_seqReset = start_seqreset
    end_seqReset = end_seqreset
    start_seqChain = start_seqchain
    end_seqChain = end_seqchain
    start_seqFormat = start_seqformat
    end_seqFormat = end_seqformat

    def start_seq(self, attr):
        #if it has a template, use that; otherwise try for id;
        #otherwise take default sequence
        if 'template' in attr:
            templ = attr['template']
            self.handle_data(templ % self._seq)
            return
        elif 'id' in attr:
            id = attr['id']
        else:
            id = None
        increment = attr.get('inc', None)
        if not increment:
            output = self._seq.nextf(id)
        else:
            #accepts "no" for do not increment, or an integer.
            #thus, 0 and 1 increment by the right amounts.
            if increment.lower() == 'no':
                output = self._seq.thisf(id)
            else:
                incr = int(increment)
                output = self._seq.thisf(id)
                self._seq.reset(id, self._seq._this() + incr)
        self.handle_data(output)

    def end_seq(self):
        pass

    def start_onDraw(self,attr):
        defn = ABag()
        if 'name' in attr: defn.name = attr['name']
        else: self._syntax_error('<onDraw> needs at least a name attribute')

        if 'label' in attr: defn.label = attr['label']
        defn.kind='onDraw'
        self._push(cbDefn=defn)
        self.handle_data('')
        self._pop()
    end_onDraw=end_seq

    def start_index(self,attr):
        attr=self.getAttributes(attr,_indexAttrMap)
        defn = ABag()
        if 'item' in attr:
            label = attr['item']
        else:
            self._syntax_error('<index> needs at least an item attribute')
        if 'name' in attr:
            name = attr['name']
        else:
            name = DEFAULT_INDEX_NAME
        format = attr.get('format',None)
        if format is not None and format not in ('123','I','i','ABC','abc'):
            raise ValueError('index tag format is %r not valid 123 I i ABC or abc' % offset)
        offset = attr.get('offset',None)
        if offset is not None:
            try:
                offset = int(offset)
            except:
                raise ValueError('index tag offset is %r not an int' % offset)
        defn.label = encode_label((label,format,offset))
        defn.name = name
        defn.kind='index'
        self._push(cbDefn=defn)
        self.handle_data('')
        self._pop()
    end_index=end_seq

    def start_unknown(self,attr):
        pass
    end_unknown=end_seq

    #---------------------------------------------------------------
    def _push(self,**attr):
        frag = copy.copy(self._stack[-1])
        _applyAttributes(frag,attr)
        self._stack.append(frag)

    def _pop(self,**kw):
        frag = self._stack[-1]
        del self._stack[-1]
        for k, v in kw.items():
            assert getattr(frag,k)==v
        return frag

    def getAttributes(self,attr,attrMap):
        A = {}
        for k, v in attr.items():
            if not self.caseSensitive:
                k = k.lower()
            if k in list(attrMap.keys()):
                j = attrMap[k]
                func = j[1]
                try:
                    A[j[0]] = v if func is None else func(v)
                except:
                    self._syntax_error('%s: invalid value %s'%(k,v))
            else:
                self._syntax_error('invalid attribute name %s'%k)
        return A

    #----------------------------------------------------------------

    def __init__(self,verbose=0, caseSensitive=0, ignoreUnknownTags=1):
        HTMLParser.__init__(self)
        self.verbose = verbose
        self.caseSensitive = caseSensitive
        self.ignoreUnknownTags = ignoreUnknownTags

    def _iReset(self):
        self._handled_text = False
        self.fragList = []
        if hasattr(self, 'bFragList'): delattr(self,'bFragList')

    def _reset(self, style):
        '''reset the parser'''

        # initialize list of string segments to empty
        self.errors = []
        self._style = style
        self._iReset()

    #----------------------------------------------------------------
    def handle_data(self,data):
        "Creates an intermediate representation of string segments."

        #The old parser would only 'see' a string after all entities had
        #been processed.  Thus, 'Hello &trade; World' would emerge as one
        #fragment.    HTMLParser processes these separately.  We want to ensure
        #that successive calls like this are concatenated, to prevent too many
        #fragments being created.

        #print("\n called handle_data('%s')" % data)
        #print('handle_data("%s")' % data)
        if self._handled_text:
            #print('handle_more_data("%s")' % data)
            self.handle_more_data(data)
            return

        frag = copy.copy(self._stack[-1])
        if hasattr(frag,'cbDefn'):
            kind = frag.cbDefn.kind
            if data: self._syntax_error('Only empty <%s> tag allowed' % kind)
        elif hasattr(frag,'_selfClosingTag'):
            if data!='': self._syntax_error('No content allowed in %s tag' % frag._selfClosingTag)
            return
        else:
            # if sub and super are both on they will cancel each other out
            if frag.sub == 1 and frag.super == 1:
                frag.sub = 0
                frag.super = 0

            if frag.sub:
                frag.rise = -frag.fontSize*subFraction
                frag.fontSize = max(frag.fontSize-sizeDelta,3)
            elif frag.super:
                frag.rise = frag.fontSize*superFraction
                frag.fontSize = max(frag.fontSize-sizeDelta,3)

            if frag.greek:
                frag.fontName = 'symbol'
                data = _greekConvert(data)

        # bold, italic, and underline
        frag.fontName = tt2ps(frag.fontName,frag.bold,frag.italic)

        #save our data
        frag.text = data

        if hasattr(frag,'isBullet'):
            delattr(frag,'isBullet')
            self.bFragList.append(frag)
        else:
            self.fragList.append(frag)

        #Set this if we just processed sme text, but not if it was a br tag.
        #Ugly, but seems necessary to get pyRXP and HTMLParser working the
        #same way.
        if not hasattr(frag, 'lineBreak'):
            self._handled_text = True

    def handle_cdata(self,data):
        self.handle_data(data)

    def _setup_for_parse(self,style):
        self._seq = reportlab.lib.sequencer.getSequencer()
        self._reset(style)  # reinitialise the parser



    def old_parse(self, text, style):
        """Given a formatted string will return a list of
        ParaFrag objects with their calculated widths.
        If errors occur None will be returned and the
        self.errors holds a list of the error messages.
        """
        self._setup_for_parse(style)
        text = asUnicode(text)
        if not(len(text)>=6 and text[0]=='<' and _re_para.match(text)):
            text = u"<para>"+text+u"</para>"
        try:
            tt = makeParser(caseInsensitive=not self.caseSensitive)(text)

            #from pprint import pprint
            #pprint(tt)
        except:
            annotateException('paragraph text %s caused exception' % ascii(text))
        self._tt_start(tt)
        return self._complete_parse()

    def _complete_parse(self):
        "Reset after parsing, to be ready for next paragraph"
        del self._seq
        style = self._style
        del self._style
        if len(self.errors)==0:
            fragList = self.fragList
            bFragList = hasattr(self,'bFragList') and self.bFragList or None
            self._iReset()
        else:
            fragList = bFragList = None

        return style, fragList, bFragList

    def _tt_handle(self,tt):
        "Iterate through a pre-parsed tuple tree (e.g. from pyRXP)"
        #import pprint
        #pprint.pprint(tt)
        #find the corresponding start_tagname and end_tagname methods.
        #These must be defined.
        tag = tt[0]
        try:
            start = getattr(self,'start_'+tag)
            end = getattr(self,'end_'+tag)
        except AttributeError:
            if not self.ignoreUnknownTags:
                raise ValueError('Invalid tag "%s"' % tag)
            start = self.start_unknown
            end = self.end_unknown

        #call the start_tagname method
        start(tt[1] or {})
        self._handled_text = False
        #if tree node has any children, they will either be further nodes,
        #or text.  Accordingly, call either this function, or handle_data.
        C = tt[2]
        if C:
            M = self._tt_handlers
            for c in C:
                M[isinstance(c,(list,tuple))](c)

        #call the end_tagname method
        end()
        self._handled_text = False

    def _tt_start(self,tt):
        self._tt_handlers = self.handle_data,self._tt_handle
        self._tt_handle(tt)

    def tt_parse(self,tt,style):
        '''parse from tupletree form'''
        self._setup_for_parse(style)
        self._tt_start(tt)
        return self._complete_parse()

    def findSpanStyle(self,style):
        raise ValueError('findSpanStyle not implemented in this parser')



    #New methods to supprt HTML parser
    def new_parse(self, text, style):
        "attempt replacement for parse"
        self._setup_for_parse(style)
        text = asUnicode(text)
        if not(len(text)>=6 and text[0]=='<' and _re_para.match(text)):
            text = u"<para>"+text+u"</para>"
        self.feed(text)
        return self._complete_parse()

    def handle_starttag(self, tag, attrs):
        "Called by HTMLParser when a tag starts"

        #tuple tree parser used to expect a dict.  HTML parser
        #gives list of two-element tuples
        if isinstance(attrs, list):
            d = {}
            for (k,  v) in attrs:
                d[k] = v
            attrs = d

        if tag not in ['br']:
            self._handled_text = False
        try:
            start = getattr(self,'start_'+tag)
        except AttributeError:
            if not self.ignoreUnknownTags:
                raise ValueError('Invalid tag "%s"' % tag)
            start = self.start_unknown
        #call it
        start(attrs or {})
        
    def handle_endtag(self, tag):
        "Called by HTMLParser when a tag ends"
        if tag not in ['br']:
            self._handled_text = False
        #find the existing end_tagname method
        try:
            end = getattr(self,'end_'+tag)
        except AttributeError:
            if not self.ignoreUnknownTags:
                raise ValueError('Invalid tag "%s"' % tag)
            end = self.end_unknown
        #call it
        end()

    

    def handle_entityref(self, name):
        "Handles a named entity.  "
        #print('handle_entityref called for "%s"' % name)
        #The old parser saw these automatically resolved, so
        #just tack it onto the current fragment.
        resolved = UniChr(name2codepoint[name])
        if self._handled_text:
            self.fragList[-1].text += resolved
        else:
            self.handle_data(resolved)
        
    def handle_more_data(self, data):
        """We call this when we get successive text chunks

        This is to ensure that successive strings with no
        formatting changes are concatenated.
        """
        frag = self._stack[-1]
        if hasattr(frag,'isBullet'):
            last = self.bFragList[-1]
        else:
            last = self.fragList[-1]
        last.text += data

    def parse(self, text, style):
        if os.environ.get('HTMLPARSE', '0') == '1':
            return self.new_parse(text, style)
        else:
            return self.old_parse(text, style)



if __name__=='__main__':
    from reportlab.platypus import cleanBlockQuotedText
    from reportlab.lib.styles import _baseFontName
    _parser=ParaParser()
    def check_text(text,p=_parser):
        print('##########')
        text = cleanBlockQuotedText(text)
        l,rv,bv = p.parse(text,style)
        if rv is None:
            for l in _parser.errors:
                print(l)
        else:
            print('ParaStyle', l.fontName,l.fontSize,l.textColor)
            for l in rv:
                sys.stdout.write(l.fontName,l.fontSize,l.textColor,l.bold, l.rise, '|%s|'%l.text[:25])
                if hasattr(l,'cbDefn'):
                    print('cbDefn',getattr(l.cbDefn,'name',''),getattr(l.cbDefn,'label',''),l.cbDefn.kind)
                else: print()

    style=ParaFrag()
    style.fontName=_baseFontName
    style.fontSize = 12
    style.textColor = black
    style.bulletFontName = black
    style.bulletFontName=_baseFontName
    style.bulletFontSize=12

    text='''
    <b><i><greek>a</greek>D</i></b>&beta;<unichr value="0x394"/>
    <font name="helvetica" size="15" color=green>
    Tell me, O muse, of that ingenious hero who travelled far and wide
    after</font> he had sacked the famous town of Troy. Many cities did he visit,
    and many were the nations with whose manners and customs he was acquainted;
    moreover he suffered much by sea while trying to save his own life
    and bring his men safely home; but do what he might he could not save
    his men, for they perished through their own sheer folly in eating
    the cattle of the Sun-god Hyperion; so the god prevented them from
    ever reaching home. Tell me, too, about all these things, O daughter
    of Jove, from whatsoever source you<super>1</super> may know them.
    '''
    check_text(text)
    check_text('<para> </para>')
    check_text('<para font="%s" size=24 leading=28.8 spaceAfter=72>ReportLab -- Reporting for the Internet Age</para>'%_baseFontName)
    check_text('''
    <font color=red>&tau;</font>Tell me, O muse, of that ingenious hero who travelled far and wide
    after he had sacked the famous town of Troy. Many cities did he visit,
    and many were the nations with whose manners and customs he was acquainted;
    moreover he suffered much by sea while trying to save his own life
    and bring his men safely home; but do what he might he could not save
    his men, for they perished through their own sheer folly in eating
    the cattle of the Sun-god Hyperion; so the god prevented them from
    ever reaching home. Tell me, too, about all these things, O daughter
    of Jove, from whatsoever source you may know them.''')
    check_text('''
    Telemachus took this speech as of good omen and rose at once, for
    he was bursting with what he had to say. He stood in the middle of
    the assembly and the good herald Pisenor brought him his staff. Then,
    turning to Aegyptius, "Sir," said he, "it is I, as you will shortly
    learn, who have convened you, for it is I who am the most aggrieved.
    I have not got wind of any host approaching about which I would warn
    you, nor is there any matter of public moment on which I would speak.
    My grieveance is purely personal, and turns on two great misfortunes
    which have fallen upon my house. The first of these is the loss of
    my excellent father, who was chief among all you here present, and
    was like a father to every one of you; the second is much more serious,
    and ere long will be the utter ruin of my estate. The sons of all
    the chief men among you are pestering my mother to marry them against
    her will. They are afraid to go to her father Icarius, asking him
    to choose the one he likes best, and to provide marriage gifts for
    his daughter, but day by day they keep hanging about my father's house,
    sacrificing our oxen, sheep, and fat goats for their banquets, and
    never giving so much as a thought to the quantity of wine they drink.
    No estate can stand such recklessness; we have now no Ulysses to ward
    off harm from our doors, and I cannot hold my own against them. I
    shall never all my days be as good a man as he was, still I would
    indeed defend myself if I had power to do so, for I cannot stand such
    treatment any longer; my house is being disgraced and ruined. Have
    respect, therefore, to your own consciences and to public opinion.
    Fear, too, the wrath of heaven, lest the gods should be displeased
    and turn upon you. I pray you by Jove and Themis, who is the beginning
    and the end of councils, [do not] hold back, my friends, and leave
    me singlehanded- unless it be that my brave father Ulysses did some
    wrong to the Achaeans which you would now avenge on me, by aiding
    and abetting these suitors. Moreover, if I am to be eaten out of house
    and home at all, I had rather you did the eating yourselves, for I
    could then take action against you to some purpose, and serve you
    with notices from house to house till I got paid in full, whereas
    now I have no remedy."''')

    check_text('''
But as the sun was rising from the fair sea into the firmament of
heaven to shed light on mortals and immortals, they reached Pylos
the city of Neleus. Now the people of Pylos were gathered on the sea
shore to offer sacrifice of black bulls to Neptune lord of the Earthquake.
There were nine guilds with five hundred men in each, and there were
nine bulls to each guild. As they were eating the inward meats and
burning the thigh bones [on the embers] in the name of Neptune, Telemachus
and his crew arrived, furled their sails, brought their ship to anchor,
and went ashore. ''')
    check_text('''
So the neighbours and kinsmen of Menelaus were feasting and making
merry in his house. There was a bard also to sing to them and play
his lyre, while two tumblers went about performing in the midst of
them when the man struck up with his tune.]''')
    check_text('''
"When we had passed the [Wandering] rocks, with Scylla and terrible
Charybdis, we reached the noble island of the sun-god, where were
the goodly cattle and sheep belonging to the sun Hyperion. While still
at sea in my ship I could bear the cattle lowing as they came home
to the yards, and the sheep bleating. Then I remembered what the blind
Theban prophet Teiresias had told me, and how carefully Aeaean Circe
had warned me to shun the island of the blessed sun-god. So being
much troubled I said to the men, 'My men, I know you are hard pressed,
but listen while I <strike>tell you the prophecy that</strike> Teiresias made me, and
how carefully Aeaean Circe warned me to shun the island of the blessed
sun-god, for it was here, she said, that our worst danger would lie.
Head the ship, therefore, away from the island.''')
    check_text('''A&lt;B&gt;C&amp;D&quot;E&apos;F''')
    check_text('''A&lt; B&gt; C&amp; D&quot; E&apos; F''')
    check_text('''<![CDATA[<>&'"]]>''')
    check_text('''<bullet face=courier size=14 color=green>+</bullet>
There was a bard also to sing to them and play
his lyre, while two tumblers went about performing in the midst of
them when the man struck up with his tune.]''')
    check_text('''<onDraw name="myFunc" label="aaa   bbb">A paragraph''')
    check_text('''<para><onDraw name="myFunc" label="aaa   bbb">B paragraph</para>''')
    # HVB, 30.05.2003: Test for new features
    _parser.caseSensitive=0
    check_text('''Here comes <FONT FACE="Helvetica" SIZE="14pt">Helvetica 14</FONT> with <STRONG>strong</STRONG> <EM>emphasis</EM>.''')
    check_text('''Here comes <font face="Helvetica" size="14pt">Helvetica 14</font> with <Strong>strong</Strong> <em>emphasis</em>.''')
    check_text('''Here comes <font face="Courier" size="3cm">Courier 3cm</font> and normal again.''')
    check_text('''Before the break <br/>the middle line <br/> and the last line.''')
    check_text('''This should be an inline image <img src='../../../docs/images/testimg.gif'/>!''')
    check_text('''aaa&nbsp;bbbb <u>underline&#32;</u> cccc''')
