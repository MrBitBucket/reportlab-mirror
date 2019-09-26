#Copyright ReportLab Europe Ltd. 2000-2017
#see license.txt for license details
#history https://hg.reportlab.com/hg-public/reportlab/log/tip/docs/userguide/ch3_pdffeatures.py
from tools.docco.rl_doc_utils import *

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
    to another, and to control the zoom level of the window after
    the jump.  The bookmarkPage method defines a destination that
    is the endpoint of a jump.""")
#todo("code example here...")

eg("""
    canvas.bookmarkPage(name,
                        fit="Fit",
                        left=None,
                        top=None,
                        bottom=None,
                        right=None,
                        zoom=None
                        )
""")
disc("""
By default the $bookmarkPage$ method defines the page itself as the
destination. After jumping to an endpoint defined by bookmarkPage,
the PDF browser will display the whole page, scaling it to fit the
screen:""")

eg("""canvas.bookmarkPage(name)""")

disc("""The $bookmarkPage$ method can be instructed to display the
page in a number of different ways by providing a $fit$
parameter.""")

eg("")

t = Table([
           ['fit','Parameters Required','Meaning'],
           ['Fit',None,'Entire page fits in window (the default)'],
           ['FitH','top','Top coord at top of window, width scaled to fit'],
           ['FitV','left','Left coord at left of window, height scaled to fit'],
           ['FitR','left bottom right top','Scale window to fit the specified rectangle'],
           ['XYZ','left top zoom','Fine grained control. If you omit a parameter\nthe PDF browser interprets it as "leave as is"']
          ])
t.setStyle(TableStyle([
            ('FONT',(0,0),(-1,1),'Times-Bold',10,12),
            ('VALIGN',(0,0),(-1,-1),'MIDDLE'),
            ('INNERGRID', (0,0), (-1,-1), 0.25, colors.black),
            ('BOX', (0,0), (-1,-1), 0.25, colors.black),
            ]))

getStory().append(t)
caption("""Table <seq template="%(Chapter)s-%(Table+)s"/> - Required attributes for different fit types""")

disc("""
Note : $fit$ settings are case-sensitive so $fit="FIT"$ is invalid
""")


disc("""
Sometimes you want the destination of a jump to be some part of a page.
The $FitR$ fit allows you to identify a particular rectangle, scaling
the area to fit the entire page.
""")

disc("""
To set the display to a particular x and y coordinate of the page and to
control the zoom directly use fit="XYZ".
""")

eg("""
canvas.bookmarkPage('my_bookmark',fit="XYZ",left=0,top=200)
""")



disc("""
This destination is at the leftmost of the page with the top of the screen
at position 200. Because $zoom$ was not set the zoom remains at whatever the
user had it set to.
""")

eg("""
canvas.bookmarkPage('my_bookmark',fit="XYZ",left=0,top=200,zoom=2)
""")

disc("""This time zoom is set to expand the page 2X its normal size.""")

disc("""
Note  : Both $XYZ$ and $FitR$ fit types require that their positional parameters
($top, bottom, left, right$) be specified in terms of the default user space.
They ignore any geometric transform in effect in the canvas graphic state.
""")



pencilnote()

disc("""
<i>Note:</i> Two previous bookmark methods are supported but deprecated now
that bookmarkPage is so general.  These are $bookmarkHorizontalAbsolute$
and $bookmarkHorizontal$.
""")

heading3("Defining internal links")
eg("""
 canvas.linkAbsolute(contents, destinationname, Rect=None, addtopage=1, name=None, 
 thickness=0, color=None, dashArray=None, **kw)
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
    canvas.bookmarkPage("Meaning_of_life")
""")

disc("""
defines a location as the whole of the current page with the identifier
$Meaning_of_life$.  To create a rectangular link to it while drawing a possibly
different page, we would use this code:
""")

eg("""
 canvas.linkAbsolute("Find the Meaning of Life", "Meaning_of_life",
                     (inch, inch, 6*inch, 2*inch))
""")

disc("""
By default during interactive viewing a rectangle appears around the
link. Use the keyword argument $Border='[0 0 0]'$ to
suppress the visible rectangle around the during viewing link.
For example
""")

eg("""
 canvas.linkAbsolute("Meaning of Life", "Meaning_of_life",
                     (inch, inch, 6*inch, 2*inch), Border='[0 0 0]')
""")

disc("""The $thickness$, $color$ and $dashArray$ arguments may be used alternately
to specify a border if no Border argument is specified.
If Border is specified it must be either a string representation of a PDF
array or a $PDFArray$ (see the pdfdoc module). The $color$ argument (which should be a $Color$ instance) is equivalent to a keyword argument $C$ which should resolve to a PDF color definition (Normally a three entry PDF array).
""")
disc("""The $canvas.linkRect$ method is similar in intent to the $linkAbsolute$ method, but has an extra argument $relative=1$ so is intended to obey the local userspace transformation.""")

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
slide presentations, among other places.
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
They add internal annotations to the document.  These annotations can be
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

heading2("Encryption")

heading3("About encrypting PDF files")

disc("""
Adobe's PDF standard allows you to do three related things to a PDF file when you encrypt it:
""")
bullet("""Apply password protection to it, so a user must supply a valid password before being able to read it,
""")
bullet("""Encrypt the contents of the file to make it useless until it is decrypted, and
""")
bullet("""Control whether the user can print, copy and paste or modify the document while viewing it.
""")

disc("""
The PDF security handler allows two different passwords to be specified for a document:
""")

bullet("""The 'owner' password (aka the 'security password' or 'master password')
""")

bullet("""The 'user' password (aka the 'open password')
""")

disc("""
When a user supplies either one of these passwords, the PDF file will be opened, decrypted and displayed on
screen.
""")

disc("""
If the owner password is supplied, then the file is opened with full control - you can do anything to it,
including changing the security settings and passwords, or re-encrypting it with a new password.
""")

disc("""
     If the user password was the one that was supplied, you open it up in a more restricted mode. The restrictions were put in
place when the file was encrypted, and will either allow or deny the user permission to do the following:
""")

bullet("""
Modifying the document's contents
""")

bullet("""
Copying text and graphics from the document
""")

bullet("""
Adding or modifying text annotations and interactive form fields
""")

bullet("""
Printing the document
""")

disc("""
Note that all password protected PDF files are encrypted, but not all encrypted PDFs are password protected. If
a document's user password is an empty string, there will be no prompt for the password when the file is
opened. If you only secure a document with the owner password, there will also not be a prompt for the
password when you open the file. If the owner and user passwords are set to the same string when encrypting
the PDF file, the document will always open with the user access privileges. This means that it is possible to
create a file which, for example, is impossible for anyone to print out, even the person who created it.
""")

t = Table([
           ['Owner Password \nset?','User Password \nset?','Result'],
           ['Y','-','No password required when opening file. \nRestrictions apply to everyone.'],
           ['-','Y','User password required when opening file. \nRestrictions apply to everyone.'],
           ['Y','Y','A password required when opening file. \nRestrictions apply only if user password supplied.'],
          ],[90, 90, 260])

t.setStyle(TableStyle([
            ('FONT',(0,0),(-1,0),'Times-Bold',10,12),
            ('VALIGN',(0,0),(-1,-1),'MIDDLE'),
            ('INNERGRID', (0,0), (-1,-1), 0.25, colors.black),
            ('BOX', (0,0), (-1,-1), 0.25, colors.black),
            ]))

getStory().append(t)

disc("""
When a PDF file is encrypted, encryption is applied to all the strings and streams in the file. This prevents
people who don't have the password from simply removing the password from the PDF file to gain access to it - 
it renders the file useless unless you actually have the password.
""")
disc("""
PDF's standard encryption methods use the
MD5 message digest algorithm (as described in RFC 1321, The MD5 Message-Digest Algorithm) and an
encryption algorithm known as RC4. RC4 is a symmetric stream cipher - the same algorithm is used both for
encryption and decryption, and the algorithm does not change the length of the data.
""")

heading3("How To Use Encryption")

disc("""
     Documents can be encrypted by passing an argument to the canvas object.
     """)

disc("""
     If the argument is a string object, it is used as the User password to the PDF.
     """)

disc("""
     The argument can also be an instance of the class $reportlab.lib.pdfencrypt.StandardEncryption$,
     which allows more finegrained control over encryption settings.
     """)

disc("""
     The $StandardEncryption$ constructor takes the following arguments:
     """)

eg("""
    def __init__(self, userPassword,
            ownerPassword=None,
            canPrint=1,
            canModify=1,
            canCopy=1,
            canAnnotate=1,
            strength=40):
    """)

disc("""
     The $userPassword$ and $ownerPassword$ parameters set the relevant password on the encrypted PDF.
     """)

disc("""
     The boolean flags $canPrint$, $canModify$, $canCopy$, $canAnnotate$ determine wether a user can
    perform the corresponding actions on the PDF when only a user password has been supplied.
    """)
disc("""
    If the user supplies the owner password while opening the PDF, all actions can be performed regardless
    of the flags.
    """)

heading3("Example")

disc("""
     To create a document named hello.pdf with a user password of 'rptlab' on which printing is not allowed,
     use the following code:
     """)

eg("""
from reportlab.pdfgen import canvas
from reportlab.lib import pdfencrypt

enc=pdfencrypt.StandardEncryption("rptlab",canPrint=0)

def hello(c):
    c.drawString(100,100,"Hello World")
c = canvas.Canvas("hello.pdf",encrypt=enc)
hello(c)
c.showPage()
c.save()

""")

heading2("Interactive Forms")
heading3("Overview of Interactive Forms")

disc("""The PDF standard allows for various kinds of interactive elements,
the ReportLab toolkit currently supports only a fraction of the possibilities and should be considered a work in progress.
At present we allow choices with
<i>checkbox</i>, <i>radio</i>, <i>choice</i> &amp; <i>listbox</i> widgets; text values can be entered with a
<i>textfield</i> widget. All the widgets are created by calling methods on the <i>canvas.acroform</i> property."""
)
heading3("Example")
disc("This shows the basic mechanism of creating an interactive element on the current page.")
eg("""
        canvas.acroform.checkbox(
                name='CB0',
                tooltip='Field CB0',
                checked=True,
                x=72,y=72+4*36,
                buttonStyle='diamond',
                borderStyle='bevelled',
                borderWidth=2,
                borderColor=red,
                fillColor=green,
                textColor=blue,
                forceBorder=True)
""")
alStyle=TableStyle([
            ('SPAN',(0,0),(-1,0)),
            ('FONT',(0,0),(-1,0),'Helvetica-Bold',10,12),
            ('FONT',(0,1),(-1,1),'Helvetica-BoldOblique',8,9.6),
            ('FONT',(0,2),(0,-1),'Helvetica-Bold',7,8.4),
            ('FONT',(1,2),(1,-1),'Helvetica',7,8.4),
            ('FONT',(2,2),(2,-1),'Helvetica-Oblique',7,8.4),
            ('ALIGN',(0,0),(-1,0),'CENTER'),
            ('ALIGN',(1,1),(1,1),'CENTER'),
            ('INNERGRID', (0,0), (-1,-1), 0.25, colors.black),
            ('BOX', (0,0), (-1,-1), 0.25, colors.black),
            ])

disc("""<b>NB</b> note that the <i>acroform</i> canvas property is created automatically on demand and that there is only one form allowd in a document.""")
heading3("Checkbox Usage")
disc("""The <i>canvas.acroform.checkbox</i> method creates a <i>checkbox</i> widget on the current page. The value of the checkbox is either <b>YES</b> or <b>OFF</b>.
The arguments are""")
t = Table([
            ['canvas.acroform.checkbox parameters','',''],
            ['Parameter','Meaning','Default'],
            ["name","the parameter's name","None"],
            ["x","the horizontal position on the page (absolute coordinates)","0"],
            ["y","the vertical position on the page (absolute coordinates)","0"],
            ["size","The outline dimensions size x size","20"],
            ["checked","if True the checkbox is initially checked","False"],
            ["buttonStyle","the checkbox style (see below)","'check'"],
            ["shape","The outline of the widget (see below)","'square'"],
            ["fillColor","colour to be used to fill the widget","None"],
            ["textColor","the colour of the symbol or text","None"],
            ["borderWidth","as it says","1"],
            ["borderColor","the widget's border colour","None"],
            ["borderStyle","The border style name","'solid'"],
            ["tooltip","The text to display when hovering over the widget","None"],
            ["annotationFlags","blank separated string of annotation flags","'print'"],
            ["fieldFlags","Blank separated field flags (see below)","'required'"],
            ["forceBorder","when true a border force a border to be drawn","False"],
            ["relative","if true obey the current canvas transform","False"],
            ["dashLen ","the dashline to be used if the borderStyle=='dashed'","3"],
          ],[90, 260, 90],style=alStyle,repeatRows=2)
getStory().append(t)

heading3("Radio Usage")
disc("""The <i>canvas.acroform.radio</i> method creates a <i>radio</i> widget on the current page. The value of the radio is the value of the radio group's
selected value or <b>OFF</b> if none are selected.
The arguments are""")
t = Table([
            ['canvas.acroform.radio parameters','',''],
            ['Parameter','Meaning','Default'],
            ["name","the radio's group (ie parameter) name","None"],
            ["value","the radio's group name","None"],
            ["x","the horizontal position on the page (absolute coordinates)","0"],
            ["y","the vertical position on the page (absolute coordinates)","0"],
            ["size","The outline dimensions size x size","20"],
            ["selected","if True this radio is the selected one in its group","False"],
            ["buttonStyle","the checkbox style (see below)","'check'"],
            ["shape","The outline of the widget (see below)","'square'"],
            ["fillColor","colour to be used to fill the widget","None"],
            ["textColor","the colour of the symbol or text","None"],
            ["borderWidth","as it says","1"],
            ["borderColor","the widget's border colour","None"],
            ["borderStyle","The border style name","'solid'"],
            ["tooltip","The text to display when hovering over the widget","None"],
            ["annotationFlags","blank separated string of annotation flags","'print'"],
            ["fieldFlags","Blank separated field flags (see below)","'noToggleToOff required radio'"],
            ["forceBorder","when true a border force a border to be drawn","False"],
            ["relative","if true obey the current canvas transform","False"],
            ["dashLen ","the dashline to be used if the borderStyle=='dashed'","3"],
          ],[90, 260, 90],style=alStyle,repeatRows=2)
getStory().append(t)
heading3("Listbox Usage")
disc("""The <i>canvas.acroform.listbox</i> method creates a <i>listbox</i> widget on the current page. The listbox contains a
list of options one or more of which (depending on fieldFlags) may be selected.
""")
t = Table([
            ['canvas.acroform.listbox parameters','',''],
            ['Parameter','Meaning','Default'],
            ["name","the radio's group (ie parameter) name","None"],
            ["options","List or tuple of avaiable options","[]"],
            ["value","Singleton or list of strings of selected options","[]"],
            ["x","the horizontal position on the page (absolute coordinates)","0"],
            ["y","the vertical position on the page (absolute coordinates)","0"],
            ["width","The widget width","120"],
            ["height","The widget height","36"],
            ["fontName","The name of the type 1 font to be used","'Helvetica'"],
            ["fontSize","The size of font to be used","12"],
            ["fillColor","colour to be used to fill the widget","None"],
            ["textColor","the colour of the symbol or text","None"],
            ["borderWidth","as it says","1"],
            ["borderColor","the widget's border colour","None"],
            ["borderStyle","The border style name","'solid'"],
            ["tooltip","The text to display when hovering over the widget","None"],
            ["annotationFlags","blank separated string of annotation flags","'print'"],
            ["fieldFlags","Blank separated field flags (see below)","''"],
            ["forceBorder","when true a border force a border to be drawn","False"],
            ["relative","if true obey the current canvas transform","False"],
            ["dashLen ","the dashline to be used if the borderStyle=='dashed'","3"],
          ],[90, 260, 90],style=alStyle,repeatRows=2)
getStory().append(t)
heading3("Choice Usage")
disc("""The <i>canvas.acroform.choice</i> method creates a <i>dropdown</i> widget on the current page. The dropdown contains a
list of options one or more of which (depending on fieldFlags) may be selected. If you add <i>edit</i> to the <i>fieldFlags</i>
then the result may be edited.
""")
t = Table([
            ['canvas.acroform.choice parameters','',''],
            ['Parameter','Meaning','Default'],
            ["name","the radio's group (ie parameter) name","None"],
            ["options","List or tuple of avaiable options","[]"],
            ["value","Singleton or list of strings of selected options","[]"],
            ["x","the horizontal position on the page (absolute coordinates)","0"],
            ["y","the vertical position on the page (absolute coordinates)","0"],
            ["width","The widget width","120"],
            ["height","The widget height","36"],
            ["fontName","The name of the type 1 font to be used","'Helvetica'"],
            ["fontSize","The size of font to be used","12"],
            ["fillColor","colour to be used to fill the widget","None"],
            ["textColor","the colour of the symbol or text","None"],
            ["borderWidth","as it says","1"],
            ["borderColor","the widget's border colour","None"],
            ["borderStyle","The border style name","'solid'"],
            ["tooltip","The text to display when hovering over the widget","None"],
            ["annotationFlags","blank separated string of annotation flags","'print'"],
            ["fieldFlags","Blank separated field flags (see below)","'combo'"],
            ["forceBorder","when true a border force a border to be drawn","False"],
            ["relative","if true obey the current canvas transform","False"],
            ["dashLen ","the dashline to be used if the borderStyle=='dashed'","3"],
            ["maxlen ","None or maximum length of the widget value","None"],
          ],[90, 260, 90],style=alStyle,repeatRows=2)
getStory().append(t)

heading3("Textfield Usage")
disc("""The <i>canvas.acroform.textfield</i> method creates a <i>textfield</i> entry widget on the current page. The textfield may be edited
to change tha value of the widget
""")
t = Table([
            ['canvas.acroform.textfield parameters','',''],
            ['Parameter','Meaning','Default'],
            ["name","the radio's group (ie parameter) name","None"],
            ["value","Value of the text field","''"],
            ["maxlen ","None or maximum length of the widget value","100"],
            ["x","the horizontal position on the page (absolute coordinates)","0"],
            ["y","the vertical position on the page (absolute coordinates)","0"],
            ["width","The widget width","120"],
            ["height","The widget height","36"],
            ["fontName","The name of the type 1 font to be used","'Helvetica'"],
            ["fontSize","The size of font to be used","12"],
            ["fillColor","colour to be used to fill the widget","None"],
            ["textColor","the colour of the symbol or text","None"],
            ["borderWidth","as it says","1"],
            ["borderColor","the widget's border colour","None"],
            ["borderStyle","The border style name","'solid'"],
            ["tooltip","The text to display when hovering over the widget","None"],
            ["annotationFlags","blank separated string of annotation flags","'print'"],
            ["fieldFlags","Blank separated field flags (see below)","''"],
            ["forceBorder","when true a border force a border to be drawn","False"],
            ["relative","if true obey the current canvas transform","False"],
            ["dashLen ","the dashline to be used if the borderStyle=='dashed'","3"],
          ],[90, 260, 90],style=alStyle,repeatRows=2)
getStory().append(t)

heading3("Button styles")
disc("""The button style argument indicates what style of symbol should appear in the button when it is selected. There are several choices""")
eg("""  check
  cross
  circle
  star
  diamond
""")
disc("""note that the document renderer can make some of these symbols wrong for their intended application.  Acrobat reader
prefers to use its own rendering on top of what the specification says should be shown (especially when the forms hihlighting features are used""")

heading3("Widget shape")
disc("""The shape argument describes how the outline of the checkbox or radio widget should appear you can use""")
eg("""  circle
  square
""")

disc("""The renderer may make its own decisions about how the widget should look; so Acrobat Reader prefers circular outlines for radios.""")

heading3("Border style")
disc("""The borderStyle argument changes the 3D appearance of the widget on the page alternatives are""")
eg("""  solid
  dashed
  inset
  bevelled
  underlined
    """)
heading3("fieldFlags Argument")
disc("""The fieldFlags arguments can be an integer or a string containing blank separate tokens the values are shown in the table below. For
more information consult the PDF specification.""")
t = Table([
            ['Field Flag Tokens and values','',''],
            ['Token','Meaning','Value'],
            ["readOnly","The widget is read only","1<<0"],
            ["required","the widget is required","1<<1"],
            ["noExport","don't export the widget value","1<<2"],
            ["noToggleToOff","radios one only must be on","1<<14"],
            ["radio","added by the radio method","1<<15"],
            ["pushButton","if the button is a push button","1<<16"],
            ["radiosInUnison","radios with the same value toggle together","1<<25"],
            ["multiline","for multiline text widget","1<<12"],
            ["password","password textfield","1<<13"],
            ["fileSelect","file selection widget","1<<20"],         #1.4
            ["doNotSpellCheck","as it says","1<<22"],   #1.4
            ["doNotScroll","text fields do not scroll","1<<23"],        #1.4
            ["comb","make a comb style text based on the maxlen value","1<<24"],                #1.5
            ["richText","if rich text is used","1<<25"],            #1.5
            ["combo","for choice fields","1<<17"],
            ["edit","if the choice is editable","1<<18"],
            ["sort","if the values should be sorted","1<<19"],
            ["multiSelect","if the choice allows multi-select","1<<21"],        #1.4
            ["commitOnSelChange","not used by reportlab","1<<26"],  #1.5
          ],[90, 260, 90],style=alStyle,repeatRows=2)
getStory().append(t)
heading3("annotationFlags Argument")
disc("""PDF widgets are annotations and have annotation properties these are shown in the table below""")
t = Table([
            ['Annotation Flag Tokens and values','',''],
            ['Token','Meaning','Value'],
            ["invisible","The widget is not shown","1<<0"],
            ["hidden","The widget is hidden","1<<1"],
            ["print","The widget will print","1<<2"],
            ["nozoom","The annotation will notscale with the rendered page","1<<3"],
            ["norotate","The widget won't rotate with the page","1<<4"],
            ["noview","Don't render the widget","1<<5"],
            ["readonly","Widget cannot be interacted with","1<<6"],
            ["locked","The widget cannot be changed","1<<7"],           #1.4
            ["togglenoview","Teh widget may be viewed after some events","1<<8"],       #1.9
            ["lockedcontents","The contents of the widget are fixed","1<<9"],   #1.7
          ],[90, 260, 90],style=alStyle)
getStory().append(t)
