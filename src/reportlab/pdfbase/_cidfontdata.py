#Copyright ReportLab Europe Ltd. 2000-2012
#see license.txt for license details
#history http://www.reportlab.co.uk/cgi-bin/viewcvs.cgi/public/reportlab/trunk/reportlab/pdfbase/_cidfontdata.py
#$Header $
__version__=''' $Id$ '''
__doc__="""
This defines additional static data to support CID fonts.

Canned data is provided for the Japanese fonts supported by Adobe. We
can add Chinese, Korean and Vietnamese in due course. The data was
extracted by creating very simple postscript documents and running
through Distiller, then examining the resulting PDFs.

Each font is described as a big nested dictionary.  This lets us keep
code out of the module altogether and avoid circular dependencies.

The encoding and font data are grouped by some standard 'language
prefixes'::

    chs = Chinese Simplified (mainland)
    cht = Chinese Traditional (Taiwan)
    kor = Korean
    jpn = Japanese
"""


languages = ['jpn', 'kor', 'cht', 'chs']

#breaking down the lists let us check if something is present
#for a specific language
typeFaces_chs = ['STSong-Light'] # to do
typeFaces_cht = ['MSung-Light']  #, 'MHei-Medium'] # to do
typeFaces_jpn = ['HeiseiMin-W3', 'HeiseiKakuGo-W5']
typeFaces_kor = ['HYSMyeongJo-Medium','HYGothic-Medium']

allowedTypeFaces = typeFaces_chs + typeFaces_cht + typeFaces_jpn + typeFaces_kor




encodings_jpn = [
    # official encoding names, comments taken verbatim from PDF Spec
    '83pv-RKSJ-H',      #Macintosh, JIS X 0208 character set with KanjiTalk6
                        #extensions, Shift-JIS encoding, Script Manager code 1
    '90ms-RKSJ-H',      #Microsoft Code Page 932 (lfCharSet 0x80), JIS X 0208
                        #character set with NEC and IBM extensions
    '90ms-RKSJ-V',      #Vertical version of 90ms-RKSJ-H
    '90msp-RKSJ-H',     #Same as 90ms-RKSJ-H, but replaces half-width Latin
                        #characters with proportional forms
    '90msp-RKSJ-V',     #Vertical version of 90msp-RKSJ-H
    '90pv-RKSJ-H',      #Macintosh, JIS X 0208 character set with KanjiTalk7
                        #extensions, Shift-JIS encoding, Script Manager code 1
    'Add-RKSJ-H',       #JIS X 0208 character set with Fujitsu FMR extensions,
                        #Shift-JIS encoding
    'Add-RKSJ-V',       #Vertical version of Add-RKSJ-H
    'EUC-H',            #JIS X 0208 character set, EUC-JP encoding
    'EUC-V',            #Vertical version of EUC-H
    'Ext-RKSJ-H',       #JIS C 6226 (JIS78) character set with NEC extensions,
                        #Shift-JIS encoding
    'Ext-RKSJ-V',       #Vertical version of Ext-RKSJ-H
    'H',                #JIS X 0208 character set, ISO-2022-JP encoding,
    'V',                #Vertical version of H
    'UniJIS-UCS2-H',    #Unicode (UCS-2) encoding for the Adobe-Japan1 character
                        #collection
    'UniJIS-UCS2-V',    #Vertical version of UniJIS-UCS2-H
    'UniJIS-UCS2-HW-H', #Same as UniJIS-UCS2-H, but replaces proportional Latin
                        #characters with half-width forms
    'UniJIS-UCS2-HW-V'  #Vertical version of UniJIS-UCS2-HW-H
    ]
encodings_kor = [
    'KSC-EUC-H',        # KS X 1001:1992 character set, EUC-KR encoding
    'KSC-EUC-V',        # Vertical version of KSC-EUC-H
    'KSCms-UHC-H',      # Microsoft Code Page 949 (lfCharSet 0x81), KS X 1001:1992
                        #character set plus 8,822 additional hangul, Unified Hangul
                        #Code (UHC) encoding
    'KSCms-UHC-V',      #Vertical version of KSCms-UHC-H
    'KSCms-UHC-HW-H',   #Same as KSCms-UHC-H, but replaces proportional Latin
                        # characters with halfwidth forms
    'KSCms-UHC-HW-V',   #Vertical version of KSCms-UHC-HW-H
    'KSCpc-EUC-H',      #Macintosh, KS X 1001:1992 character set with MacOS-KH
                        #extensions, Script Manager Code 3
    'UniKS-UCS2-H',     #Unicode (UCS-2) encoding for the Adobe-Korea1 character collection
    'UniKS-UCS2-V'      #Vertical version of UniKS-UCS2-H

    ]

encodings_chs = [

    'GB-EUC-H',         # Microsoft Code Page 936 (lfCharSet 0x86), GB 2312-80
                        # character set, EUC-CN encoding
    'GB-EUC-V',         # Vertical version of GB-EUC-H
    'GBpc-EUC-H',       # Macintosh, GB 2312-80 character set, EUC-CN encoding,
                        # Script Manager code 2
    'GBpc-EUC-V',       # Vertical version of GBpc-EUC-H
    'GBK-EUC-H',        # Microsoft Code Page 936 (lfCharSet 0x86), GBK character
                        # set, GBK encoding
    'GBK-EUC-V',        # Vertical version of GBK-EUC-V
    'UniGB-UCS2-H',     # Unicode (UCS-2) encoding for the Adobe-GB1
                        # character collection
    'UniGB-UCS2-V'     # Vertical version of UniGB-UCS2-H.
    ]

encodings_cht = [
    'B5pc-H',           # Macintosh, Big Five character set, Big Five encoding,
                        # Script Manager code 2
    'B5pc-V',           # Vertical version of B5pc-H
    'ETen-B5-H',        # Microsoft Code Page 950 (lfCharSet 0x88), Big Five
                        # character set with ETen extensions
    'ETen-B5-V',        # Vertical version of ETen-B5-H
    'ETenms-B5-H',      # Microsoft Code Page 950 (lfCharSet 0x88), Big Five
                        # character set with ETen extensions; this uses proportional
                        # forms for half-width Latin characters.
    'ETenms-B5-V',      # Vertical version of ETenms-B5-H
    'CNS-EUC-H',        # CNS 11643-1992 character set, EUC-TW encoding
    'CNS-EUC-V',        # Vertical version of CNS-EUC-H
    'UniCNS-UCS2-H',    # Unicode (UCS-2) encoding for the Adobe-CNS1
                        # character collection
    'UniCNS-UCS2-V'    # Vertical version of UniCNS-UCS2-H.
    ]

# the Identity encodings simply dump out all character
# in the font in the order they were defined.
allowedEncodings = (['Identity-H', 'Identity-V'] +
                    encodings_chs +
                    encodings_cht +
                    encodings_jpn +
                    encodings_kor
                    )

defaultUnicodeEncodings = {
    #we ddefine a default Unicode encoding for each face name;
    #this should be the most commonly used horizontal unicode encoding;
    #also define a 3-letter language code.
    'HeiseiMin-W3': ('jpn','UniJIS-UCS2-H'),
    'HeiseiKakuGo-W5': ('jpn','UniJIS-UCS2-H'),
    'STSong-Light': ('chs', 'UniGB-UCS2-H'),
    'MSung-Light': ('cht', 'UniGB-UCS2-H'),
    #'MHei-Medium': ('cht', 'UniGB-UCS2-H'),
    'HYSMyeongJo-Medium': ('kor', 'UniKS-UCS2-H'),
    'HYGothic-Medium': ('kor','UniKS-UCS2-H'),
    }

typeFaces_chs = ['STSong-Light'] # to do
typeFaces_cht = ['MSung-Light', 'MHei-Medium'] # to do
typeFaces_jpn = ['HeiseiMin-W3', 'HeiseiKakuGo-W5']
typeFaces_kor = ['HYSMyeongJo-Medium','HYGothic-Medium']


#declare separately those used for unicode
unicode_encodings = [enc for enc in allowedEncodings if 'UCS2' in enc]


CIDFontInfo = {}
#statically describe the fonts in Adobe's Japanese Language Packs
CIDFontInfo['HeiseiMin-W3'] = {
            'Type':'/Font',
            'Subtype':'/Type0',
            'Name': '/%(internalName)s' , #<-- the internal name
            'BaseFont': '/HeiseiMin-W3',
            'Encoding': '/%(encodings)s',

            #there could be several descendant fonts if it is an old-style
            #type 0 compound font.  For CID fonts there is just one.
            'DescendantFonts': [{
                'Type':'/Font',
                'Subtype':'/CIDFontType0',
                'BaseFont':'/HeiseiMin-W3',
                'FontDescriptor': {
                    'Type': '/FontDescriptor',
                    'Ascent': 723,
                    'CapHeight': 709,
                    'Descent': -241,
                    'Flags': 6,
                    'FontBBox': (-123, -257, 1001, 910),
                    'FontName': '/HeiseiMin-W3',
                    'ItalicAngle': 0,
                    'StemV': 69,
                    'XHeight': 450#,
#                    'Style': {'Panose': '<010502020400000000000000>'}
                    },
                'CIDSystemInfo': {
                    'Registry': '(Adobe)',
                    'Ordering': '(Japan1)',
                    'Supplement': 2
                    },
                #default width is 1000 em units
                'DW': 1000,
                #widths of any which are not the default.
                'W': [1, [250, 333, 408, 500],
                      5, [500, 833, 778, 180, 333],
                      10, [333, 500, 564, 250, 333, 250, 278, 500],
                      18, 26, 500, 27, 28, 278, 29, 31, 564,
                      32, [444, 921, 722, 667],
                      36, [667, 722, 611, 556, 722],
                      41, [722, 333, 389, 722, 611, 889, 722],
                      48, [722, 556, 722, 667, 556, 611, 722],
                      55, [722, 944, 722],
                      58, [722, 611, 333, 500, 333, 469, 500, 333,
                           444, 500, 444, 500, 444, 333, 500],
                      73, [500, 278],
                      75, [278, 500, 278, 778, 500], 80, 82, 500,
                      83, [333, 389, 278, 500],
                      87, [500, 722, 500],
                      90, [500, 444, 480, 200, 480, 333],
                      97, [278], 99, [200], 101, [333, 500], 103, [500, 167],
                      107, [500], 109, [500, 333], 111, [333, 556],
                      113, [556, 500], 117, [250], 119, [350, 333, 444],
                      123, [500], 126, [444, 333], 128, 137, 333,
                      138, [1000, 889, 276, 611, 722, 889, 310, 667, 278],
                      147, [278, 500, 722, 500, 564, 760, 564, 760],
                      157, 158, 300, 159, [500, 300, 750], 162, 163, 750,
                      164, 169, 722, 170, [667, 611], 172, 174, 611, 175,
                      178, 333, 179, 185, 722, 187, 191, 722, 192,
                      [556, 444], 194, 203, 444, 204, 207, 278, 208,
                      214, 500, 216, 222, 500,
                      223, [556, 722, 611, 500, 389, 980, 444],
                      231, [500], 323, [500], 325, [500],
                      327, 389, 500]
##                'W': (
##                    # starting at character ID 1, next n  characters have the widths given.
##                    1,  (277,305,500,668,668,906,727,305,445,445,508,668,305,379,305,539),
##                    # all Characters from ID 17 to 26 are 668 em units wide
##                    17, 26, 668,
##                    27, (305, 305, 668, 668, 668, 566, 871, 727, 637, 652, 699, 574, 555,
##                         676, 687, 242, 492, 664, 582, 789, 707, 734, 582, 734, 605, 605,
##                         641, 668, 727, 945, 609, 609, 574, 445, 668, 445, 668, 668, 590,
##                         555, 609, 547, 602, 574, 391, 609, 582, 234, 277, 539, 234, 895,
##                         582, 605, 602, 602, 387, 508, 441, 582, 562, 781, 531, 570, 555,
##                         449, 246, 449, 668),
##                    # these must be half width katakana and the like.
##                    231, 632, 500
##                    )
                }]# end list of descendant fonts
            } #end HeiseiMin-W3

CIDFontInfo['HeiseiKakuGo-W5'] =  {'Type':'/Font',
            'Subtype':'/Type0',
            'Name': '/%(internalName)s', #<-- the internal name
            'BaseFont': '/HeiseiKakuGo-W5',
            'Encoding': '/%(encodings)s',
            'DescendantFonts': [{'Type':'/Font',
                'Subtype':'/CIDFontType0',
                'BaseFont':'/HeiseiKakuGo-W5',
                'FontDescriptor': {
                    'Type': '/FontDescriptor',
                    'Ascent': 752,
                    'CapHeight': 737,
                    'Descent': -221,
                    'Flags': 4,
                    'FontBBox': [-92, -250, 1010, 922],
                    'FontName': '/HeiseKakuGo-W5',
                    'ItalicAngle': 0,
                    'StemH': 0,
                    'StemV': 114,
                    'XHeight': 553,
##                    'Style': {'Panose': '<0801020b0600000000000000>'}
                    },
                'CIDSystemInfo': {
                    'Registry': '(Adobe)',
                    'Ordering': '(Japan1)',
                    'Supplement': 2
                    },
                'DW': 1000,
                'W': (
                    1, (277,305,500,668,668,906,727,305,445,445,508,668,305,379,305,539),
                    17, 26, 668,
                    27, (305, 305, 668, 668, 668, 566, 871, 727, 637, 652, 699, 574, 555,
                                         676, 687, 242, 492, 664, 582, 789, 707, 734, 582, 734, 605, 605,
                                         641, 668, 727, 945, 609, 609, 574, 445, 668, 445, 668, 668, 590,
                                         555, 609, 547, 602, 574, 391, 609, 582, 234, 277, 539, 234, 895,
                                         582, 605, 602, 602, 387, 508, 441, 582, 562, 781, 531, 570, 555,
                                         449, 246, 449, 668),
                    231, 632, 500
                    )
                }] # end descendant fonts
            }

CIDFontInfo['HYGothic-Medium'] =  {'Type':'/Font',
            'Subtype':'/Type0',
            'Name': '/%(internalName)s', #<-- the internal name
            'BaseFont': '/' + 'HYGothic-Medium',
            'Encoding': '/%(encodings)s',
            'DescendantFonts': [{'Type':'/Font',
                'Subtype':'/CIDFontType0',
                'BaseFont':'/'+'HYGothic-Medium',
                'FontDescriptor': {
                    'Type': '/FontDescriptor',
                    'Ascent': 752,
                    'AvgWidth': -271,
                    'CapHeight': 737,
                    'Descent': -142,
                    'Flags': 6,
                    'FontBBox': [-6, -145, 1003, 880],
                    'FontName': '/'+'HYSMyeongJo-Medium',
                    'ItalicAngle': 0,
                    'Leading': 148,
                    'MaxWidth': 1000,
                    'MissingWidth': 500,
                    'StemH': 0,
                    'StemV': 58,
                    'XHeight': 553
                    },
                'CIDSystemInfo': {
                    'Registry': '(Adobe)',
                    'Ordering': '(Korea1)',
                    'Supplement': 1
                    },
                'DW': 1000,
                'W': (1, 94, 500)
                }] # end descendant fonts
            }

CIDFontInfo['HYSMyeongJo-Medium'] =  {'Type':'/Font',
            'Subtype':'/Type0',
            'Name': '/%(internalName)s', #<-- the internal name
            'BaseFont': '/' + 'HYSMyeongJo-Medium',
            'Encoding': '/%(encodings)s',
            'DescendantFonts': [{'Type':'/Font',
                'Subtype':'/CIDFontType2',
                'BaseFont':'/'+'HYSMyeongJo-Medium',
                'FontDescriptor': {
                    'Type': '/FontDescriptor',
                    'Ascent': 752,
                    'AvgWidth': 500,
                    'CapHeight': 737,
                    'Descent': -271,
                    'Flags': 6,
                    'FontBBox': [0, -148, 1001, 880],
                    'FontName': '/'+'HYSMyeongJo-Medium',
                    'ItalicAngle': 0,
                    'Leading': 148,
                    'MaxWidth': 1000,
                    'MissingWidth': 500,
                    'StemH': 91,
                    'StemV': 58,
                    'XHeight': 553
                    },
                'CIDSystemInfo': {
                    'Registry': '(Adobe)',
                    'Ordering': '(Korea1)',
                    'Supplement': 1
                    },
                'DW': 1000,
                'W': [1, [333, 416],
                      3, [416, 833, 625, 916, 833, 250, 500],
                      10, 11, 500,
                      12, [833, 291, 833, 291, 375, 625],
                      18, 26, 625, 27, 28, 333, 29, 30, 833,
                      31, [916, 500, 1000, 791, 708],
                      36, [708, 750, 708, 666, 750, 791, 375,
                           500, 791, 666, 916, 791, 750, 666,
                           750, 708, 666, 791],
                      54, [791, 750, 1000, 708],
                      58, [708, 666, 500, 375, 500],
                      63, 64, 500,
                      65, [333, 541, 583, 541, 583],
                      70, [583, 375, 583],
                      73, [583, 291, 333, 583, 291, 875, 583],
                      80, 82, 583,
                      83, [458, 541, 375, 583],
                      87, [583, 833, 625],
                      90, [625, 500, 583], 93, 94, 583,
                      95, [750]
                      ]
                }] # end descendant fonts
            }

#WARNING - not checked, just copied Korean to get some output

CIDFontInfo['STSong-Light'] =  {'Type':'/Font',
            'Subtype':'/Type0',
            'Name': '/%(internalName)s', #<-- the internal name
            'BaseFont': '/' + 'STSong-Light',
            'Encoding': '/%(encodings)s',
            'DescendantFonts': [{'Type':'/Font',
                'Subtype':'/CIDFontType0',
                'BaseFont':'/'+'STSong-Light',
                'FontDescriptor': {
                    'Type': '/FontDescriptor',
                    'Ascent': 752,
                    'CapHeight': 737,
                    'Descent': -271,
                    'Flags': 6,
                    'FontBBox': [-25, -254, 1000, 880],
                    'FontName': '/'+'STSongStd-Light',
                    'ItalicAngle': 0,
                    'Leading': 148,
                    'MaxWidth': 1000,
                    'MissingWidth': 500,
                    'StemH': 91,
                    'StemV': 58,
                    'XHeight': 553
                    },
                'CIDSystemInfo': {
                    'Registry': '(Adobe)',
                    'Ordering': '(GB1)',
                    'Supplement': 0
                    },
                'DW': 1000,
                'W': [1, [207, 270, 342, 467, 462, 797, 710, 239, 374],
                      10, [374, 423, 605, 238, 375, 238, 334, 462],
                      18, 26, 462, 27, 28, 238, 29, 31, 605,
                      32, [344, 748, 684, 560, 695, 739, 563, 511, 729,
                           793, 318, 312, 666, 526, 896, 758, 772, 544,
                           772, 628, 465, 607, 753, 711, 972, 647, 620,
                           607, 374, 333, 374, 606, 500, 239, 417, 503,
                           427, 529, 415, 264, 444, 518, 241, 230, 495,
                           228, 793, 527, 524],
                      81, [524, 504, 338, 336, 277, 517, 450, 652, 466,
                           452, 407, 370, 258, 370, 605]
                      ]
                }] # end descendant fonts
            }
CIDFontInfo['MSung-Light'] =  {'Type':'/Font',
            'Subtype':'/Type0',
            'Name': '/%(internalName)s', #<-- the internal name
            'BaseFont': '/' + 'MSung-Light',
            'Encoding': '/%(encodings)s',
            'DescendantFonts': [{'Type':'/Font',
                'Subtype':'/CIDFontType0',
                'BaseFont':'/'+'MSung-Light',
                'FontDescriptor': {
                    'Type': '/FontDescriptor',
                    'Ascent': 752,
                    'CapHeight': 737,
                    'Descent': -271,
                    'Flags': 6,
                    'FontBBox': [-160, -249, 1015, 888],
                    'FontName': '/'+'MSung-Light',
                    'ItalicAngle': 0,
                    'Leading': 148,
                    'MaxWidth': 1000,
                    'MissingWidth': 500,
                    'StemH': 45,
                    'StemV': 58,
                    'XHeight': 553
                    },
                'CIDSystemInfo': {
                    'Registry': '(Adobe)',
                    'Ordering': '(CNS1)',
                    'Supplement': 1
                    },
                'DW': 1000,
                'W': [1, 2, 250, 3, [408, 668, 490, 875, 698, 250, 240],
                      10, [240, 417, 667, 250, 313, 250, 520, 500],
                      18, 26, 500, 27, 28, 250, 29, 31, 667,
                      32, [396, 921, 677, 615, 719, 760, 625, 552, 771,
                           802, 354],
                      43, [354, 781, 604, 927, 750, 823, 563, 823, 729,
                           542, 698, 771, 729, 948, 771, 677, 635, 344,
                           520, 344, 469, 500, 250, 469, 521, 427, 521,
                           438, 271, 469, 531, 250],
                      75, [250, 458, 240, 802, 531, 500, 521],
                      82, [521, 365, 333, 292, 521, 458, 677, 479, 458,
                           427, 480, 496, 480, 667]]

                }] # end descendant fonts
            }


#this data was derived from the above width information and removes all dependency on CMAP files as long as we only use the unicode fonts.
widthsByUnichar = {}
widthsByUnichar["MSung-Light"] = {' ': 250, '$': 490, '(': 240, ',': 250, '0': 500, '4': 500, '8': 500, '<': 667, '@': 921, 'D': 760, 'H': 802, 'L': 604, 'P': 563, 'T': 698, 'X': 771, '\\': 520, '`': 250, 'd': 521, 'h': 531, 'l': 240, 'p': 521, 't': 292, 'x': 479, '|': 496, '#': 668, "'": 250, '+': 667, '/': 520, '3': 500, '7': 500, ';': 250, '?': 396, 'C': 719, 'G': 771, 'K': 781, 'O': 823, 'S': 542, 'W': 948, '[': 344, '_': 500, 'c': 427, 'g': 469, 'k': 458, 'o': 500, 's': 333, 'w': 677, '{': 480, '"': 408, '&': 698, '*': 417, '.': 250, '2': 500, '6': 500, ':': 250, '>': 667, 'B': 615, 'F': 552, 'J': 354, 'N': 750, 'R': 729, 'V': 729, 'Z': 635, '^': 469, 'b': 521, 'f': 271, 'j': 250, 'n': 531, 'r': 365, 'v': 458, 'z': 427, '~': 667, '!': 250, '%': 875, ')': 240, '-': 313, '1': 500, '5': 500, '9': 500, '=': 667, 'A': 677, 'E': 625, 'I': 354, 'M': 927, 'Q': 823, 'U': 771, 'Y': 677, ']': 344, 'a': 469, 'e': 438, 'i': 250, 'm': 802, 'q': 521, 'u': 521, 'y': 458, '}': 480}
widthsByUnichar["HeiseiKakuGo-W5"] = {'\uff81': 500, '\uff85': 500, '\uff89': 500, '\uff8d': 500, '\uff91': 500, '\uff95': 500, '\uff99': 500, '\uff9d': 500, ' ': 277, '$': 668, '(': 445, ',': 305, '0': 668, '\u0332': 668, '4': 668, '8': 668, '<': 668, '@': 871, 'D': 699, 'H': 687, 'L': 582, 'P': 582, 'T': 641, 'X': 609, '`': 590, '\uff62': 500, 'd': 602, '\uff66': 500, 'h': 582, '\uff6a': 500, 'l': 234, '\uff6e': 500, 'p': 602, '\uff72': 500, 't': 441, '\uff76': 500, 'x': 531, '\uff7a': 500, '|': 246, '\uff7e': 500, '\uff82': 500, '\uff86': 500, '\uff8a': 500, '\uff8e': 500, '\uff92': 500, '\uff96': 500, '\uff9a': 500, '\uff9e': 500, '#': 668, "'": 305, '+': 668, '/': 539, '3': 668, '7': 668, ';': 305, '?': 566, 'C': 652, 'G': 676, 'K': 664, 'O': 734, 'S': 605, 'W': 945, '[': 445, '_': 668, '\uff61': 500, 'c': 547, '\uff65': 500, 'g': 609, '\uff69': 500, 'k': 539, '\uff6d': 500, 'o': 605, '\uff71': 500, 's': 508, '\uff75': 500, 'w': 781, '\uff79': 500, '{': 449, '\uff7d': 500, '\u0300': 590, '\uff83': 500, '\u2002': 500, '\uff87': 500, '\uff8b': 500, '\uff8f': 500, '\uff93': 500, '\uff97': 500, '\uff9b': 500, '\uff9f': 500, '"': 500, '\xa5': 668, '&': 727, '*': 508, '.': 305, '2': 668, '6': 668, ':': 305, '>': 668, 'B': 637, 'F': 555, 'J': 492, 'N': 707, '\u203e': 500, 'R': 605, 'V': 727, 'Z': 574, '^': 668, 'b': 609, '\uff64': 500, 'f': 391, '\uff68': 500, 'j': 277, '\uff6c': 500, 'n': 582, '\uff70': 500, 'r': 387, '\uff74': 500, 'v': 562, '\uff78': 500, 'z': 555, '\uff7c': 500, '~': 668, '\uff80': 500, '\u0303': 668, '\uff84': 500, '\uff88': 500, '\uff8c': 500, '\u2011': 379, '\uff90': 500, '\uff94': 500, '\uff98': 500, '\uff9c': 500, '!': 305, '%': 906, ')': 445, '-': 379, '1': 668, '5': 668, '9': 668, '=': 668, 'A': 727, 'E': 574, 'I': 242, 'M': 789, 'Q': 734, 'U': 668, 'Y': 609, ']': 445, 'a': 555, '\uff63': 500, 'e': 574, '\uff67': 500, 'i': 234, '\uffe8': 500, '\uff6b': 500, 'm': 895, '\uff6f': 500, 'q': 602, '\uff73': 500, 'u': 582, '\uff77': 500, 'y': 570, '\uff7b': 500, '}': 449, '\uff7f': 500}
widthsByUnichar["HYSMyeongJo-Medium"] = {' ': 333, '$': 625, '(': 500, ',': 291, '0': 625, '4': 625, '8': 625, '<': 833, 'D': 750, 'H': 791, 'L': 666, 'P': 666, 'T': 791, 'X': 708, '\\': 375, '`': 333, 'd': 583, 'h': 583, 'l': 291, 'p': 583, 't': 375, 'x': 625, '|': 583, '#': 833, "'": 250, '+': 833, '/': 375, '3': 625, '7': 625, ';': 333, '?': 500, 'C': 708, 'G': 750, 'K': 791, 'O': 750, 'S': 666, '[': 500, '_': 500, 'c': 541, 'g': 583, 'k': 583, 'o': 583, 's': 541, 'w': 833, '{': 583, '"': 416, '&': 833, '*': 500, '.': 291, '2': 625, '6': 625, ':': 333, '>': 916, 'B': 708, 'F': 666, 'J': 500, 'N': 791, 'R': 708, 'V': 750, 'Z': 666, '^': 500, 'b': 583, 'f': 375, 'j': 333, 'n': 583, 'r': 458, 'v': 583, 'z': 500, '~': 750, '!': 416, '%': 916, ')': 500, '-': 833, '1': 625, '5': 625, '9': 625, '=': 833, 'A': 791, 'E': 708, 'I': 375, 'M': 916, 'Q': 750, 'U': 791, 'Y': 708, ']': 500, 'a': 541, 'e': 583, 'i': 291, 'm': 875, 'q': 583, 'u': 583, 'y': 625, '}': 583}
widthsByUnichar["STSong-Light"] = {' ': 207, '$': 462, '(': 374, ',': 238, '0': 462, '4': 462, '8': 462, '<': 605, '@': 748, 'D': 739, 'H': 793, 'L': 526, 'P': 544, 'T': 607, 'X': 647, '\\': 333, '`': 239, 'd': 529, 'h': 518, 'l': 228, 'p': 524, 't': 277, 'x': 466, '|': 258, '#': 467, "'": 239, '+': 605, '/': 334, '3': 462, '7': 462, ';': 238, '?': 344, 'C': 695, 'G': 729, 'K': 666, 'O': 772, 'S': 465, 'W': 972, '[': 374, '_': 500, 'c': 427, 'g': 444, 'k': 495, 'o': 524, 's': 336, 'w': 652, '{': 370, '"': 342, '&': 710, '*': 423, '.': 238, '2': 462, '6': 462, ':': 238, '>': 605, 'B': 560, 'F': 511, 'J': 312, 'N': 758, 'R': 628, 'V': 711, 'Z': 607, '^': 606, 'b': 503, 'f': 264, 'j': 230, 'n': 527, 'r': 338, 'v': 450, 'z': 407, '~': 605, '!': 270, '%': 797, ')': 374, '-': 375, '1': 462, '5': 462, '9': 462, '=': 605, 'A': 684, 'E': 563, 'I': 318, 'M': 896, 'Q': 772, 'U': 753, 'Y': 620, ']': 374, 'a': 417, 'e': 415, 'i': 241, 'm': 793, 'q': 504, 'u': 517, 'y': 452, '}': 370}
widthsByUnichar["HeiseiMin-W3"] = {'\uff81': 500, '\u0302': 333, '\uff85': 500, '\u0306': 333, '\uff89': 500, '\u030a': 333, '\uff8d': 500, '\uff91': 500, '\ufb02': 556, '\uff95': 500, '\uff99': 500, '\uff9d': 500, ' ': 250, '\xa3': 500, '\u2122': 980, '$': 500, '(': 333, '\xab': 500, ',': 250, '\xaf': 333, '0': 500, '\xb3': 300, '\u0332': 500, '4': 500, '\xb7': 250, '8': 500, '\xbb': 500, '<': 564, '\xbf': 444, '@': 921, '\xc3': 722, '\u0142': 278, 'D': 722, '\xc7': 667, 'H': 722, '\xcb': 611, 'L': 611, '\xcf': 333, 'P': 556, '\xd3': 722, '\u0152': 889, 'T': 611, 'X': 722, '\xdb': 722, '\\': 278, '\xdf': 500, '\uff64': 500, '`': 333, '\xe3': 444, '\uff62': 500, 'd': 500, '\xe7': 444, '\uff66': 500, 'h': 500, '\xeb': 444, '\uff6a': 500, 'l': 278, '\xef': 278, '\uff6e': 500, 'p': 500, '\xf3': 500, '\uff72': 500, 't': 278, '\uff76': 500, 'x': 500, '\xfb': 500, '\uff7a': 500, '|': 200, '\xff': 500, '\u017e': 444, '\u0301': 333, '\uff82': 500, '\u0305': 500, '\uff86': 500, '\uff8a': 500, '\uff8e': 500, '\u2013': 500, '\uff92': 500, '\uff96': 500, '\uff9a': 500, '\uff9e': 500, '#': 500, '\xa4': 500, "'": 180, '\u203a': 333, '+': 564, '\xac': 564, '/': 278, '\u0131': 278, '3': 500, '7': 500, '\xb8': 333, ';': 278, '\xbc': 750, '?': 444, '\u0141': 611, '\xc0': 722, 'C': 667, '\xc4': 722, 'G': 722, '\xc8': 611, 'K': 722, '\xcc': 333, 'O': 722, '\xd0': 722, 'S': 556, '\u2022': 350, '\xd4': 722, 'W': 944, '\uff78': 500, '\xd8': 722, '[': 333, '\xdc': 722, '_': 500, '\u0161': 389, '\xe0': 444, 'c': 444, '\uff65': 500, '\xe4': 444, 'g': 500, '\uff69': 500, '\xe8': 444, 'k': 500, '\uff6d': 500, '\xec': 278, 'o': 500, '\uff71': 500, '\xf0': 500, 's': 389, '\uff75': 500, '\xf4': 500, 'w': 722, '\uff79': 500, '\xf8': 500, '{': 480, '\uff7e': 500, '\u017d': 611, '\xfc': 500, '\u0300': 333, '\uff83': 500, '\u2002': 500, '\u0304': 333, '\uff87': 500, '\u0308': 333, '\uff8b': 500, '\u030c': 333, '\uff8f': 500, '\uff93': 500, '\u2012': 500, '\uff97': 500, '\uff9b': 500, '\u201a': 333, '\uff9f': 500, '\u201e': 444, '\xa1': 333, '"': 408, '\xa5': 500, '&': 778, '\xa9': 760, '\u0328': 333, '*': 500, '\xad': 564, '.': 250, '\uffe8': 500, '2': 500, '\xb5': 500, '6': 500, '\xb9': 300, ':': 278, '\xbd': 750, '>': 564, '\xc1': 722, '\uff61': 500, 'B': 667, '\xc5': 722, 'F': 556, '\xc9': 611, 'J': 389, '\xcd': 333, 'N': 722, '\xd1': 722, '\u203e': 500, 'R': 667, '\xd5': 722, 'V': 722, '\xd9': 722, 'Z': 611, '\xdd': 722, '^': 469, '\xe1': 444, '\u0160': 556, 'b': 500, '\xe5': 444, '\u2039': 333, 'f': 333, '\xe9': 444, '\uff68': 500, 'j': 278, '\xed': 278, '\uff6c': 500, 'n': 500, '\xf1': 500, '\uff70': 500, 'r': 333, '\xf5': 500, '\uff74': 500, 'v': 500, '\xf9': 500, '\u0178': 722, 'z': 444, '\xfd': 500, '\uff7c': 500, '~': 333, '\uff80': 500, '\u0303': 333, '\uff84': 500, '\u0307': 333, '\uff88': 500, '\u030b': 333, '\uff8c': 500, '\u2011': 333, '\uff90': 500, '\uff94': 500, '\uff98': 500, '\uff9c': 500, '\u2044': 167, '!': 333, '\xa2': 500, '%': 833, '\u0327': 333, '\xa6': 200, ')': 333, '\xaa': 276, '-': 333, '\xae': 760, '1': 500, '\xb2': 300, '5': 500, '9': 500, '\xba': 310, '=': 564, '\xbe': 750, 'A': 722, '\u01c0': 200, '\xc2': 722, 'E': 611, '\xc6': 889, 'I': 333, '\xca': 611, 'M': 889, '\xce': 333, 'Q': 722, '\u0153': 722, '\xd2': 722, 'U': 722, '\xd6': 722, 'Y': 722, '\ufb01': 556, '\xda': 722, ']': 333, '\xde': 556, 'a': 444, '\uff63': 500, '\xe2': 444, 'e': 444, '\uff67': 500, '\xe6': 667, 'i': 278, '\uff7d': 500, '\uff6b': 500, '\xea': 444, 'm': 778, '\uff6f': 500, '\xee': 278, 'q': 500, '\uff73': 500, '\xf2': 500, 'u': 500, '\uff77': 500, '\xf6': 500, 'y': 500, '\uff7b': 500, '\xfa': 500, '}': 480, '\uff7f': 500, '\xfe': 500}
widthsByUnichar["HYGothic-Medium"] = {' ': 500, '$': 500, '(': 500, ',': 500, '0': 500, '4': 500, '8': 500, '<': 500, '@': 500, 'D': 500, 'H': 500, 'L': 500, 'P': 500, 'T': 500, 'X': 500, '\\': 500, '`': 500, 'd': 500, 'h': 500, 'l': 500, 'p': 500, 't': 500, 'x': 500, '|': 500, '#': 500, "'": 500, '+': 500, '/': 500, '3': 500, '7': 500, ';': 500, '?': 500, 'C': 500, 'G': 500, 'K': 500, 'O': 500, 'S': 500, 'W': 500, '[': 500, '_': 500, 'c': 500, 'g': 500, 'k': 500, 'o': 500, 's': 500, 'w': 500, '{': 500, '"': 500, '&': 500, '*': 500, '.': 500, '2': 500, '6': 500, ':': 500, '>': 500, 'B': 500, 'F': 500, 'J': 500, 'N': 500, 'R': 500, 'V': 500, 'Z': 500, '^': 500, 'b': 500, 'f': 500, 'j': 500, 'n': 500, 'r': 500, 'v': 500, 'z': 500, '!': 500, '%': 500, ')': 500, '-': 500, '1': 500, '5': 500, '9': 500, '=': 500, 'A': 500, 'E': 500, 'I': 500, 'M': 500, 'Q': 500, 'U': 500, 'Y': 500, ']': 500, 'a': 500, 'e': 500, 'i': 500, 'm': 500, 'q': 500, 'u': 500, 'y': 500, '}': 500}


#shift-jis saying 'This is Heisei-Minchou'
message1 =  '\202\261\202\352\202\315\225\275\220\254\226\276\222\251\202\305\202\267\201B'
message2 = '\202\261\202\352\202\315\225\275\220\254\212p\203S\203V\203b\203N\202\305\202\267\201B'

##def pswidths(text):
##    words = text.split()
##    out = []
##    for word in words:
##        if word == '[':
##            out.append(word)
##        else:
##            out.append(word + ',')
##    return eval(''.join(out))
