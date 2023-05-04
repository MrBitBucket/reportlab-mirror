CHANGES
=======

This is a summary of changes made to the reportlab source code for each release.
Please refer to subversion backlogs (using the release dates) for more details
or for releases which we have not provide a hig`her level changes list for.
E.g. to retrieve the changes made between release 3.4 and release 3.5, type::

  $ hg log -r 54ce2469ba5c

The contributors lists are in no order and apologies to those accidentally not
mentioned. If we missed you, please let us know!

CHANGES  4.0.0a3 18/04/2023
---------------------------
	* initial support for rml ul ol dl tagging
    * added support for an ol/ul/dl caption paragraph
	* implement a safer toColor with rl_config.toColorCanUse option and rl_extended_literal_eval

CHANGES  4.0.0a2 14/03/2023
---------------------------
	* added _ExpandedCellTupleEx for more tagging support

CHANGES  4.0.0a1 08/03/2023
---------------------------
	* release 4.0.0a1 with support for rlextra pluscode

CHANGES  3.6.13  24/04/2023
---------------------------
	* fixes for python 3.12.0a1
	* tables.py error improvement
	* allow exclusions in tests in runAll.py and setup.py; allows for coverage.py importing failures.
	* implement a safer toColor with rl_config.toColorCanUse option and rl_extended_literal_eval

CHANGES  3.6.12  25/10/2022
---------------------------
	* fix dpi handling in renderPM.py; bug found by Terry Zhao Terry dot Zhao at fil dot com
	* attempt fix in rparsexml.py
	* add rl_settings.xmlParser with default 'lxml'
	* nano RHEL related fix to setup.py contributed by James Brown jbrown at easypost dot com
	* minor speedup in reportlab.graphics.transform functions
	* allow usage of freetype testpaths via rl_config/rl_settings textPaths
	* _renderPM.c remove parse_utf8, make pict_putrow same as for rlPyCairo

CHANGES  3.6.11  24/06/2022
---------------------------
	* support HORIZONTAL2 & VERTICAL2 table cell backgrounds; as suggested by Sina Khelil < sina at khelil dot com >
	* support general LINEAR & RADIAL gradient table cell backgrounds
	* support ShowBoundaryValue in canv.drawImage

CHANGES  3.6.10  31/05/2022
---------------------------
	* fix symlink looping in setup.py reported by Michał Górny &lt; mgorny at gentoo dot org &gt;
	* allow bearerBox attribute for some barcodes
	* require pillow>=9.0.0 patch contributed by Claude Paroz claude at 2xlibre.net
	* Apply Claude Paroz  < claude at 2xlibre dot net > patch to assume hashlib md5 exists
	* ImageReader updated to allow deepcopy; similarly for doctemplate.onDrawStr
	* fix 3.11.0b2 regression in rl_safe_eval.
	* apply massive contribution for Table inRowSplit from Lennart Regebro < lregebro at shoobx dot com >

CHANGES  3.6.9   22/03/2022
---------------------------
	* fix up _rl_accel.c 0.81 to allow better error messages and support python 3.11.0a6
	* change the cibuildwheel setup to support macos M1 build

CHANGES  3.6.8   28/02/2022
---------------------------
	* remove old Python2 constructs; patch from Claude Paroz < claude at 2xlibre dot net >

CHANGES  3.6.7   18/02/2022
---------------------------
	* Remove use of cPickle; patch from Claude Paroz < claude at 2xlibre dot net >
	* Remove unneccessary object inheritance; patch by Claude Paroz
	* minor changes to python rendering in shapes.Drawing
	* remove jython (dead project no python3) patch by  Claude Paroz < claude at 2xlibre dot net >
	* remove unicodeT/bytesT patch by  Claude Paroz < claude at 2xlibre dot net >
	* import directly from string module patch by  Claude Paroz < claude at 2xlibre dot net >
	* eliminate getBytesIO and getStringIO patch by  Claude Paroz < claude at 2xlibre dot net >
	* remove unused and indirect imports patch by  Claude Paroz < claude at 2xlibre dot net >

CHANGES  3.6.6	 24/01/2022
---------------------------
	* remove uniChr alias of chr (patch contribution from Claude Paroz)
	* modify pdfdoc template to be eventually compatible with pikepdf suggested by Lennart Regebro lregebro at shoobx.com
	* fix bug in table gradient bg; contribution by Justin Brzozoski justin.brzozoski at gmail.com
	* fix bug in validateSetattr (__dict__) discovered and reported by Chris Buergi  cb at enerweb dot ch
	* fix handling of ddfStyle in XLabel class

CHANGES  3.6.5	 24/12/2021
---------------------------
	* only skip listwrap on for small height objects
	* changes to allow for deprecated stuff in Python-3.11

CHANGES  3.6.4	  7/12/2021
---------------------------
	* try to improve multi-frag paragraph justification
	* fix justification condition
	* allow validator OneOf to take re.Pattern

CHANGES  3.6.3	  4/11/2021
---------------------------
	* modernisation of para.py contribution from <Andrews Searle at BMC dot com>
	* many changes to .github workflows
	* changes to setup.py to support cibuildwheel
	* _FindSplitterMixin protect against deepcopy failure
	* allow textAnnotation to have QuadPoints keyword

CHANGES  3.6.2	  1/10/2021
---------------------------
	* minor changes to datareader
	* fix XLabel argument usage

CHANGES  3.6.1	  6/08/2021
---------------------------
	* add mock for urlopen calls so tests can run off line. Contribution by Antonio Trande sagitter at fedoraproject dot org

CHANGES  3.6.0	 23/07/2021
---------------------------
	* create py-2-3 branch
	* Cease support for Python-2.7

CHANGES  3.5.68	 25/06/2021
---------------------------
	* graphics improve some error messages for renderPM
	* changed lib.urilt.recursiveImport after errors in python3.10, reflect changes in readJPEGInfo
	* pdfutils readJPEGInfo extracts dpi if present defaults to (72, 72)
	* Image flowable allows a useDPI argument
	* paraparser annotate some errors

CHANGES  3.5.67	 12/04/2021
---------------------------
	* Allow unicode PDFString to use encoding directly; fixes bug where colorspace indexes are broken
	* Ensure PIL images can be size checked

CHANGES  3.5.66	 19/03/2021
---------------------------
	* fix obvious bug in renderPS.py cut'n'paste bah :(
	* fix bug saving to SpooledtemporaryFile's reported by Robert Schroll <rschroll at gmail.com>
	* fix bug in justified RTL paragraphs example & bugfix contributed by Moshe Uminer <mosheduminer at gmail.com>
	* fix regex deprecation reported by Jürgen Gmach <juergen.gmach at apis.de>

CHANGES  3.5.65	 10/03/2021
---------------------------
	* add yieldNoneSplits utility function
	* fix BarChart so it lines can have markers and Nones in their data

CHANGES  3.5.64	 09/03/2021
---------------------------
	* add ability to have lineplots in barcharts; no support yet for line markers
	* added checkAttr method to TypedPropertyCollection

CHANGES  3.5.63	 05/03/2021
---------------------------
	* ensure setup.py works from sdist; bug reported by Antonio P. Sagitter (sagitter at fedoraproject.org)
	* restore broken MANIFEST.in somehow overwritten by Robin :(

CHANGES  3.5.62	 03/03/2021
---------------------------
	* simplify annotateException and add better error messages for asUnicode/Bytes etc
	* improve embeddedHyphenation in paragraph.py

CHANGES  3.5.61	 25/02/2021
---------------------------
	* add adjustableArrow widget
	* allow para tag borderPadding attribute
	* minor cosmetics in renderPM C extension and add fontSize setattr 
	* allow a bounding box constraint in definePath
	* efficiency savings in text2Path
	* refactor transformation math and text2Path functionality	
	* allow a renderPM plugin cairo backend package rlPyCairo

CHANGES  3.5.60	 22/01/2021
---------------------------
	* Allow legend column control of vertical alignment
	* Allow renderTextMode attribute in reportlab.graphics.shapes.String
	* Allow renderTextMode drawString handling in renderPDF/PM/PS/SVG
	* Some fixes to fillMode handling

CHANGES  3.5.59	 04/01/2021
---------------------------
	* Minor changes to table rounded corners; some documentation updates

CHANGES  3.5.58	 01/01/2021
---------------------------
	* Allow variant corners in Canvas.roundRect
	* Allow tables to have rounded corners

CHANGES  3.5.57	 27/12/2020
---------------------------
	* added ddfStyle to Label
	* allowed for embedded(and ordinary)Hyphenation to pre-empt splitting when embeddedHyphenation>=2
	* fix extension escapePDF so it can handle unicode
	* fix poundsign in Ean5BarcodeWidget
	* Table can use __styledWrap__ for sizing
	* test fixes so 3.9 and 2.7 produce same pdf

CHANGES  3.5.56	 10/12/2020
---------------------------
	* added .github action wheel.yml
	* micro change to userguide doc

RELEASE 3.5.56	 01/12/2020
---------------------------
	* micro changes for Big Sur in C extensions
	* allow Drawing.outDir to be a callable for more control in save method

RELEASE 3.5.55	 29/10/2020
---------------------------
	* add trustedHosts and trustedSchemes for url management
	* deifinitely drop 3.5 support (Jon Ribbens points out it may have happened in 3.5.54).

RELEASE 3.5.54	 23/10/2020
---------------------------
	* Allow extra fields in AcroForm suggested by Chris Else ubuntu247 at gmail.com
	* Allow DocTemplate.\_firstPageTemplateIndex to be a list of PageTemplate ids
	* improve PageBreak repr
	* minor changes to travis & appveyor scripts; drop forml support for python 3.5

RELEASE 3.5.53	 02/10/2020
---------------------------
	* Fix bug that allowed type 0 postscript commands to persist

RELEASE 3.5.52	 01/10/2020
---------------------------
	* add support for DataMatrix barcode

RELEASE 3.5.51	 24/09/2020
---------------------------
	* fix malloc(0) issue in \_rl_accel.c \_fp_str thanks to Hans-Peter Jansen <hpj@urpla.net> @ openSUSE

RELEASE 3.5.50	 18/09/2020
---------------------------
	* Add BM ExtGState option (suggestion by tjj021 @ github
	* Fix memory leak in \_renderPM.c

RELEASE 3.5.49	 02/09/2020
---------------------------
	* ViewerPreferencesPDFDictionary add /Duplex as possibility
	* Doctemplate add support for all ViewerPreferencesPDFDictionary keys
	* fix bugs in USPS_4State; Barcode inherits from Flowable and object.

RELEASE 3.5.48	 18/08/2020
---------------------------
	* bug fix for balanced column special case unsplittable half column

RELEASE 3.5.47	  7/08/2020
---------------------------
	* try to limit table style cell ranges

RELEASE 3.5.46	 22/07/2020
---------------------------
	* fix style-data mismatch in LinePlot found by Anshika Sahay

RELEASE 3.5.45	 10/07/2020
---------------------------
	* fix some documentation bugs reported by Lele Gaifax
	* fix error in BarChart axes joining reported by Faisal.Fareed

RELEASE 3.5.44	 26/06/2020
---------------------------
	* ensure qr bar colour is passed (contrib by Lele Gaifax)
	* fix img layout bug (reported by Lele Gaifax) 

RELEASE 3.5.43	 03/06/2020
---------------------------
	* small change to improve strokeDashArray handling to allow [phase, [values]] and allow stroke-dashoffset
	* Hatching class which inherits from shapes.Path
	* add support for soft hyphens u'\xad'
	* apply a pr from KENLYST @ bitbucket (gfe.py)

RELEASE 3.5.42	 17/03/2020
--------------------------
	* fix bug in tables.py reported by Kamil Niski https://bitbucket.org/rptlab/reportlab/issues/182 & Adam Kalinsky

RELEASE 3.5.41	 4/03/2020
--------------------------
	* fix python3 bug in DDIndenter.__getattr__

RELEASE 3.5.40	28/02/2020
--------------------------
	* fix broken (by robin) simple bar lables found by Djan

RELEASE 3.5.39	26/02/2020
--------------------------
	* allow selection of ttf subfonts by PS name
	* revert to old style recursiveGetAttr
	* raise error for problematic Canvas.setDash reported by Mike Carter from sitemorse

RELEASE 3.5.38	14/02/2020
--------------------------
	* bug fix for normalDate monthnames; bump travis; version-->3.5.38

RELEASE 3.5.37	07/02/2020
--------------------------
	* experimental support for 2d pie/doughnut shading

RELEASE 3.5.36	28/01/2020
--------------------------
	* update travis version of multibuild contrib by Matthew Brett
	* fixes to cope with python 3.9
	* imrove Drawing formats handling and ensure asString can do svg

RELEASE 3.5.35	22/01/2020
--------------------------
	* test fixes
	* Label enhancement
	* added isSubclassOf validator
	* added CrossHair widget

RELEASE 3.5.34	14/01/2020
--------------------------
	* attempted restriction of the reportlab.lib.color.toColor function

RELEASE 3.5.33	30/10/2019
--------------------------
	* fix bug in Pie3d reported by Eldon Ziegler <eldonz@atlanticdb.com>
	* fix bug in background splitting in repeatRows cases reported by David VanEe <david.vanee@convergent.ca>
	* small improvements to CandleSticks
	* created NotSet validator (use in  CandleStickProperties)
	* update .travis.yml and .appeyor.yml hopefully to create 3.8 wheels

RELEASE 3.5.32	24/10/2019
--------------------------
	* some chart efficiency changes
	* use clock in fontFinder contributed by Matěj Cepl @ bitbucket
	* improve recursive access and do some minor eval/exec fixes
	* improve use of eval/exec

RELEASE 3.5.31	15/10/2019
--------------------------
	* paraparser fix contributed by ravi prakash giri <raviprakashgiri@gmail.com>

RELEASE 3.5.30	15/10/2019
--------------------------
	* better support for candlestick charts using smartGetItem

RELEASE 3.5.29	14/10/2019
--------------------------
	* Support for candlestick charts and infilled pair plots

RELEASE 3.5.28	02/10/2019
--------------------------
	* improve support for AES encryption

RELEASE 3.5.27	01/10/2019
--------------------------
	* fix to justified para splits contributed by Niharika Singh <nsingh@shoobx.com>
	* fix BalanceColumn width calculation
	* preliminary support for AES encryption (contributed by https://github.com/talebi1)

RELEASE 3.5.26	17/09/2019
--------------------------
	* micro changes to normalDate
	* fix warnings about is not (detected in python 3.8b4)
	* implement PR #59 bug fix contributed by Vytis Banaitis

RELEASE 3.5.25	23/08/2019
--------------------------
	* add recursive ttf searching
	* sync with rlextra
	* fix Barchart axis crossing issue reported by Martin Jones (Zeidler)

RELEASE 3.5.24	07/08/2019
--------------------------
	* prepare for python3.8, drop support for python3.4

RELEASE 3.5.23	31/05/2019
--------------------------
	* fix issue #180 raised by Christoph Berg
	* fix issue #181 raised by Daniel Terecuk
	* brutalist fix for Marius Gedminas' issue #183
	* add wordSpace keyword to Canvas draw methods
	* fix for Marius Gedminas' issue #184

RELEASE 3.5.22	23/05/2019
--------------------------
	* Allow kewords in PDFResourceDictionary
	* pr #58 issue #174 contribution by Marius Gedminas
	* Allow AcroForm to have SigFlags
	* Bug Fixes and tests

RELEASE 3.5.21	 3/05/2019
--------------------------
	* fix bug in legends
	* add extra table info in spanning error case

RELEASE 3.5.20	25/04/2019
--------------------------
	* Preliminary MultiCol implementation
	* fix missing xrange import
	* allow rgb to have fractions of 1 in css colors

RELEASE 3.5.19	15/04/2019
--------------------------
	* fix bug with a tag href not having a scheme
	* all0w LineChart/LinePlot area fills to differe from the stroke colour
	* add canvas setProducer method

RELEASE 3.5.18	03/04/2019
--------------------------
	* more FrameBG changes vs BalancedColumns
	* fix bb issues #176/#177 reported by graingert & droidzone 

RELEASE 3.5.17	29/03/2019
--------------------------
	* more FrameBG fixes; added canvas cross method, frame static drawBoundary

RELEASE 3.5.16	27/03/2019
--------------------------
	* fix stroking for frame background in container

RELEASE 3.5.15	27/03/2019
--------------------------
	* add stroking for frame background

RELEASE 3.5.14	14/03/2019
--------------------------
	* added axes tickStrokeWidth etc etc

RELEASE 3.5.13	15/01/2019
--------------------------
	* added rl_setting.reserveTTFNotdef inspired by e3office at bitbucket (pr #50)

RELEASE 3.5.12	30/11/2018
--------------------------
	* log axis handles rangeRound & avoidBoundspace
	* FrameBG can start with "frame" & frame-permanent" start options

RELEASE 3.5.11	20/11/2018
--------------------------
	* Improve log axis ticks & grids
	* move some samples into tests


RELEASE 3.5.10	15/11/2018
--------------------------
	* Bug fix for underline (contrib. Lennart Regebro @ bitbucket)
	* Paragraph indentation bug fix
	* Initial support for richtext graphics text labels
	* Initial support for log axes (ideas from hoel@germanlloyd.org)

RELEASE 3.5.9  01/10/2018
-------------------------
	* add hyphenationMinWordLength to address PR #44 (contrib Michael V. Reztsov)

RELEASE 3.5.8  21/09/2018
-------------------------
	* Allow structured barLabelFormat (suggestion from Ravinder Baid)

RELEASE 3.5.7  22/08/2018
-------------------------
	* Fix tables.py splitting for line comands.

RELEASE 3.5.6  20/08/2018
-------------------------
	* Restore DocTemplate seq attribute lost in rev c985bd7093ad (4405)
	  version 3.4.41 bug report from Jim Parinisi jimandkimparinisi@yahoo.com

RELEASE 3.5.5  14/08/2018
-------------------------
	* Bug fix underlined space in XPreformatted

RELEASE 3.5.4  06/08/2018
-------------------------
	* Bug fix for Paragraph space bugs reported by Kayley Lane
	* Use local libart code by default (libart 2.3.21-3)

RELEASE 3.5.3  06/07/2018
-------------------------
	* Bug fix release to make really simple paras work OK 
	  Reported by Kayley.Lane @ oracle.com
	* Use local libart by default
	* Use upgrade libart source to 2.3.21-3 https://salsa.debian.org/gnome-team/libart-lgpl@aa059539

RELEASE 3.5.2  23/07/2018
-------------------------
	* Bug fix release to make th sdist work properly

RELEASE 3.5.1  17/07/2018
-------------------------
	* Bug fix for infinite looping in Paragraph (likely caused by small available Widths).
	  Reported by Kayley.Lane @ oracle.com

RELEASE 3.5  07/07/2018
-----------------------
	* BalancedColumns flowable added
	* primitive hyphenation functionality (with Pyphen installed)
	* simple paragraphs now allow space shrinkage
	* mixed parallel / stacked barcharts mechanism
	* makeStream compression fix for python 3.x
	* reproducibility fixes
	* Bugfix for KeepWithNext and None
	* Fix pie chart issue
	* allow canvas filename to be a wrapped OS level file
	* added DocTemplate._makeCanvas
	* _text2Path fix
	* AcroForm improvements
	* added anchorAtXY parameter for images
	* fix PDF syntax error with no Outlines
	* fix bullet code
	* qrencoder fix
	* table minRowHeights support
	* stopped abusing builtins to aid compatibility
	* fix embedded font & fontfinder bugs
	* fix zero width paragraph layout error
	* doughnut charts support innerRadiusFraction
	* more controllable under and strike lines

### Contributors:
	* Axel P. Kielhorn
	* ben @ readingtype.org.uk
	* Chris Jerdonek cjerdonek @ bitbucket
	* Dan Palmer danpalmer @ bitbucket
	* Garry Williams gary_williams @ bit_bucket
	* Greg Svitak
	* htgoebel @ bitbucket
	* Johann Du Toit https://bitbucket.org/johanndt/ 
	* Jon Hinton (inivatajon @ bitbucket.org)
	* Lele Gaifax
	* lisandrija @ bitbucket.org
	* lostbard @ bitbucket
	* Martin J. Laubach bitbucket issue #140
	* Moritz Pfeiffer moritzpfeiffer @ bitbucket
	* Raji Sundar
	* Silas Sewell silassewell @ bitbucket
	* simonkagwe @ bitbucket
	* Tom Alexander @ bitbucket
	* Trevor Bullock
	* Waldemar Osuch

RELEASE 3.4  07/03/2017
-----------------------
	* More pagesizes from https://en.wikipedia.org/wiki/Paper_size (contributed by https://bitbucket.org/alainchiasson/)
	* add in fillMode (fill-rule) variable to the graphics state for drawings
	* add support for automatic bullet rotation in ListFlowables.
	* fix acroform annotation bug in radios (reported by Olivia Zhang)
	* fix split paragraph rendering bug (reported by Olivia Zhang & Echo Bell)
	* Allow Image to have a drawing as argument
	* support for Path autoclose & fillMode; version --> 3.3.29
	* add support for different fill policies in renderXX drawPath; version-->3.3.28
	* allow for UTF_16_LE BOM, fix for bug contributed by Michael Poindexter mpoindexter@housecanary.com
	* improved support for images in renderPM/renderSVG bug report from Claude Paroz
	* add AcroForm support to canvas; version --> 3.3.22
	* avoid cr lf line endings
	* attempt to ensure zipImported has some files or returns None
	* added additonal test to barcode/test.py
	* add an invisible font test thanks https://bitbucket.org/kb/ Konstantin Baierer
	* add mailto href test
	* improve UPCA barcode contribution by Kyle McFarlane https://bitbucket.org/kylemacfarlane/
	* attempt to fix __loader__ issues in pyinstaller suggested by dbrnz @ bitbucket
	* fix NormalDate comprisons in python3.x
	* fix ypad use in ParagraphAndImage contrib annamarianfr@bitbucket, version-->3.3.16
	* try to prevent multiple saving contrib by Tim Meneely
	* fix problems with svg drawToString contrib by Eric Gillet & Johann Du Toit
	* fix issue reported by Yitzchak Scott-Thoennes <sthoenna@gmail.com>
	* fix fake KeepTogether setup in handle_keepWithNext
	* add NullActionFlowable, fix empty KeepTogether
	* really merge para-measure-fix
	* merge para-measure-fix changes
	* fixes to TypedPropertyCollection
	* changes to Render class; allow drawings to specify initialFontName/Size
	* fix python>=3.2 default axis labelling to match python2.x; bugfix contributed by Robin Westin bitbucket issue #82
	* fix AttributeError reported by Kay Schluehr bitbucket issue #81
	* add experimental time value axis
	* fix bug in python shapes rendering
	* add negative span style to test_platypus_tables splitting example
	* fix segfault in _rl_accel.c; fix contributed by Neil Schemenauer as issue #78
	* attempt to remove quadratic performance hit when longTableOptimize is set
	* allow DATA: scheme in open for read
	* import Table _rowpositions calculation
	* support small ttfs which do not allow subsets
	* add rl_settings allowTTFSubsetting
	* address issue #76 (deprecated immports) reported by Richard Eames
	* add table cell support for simple background shadings, contributed by Jeffrey Creem jcreem@bitbucket
	* fix bug in tables.py reported by Vytis Banaitis @ bitbucket; version-->3.3.2
	* minor change to allow barWidth setting in ecc200datamatrix.py (suggested by Kyle MacFarlane @ bitbucket)
	* make paraparser syntax errors real and fix <sup/sub> tags to have relative values; version-->3.3.1
	* ReportLab now runs all tests under Python 2.7, 3.3, 3.4, 3.5 & 3.6.

### Contributors:
	* Alain Chiasson https://bitbucket.org/alainchiasson/
	* annamarianfr@bitbucket
	* Claude Paroz
	* dbrnz @ bitbucket
	* Dinu Gherman
	* Echo Bell
	* Eric Gillet
	* Jeffrey Creem jcreem@bitbucket
	* Johann Du Toit
	* Kay Schluehr bitbucket issue #81
	* Konstantin Baierer
	* Kyle McFarlane https://bitbucket.org/kylemacfarlane/
	* Michael Poindexter mpoindexter@housecanary.com
	* Neil Schemenauer
	* Olivia Zhang
	* Richard Eames
	* Robin Westin
	* Tim Meneely
	* Vytis Banaitis @ bitbucket
	* Yitzchak Scott-Thoennes <sthoenna@gmail.com>


RELEASE 3.3  17/02/2016
-----------------------
	* Canvas & Doctemplate now allow specification of the initial font Name, Size & Leading. Prevously you had to mess with rl_settings to accomplish this.
	* Canvas & Doctemplate now support specification of the crop/art/trim/bleed boxes.
	* Add option to auto generate missing TTF font names. Handy for CJKers with home produced fonts. Also attempt to prevent usage of multiple TTFs with same name.
	* Paragraph styles now have justifyBreaks to control justification of lines broken with <br/>.
	* Paragraph styles now have justifyLastLine=n to control justification of last lines with more than n words (0 means do not).
	* Added EAN-5 and ISBN barcode widgets (contribution by Edward Greve).
	* Bug fix of QrCodeWidget (prompted by https://bitbucket.org/fubu/).
	* Frames now have support for automatic flowables at the top of frame. story support via the class reportlab.platypus.flowables.SetTopFlowables.
	* Added support for Trapped and ModDate PDF info dictionary keys.
	* Bug fix for pie charts with no data (raised by  Michael Spector).
	* New barcodes BarcodeCode128Auto & BarcodeECC200DataMatrix (contributed by Kyle MacFarlane).
	* Improved LinePlot marker handling.
	* PyPy improvements inspired by Marius Gedminas.
	* Bug fix in reportlab.lib.utils.simpleSplit (reported by Chris Buergi <cb@enerweb.ch>).
	* Unwanted escaping in renderSVG fixed (reported by Ruby Yocum).
	* Bug fix in _rl_accel.c (remove excess state and fix refcount breakage reported by Mark De Wit <mark.dewit@iesve.com>).
	* Code128 barcode length optimization inspired by Klaas Feenstra.
	* Paragraph <sup>/<super> & <sub> tags now support rise & size attributes to allow special control over position & font size.
	* Splitting tables now remove unwanted styles in the first part of the split (reported by Lele Gaifax). 
	* test changes inspired by https://bitbucket.org/stoneleaf
	* ReportLab now runs all tests under Python 2.7, 3.3, 3.4 & 3.5.


### Contributors:
	* Edward Greve
	* https://bitbucket.org/fubu/
	* Michael Spector
	* Kyle MacFarlane
	* Marius Gedminas
	* Chris Buergi
	* Ruby Yocum
	* Mark de Wit
	* Klaas Feenstra
	* Lele Gaifax
	* https://bitbucket.org/stoneleaf

RELEASE 3.2  01/06/2015
-----------------------

   * Added proportional underlining specific to font sizes, set via the `underlineProportion` attribute of ParagraphStyles. 
   * TrueType fonts: added support for cmaps 10 & 13
   * DocTemplate class now supports a boolean `displayDocTitle` argument.
   * TableofContents now supports a formatter argument to allow formatting of the displayed page numbers (eg for appendices etc).
   * Table `repeatRows` can now be a tuple of row numbers to allow incomplete ranges of rows to be repeated. 
   * Tables now do pass instance.`spaceBefore` & `spaceAfter` to their split children when split 
   * Several strangenesses were fixed in the pdfbase.pdfform module; Multiple usage is now allowed.
   * Error message fixes
   * Various environment fixes for Google Application Environment
   * Resource fixes
   * PDFDoc can now set the `Lang` attribute
   * canvas.drawString and similar now allow the character spacing to be set 
   * Index of accented stuff has been improved
   * RTL code was improved
   * fix Propertyset.clone
   * `flowables.py`: fix ImageAndFlowables so it avoids testing negative availableWidth 

### Contributors:
   * Steven Jacobs
   * Philip Semanchuk
   * Marius Gedminas
   * masklinn
   * Kale Franz
   * Albertas Agejavas
   • Anders Hammarquist
   * jvanzuela @ bitbucket
   * Glen Lindermann
   * Greg Jones
   * James Bynd
   * fcoelho @ bitbucket


RELEASE 3.1  22/04/2014
-----------------------

If you are running ReportLab 3.0.x, the changes are minor.
   * support for emoji - characters outside the Unicode basic multilingual plane
   * improved pip-based installers will pull in all the needed dependencies; Pillow 2.4 appears to deal with all our issues.

### Contributors
   * Ivan Tchomgue
   * Waldemar Osuch
   * masayuku
   * alexandrel_sgi


RELEASE 3.0  14/02/2014
-----------------------

ReportLab 3.0 now supports Python 2.7, 3.3 and higher.	

There has been a substantial internal rewrite to ensure consistent use of unicode strings for
  natural-language text, and of bytes for all file format internals.  The intent
  is to make as few API changes as possible so that there should be little or no
  impact on users and their applications.  Changes are too numerous but can be
  seen on Bitbucket.

### Python 3.x compatibility
  * Python 3.x compatibility.  A single line of code should run on 2.7 and 3.3
  * __init__.py restricts to 2.7 or >=3.3
  * __init__.py allow the import of on optional reportlab.local_rl_mods to allow monkey patching etc.
  * rl_config now imports rl_settings & optionally local_rl_settings
  * ReportLab C extensions now live inside reportlab; _rl_accel is no longer required; All _rl_accel imports now 
	pass through reportlab.lib.rl_accel
  * xmllib is gone, alongside the paraparser stuff that caused issues in favour of HTMLParser.
  * some obsolete C extensions (sgmlop and pyHnj) are gone
  * Improved support for multi-threaded systems to the _rl_accel extension module.
  * Removed reportlab/lib/ para.py & pycanvas.py;  these would better belong in third party packages, 
	which can make use of the monkeypatching feature above.


### New features
  * Add ability to output greyscale and 1-bit PIL images without conversion to RGB. (contributed by Matthew Duggan)
  * highlight annotation (contributed by Ben Echols)

### Other
  * numerous very minor fixes, visible through BitBucket.


RELEASE 2.7  04/04/2013
-----------------------

#### Charts / graphics enhancements
  * Added SimpleTimeSeriesPlot
  * added _computeMaxSpace
  * added in lineStyle (for bars)
  * improved SVG rendering
  * Pie Chart now has an `innerRadiusFraction` to allow doughnut-like appearance for 2d charts	(it has no effect with 3d charts). 
	The separate 'doughnut' chart lacks many pie chart features and should only be used if you wanted multiple nested doughnuts. 

#### Charts/graphics bug fixes
  * piecharts.py: fix Pie3d __init__ to call its superclass
  * linecharts.py: fix swatch creation
  * fixed `y` axis in the simple time series plot

#### PDF
  * Fixes to testshapes & pdfform resetting
  * colors.py
  * various minor fixes

#### Platypus
  * Defined a small bullet rather than a big circle as the default for unordered lists
  * fixed attribute spelling bug
  * fixed CJK + endDots

### Acknowledgements
  Many thanks to Andrew Cutler, Dinu Gherman, Matthias Kirst and Stephan Richter for their contributions to this release.


RELEASE 2.6  27/09/2012
-----------------------

This is a minor release focusing mainly on improved documentation.	There are a 
number of minor enhancements, and a larger number of previous-undocumented
enhancements which we have documented better.

#### General changes
   * Manuals have been reformatted with more pleasing code snippets and tables of 
	 contents, and reviewed and expanded

#### Flowing documents (Platypus)
   * Added support for HTML-style list objects
   * Added flexible mechanism for drawing bullets
   * Allowed XPreformatted objects to use Asian line wrapping
   * Added an `autoNextPageTemplate` attribute to PageTemplates.  For example you 
	 can now set up a 'chapter first page template' which will always be followed
	 by a 'continuation template' on the next page break, saving the programmer from
	 having to issue control flow commands in the story.
   * added a TopPadder flowable, which will 'wrap' another Flowable and move it 
	 to the bottom of the current page.  
   * More helpful error messages when large tables cannot be rendered
   * Documentation for images within text (`test_032_images`)
   * Trailing dots for use on contents pages

#### Charts and graphics
   * Support for UPCA bar codes
   * We now have a semi-intelligent system for labelling pie charts with 
	 callout lines.  Thanks to James Martin-Collar, a maths student at Warwick 
	 University, who did this as his summer internship.
   * Axes - added startOffset and endOffset properties; allowed for axis 
	 background annotations.
   * Bar charts - allow more control of z Index (i.e. drawing order of axes and
	 lines)
   * Pie charts - fixed bugs in 3d appearance
   * SVG output back end has seen some bugs fixed and now outputs resizeable SVG
   
### Contributors
   * Alex Buck
   * Felix Labrecque <felixl@densi.com>
   * Peter Johnson <johnson.peter@gmail.com>
   * James Martin-Collar
   * Guillaume Francois
   

RELEASE 2.5  at 18:00 GMT  01/Oct/2010
--------------------------------------

Many new features have been added and numerous bugs have been fixed.

Thanks to everybody who has contributed to the open-source toolkit in
the run-up to the 2.5 release, whether by reporting bugs, sending patches,
or contributing to the reportlab-users mailing list.
Major contributors are credited in the user documentation.

   * Support for colour separated PDF output and other optimisations and
	 features for high-quality printing, including enforcement of colour
	 models for CMYK, RGB, and "spot colours"
   * Long table optimisations are now turned on by default.  Previously,
	 documents with very long tables spanning many pages could take a long
	 time to create because we considered the whole table to work out row
	 and column sizes.	A patch was submitted some time ago to fix this
	 controlled by a flag in the rl_config file, but this was set 'off'
	 for compatibility.  Users are often not aware of this and we haven't
	 found any real-world cases where the new layout technique works badly,
	 so we are turning this behaviour on.
   * New support for QR barcodes - [try our demo!](https://www.reportlab.com/demos/qr/)

#### PDF
   * Colour separation and other enhancements for high-end print
   * Python 2.7 support

#### Charts
   * reportlab.graphics.charts.axes
	   * ValueAxis
		   * avoidBoundSpace - Space to allow above and below
		   * abf_ignore_zero - Set to True to make the avoidBoundFrac calculations treat zero as non-special
		   * keepTickLabelsInside - Ensure tick labels do not project beyond bounds of axis if true
	   * NormalDateXValueAxis
		   * specialTickClear - clear rather than delete close ticks when forced first/end dates
	   * AdjYValueAxis
		   * labelVOffset - add this to the labels
   * reportlab.graphics.charts.barcharts
	   * BarChart
		   * categoryLabelBarSize - width to leave for a category label to go between categories
		   * categoryLabelBarOrder - where any label bar should appear first/last
		   * barRecord (advanced) - callable(bar,label=labelText,value=value,**kwds) to record bar information
   * reportlab.graphics.charts.legends
	   * SubColProperty
		   * dx - x offset from default position
		   * dy - y offset from default position
	   * Legend
		   * swdx - x position adjustment for the swatch
		   * swdy - y position adjustment for the swatch
   * reportlab.graphics.charts.piecharts
	   * Pie
		   * wedgeRecord (advanced) - callable(wedge,*args,**kwds)

   * reportlab.graphics.charts.utils
	   * DrawTimeCollector - generic mechanism for collecting information about nodes at the time they are about to be drawn


RELEASE 2.4  at 18:00 GMT  20/Jan/2010
--------------------------------------

#### PDF
   * lots of improvements and verbosity to error messages and the way they are handled.
   * font size can now be specified in pixels
   * unicode file names are now accepted

#### Platypus
   * canvas auto cropmarks
   * added support for styles h4-h6
   * Improved support for onDraw and SimpleIndex
   * Add support for index tableStyle
   * Added an alphabetic grouping indexing class
   * Added support for multi-level and alphabetical indexes
   * Added support for an unlimited number of TOC levels with default styles
   * Index entries can now be clickable.

#### Graphics
   * Axes values can be reversible.
   * Labels on the axes can now be drawn above or below the axes (hi or low).
   * A per swatch callout is now allowed in the legend.
   * A new anchroing mode for string 'numeric' that align numerical strings by their decimal place.
   * Shapes have new attributes to specify if the shape should grow to take all canvas area (vertically or horizontally) or if the canvas should shrink to fit the shape size.
   * color objects now have a clone method.
   * colors module has a fade function that returns a list of different shades made up of one base colour.
   * added in support for Overprint/Opacity & Separated colours

#### Bugs fixes
   * word counting in complex paragraphs has been fixed.
   * SimpleIndex and TableOfContents bugs have been fixed.
   * Fix for position of hyperlinks when crop marks are added.
   * flowables.py: fix special case of doctemplate with no frames
   * PDFFormXObject.format missing Resources bug patch from Scott Meyer
   * KeepInFrame justification bug has been fixed.
   * paragraph.py: fix linebreaking bug thanks to Roberto Alsina
   * fix unicode/str issue bug found by Michael Egorov <michwill@gmail.com>
   * YCategoryAxis makeTickLabels fix contributed by Mike Folwell <mjf@pearson.co.uk>
   * pdfdoc.py: fix ro PDFDate contributed by Robert Alsina
   * and others ..

### Contributors
   * PJACock's (<peter@maubp.freeserve.co.uk>)
   * Hans Brand
   * Ian Stevens
   * Yoann Roman <yroman-reportlab@altalang.com>
   * Randolph Bentson
   * Volker Haas
   * Simon King
   * Henning Vonbargen
   * Michael Egorov <michwill@gmail.com>
   * Mike Folwell <mjf@pearson.co.uk>
   * Robert Alsina
   * and more ...


RELEASE 2.3  at 18:00 GMT  04/Feb/2009
--------------------------------------

#### PDF
   * Encryption support (see encrypt parameter on Canvas and BaseDocTemplate constructor)

#### Platypus
   * TableOfContents - Creates clickable tables of contents
   * Variable border padding for paragraphs (using the borderPadding style attribute)
   * New programming Flowable, docAssert, used to assert expressions on wrap time.

#### Bug fixes
   * Fixed old documentation and installation issues
   * 610 - Fixed Image anchoring code to match documentation
   * 704 - renderSVG groups problem
   * 706 - rl_codecs.py now compatible with WordAxe
   * and others...

### Contributors 
   * Yoann Roman
   * Dinu Gherman
   * Dirk Holtwick
   * Marcel Tromp
   * Henning von Bargen
   * Paul Barrass
   * Adrian Klaver
   * Hans Brand
   * Ian Stevens


RELEASE 2.2  at 18:00 GMT  10/Sep/2008
--------------------------------------

#### PDF
   * pdfmetrics: Added registerFontFamily function
   * Basic support for pdf document viewer preferences (e.g.: fullscreen).

#### Platypus
   * Paragraph <img> tag support for inline images.
   * Paragraph autoleading support (helps with <img> tags).
   * Platypus doctemplate programming support.
   * Support for tables with non-uniform row length.

#### Graphics
   * RGBA image support for suitable bitmap types.
   * LTO labelling barcode.

And many bugfixes...

### Contributors 
   * Matt Folwell
   * Jerome Alet
   * Harald Armin Massa
   * kevin@booksys.com
   * Sebastian Ware
   * Martin Tate
   * Wietse Jacobs
   * Christian Jacobs
   * Volker Haas
   * Dinu Gherman
   * Dirk Datzert
   * Yuan Hong
   * Ilpo Nyyss�nen
   * Thomas Heller
   * Gael Chardon
   * Alex Smishlajev
   * Martin Loewis
   * Dirk Holtwick
   * Philippe Makowskic
   * Ian Sparks
   * Albertas Agejevas
   * Gary Poster
   * Martin Zohlhuber
   * Francesco Pierfederici
   * michael@stroeder.com
   * Derik Barclay
   * Publio da Costa Melo 
   * Jon Dyte
   * David Horkoff
   * picodello@yahoo.it
   * R�diger M�hl
   * Paul Winkler
   * Bernhard Herzog
   * Alex Martelli
   * Stuart Bishop
   * Gael Chardon


RELEASE 2.1  at 15:00 GMT  24/May/2007
--------------------------------------

### Contributors 
   * Ilpo Nyyss�nen
   * Thomas Heller
   * Gael Chardon
   * Alex Smishlajev
   * Martin Loewis		 
   * Dirk Holtwick
   * Philippe Makowskic
   * Dinu Gherman
   * Ian Sparks
 

RELEASE 2.0  at 15:00 GMT  23/May/2006
--------------------------------------

### Contributions
   * Andre Reitz
   * Max M
   * Albertas Agejevas
   * T Blatter
   * Ron Peleg
   * Gary Poster
   * Steve Halasz
   * Andrew Mercer
   * Paul McNett
   * Chad Miller

### Unicode support

This is the Big One, and the reason some apps may break. You must now pass in 
text either in UTF-8 or as unicode string objects. The library will handle 
everything to do with output encoding. There is more information on this below.

Since this is the biggest change, we'll start by reviewing how it worked in the 
past. In ReportLab 1.x, any string input you passed to our APIs was supposed to 
be in the same encoding as the font you selected for output. If using the 
default fonts in Acrobat Reader (Helvetica/Times/Courier), you would have 
implicitly used WinAnsi encoding, which is almost exactly the same as Latin-1. 
However, if using TrueType fonts, you would have been using UTF-8. For Asian 
fonts, you had a wide choice of encodings but had to specify which one (e.g 
Shift-JIS or EUC for Japanese). This state of affairs meant that you had to 
make sure that every piece of text input was in the same encoding as the font 
used to display it.

With ReportLab 2, none of that necessary. Instead:

Here is what's different now:

#### Input text encoding is UTF-8 or Python Unicode strings

  Any text you pass to a canvas API (drawString etc.), Paragraph or other 
  flowable constructor, into a table cell, or as an attribute of a graphic (e.g. 
  chart.title.text), is supposed to be unicode. If you use a traditional Python 
  string, it is assumed to be UTF-8. If you pass a Unicode object, we know it's 
  unicode. 

#### Font encodings

  Fonts still work in different ways, and the built-in ones will still use 
  WinAnsi or MacRoman internally while TrueType will use UTF-8. However, the 
  library hides this from you; it converts as it writes out the PDF file. As 
  before, it's still your job to make sure the font you use has the characters 
  you need, or you may get either a traceback or a visible error character. 
  Asian CID fonts

  You no longer need to specify the encoding for the built-in Asian fonts, 
  just the face name. ReportLab knows about the standard fonts in Adobe's Asian 
  Language Packs. 

#### Asian Truetype fonts

  The standard Truetype fonts differ slightly for Asian languages (e.g 
  msmincho.ttc). These can now be read and used, albeit somewhat inefficiently. 
  Asian word wrapping

  Previously we could display strings in Asian languages, but could not 
  properly wrap paragraphs as there are no gaps between the words. We now have a 
  basic word wrapping algorithm.

#### unichar tag

  A convenience tag, <unichar/> has also been added. You can now do <unichar 
  code="0xfc"/> or <unichar name='LATIN SMALL LETTER U WITH DIAERESIS'/> and get 
  a lowercase u umlaut. Names should be those in the Unicode Character Database.
  Accents, Greeks and symbols

  The correct way to refer to all non-ASCII characters is to use their 
  unicode representation. This can be literal Unicode or UTF-8. Special symbols 
  and Greek letters (collectively, "greeks") inserted in paragraphs using the 
  greek tag (e.g. <greek>lambda</greek>) or using the entity references (e.g. 
  &lambda;) are now processed in a different way than in version 1. Previously, 
  these were always rendered using the Zapf Dingbats font. Now they are always 
  output in the font you specified, unless that font does not support that 
  character. If the font does not support the character, and the font you 
  specified was an Adobe Type 1 font, Zapf Dingbats is used as a fallback. 
  However, at present there is no fallback in the case of TTF fonts. Note that 
  this means that documents that contain greeks and specify a TTF font may need 
  changing to explicitly specify the font to use for the greek character, or you 
  will see a black square in place of that character when you view your PDF 
  output in Acrobat Reader.

### Other New Features

#### PDF

  * Improved low-level annotation support for PDF "free text annotations"
	FreeTextAnnotation allows showing and hiding of an arbitrary PDF "form" 
	(reusable chunk of PDF content) depending on whether the document is printed or 
	viewed on-screen, or depending on whether the mouse is hovered over the 
	content, etc.
  * TTC font collection files are now readable:
	ReportLab now supports using TTF fonts packaged in .TTC files
  * East Asian font support (CID and TTF):
	You no longer need to specify the encoding for the built-in Asian 
	fonts, just the face name. ReportLab knows about the standard fonts in Adobe's 
	Asian Language Packs. 
  * Native support for JPEG CMYK images:
	ReportLab now takes advantage of PDF's native JPEG CMYK image support, 
	so that JPEG CMYK images are no longer (lossily) converted to RGB format before 
	including them in PDF. 

#### Platypus

  * Link support in paragraphs:
	Platypus paragraphs can now contain link elements, which support both 
	internal links to the same PDF document, links to other local PDF documents, 
	and URL links to pages on the web. Some examples:

	Web links::

		<link href="http://www.reportlab.com/">ReportLab<link>

	Internal link to current PDF document::

		<link href="summary">ReportLab<link>

	External link to a PDF document on the local filesystem::

		<link href="pdf:c:/john/report.pdf">ReportLab<link>

  * Improved wrapping support:
	Support for wrapping arbitrary sequence of flowables around an image, 
	using reportlab.platypus.flowables.ImageAndFlowables (similar to 
	ParagraphAndImage).
  * `KeepInFrame`:
	Sometimes the length of a piece of text you'd like to include in a 
	fixed piece of page "real estate" is not guaranteed to be constrained to a 
	fixed maximum length. In these cases, KeepInFrame allows you to specify an 
	appropriate action to take when the text is too long for the space allocated 
	for it. In particular, it can shrink the text to fit, mask (truncate) 
	overflowing text, allow the text to overflow into the rest of the document, or 
	raise an error.
  * Improved convenience features for inserting unicode symbols and other 
  characters:
	`<unichar/>` lets you conveniently insert unicode characters using the 
	standard long name or code point. Characters inserted with the `<greek>` tags 
	(e.g. `<greek>lambda</greek>`) or corresponding entity references (e.g. &lambda;) 
	support arbitrary fonts (rather than only Zapf Dingbats).
  * Table spans and splitting improved:
	Cell spanning in tables used to go wrong sometimes when the table split 
	over a page. We believe this is improved, although there are so many table 
	features that it's hard to define correct behaviour in all cases.
  * `KeepWithNext` improved:
	Paragraph styles have long had an attribute keepWithNext, but this was 
	buggy when set to True. We believe this is fixed now. keepWithNext is important 
	for widows and orphans control; you typically set it to True on headings, to 
	ensure at least one paragraph appears after the heading and that you don't get 
	headings alone at the bottom of a column. 

#### Graphics
  * Barcodes:
	The barcode package has been added to the standard reportlab 
	toolkit distribution (it used to live separately in our contributions area). It 
	has also seen fairly extensive reworking for production use in a recent 
	project. These changes include adding support for the standard European EAN 
	barcodes (EAN 8 and EAN13).
  * Improvements to Legending:
	Instead of manual placement, there is now a attachment point (N, 
	S, E, W, etc.), so that the legend is always automatically positioned correctly 
	relative to the chart. Swatches (the small sample squares of colour / pattern 
	fill sometimes displayed in the legend) can now be automatically created from 
	the graph data. Legends can now have automatically-computed totals (useful for 
	financial applications).
  * More and better ways to place piechart labels:
	New smart algorithms for automatic pie chart label positioning 
	have been added. You can now produce nice-looking labels without manual 
	positioning even for awkward cases in big runs of charts.
  * Adjustable piechart slice ordering:
	For example. pie charts with lots of small slices can be 
	configured to alternate thin and thick slices to help the label placement 
	algorithm work better.
  * Improved spiderplots

#### Noteworthy bug fixes
  * Fixes to TTF splitting (patch from Albertas Agejevas):
	This affected some documents using font subsetting
  * Tables with spans improved splitting:
	Splitting of tables across pages did not work correctly when the table had
	row/column spans
  * Fix runtime error affecting keepWithNext


Older releases
--------------

Please refer to subversion backlogs for a low level change list

	RELEASE 1.20 at 18:00 GMT  25/Nov/2004
	RELEASE 1.19 at 18:00 GMT  21/Jan/2004
	RELEASE 1.18 at 12:00 GMT  9/Jul/2003
	RELEASE 1.17 at 16:00 GMT  3/Jan/2003
	RELEASE 1.16 at 16:00 GMT  7/Nov/2002
	RELEASE 1.15 at 14:00 GMT  9/Aug/2002
	RELEASE 1.14 at 18:00 GMT 28/May/2002
	RELEASE 1.13 at 15:00 GMT 27/March/2002
	RELEASE 1.12 at 17:00 GMT 28/February/2002
	RELEASE 1.11 at 14:00 GMT 12/December/2001
	RELEASE 1.10 at 14:00 GMT 06/November/2001
	RELEASE 1.09 at 14:00 BST 13/August/2001
	RELEASE 1.08 at 12:00 BST 19/June/2001
	RELEASE 1.07 at 11:54 BST 2001/05/02
	RELEASE 1.06 at 14:00 BST 2001/03/30
	RELEASE 1.03 on 2001/02/09
	RELEASE 1.02 on 2000/12/11
	RELEASE 1.01 on 2000/10/10
	RELEASE 1.00 on 2000/07/20
	RELEASE 0.95 on 2000/07/14
	RELEASE 0.94 on 2000/06/20
