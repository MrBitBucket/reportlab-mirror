# this updates the template for all pages on the site.
import os
import sys
import string

#page template
TEMPLATE_FN='reportlab_template.html'
START_DELIM = '<!--User Content Starts Here-->'
END_DELIM = '<!--User Content Ends Here-->'

DUAL_FMT_HTML='<title>%(title)s</title>'+START_DELIM+'''
<H1><center>%(title)s</center></H1>
<center>This page is also available in <a href="%(pdfname)s"><b>PDF</b></a></center>
<p>
%(body)s
<p>
<center>This page is also available in <a href="%(pdfname)s"><b>PDF</b></a>
'''+END_DELIM

DUMB_FMT_HTML='<title>%(title)s</title>'+START_DELIM+'''
%(heading)s
<p>
%(body)s
<p>
'''+END_DELIM

def	find_template(template_fn):
	pp = ''
	while 1:
		p  = os.getcwd()
		if p == pp: raise "Can't find template file"
		fn = os.path.join(p,template_fn)
		if os.path.isfile(fn): return fn
		pp = p
		os.chdir('..')

def DoNormalPages(pages):
	for filename in pages:
		if os.path.isfile(filename):
			applyTemplate(filename, find_template(TEMPLATE_FN))
		else:
			print '    Specified file %s not found' % filename

def get_templated_HTML( src_template=DUMB_FMT_HTML, title=None, heading=None, body=None):
	from StringIO import StringIO
	p = DocStyle0HTML()
	D = p.processfile( StringIO(body), None )
	if title is not None: D['title'] = title
	if heading is not None: D['heading'] = '<h1><center>%s</center></h1>' % heading
	return get_templated_pagedata( find_template(TEMPLATE_FN), src_template % D)

def DoDualFormatPages(pages):
	for filename in pages:
		if os.path.isfile(filename):
			p=DocStyle0PDF()
			pdfname = os.path.splitext(filename)[0]+'.pdf'
			p.processfile(filename, pdfname )
			p = DocStyle0HTML()
			D = p.processfile( filename, None )
			D['pdfname'] = pdfname
			p = DUAL_FMT_HTML % D
			_applyTemplate(p, os.path.splitext(filename)[0]+'.html',  find_template(TEMPLATE_FN))
		else:
			print '    Specified file %s not found' % filename

def get_templated_pagedata( templatefile, rawdata):
	rawtemplate = open(templatefile, 'r').read()
	pagedata = intersperse(rawtemplate, rawdata, '<title>','</title>')
	return intersperse(pagedata, rawdata, START_DELIM, END_DELIM)

def _applyTemplate(rawdata, destfile, templatefile):
	'''
	As applyTemplate, but works on the string rawdata not a file
	destfile gets the result.
	'''
	open(destfile, 'w').write(get_templated_pagedata(templatefile,rawdata))
	print '    File %s updated.' % destfile

def applyTemplate(sourcefile, templatefile):
	"""recreates the source file using its content block and the template file.
	The important content of the source file is presumed to be between two
	blocks exactly like this (defined above):
		<!--User Content Starts Here-->
		<!--User Content Ends Here-->
	If they are not found, no action is taken.
	"""
	_applyTemplate(open(sourcefile, 'r').read(), sourcefile, templatefile)


def intersperse(data1, data2, delim1, delim2):
	"""takes data1 up to start of delim1; data2 between delim1 and delim2;
	and data1 from the end of delim2 onwards.  Used to grab the content
	block and the title out of source pages. Accepts any case in the delimiters.
	Returns the interspersed data, or the original (data1) is nothing found.

	Example:
		data1 = 'Made By ReportLab <TITLE>Title Goes Here</Title> 2000-02-28'
		data2 = 'Made by PageMill <TITLE>MyPage</TITLE> copyright Adobe'
	When interspersed, you get 'MyPage' in the first line.
	"""
	data1_delim1_start = string.find(string.lower(data1), string.lower(delim1))
	if data1_delim1_start == -1:
		return data1
	data1_delim2_start = string.find(string.lower(data1), string.lower(delim2))
	if data1_delim2_start == -1:
		return data1
	data2_delim1_start = string.find(string.lower(data2), string.lower(delim1))
	if data2_delim1_start == -1:
		return data1
	data2_delim2_start = string.find(string.lower(data2), string.lower(delim2))
	if data2_delim2_start == -1:
		return data1
	#if we get this far, the two strings match and can be interspersed
	combined = data1[0:data1_delim1_start] + \
			   data2[data2_delim1_start:data2_delim2_start] + \
			   data1[data1_delim2_start:]
	return combined

"""
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

.u URL definition as URL (annotation text)

.H stuff for HTML ONLY you've been warned RGB :)
"""
from reportlab.platypus.doctemplate import *
from reportlab.platypus.paragraph import Paragraph
from reportlab.lib.styles import getSampleStyleSheet
import string

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

	def addURL(self, URLdef):
		URLdef = string.split(URLdef)
		self.paragraph.append(' <'+URLdef[0]+'> ')

	def myFirstPage(self, canvas, doc):
		canvas.saveState()
		canvas.setFillColorRGB(0,0,0.8)
		canvas.rect(20,20,90,802,stroke=0, fill=1)
		#if do_images:
		#	canvas.drawInlineImage("images/replog.gif",20,750,90,60)
		#	canvas.drawInlineImage("images/reppow.jpg", 2*inch, PAGE_HEIGHT-3*inch)
		canvas.setStrokeColorRGB(1,0,0)
		canvas.setLineWidth(5)
		canvas.setFont("Helvetica-Bold",16)
		canvas.drawCentredString(4*inch, PAGE_HEIGHT-4*inch, self.Title)
		canvas.setFont('Times-Roman',9)
		canvas.drawString(2*inch, PAGE_HEIGHT-0.50 * inch, "First Page / %s" % self.Title)
		canvas.restoreState()
	
	def myLaterPages(self, canvas, doc):
		canvas.saveState()
		canvas.setFillColorRGB(0,0,0.8)
		canvas.rect(20,20,90,802,stroke=0, fill=1)
		#if do_images:
		#	canvas.drawInlineImage("images/replog.gif",20,750,90,60)
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
				elif tag=="u":
					self.addURL(remainder)
				elif tag=="p":
					self.mode = "preformatted"
				elif tag=='H' and self.__class__ is DocStyle0HTML:
					self.add_text(remainder)
				elif tag=="n":
					self.end_paragraph()
					self.mode = "normal"
			else:
				self.add_text(l)
		self.end_paragraph()
		if tofilename is None:
			return self.finish(tofilename)
		else:
			self.finish(tofilename)

	def finish(self, tofilename):
		doc = SimpleDocTemplate(tofilename, DEFAULT_PAGE_SIZE)
		doc.onFirstPage = self.myFirstPage
		doc.onLaterPages = self.myLaterPages
		doc.leftMargin = 144
		elts = self.elts
		elts.insert(0, Spacer(4*inch, 4*inch)) # make space for title
		doc.build(self.elts)

	def processfile(self, fn, tofilename):
		f = type(fn) is type('') and open(fn) or fn
		lines = f.readlines()
		if tofilename is None:
			return self.process(lines, tofilename)
		else:
			self.process(lines, tofilename)

class DocStyle0HTML(DocStyle0PDF):
	def __init__(self):
		self.elts = []
		self.paragraph = []

	def finish(self,tofilename):
		if tofilename is not None:
			f = open(tofilename, "w")
		body = string.join(self.elts, "\n")
		D = {}
		D["title"] = self.Title
		D["body"] = body
		if tofilename is not None:
			out = htmlfmt % D
			f.write(out)
			f.close()
		else:
			return D

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

	def addURL(self, URLdef):
		URLdef = string.split(URLdef)
		U=URLdef[0]
		if len(URLdef)<2:
			T = U
		else:
			T = string.join(URLdef[1:])
		self.paragraph.append(' <a href="%s"><b>%s</b></a>'%(U,T))

if __name__=='__main__':
	if len(sys.argv) <> 2:
		print 'Usage: simple_doc.py myfile.txt  will create HTML and PDF versions'
		filename = 'sample.txt'
	else:
		filename = sys.argv[1]
	if os.path.isfile(filename):
		DoDualFormatPages([filename])
	else:
		print '%s not found' % filename
