#copyright ReportLab Inc. 2000
#see license.txt for license details
#history http://cvs.sourceforge.net/cgi-bin/cvsweb.cgi/docs/tools/platdemos.py?cvsroot=reportlab
#$Header: /tmp/reportlab/docs/tools/platdemos.py,v 1.1 2001/08/11 14:33:13 rgbecker Exp $
"""This includes some demos of platypus for use in the API proposal"""
from reportlab.lib import colors
from reportlab.pdfgen.canvas import Canvas
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import Frame
from reportlab.platypus import Flowable
from reportlab.platypus import Paragraph
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_LEFT, TA_RIGHT, TA_CENTER

captionStyle = ParagraphStyle('Caption', fontName='Times-Italic', fontSize=10, alignment=TA_CENTER)

class Figure(Flowable):
	def __init__(self, width, height, caption=""):
		Flowable.__init__(self)
		self.width = width
		self.figureHeight = height
		self.captionHeight = 0	# work out later
		self.caption = caption
		self.captionStyle = ParagraphStyle('Caption', fontName='Times-Italic', fontSize=12, spaceBefore=6, alignment=TA_CENTER)
		#must build paragraph now to get sequencing in synch
		#with rest of story
		self.captionPara = Paragraph(self.caption, self.captionStyle)

		self.spaceBefore = 12
		self.spaceAfter = 12

	def wrap(self, availWidth, availHeight):
		# try to get the caption aligned
		(w, h) = self.captionPara.wrap(self.width, availHeight - self.figureHeight)
		self.captionHeight = h
		self.height = self.captionHeight + self.figureHeight
		self.dx = 0.5 * (availWidth - self.width)
		return (self.width, self.height)

	def draw(self):
		self.canv.translate(self.dx, 0)
		self.drawCaption()
		self.canv.translate(0, self.captionHeight)
		self.drawBorder()
		self.drawFigure()

	def drawBorder(self):
		self.canv.rect(0, 0, self.width, self.figureHeight)

	def drawCaption(self):
		self.captionPara.drawOn(self.canv, 0, 0)

	def drawFigure(self):
		pass

def drawPage(canvas,x, y, width, height):
	#draws something which looks like a page
	pth = canvas.beginPath()
	corner = 0.05*width

	# shaded backdrop offset a little
	canvas.setFillColorRGB(0.5,0.5,0.5)
	canvas.rect(x + corner, y - corner, width, height, stroke=0, fill=1)

	#'sheet of paper' in light yellow
	canvas.setFillColorRGB(1,1,0.9)
	canvas.setLineWidth(0)
	canvas.rect(x, y, width, height, stroke=1, fill=1)

	#reset
	canvas.setFillColorRGB(0,0,0)
	canvas.setStrokeColorRGB(0,0,0)



class PageFigure(Figure):
	"""Shows a blank page in a frame, and draws on that.  Used in
	illustrations of how PLATYPUS works."""
	def __init__(self):
		Figure.__init__(self, 3*inch, 3*inch)
		self.caption = 'Figure 1 - a blank page'
		self.captionStyle = captionStyle

	def drawVirtualPage(self):
		pass

	def drawFigure(self):
		drawPage(self.canv, 0.625*inch, 0.25*inch, 1.75*inch, 2.5*inch)
		self.canv.translate(0.625*inch, 0.25*inch)
		self.canv.scale(1.75/8.27, 2.5/11.69)
		self.drawVirtualPage()

class PlatPropFigure1(PageFigure):
	"""This shows a page with a frame on it"""
	def __init__(self):
		PageFigure.__init__(self)
		self.caption = "Figure 1 - a page with a simple frame"
	def drawVirtualPage(self):
		demo1(self.canv)


def demo1(canvas):
	frame = Frame(
					2*inch,		# x
					4*inch,		# y at bottom
					4*inch,		# width
					5*inch,		# height
					showBoundary = 1  # helps us see what's going on
					)

	bodyStyle = ParagraphStyle('Body', fontName='Times-Roman', fontSize=24, leading=28, spaceBefore=6)

	para1 = Paragraph('Spam spam spam spam. ' * 5, bodyStyle)
	para2 = Paragraph('Eggs eggs eggs. ' * 5, bodyStyle)

	mydata = [para1, para2]

	#this does the packing and drawing.  The frame will consume
	#items from the front of the list as it prints them
	frame.addFromList(mydata,canvas)


def test1():
	c  = Canvas('platdemos.pdf')
	f = Frame(inch, inch, 6*inch, 9*inch, showBoundary=1)
	v = PlatPropFigure1()
	f.addFromList([v],c)
	c.save()

if __name__ == '__main__':
	test1()
