import string
from reportlab.graphics.shapes import *
from reportlab.graphics.widgetbase import Widget
from reportlab.lib import colors
from reportlab.pdfbase.pdfmetrics import stringWidth

class Label(Widget):
    """A text label to attach to something else, such as a chart axis.

    This allows you to specify an offset, angle and many anchor
    properties relative to the label's origin.  It allows, for example,
    angled multiline axis labels.
    """
    # fairly straight port of Robin Becker's textbox.py to new widgets
    # framework.
    _attrMap = {
        'dx':isNumber,
        'dy':isNumber,
        'angle':isNumber,
        'boxAnchor':OneOf(('nw','n','ne','w','c','e','sw','s','se')),
        'boxStrokeColor':isColorOrNone,
        'boxStrokeWidth':isNumber,
        'boxFillColor':isColorOrNone,
        'text':isString,
        'fontName':isString,
        'fontSize':isNumber,
        'leading':isNumber,
        'textAnchor':OneOf(('start','middle','end'))
        }
    def __init__(self):
        self._x = 100
        self._y = 75
        self._text = 'Multi-Line\nString' 

        self.dx = 0
        self.dy = 0
        self.angle = 0
        self.boxAnchor = 'c'
        self.boxStrokeColor = None  #boxStroke
        self.boxStrokeWidth = 0.5 #boxStrokeWidth
        self.boxFillColor = None
        self.fontName = STATE_DEFAULTS['fontName']
        self.fontSize = STATE_DEFAULTS['fontSize']
        self.leading = self.fontSize * 1.2
        self.textAnchor = 'start'

    def setText(self, text):
        """Set the text property.  May contain embedded newline characters.
        Called by the containing chart or axis."""
        self._text = text

    def setOrigin(self, x, y):
        """Set the origin.  This would be the tick mark or bar top relative to
        which it is defined.  Called by the containing chart or axis."""
        self._x = x
        self._y = y
        
    def demo(self):
        """This shows a label positioned with its top right corner
        at the top centre of the drawing, and rotated 45 degrees."""
        d = Drawing(200, 100)
        
        self.boxStrokeColor = colors.green
        self.boxFillColor = colors.beige
        self.boxAnchor = 'ne'
        self.angle = 45
        self.setOrigin(100,100)
        self.setText('Another\nMulti-Line\nString')

        g = Group(transform=translate(0, -100))

        #BUG - if I do
        #g.add(self) then the transform of self gets ignored
        #by the renderer
        
        g.add(self.draw())
        d.add(g)
        #d.add(self)
        return d

    def computeSize(self):
        # the thing will draw in its own coordinate system
        self._lines = string.split(self._text, '\n')
        self._lineWidths = []
        w = 0
        for line in self._lines:
            thisWidth = stringWidth(line, self.fontName, self.fontSize)
            self._lineWidths.append(thisWidth)
            w = max(w,thisWidth)
        self._width = w
        self._height = self.leading * len(self._lines)
        
        self._top = 0        
        if self.boxAnchor in ['n','ne','nw']:
            self._top = 0
            self._bottom = - self._height
        elif self.boxAnchor in ['s','sw','se']:
            self._top = self._height
            self._bottom = 0
        else: 
            self._top = 0.5 * self._height
            self._bottom = - 0.5 * self._height
            
        if self.boxAnchor in ['ne','e','se']:
            self._left = - self._width
            self._right = 0
        elif self.boxAnchor in ['nw','w','sw']:
            self._left = 0
            self._right = self._width
        else:
            self._left = - self._width * 0.5
            self._right = self._width * 0.5
            
        
    def draw(self):
        self.computeSize()
        g = Group()
        g.translate(self._x + self.dx, self._y + self.dy)
        g.rotate(self.angle)


        y = self._top - self.fontSize
        if self.textAnchor == 'start':
            x = self._left
        elif self.textAnchor == 'middle':
            x = self._left + 0.5 * self._width
        else:
            x = self._left + self._width

        # paint box behind text just in case they
        # fill it
        if self.boxStrokeColor is not None:
            g.add(Rect(self._left,
                       self._bottom,
                       self._width,
                       self._height,
                       strokeColor=self.boxStrokeColor,
                       strokeWidth=self.boxStrokeWidth,
                       fillColor=self.boxFillColor)
                  )

            
        for line in self._lines:
            g.add(String(x, y, line, textAnchor = self.textAnchor))
            y = y - self.leading

        return g
    
        

if __name__=='__main__':
    from reportlab.graphics.renderPDF import drawToFile
    tx = Label()
    d = tx.demo()
    drawToFile(d, 'textlabel.pdf', 'example text label')
    
