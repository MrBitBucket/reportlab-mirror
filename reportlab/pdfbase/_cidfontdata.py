#copyright ReportLab Inc. 2001
#see license.txt for license details
#history http://cvs.sourceforge.net/cgi-bin/cvsweb.cgi/reportlab/pdfbase/_cidfontdata.py?cvsroot=reportlab
#$Header $
__version__=''' $Id: _cidfontdata.py,v 1.3 2001/09/25 21:18:53 andy_robinson Exp $ '''
__doc__="""
This defines additional static data to support CID fonts.

Canned data is provided for the Japanese fonts supported by Adobe. We
can add Chinese, Korean and Vietnamese in due course. The data was
extracted by creating very simple postscript documents and running
through Distiller, then examining the resulting PDFs.

Each font is described as a big nested dictionary.  This lets us keep
code out of the module altogether and avoid circular dependencies.

The encoding and font data are grouped by some standard 'language
prefixes':
   chs = Chinese Simplified (mainland)
   cht = Chinese Traditional (Taiwan)
   kor = Korean
   jpn = Japanese
"""
languages = ['japanese', 'korean']

#breaking down the lists let us check if something is present
#for a specific language
typeFaces_chs = [] # to do
typeFaces_cht = [] # to do
typeFaces_jpn = ['HeiseiMin-W3', 'HeiseiKakuGo-W5']
typeFaces_kor = ['HYSMyeongJoStd-Medium-Acro']

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

allowedEncodings = (['Identity-H', 'Identity-V'] +
                    encodings_chs +
                    encodings_cht +
                    encodings_jpn +
                    encodings_kor
                    )


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
                    'Ascent': 752,
                    'CapHeight': 737,
                    'Descent': -221,
                    'Flags': 4,
                    'FontBBox': (-92, -250, 1010, 922),
                    'FontName': '/HeiseiMin-W3',
                    'ItalicAngle': 0,
                    'StemV': 114,
                    'XHeight': 553,
                    'Style': {'Panose': '<0801020b0600000000000000>'}
                    },
                'CIDSystemInfo': {
                    'Registry': '(Adobe)',
                    'Ordering': '(Japan1)',
                    'Supplement': 2
                    },
                #default width is 1000 em units
                'DW': 1000,
                #widths of any which are not the default.
                'W': (
                    # starting at character ID 1, next n  characters have the widths given.
                    1,  (277,305,500,668,668,906,727,305,445,445,508,668,305,379,305,539),
                    # all Characters from ID 17 to 26 are 668 em units wide
                    17, 26, 668,
                    27, (305, 305, 668, 668, 668, 566, 871, 727, 637, 652, 699, 574, 555,
                         676, 687, 242, 492, 664, 582, 789, 707, 734, 582, 734, 605, 605,
                         641, 668, 727, 945, 609, 609, 574, 445, 668, 445, 668, 668, 590,
                         555, 609, 547, 602, 574, 391, 609, 582, 234, 277, 539, 234, 895,
                         582, 605, 602, 602, 387, 508, 441, 582, 562, 781, 531, 570, 555,
                         449, 246, 449, 668),
                    # these must be half width katakana and the like.
                    231, 632, 500
                    )
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
                    'StemV': 114,
                    'XHeight': 553,
                    'Style': {'Panose': '<0801020b0600000000000000>'}
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


CIDFontInfo['HYSMyeongJoStd-Medium-Acro'] =  {'Type':'/Font',
            'Subtype':'/Type0',
            'Name': '/%(internalName)s', #<-- the internal name
            'BaseFont': '/' + 'HYSMyeongJoStd-Medium-Acro',
            'Encoding': '/%(encodings)s',
            'DescendantFonts': [{'Type':'/Font',
                'Subtype':'/CIDFontType2',
                'BaseFont':'/'+'HYSMyeongJoStd-Medium-Acro',
                'FontDescriptor': {
                    'Type': '/FontDescriptor',
                    'Ascent': 858,
                    'AvgWidth': 500,
                    'CapHeight': 858,
                    'Descent': -142,
                    'Flags': 7,
                    'FontBBox': [-100, -142, 1100, 1000],
                    'FontName': '/'+'HYSMyeongJoStd-Medium-Acro',
                    'ItalicAngle': 0,
                    'Leading': 148,
                    'MaxWidth': 1000,
                    'MissingWidth': 500,
                    'StemH': 91,
                    'StemV': 91,
                    'XHeight': 429,
                    'Style': {'Panose': '<000000000000000000000000>'}
                    },
                'CIDSystemInfo': {
                    'Registry': '(Adobe)',
                    'Ordering': '(Korea1)',
                    'Supplement': 1
                    },
                'DW': 1000,
                'W': (1, 94, 500),
                'WinCharSet': 129
                }] # end descendant fonts
            }

            
#shift-jis saying 'This is Heisei-Minchou'
message1 =  '\202\261\202\352\202\315\225\275\220\254\226\276\222\251\202\305\202\267\201B'
message2 = '\202\261\202\352\202\315\225\275\220\254\212p\203S\203V\203b\203N\202\305\202\267\201B'
