#Copyright ReportLab Europe Ltd. 2000-2004
#see license.txt for license details
#history http://www.reportlab.co.uk/cgi-bin/viewcvs.cgi/public/reportlab/trunk/reportlab/docs/userguide/ch2_graphics.py
from reportlab.tools.docco.rl_doc_utils import *
from reportlab.lib.codecharts import SingleByteEncodingChart
from reportlab.tools.docco.stylesheet import getStyleSheet
styles = getStyleSheet()
indent0_style = styles['Indent0']
indent1_style = styles['Indent1']


heading1("What's New in ReportLab 2.0")
heading4("Version 2.0 of the ReportLab open-source toolkit is out!")

heading2("Reportlab version 2.0 ")
disc("""
Many new features have been added, foremost amongst which is the support
for unicode. This page documents what has changed since version 1.20.""")

disc("""
Adding full unicode support meant that we had to break backwards-compatibility,
so old code written for ReportLab 1 will sometimes need changes before it will
run correctly with ReportLab 2. Now that we have made the clean break to
introduce this important new feature, we intend to keep the API
backwards-compatible throughout the 2.* series.
""")
heading2("Goals for the 2.x series")
disc("""
The main rationale for 2.0 was an incompatible change at the character level:
to properly support Unicode input. Now that it's out we will maintain compatibility
with 2.0. There are no pressing feature wishlists and new features will be driven,
as always, by contributions and the demands of projects.""")

disc("""
Our 1.x code base is still Python 2.1 compatible. The new version lets us move forwards
with a baseline of Python 2.4 (2.3 will work too, for the moment, but we don't promise
that going forwards) so we can use newer language features freely in our development.""")

disc("""
One area where we do want to make progress from release to release is with documentation
and installability. We'll be looking into better support for distutils, setuptools,
eggs and so on; and into better examples and tools to help people learn what's in the
(substantial) code base.""")

disc("""
Bigger ideas and more substantial rewrites are deferred to Version 3.0, with no particular
target dates.
""")

heading2("Contributions")
disc("""Thanks to everybody who has contributed to the open-source toolkit in the run-up
to the 2.0 release, whether by reporting bugs, sending patches, or contributing to the
reportlab-users mailing list. Thanks especially to the following people, who contributed
code that has gone into 2.0: Andre Reitz, Max M, Albertas Agejevas, T Blatter, Ron Peleg,
Gary Poster, Steve Halasz, Andrew Mercer, Paul McNett, Chad Miller.
""")
todo("""If we missed you, please let us know!""")

heading2("Unicode support")
disc("""
This is the Big One, and the reason some apps may break. You must now pass in text either
in UTF-8 or as unicode string objects. The library will handle everything to do with output
encoding. There is more information on this below.
Since this is the biggest change, we'll start by reviewing how it worked in the past.""")

disc("""
In ReportLab 1.x, any string input you passed to our APIs was supposed to be in the same
encoding as the font you selected for output. If using the default fonts in Acrobat Reader
(Helvetica/Times/Courier), you would have implicitly used WinAnsi encoding, which is almost
exactly the same as Latin-1. However, if using TrueType fonts, you would have been using UTF-8.""")

disc("""For Asian fonts, you had a wide choice of encodings but had to specify which one
(e.g Shift-JIS or EUC for Japanese). This state of affairs meant that you had
to make sure that every piece of text input was in the same encoding as the font used
to display it.""")



disc("""Input text encoding is UTF-8 or Python Unicode strings""")
disc("""
Any text you pass to a canvas API (drawString etc.), Paragraph or other flowable
constructor, into a table cell, or as an attribute of a graphic (e.g. chart.title.text),
is supposed to be unicode. If you use a traditional Python string, it is assumed to be UTF-8.
If you pass a Unicode object, we know it's unicode.""", style=indent1_style)

disc("""Font encodings""")
disc("""
Fonts still work in different ways, and the built-in ones will still use WinAnsi or MacRoman
internally while TrueType will use UTF-8. However, the library hides this from you; it converts
as it writes out the PDF file. As before, it's still your job to make sure the font you use has
the characters you need, or you may get either a traceback or a visible error character.""",style=indent1_style)

disc("""Asian CID fonts""")
disc("""
You no longer need to specify the encoding for the built-in Asian fonts, just the face name.
ReportLab knows about the standard fonts in Adobe's Asian Language Packs
""", style=indent1_style)

disc("""Asian Truetype fonts""")
disc("""
The standard Truetype fonts differ slightly for Asian languages (e.g msmincho.ttc).
These can now be read and used, albeit somewhat inefficiently. 
""", style=indent1_style)

disc("""Asian word wrapping""")
disc("""
Previously we could display strings in Asian languages, but could not properly
wrap paragraphs as there are no gaps between the words. We now have a basic word wrapping
algorithm.
""", style=indent1_style)

disc("""unichar tag""")
disc("""
A convenience tag, &lt;unichar/&gt; has also been added. You can now do <unichar code="0xfc"/>
or &lt;unichar name='LATIN SMALL LETTER U WITH DIAERESIS'/&gt; and
get a lowercase u umlaut. Names should be those in the Unicode Character Database.
""", style=indent1_style)

disc("""Accents, greeks and symbols""")
disc("""
The correct way to refer to all non-ASCII characters is to use their unicode representation.
This can be literal Unicode or UTF-8. Special symbols and Greek letters (collectively, "greeks")
inserted in paragraphs using the greek tag (e.g. &lt;greek&gt;lambda&lt;/greek&gt;) or using the entity
references (e.g. &lambda;) are now processed in a different way than in version 1.""", style=indent1_style)
disc("""
Previously, these were always rendered using the Zapf Dingbats font. Now they are always output
in the font you specified, unless that font does not support that character. If the font does
not support the character, and the font you specified was an Adobe Type 1 font, Zapf Dingbats
is used as a fallback. However, at present there is no fallback in the case of TTF fonts.
Note that this means that documents that contain greeks and specify a TTF font may need
changing to explicitly specify the font to use for the greek character, or you will see a black
square in place of that character when you view your PDF output in Acrobat Reader.
""", style=indent1_style)

# Other New Features Section #######################
heading2("Other New Features")
disc("""PDF""")
disc("""Improved low-level annotation support for PDF "free text annotations"
""", style=indent0_style)
disc("""FreeTextAnnotation allows showing and hiding of an arbitrary PDF "form"
(reusable chunk of PDF content) depending on whether the document is printed or
viewed on-screen, or depending on whether the mouse is hovered over the content, etc.
""", style=indent1_style)

disc("""TTC font collection files are now readable"
""", style=indent0_style)
disc("""ReportLab now supports using TTF fonts packaged in .TTC files""", style=indent1_style)

disc("""East Asian font support (CID and TTF)""", style=indent0_style)
disc("""You no longer need to specify the encoding for the built-in Asian fonts,
just the face name. ReportLab knows about the standard fonts in Adobe's Asian Language Packs.
""", style=indent1_style)

disc("""Native support for JPEG CMYK images""", style=indent0_style)
disc("""ReportLab now takes advantage of PDF's native JPEG CMYK image support,
so that JPEG CMYK images are no longer (lossily) converted to RGB format before including
them in PDF.""", style=indent1_style)


disc("""Platypus""")
disc("""Link support in paragraphs""", style=indent0_style)
disc("""
Platypus paragraphs can now contain link elements, which support both internal links
to the same PDF document, links to other local PDF documents, and URL links to pages on
the web. Some examples:""", style=indent1_style) 
disc("""Web links:""", style=indent1_style)
disc("""&lt;link href="http://www.reportlab.com/"&gt;ReportLab&lt;link&gt;""", style=styles['Link'])

disc("""Internal link to current PDF document:""", style=indent1_style)
disc("""&lt;link href="summary"&gt;ReportLab&lt;link&gt;""", style=styles['Link'])

disc("""External link to a PDF document on the local filesystem:""", style=indent1_style)
disc("""&lt;link href="pdf:C:/john/report.pdf"&gt;ReportLab&lt;link&gt;""", style=styles['Link'])

disc("""Improved wrapping support""", style=indent0_style)
disc("""Support for wrapping arbitrary sequence of flowables around an image, using
reportlab.platypus.flowables.ImageAndFlowables (similar to ParagraphAndImage)."""
,style=indent1_style)

disc("""KeepInFrame""", style=indent0_style)
disc("""Sometimes the length of a piece of text you'd like to include in a fixed piece
of page "real estate" is not guaranteed to be constrained to a fixed maximum length.
In these cases, KeepInFrame allows you to specify an appropriate action to take when
the text is too long for the space allocated for it. In particular, it can shrink the text
to fit, mask (truncate) overflowing text, allow the text to overflow into the rest of the document,
or raise an error.""",style=indent1_style)


disc("""Improved convenience features for inserting unicode symbols and other characters
""", style=indent0_style)
disc("""<unichar/> lets you conveniently insert unicode characters using the standard long name
or code point. Characters inserted with the &lt;greek&gt; tags (e.g. <greek>lambda</greek>) or corresponding
entity references (e.g. &lambda;) support arbitrary fonts (rather than only Zapf Dingbats).""",style=indent1_style)

disc("""Improvements to Legending""", style=indent0_style)
disc("""Instead of manual placement, there is now a attachment point (N, S, E, W, etc.), so that
the legend is always automatically positioned correctly relative to the chart. Swatches (the small
sample squares of colour / pattern fill sometimes displayed in the legend) can now be automatically
created from the graph data. Legends can now have automatically-computed totals (useful for
financial applications).""",style=indent1_style)

disc("""More and better ways to place piechart labels""", style=indent0_style)
disc("""New smart algorithms for automatic pie chart label positioning have been added.
You can now produce nice-looking labels without manual positioning even for awkward cases in
big runs of charts.""",style=indent1_style)

disc("""Adjustable piechart slice ordering""", style=indent0_style)
disc("""For example. pie charts with lots of small slices can be configured to alternate thin and
thick slices to help the lagel placememt algorithm work better.""",style=indent1_style)
disc("""Improved spiderplots""", style=indent0_style)


# Noteworthy bug fixes Section #######################
heading2("Noteworthy bug fixes")
disc("""Fixes to TTF splitting (patch from Albertas Agejevas)""")
disc("""This affected some documents using font subsetting""", style=indent0_style)

disc("""Tables with spans improved splitting""")
disc("""Splitting of tables across pages did not work correctly when the table had
row/column spans""", style=indent0_style)

disc("""Fix runtime error affecting keepWithNext""")

##### FILL THEM IN
