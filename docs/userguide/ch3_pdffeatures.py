#ch3_pdf_features


from genuserguide import *


heading1("Exposing PDF Special Capabilities")
disc("""PDF provides a number of features to make electronic
    document viewing more efficient and comfortable, and
    our library exposes a number of these.""")

heading2("Forms")
disc("""The Form feature lets you create a block of graphics and text
    once near the start of a PDF file, and then simply refer to it on
    subsequent pages.  If you are dealing with a run of 5000 repetitive
    business forms - for example, one-page invoices or payslips - you
    only need to store the backdrop once and simply draw the changing
    text on each page.  Used correctly, forms can dramatically cut
    file size and production time, and apparently even speed things
    up on the printer.
    """)
disc("""Forms do not need to refer to a whole page; anything which
    might be repeated often should be placed in a form.""")
disc("""The example below shows the basic sequence used.  A real
    program would probably define the forms up front and refer to
    them from another location.""")
    

eg(examples.testforms)

heading2("Links and Destinations")
disc("""PDF supports internal hyperlinks.  There is a very wide
    range of link types, destination types and events which
    can be triggered by a click.  At the moment we just
    support the basic ability to jump from one part of a document
    to another.  """)
todo("code example here...")

heading2("Outline Trees")
disc("""Acrobat Reader has a navigation page which can hold a
    document outline; it should normally be visible when you
    open this guide.  We provide some simple methods to add
    outline entries.  Typically, a program to make a document
    (such as this user guide) will call the method
    $canvas.addOutlineEntry(^self, title, key, level=0,
    closed=None^)$ as it reaches each heading in the document.
    """)

disc("""^title^ is the caption which will be displayed in
    the left pane.  The ^key^ must be a string which is
    unique within the document and which names a bookmark,
    as with the hyperlinks.  The ^level^ is zero - the
    uppermost level - unless otherwise specified, and
    it is an error to go down more than one level at a time
    (for example to follow a level 0 heading by a level 2
     heading).  Finally, the ^closed^ argument specifies
    whether the node in the outline pane is closed
    or opened by default.""")
    
disc("""The snippet below is taken from the document template
    that formats this user guide.  A central processor looks
    at each paragraph in turn, and makes a new outline entry
    when a new chapter occurs, taking the chapter heading text
    as the caption text.  The key is obtained from the
    chapter number (not shown here), so Chapter 2 has the
    key 'ch2'.  The bookmark to which the
    outline entry points aims at the whole page, but it could
    as easily have been an individual paragraph.
    """)
    
eg("""
#abridged code from our document template
if paragraph.style == 'Heading1':
    self.chapter = paragraph.getPlainText()
    key = 'ch%d' % self.chapterNo
    self.canv.bookmarkPage(key)
    self.canv.addOutlineEntry(paragraph.getPlainText(),
    """)
    
heading2("Page Transition Effects")


