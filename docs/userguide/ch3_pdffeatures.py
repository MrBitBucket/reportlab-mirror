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
    to another.  The bookmark methods define a destination that is the endpoint
    of a jump.""")
#todo("code example here...")

eg("""
 canvas.bookmarkPage(name)
 canvas.bookmarkHorizontalAbsolute(name, yhorizontal)""")
 
disc("""
    The $bookmarkPage$ method bookmarks the entire page.
    After jumping to an endpoint defined by $bookmarkPage$ the
    PDF browser will display the whole page on the screen.""")
    
disc("""
    By contrast, $bookmarkHorizontalAbsolute$ defines a destination
    associated with a horizontal position on a page.  When the PDF browser
    jumps to a destination defined by $bookmarkHorizontalAbsolute$ the
    screen will show a part of the page with the horizontal line at
    ^y=$yhorizontal$^ near the top, omitting parts of the rest of the page
    if appropriate.
""")

pencilnote()

disc("""
<i>Note:</i> The horizontal position $yhorizontal$ must be specified in terms
of the <i>default user space</i>.  In particular $bookmarkHorizontalAbsolute$
ignores any modified geometric transform in effect in the canvas graphics state.
""")

eg("""
 canvas.linkAbsolute(contents, destinationname, Rect=None, addtopage=1, name=None, **kw)
 """)
 
disc("""
    The $linkAbsolute$ method defines a starting point for a jump.  When the user
    is browsing the generated document using a dynamic viewer (such as Acrobat Reader)
    when the mouse is clicked when the pointer is within the rectangle specified
    by $Rect$ the viewer will jump to the endpoint associated with $destinationname$.
    As in the case with $bookmarkHorizontalAbsolute$ the rectangle $Rect$ must be
    specified in terms of the default user space.  The $contents$ parameter specifies
    a chunk of text which displays in the viewer if the user left-clicks on the region.
""")

disc("""
The rectangle $Rect$ must be specified in terms of a tuple ^(x1,y1,x2,y2)^ identifying
the lower left and upper right points of the rectangle in default user space.
""")

disc("""
For example the code
""")

eg("""
    canvas.bookmarkHorizontalAbsolute("Meaning_of_life", 5*inch)
""")

disc("""
defines horizontal location on the currently drawn page with the identifier
$Meaning_of_life$.  And the invocation
""")

eg("""
 canvas.linkAbsolute("Find the Meaning of Life", "Meaning_of_life", 
                     (inch, inch, 6*inch, 2*inch))
""")

disc("""
By default during interactive viewing a rectangle appears around the
link.
Use the keyword argument $Border='[0 0 0]'$ to
suppress the visible rectangle around the during viewing link.
For example
""")

eg("""
 canvas.linkAbsolute("Meaning of Life", "Meaning_of_life", 
                     (inch, inch, 6*inch, 2*inch), Border='[0 0 0]')
""")


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
                                            key, 0, 0)
    """)
    
heading2("Page Transition Effects")


eg("""
 canvas.setPageTransition(self, effectname=None, duration=1, 
                        direction=0,dimension='H',motion='I')
                        """)
                        
disc("""
The $setPageTransition$ method specifies how one page will be replaced with
the next.  By setting the page transition effect to "dissolve" for example
the current page will appear to melt away when it is replaced by the next
page during interactive viewing.  These effects are useful in spicing up
slide presentations, mong other places.
Please see the reference manual for more detail on how to use this method.
""")

heading2("Internal File Annotations")

eg("""
 canvas.setAuthor(name)
 canvas.setTitle(title)
 canvas.setSubject(subj)
 """)
 
disc("""
These methods have no automatically seen visible effect on the document.
They add internal annotations to the document.  These annotations can may be
viewed using the "Document Info" menu item of the browser and they also can
be used as a simple standard way of providing basic information about the
document to archiving software which need not parse the entire
file.  To find the annotations view the $*.pdf$ output file using a standard
text editor (such as $notepad$ on MS/Windows or $vi$ or $emacs$ on unix) and look
for the string $/Author$ in the file contents.
""")

eg(examples.testannotations)

disc("""
If you want the subject, title, and author to automatically display
in the document when viewed and printed you must paint them onto the
document like any other text.
""")

illust(examples.annotations, "Setting document internal annotations")
 