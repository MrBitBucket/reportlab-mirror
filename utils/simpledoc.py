#copyright ReportLab Inc. 2000
#see license.txt for license details
#history http://cvs.sourceforge.net/cgi-bin/cvsweb.cgi/utils/simpledoc.py?cvsroot=reportlab
#$Header: /tmp/reportlab/utils/simpledoc.py,v 1.6 2001/03/16 14:49:57 rgbecker Exp $
__version__=''' $Id: simpledoc.py,v 1.6 2001/03/16 14:49:57 rgbecker Exp $ '''
__doc__="""
simple document formatting (quickhack) for pdf:

.t title

.h Header

This is a paragraph.
This is in the same paragraph.

This is the start of the next paragraph.

.i Item title:
Item detail.
more detail.

.i next item title:
and so forth.
"""
import string
from reportlab.platypus import *
from reportlab.lib.styles import getSampleStyleSheeet
from reportlab.rl_config import defaultPageSize

do_images = 1

class DocStyle0PDF:
	Title = "Untitled Document"
	mode = "normal"

	def __init__(self):
		self.elts = []
		self.paragraph = []
		styles = getSampleStyleSheet()
		self.paraStyle = styles["Normal"]
		self.headerStyle = styles["Heading3"]
		self.preStyle = styles["Code"] 
		self.modeStyles = {"normal": self.paraStyle, "preformatted": self.preStyle}
		self.modeFormat = {"normal": Paragraph, "preformatted": Preformatted}
		self.mode = "normal"

	def add_text(self, text):
		text1 = string.strip(text)
		if self.mode=="normal":
			text = text1
			if not text:
				self.end_paragraph()
			else:
				self.paragraph.append(text)
		elif self.mode=="preformatted":
			if text1:
				self.paragraph.append(text)
			else:
				self.end_paragraph()
		else:
			raise ValueError, "invalid mode"

	def end_paragraph(self):
		p = self.paragraph
		if self.mode=="normal":
			if p:
				body = string.join(p, " ")
				self.emit_paragraph(body)
		elif self.mode=="preformatted":
			body = string.join(p, "")
			self.emit_paragraph(body)
		self.paragraph = []

	def emit_paragraph(self, body):
		#s1 = Spacer(0.2*inch, 0.2*inch)
		style = self.modeStyles[self.mode]
		formatter = self.modeFormat[self.mode]
		t = formatter(body, style)
		s2 = Spacer(10, 10)
		e = self.elts
		e.append(t)
		e.append(s2)

	def addTitle(self, title1):
		self.Title = title1

	def addHeader(self, header):
		self.addItem(header)
		s2 = Spacer(0.2*inch, 0.2*inch)
		e = self.elts
		e.append(s2)
		
	def addItem(self, item):
		s1 = Spacer(0.2*inch, 0.2*inch)
		t = Paragraph(item, self.headerStyle)
		e = self.elts
		e.append(s1)
		e.append(t)

	def myFirstPage(self, canvas, doc):
		canvas.saveState()
		canvas.setFillColorRGB(0,0,0.93)
		canvas.rect(20,20,90,802,stroke=0, fill=1)
		if do_images:
			canvas.drawInlineImage("replog.gif",20,750,90,60)
			canvas.drawInlineImage("reppow.jpg", 2*inch, PAGE_HEIGHT-3*inch)
		canvas.setStrokeColorRGB(1,0,0)
		canvas.setLineWidth(5)
		canvas.setFont("Helvetica-Bold",16)
		canvas.drawCentredString(4*inch, PAGE_HEIGHT-4*inch, self.Title)
		canvas.setFont('Times-Roman',9)
		canvas.drawString(2*inch, PAGE_HEIGHT-0.50 * inch, "First Page / %s" % self.Title)
		canvas.restoreState()
	
	def myLaterPages(self, canvas, doc):
		canvas.saveState()
		canvas.setFillColorRGB(0,0,0.93)
		canvas.rect(20,20,90,802,stroke=0, fill=1)
		if do_images:
			canvas.drawInlineImage("replog.gif",20,750,90,60)
		canvas.setFont('Times-Roman',9)
		pageinfo=self.Title
		canvas.drawString(2*inch, PAGE_HEIGHT-0.5 * inch, "Page %d %s" % (doc.page, pageinfo))
		canvas.restoreState()

	def process(self, lines, tofilename):
		for l in lines:
			if l[0]==".":
				tag = l[1]
				remainder = l[2:]
				if tag=="t":
					self.addTitle(remainder)
				elif tag=="h":
					self.addHeader(remainder)
				elif tag=="i":
					self.addItem(remainder)
				elif tag=="p":
					self.mode = "preformatted"
				elif tag=="n":
					self.end_paragraph()
					self.mode = "normal"
			else:
				self.add_text(l)
		self.end_paragraph()
		self.finish(tofilename)

	def finish(self, tofilename):
		doc = SimpleDocTemplate(tofilename, defaultPageSize)
		doc.onFirstPage = self.myFirstPage
		doc.onLaterPages = self.mylaterPages
		doc.leftMargin = 144
		elts = self.elts
		elts.insert(0, Spacer(4*inch, 4*inch)) # make space for title
		doc.build(self.elts)

	def processfile(self, fromfilename, tofilename):
		f = open(fromfilename)
		lines = f.readlines()
		self.process(lines, tofilename)

class DocStyle0HTML(DocStyle0PDF):
	def __init__(self):
		self.elts = []
		self.paragraph = []

	def finish(self,tofilename):
		f = open(tofilename, "w")
		body = string.join(self.elts, "\n")
		D = {}
		D["title"] = self.Title
		D["body"] = body
		out = htmlfmt % D
		f.write(out)
		f.close()

	def emit_paragraph(self, body):
		if self.mode=="normal":
			self.elts.append("<p>\n%s\n</p>\n"% body)
		elif self.mode=="preformatted":
			self.elts.append("<pre>\n%s\n</pre>\n"% body)
		else: raise "bad mode"

	def addHeader(self, header):
		self.elts.append("\n<h2>%s</h2>"%header)
		
	def addItem(self, item):
		self.elts.append("<b>%s</b><br>" % item)

htmlfmt = """
<HTML>
<HEAD>
  <TITLE>%(title)s</TITLE>
<BODY TEXT="#ffffff" BGCOLOR="#0000cc" LINK="#00ff00" ALINK="#ff00ff"
VLINK="#009900">

<P><CENTER><FONT FACE="Arial"><A HREF="index.html"><IMG 
SRC="replog.gif" WIDTH="450" HEIGHT="300" ALIGN="BOTTOM"
BORDER="0" NATURALSIZEFLAG="3"></A></FONT></CENTER></P>

<P><CENTER><B><FONT SIZE="+2" FACE="Arial">%(title)s</FONT></B></CENTER></P>

%(body)s

<P><CENTER><B><FONT SIZE="+2" FACE="Arial"></FONT></B><TABLE 
WIDTH="607" BORDER="1" CELLSPACING="2" CELLPADDING="0">
  <TR>
	<TD WIDTH="14%%">
	&nbsp;<B><FONT FACE="Arial"><A HREF="about.html">about
	us</A> </FONT></B></TD>
	<TD WIDTH="14%%">
	&nbsp;<B><FONT FACE="Arial"><A HREF="products.html">products</A></FONT></B></TD>
	<TD WIDTH="14%%">
	<P><CENTER><A HREF="news.html">&nbsp;<B><FONT FACE="Arial">news</FONT></B></A></CENTER></TD>
	<TD WIDTH="14%%">
	&nbsp;<B><FONT FACE="Arial"><A HREF="customers.html">customers</A></FONT></B></TD>
	<TD WIDTH="14%%">
	&nbsp;<B><FONT FACE="Arial"><A HREF="services.html">services</A></FONT></B></TD>
	<TD WIDTH="15%%">
	<A HREF="sales.html">&nbsp;<B><FONT FACE="Arial">sales</FONT></B></A></TD>
  </TR>
</TABLE></CENTER>
<center><a href="mailto:info@reportlab.com">
<font face="Arial">Contact ReportLab</font>
</a></center>

</BODY>
</HTML>

"""

if __name__=="__main__": #NORUNTESTS
	import sys
	[myname, format, fromfilename, tofilename] = sys.argv
	format = string.lower(format)
	if format=="pdf":
		processor = DocStyle0PDF()
	elif format=="html":
		processor = DocStyle0HTML()
	else:
		raise ValueError, "unknown format %s" % `format`
	processor.processfile(fromfilename, tofilename)
