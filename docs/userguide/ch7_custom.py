#most_chapters.py
"""In order to rationalize this guide, I am pulling out all the story-making
stuff into this module.  genuserguide.py contains pure definitions - stuff
any chapter needs - and does not create story content.  most_chapters.py
can be imported and will add to the BODY.  We can then break it down
into separate modules ch1_intro, ch2_pdfgen and so on, and a central
functions can import the lot."""



from genuserguide import *








heading1("Writing your own Flowable Objects")
disc("""
Flowable are intended to be an open standard for creating
reusable report content, and you can easily create your
own objects.  We hope that over time we will build up
a library of contributions, giving reportlab users a
rich selection of charts, graphics and other "report
widgets" they can use in their own reports. This section
shows you how to create our own flowables.""")

todo("""we should put the Figure class in the
standard library, as it is a very useful base.""")




heading2("A very simple Flowable")
illust(examples.hand, "a hand")



