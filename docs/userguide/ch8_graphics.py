#copyright ReportLab Inc. 2001
#see license.txt for license details
#history http://cvs.sourceforge.net/cgi-bin/cvsweb.cgi/docs/userguide/ch7_custom.py?cvsroot=reportlab
#$Header: /tmp/reportlab/docs/userguide/Attic/ch8_graphics.py,v 1.13 2001/03/29 09:24:47 dinu_gherman Exp $

from genuserguide import *

heading1("Platform Independent Graphics using $reportlab/graphics$ (DRAFT)")

heading2("Introduction")

#heading3("Background")

#seamless or what?
#from reportlab.graphics.charts import barcharts
#draw(barcharts.sampleH0a(), 'A Sample Drawing')
# draw (drawing object, 'caption')

disc("""
The ReportLab library is a general document toolkit aiming to help
generate documents for reporting solutions.
One important aspect of such applications is to present data with
graphics like diagrams or charts.
Ideally, these graphics could be used not only to generate PDF
documents, but other output formats, bitmap or vector ones, as
well.
ReportLab is in the process of adding such a graphics package to its
standard distribution.
Because of the size of the graphics library this document aims only
at sketching its design briefly while leaving a detailed presentation
to an additional document, the "ReportLab Graphics User Guide", that
provides a more tutorial-like approach.
""")


heading3("Requirements")

disc("""The graphics library should support the creation of custom
graphical applications containing charts, diagrams, drawings, plans,
etc. in various domains like business, finance, publishing, engineering
and research.
It is especially intended as a foundation for a chart library that
happens to be the first major subpackage for a real-world client
in the financial industry.
""")

disc("The general graphics package should help with the following activities: ")

bullet("creating reusable shapes collections")
bullet("supporting paths, clipping and coordinate transformations")
bullet("writing output to PDF, Postscript, bitmap and vector formats")
bullet("using a consistent font model (Type 1)")
bullet("providing identical metrics on all platforms")
bullet("""using a framework for creating, documenting and reusing graphical "widgets" """)

disc("""Within the charting domain the target features are:""")

bullet("Horizontal/vertical bar charts based on category/value axes.")
bullet("Horizontal/vertical line charts based on category/value axes.")
bullet("""Special time series charts based on genuine x/y values.""")
bullet("Simple pie charts.")
bullet("""Compounding - one can define 'multiples' placing several charts on one 
       drawing, or arbitrary decorations around the chart. This technique 
       also allows easy overlaying of lines on bars, or of different axes on 
       the right and left side of a plot.""")
bullet("""'Plug-In Architecture' - with training, you can write a new chart type
       based on an existing one but only changing/adding the features you
       need to.""")
bullet("Control over drawing size, plot rectangle size and position within drawing.")
bullet("""Control over width, dash style, line cap/join style and
       color for all lines.""")
bullet("""Choice of any solid color (or gray level, or transparent) for any
       enclosed area. Fill patterns may be added later. The public library
       will be limited to RGB and possibly plain CMYK colors but we can
       cleanly layer custom Postscript requirements on top.""")
bullet("""Control over font name (any Type 1 font on the system) and size, plus
       the ability to scale, stretch and rotate the text
       right, left and centre alignment of label text strings with correct
       metrics.""")

disc("""The charting requirements are based on a commercial sponsor who
needs to create batches of charts rapidly with precise control over
layout.""")


heading2("General Concepts")

heading3("Drawings and Renderers")

disc("""A Drawing is a platform-independent description of a collection of 
       shapes. It is not directly associated with PDF, Postscript or any 
       other output format. Fortunately most vector graphics systems have 
       followed the Postscript model and it is possible to describe shapes 
       unambiguously.""")

disc("""A Drawing contains a number of primitive Shapes. One important shape 
       is a "Group", which can hold other shapes and apply a transformation 
       to them. Just about anything can be built up from a small number of 
       basic shapes.""")

disc("""The package provides several "renderers" which know how to draw a 
       drawing into different formats. These include PDF (of course), 
       Postscript, and bitmap output. The bitmap renderer will use Raph 
       Levien's <i>libart</i> rasterizer and the Python Imaging Library. If you have 
       the right extensions installed, you can generate drawings in bitmap 
       form for the web as well as vector form for PDF documents, and get 
       "identical output".""")

disc("""We expect to add both input and output filters for many vector 
       graphics formats in future. SVG is a key one. GUIs will be able to 
       obtain screen images from the bitmap output filter working with PIL, 
       so a chart could appear in a Tkinter GUI window.""")

disc("""The PDF renderer has "special privileges" - a Drawing object is a 
       Flowable, and can be placed directly in the story in any flowing 
       document, or drawn directly on a canvas with one line. In addition, 
       the PDF renderer has a utility function to make a one-page PDF 
       quickly.""")


heading3("Verification")

disc("""Python is very dynamic and lets us execute statements at run time
that can easily be the source for unexpected behaviour.
One subtle 'error' is when assigning to an attribute that the framework
doesn't know about because the attribute's name contains a typo.
Python lets you get away with it, but the graphics framework will
not detect the typo immediately.""")

disc("""There are two verification techniques to avoid this situation.
The default is for every object to check every assignment at run time,
such that you can only assign to 'legal' attributes.
This is what happens by default.
As this imposes a small performance penalty, this behaviour
can be turned off when you need it to be.""")


heading3("Property Editing")

disc("""A cornerstone of the reportlab/graphics which we will cover below is 
       that you can automatically document widgets. This means getting hold 
       of all of their editable properties, including those of their 
       subcomponents.""")

disc("""Another goal is to be able to create GUIs and config files for 
       drawings. A generic GUI can be built to show all editable properties 
       of a drawing, and let you modify them and see the results. The Visual 
       Basic or Delphi developmen environment are good examples of this kind 
       of thing. In a batch charting application, a file could list all the 
       properties of all the components in a chart, and be merged with a 
       database query to make a batch of charts.""")

disc("""To support these applications we have two interfaces, $getProperties$ 
       and $setProperties$, as well as a convenience method $dumpProperties$. The 
       first returns a dictionary of the editable properties of an object; 
       the second sets them en masse. If an object has publicly exposed 
       'children' then one can recursively set and get their properties too. 
       This will make much more sense when we look at Widgets later on, but 
       we need to put the support into the base of the framework.""")


heading3("Automatic Documentation")

disc("""There is work under way on a generic tool to document any
Python package or module; this will be checked into ReportLab and
will be used to generate a reference for the ReportLab package.
When it encounters elements of the graphics library, it will add
extra sections to the manual.
So far this works for Widgets (see below), therefore the information
includes:""")

bullet("the doc string for your Widget class,")
bullet("""the code snippet from your <i>demo()</i> method, so people
can see how to use it,""")
bullet("the Drawing produced by the <i>demo()</i> method and")
bullet("the property dump for the Widget in the Drawing.")

disc("""This tool means that we can have guaranteed up-to-date 
documentation on our widgets and chart, both on the web site and in 
print; and that you can do the same for your own widgets too!""")


heading3("Naming Children")

disc("""You can add objects to the $Drawing$ and $Group$ objects.
These normally go into a list of contents.
However, you may also give objects a name when adding them.
This allows you to refer to and possibly change any 
element of a drawing after constructing it.""")

disc("""Note that you can use the same shape instance in several
contexts in a drawing; if you choose to use the same Circle object
in many locations (e.g. a scatter plot) and use different names
to access it, it will still be a shared object and the changes
will be global.""")

disc("""This provides one paradigm for creating and modifying
interactive drawings.""")


heading2("Shapes")

disc("""Drawings are made up of Shapes. Any graphical object can be
built up by using the same set of simple shapes.
The module $shapes.py$ supplies a number of primitive shapes and 
constructs which can be added to a drawing:""")

bullet("Rect (optionally with rounded corners)")
bullet("Circle")
bullet("Ellipse")
bullet("Wedge (a pie slice)")
bullet("Polygon")
bullet("Line")
bullet("PolyLine")
bullet("String")
bullet("Group")
bullet("Path (<i>not implemented yet, but will be added in the future</i>)")

disc("""Shapes generally have <i>style properties</i> and <i>geometry
properties</i>. <i>x</i>, <i>y</i>, <i>width</i> and <i>height</i> are
part of the geometry and must be provided when 
creating the rectangle, since it does not make much sense without 
those properties.
You may set other properties on subsequent lines, or by passing them 
as optional arguments to the constructor.
The others are optional and come with sensible defaults.
All shapes have a number of properties which can be set by the user.
The <i>dumpProperties()</i> method can be used at an interactive prompt
to list these properties.
""")

disc("""
The graphical shapes in the list above are more or less what you
would expect from reading their names.
In addition there are also Group objects.
Groups provide a tool for reuse.
You can make a bunch of shapes to represent some component - say,
a coordinate system - and put them in one group called "Axis".
You can then put that group into other groups, each with a different
translation and rotation, and you get a bunch of axis.
It is still the same group, being drawn in different places.""")


heading2("Widgets") 

disc("""Up until now, Drawings have been 'pure data'.
In fact, this is what grants portability - a renderer only 
needs to implement the primitive shapes.""")

disc("""To implement a powerful chart library though, you need
to reuse more tangible things than rectangles and circles.
We should be able to write objects for other to reuse - arrows,
gears, text boxes, UML diagram nodes, even fully fledged charts.""")

disc("""This is what widgets are made for, building on top of the
shapes module. 
Anyone can write new widgets, and build up libraries of them. 
Widgets support getProperties and setProperties, so you can inspect 
and modify as well as document them in a uniform way:""")

bullet("A widget is a reusable shape.")
bullet("""It can be initialized with no arguments 
       when its $draw()$ method is called it creates a primitive Shape or a 
       Group to represent itself.""")
bullet("""It can have any parameters you want, and they can drive the way it is 
       drawn.""")
bullet("""It has a $demo()$ method which should return an attractively drawn 
       example if itself in a 200x100 rectangle. This is the cornerstone of 
       the automatic documentation tools. The $demo()$ method should also have 
       a well written docstring, since that is printed too!""")

disc("""Widgets run contrary to the idea that a drawing is just a
bundle of shapes.
The way they work is that a widget can convert itself to a group
of primitive shapes.
If some of its components are themselves widgets, they will get
converted, too. 
This happens automatically during rendering; the renderer will not
see a chart widget, but just a collection of rectangles, lines
and strings.
A drawing can also explicitly be 'flattened out', causing all 
widgets to be converted to primitives.""")

disc("""There is one necessary trade-off to allow a uniform
interface for constructing widgets and documenting them - they
cannot require arguments in their $__init__$ method.
Instead, they are generally designed to fit in a 200 x 100 
window, and you move or resize them by setting properties such
as x, y, width and so on after creation.""")

disc("""In addition, a widget always provides a $demo()$ method.
Simple ones like this always do something sensible before setting
properties, but more complex ones like a chart would not have any
data to plot.
The documentation tool calls $demo()$ so that your fancy new chart
class can create a drawing showing what it can do.""")


heading2("Charts")

disc("""This section is not finalized and will evolve further. For now we'll 
       try to give a flavour of the isues we are dealing with, and firm them 
       up as examples are created. We need and expect feedback on this to get 
       it right!""")

heading3("Design Goals")

disc("<i>Make simple top-level use really simple </i>")
disc("""<para lindent=+36>It should be possible to create a simple chart with minimum lines of 
       code, yet have it 'do the right things' with sensible automatic 
       settings. The pie chart snippets above do this. If a real chart has 
       many subcomponents, you still should not need to interact with them 
       unless you want to customize what they do.""")

disc("<i>Allow precise positioning </i>")
disc("""<para lindent=+36>An absolute requirement in publishing and graphic design is to control 
       the placing and style of every element. We will try to have properties 
       that specify things in fixed sizes and proportions of the drawing, 
       rather than having automatic resizing. Thus, the 'inner plot 
       rectangle' will not magically change when you make the font size of 
       the y labels bigger, even if this means your labels can spill out of 
       the left edge of the chart rectangle. It is your job to preview the 
       chart and choose sizes and spaces which will work.""")

disc("""<para lindent=+36>Some things do need to be automatic. For example, if you want to fit N 
       bars into a 200 point space and don't know N in advance, we specify 
       bar separation as a percentage of the width of a bar rather than a 
       point size, and let the chart work it out. This is still deterministic 
       and controllable.""")

disc("<i>Control child elements individually or as a group</i>")
disc("""<para lindent=+36>We use smart collection classes that let you customize a group of 
       things, or just one of them. For example you can do this in our 
       experimental pie chart:""")
 
disc("""<para lindent=+36>pc.wedges[3] actually lazily creates a little object which holds 
       information about the slice in question; this will be used to format a 
       fourth slice at draw-time if there is one.""")

disc("<i>Only expose things you should change </i>")
disc("""<para lindent=+36>It would be wrong from a statistical viewpoint to let you directly 
       adjust the angle of one of the pie wedges in the above example, since 
       that is determined by the data. So not everything will be exposed 
       through the public properties. There may be 'back doors' to let you 
       violate this when you really need to, or methods to provide advanced 
       functionality, but in general properties will be orthogonal.""")

disc("<i>Composition and component based </i>")

disc("""<para lindent=+36>Charts are built out of reusable child widgets. A Legend is an 
       easy-to-grasp example. If you need a specialized type of legend (e.g. 
       circular colour swatches), you should subclass the standard Legend 
       widget. Then you could either do something like...""")

disc("""<para lindent=+36>...or create/modify your own chart or drawing class which creates one 
       of these by default. This is also very relevant for time series 
       charts, where there can be many styles of x axis.""")

disc("""<para lindent=+36>Top level chart classes will create a number of such components, and 
       then either call methods or set private properties to tell them their 
       height and position - all the stuff which should be done for you and 
       which you cannot customise. We are working on modelling what the 
       components should be and will publish their APIs here as a consensus 
       emerges.""")

disc("<i>Multiples </i>")
disc("""<para lindent=+36>A corollary of the component approach is that you can create diagrams 
       with multiple charts, or custom data graphics. Our favourite example 
       of what we are aiming for is the weather report in our gallery 
       contributed by a user; we'd like to make it easy to create such 
       drawings, hook the building blocks up to their legends, and feed that 
       data in a consistent way.""")
disc("""<para lindent=+36>(If you want to see the image, it is available on our website at 
<font color=blue>http://www.reportlab.com/demos/provencio.pdf</font>)""")


heading3("Key Concepts and Components")

disc("""A chart or plot is an object which is placed on a drawing; it is not 
       itself a drawing. You can thus control where it goes, put several on 
       the same drawing, or add annotations.""")

disc("""Charts have two axes; axes may be Value or Category axes. Axes in turn 
       have a Labels property which lets you configure all text labels or 
       each one individually. Most of the configuration details which vary 
       from chart to chart relate to axis properties, or axis labels.""")

disc("""Objects expose properties through the interfaces discussed in the 
       revious section; these are all optional and are there to let the end 
       user configire the appearance. Things which must be set for a chart to 
       work, and essential communication between a chart and its components, 
       are handled through methods.""")

disc("""You can subclass any chart component and use your replacement instead 
       of the original provided you implement the essential methods and 
       properties.""")


heading2("Further Reading")

disc("""
At this point it is recommended to continue reading the "ReportLab
Graphics Guide" which provides much more detailed information about
the existing components for the charting package.
Among them you will find building blocks like labels, axes, legends
and different types of charts like bar, line and pie charts.
A thorough description of all these would blow-up this document
which is kept on purpose rather general.
""")


##heading3("Labels")
##
##disc("""One of the most important building blocks is the <i>Label</i>, defined in 
##       $reportlab/graphics/charts/textlabels.py$. A label is a string of text 
##       attached to some chart element. They are used on axes, for titles or 
##       alongside axes, or attached to individual data points.""")
##
##disc("Labels may contain newline characters, but only one font.")
##
##disc("""The text and 'origin' of a label are typically set by its parent 
##       object. They are accessed by methods rather than properties. Thus, the 
##       X axis decides the 'reference point' for each tickmark label and the 
##       numeric or date text for each label. However, the end user can set 
##       properties of the label (or collection of labels) directly to affect 
##       its positon relative to this origin and all of its formatting.""")
##
##disc("""In the drawing above, the label is defined relative to the green blob. 
##       The text box should have its north-east corner ten points down from 
##       the origin, and be rotated by 45 degrees about that corner.""")
##
##disc("""At present labels have the following properties, which we believe are 
##       sufficient for all charts we have seen to date:""")
##
##todo("""Note: need to turn these into pretty tables with explanations """)
##
##
##heading3("Axes")
##
##disc("""We identify two basic kinds of axes - <i>Value</i> and <i>Category</i> Axes. Both 
##       come in horizontal and vertical flavors. Both can be subclassed to 
##       make very specific kinds of axis. For example, if you have complex 
##       rules for which dates to display in a time series application, or want 
##       irregular scaling, you override the axis and make a new one.""")
##
##disc("""Axes are responsible for determining the mapping from data to image 
##       coordinates; transforming points on request from the chart; drawing 
##       themselves and their tickmarks, gridlines and axis labels.""")
##
##disc("""This drawing shows two axes, one of each kind, which have been created 
##       directly without reference to any chart:""")
##
##disc("""Remember that you won't have to create axes directly; when using a 
##       standard chart, it comes with ready-made axes. The methods are what 
##       the chart uses to configure it and take care of the geometry. However, 
##       we will talk through them in detail below.""")
##
##
##heading3("Bar Charts")
##
##disc("""This describes our current VerticalBarChart class, which uses the axes 
##       and labels above. We think it is step in the right direction but is is 
##       far from final. As usual, we will start with an example:""")
##
##disc("""Note that people we speak to are divided about 50/50 on whether to 
##       call this a 'Vertical' or 'Horizontal' bar chart. We chose this name 
##       because 'Vertical' appears next to 'Bar', so we take it to mean that 
##       the bars rather than the category axis are vertical.""")
##
##disc("""Most of the code above is concerned with setting up the axes and 
##       labels, which we have already covered. Here are the top-level 
##       properties of the VerticalBarChart class:""")
##
##disc("There are several open issues:")
##
##list("""vertical position of X Axis - by default the X Axis sits at the 
##       bottom. One should be able to specify if it sits at the top, the 
##       bottom or at a specific y value (e.g. y=0).""")
##list("""bar labelling - in cases with some negative bars, the label should 
##       appear BELOW the negative labels and ABOVE the positive ones. How can 
##       we specify this?""")
##list("""color specification - right now the chart has an undocumented property 
##       defaultColors, which provides a list of colors to cycle through. If 
##       you introduce a legend, it should share the list of colors. What's 
##       more, several charts can share a legend. Should we sppecify colors and 
##       line styles on a legend object and attach charts to that, ruling that 
##       the legend need not be visible? Similar issues appear to x-y charts.""")
##
##disc("""When we are a bit more confident of the design, we expect to add 
##       variants of bar charts to deal with stacked and 100% bars as well as 
##       the side-by-side variant seen here, and variants with vertical and 
##       horizontal orientation. For now, if you want one oriented the other 
##       way, just put it in a group and rotate it - here's a VerticalBarChart 
##       where we just turned the labels and the whole chart around by 90 
##       degrees, and hid one of the axes:""")
##
##
##heading3("Pie Charts")
##
##disc("""We've already seen a pie chart example above. This is provisional but 
##       seems to do most things. At the very least we need to change the name. 
##       For completeness we will cover it here.""")
##
##
##disc("""Properties are covered below. The pie has a 'wedges' collection and we 
##       document wedge properties in the same table. This was invented before 
##       we finished the Label class and will probably be reworked to use 
##       Labels shortly.""")
##
##
##heading3("Legends")
##
##disc("""Various preliminary legend classes can be found but need a cleanup to 
##       be consistent with this model. Legends are the natural place to 
##       specify the colors and line styles of charts; we propose that each 
##       chart is created with a Legend attribute which is invisible. One would 
##       then do the following to specify colors:""")
##
##disc("""One could also define a group of charts sharing the same legend:""")
##
##
##heading3("Other Charts")
##
##disc("""It will take some time to deal with the full range of chart types. We 
##       expect to finalize bars and pies and to produce trial implementations 
##       of more general plots in February.""")
##
##
##heading4("X-Y Plots")
##
##disc("""Most other plots involve two value axes and directly plotting x-y data 
##       in some form. The series can be plotted as lines, marker symbols, 
##       both, or custom graphics such as open-high-low-close graphics. All 
##       share the concepts of scaling and axis/title formatting. At a certain 
##       point, a routine will loop over the data series and 'do something' 
##       with the data points at given x-y locations. Given a basic line plot, 
##       it should be very easy to derive a custom chart type just by 
##       overriding a single method - say, drawSeries().""")
##
##
##heading4("Marker customisation and custom shapes")
##
##disc("""Well known plotting packages such as excel, Mathematica and Excel 
##       offer ranges of marker types to add to charts. We can do better - you 
##       can write any kind of chart widget you want and just tell the chart 
##       to use it as an example.""")
##
##
##heading4("Combination Plots")
##
##disc("""Combining multiple plot types is really easy. You can just draw 
##       several charts (bar, line or whatever) in the same rectangle, 
##       suppressing axes as needed. So a chart could correlate a line with 
##       Scottish typhoid cases over a 15 year period on the left axis with a 
##       set of bars showing inflation rates on the right axis. If anyone can 
##       remind us where this example came from we'll attribute it, and happily 
##       show the well-known graph as an example.""")
##
##
##heading3("Other chart classes")
##
##disc("""This has not been an exhaustive look at all the chart classes. Those classes 
##       are constantly being worked on. To see exactly what is in the current 
##       distribution, use the $graphdocpy.py$ utility. By default, it will run 
##       on reportlab/graphics, and produce a full report. (If you want to run
##       it on other modules or packages, $graphdocpy.py -h$ print a help
##       message that will tell you how.)""")
##
##disc("This is the tool that was mentioned in the section on 'Automatic Documentation'")
