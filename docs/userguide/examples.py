

# magic function making module

test1 = """
def f(a,b):
    print "it worked", a, b
    return a+b
"""

test2 = """
def g(n):
    if n==0: return 1
    else: return n*g(n-1)
    """
    
testhello = """
def hello(c):
    from reportlab.platypus import layout
    inch = layout.inch
    # move the origin up and to the left
    c.translate(inch,inch) 
    # define a large font
    c.setFont("Helvetica", 14)
    # choose some colors
    c.setStrokeColorRGB(0.2,0.5,0.3)
    c.setFillColorRGB(1,0,1)
    # draw some lines
    c.line(0,0,0,2*inch)
    c.line(0,0,1*inch,0)
    # draw a rectangle
    c.rect(0.2*inch,0.2*inch,1*inch,1.5*inch, fill=1)
    # make text go straight up
    c.rotate(90)
    # change color
    c.setFillColorRGB(0,0,0.77)
    # say hello (note after rotate the y coord needs to be negative!)
    c.drawString(0.3*inch, -inch, "Hello World")
"""

glarp = "this would be a syntax error"

# D = dir()
g = globals()
Dprime = {}
from types import StringType
from string import strip
for (a,b) in g.items():
    if a[:4]=="test" and type(b) is StringType:
        #print 'for', a
        #print b
        b = strip(b)
        exec(b+'\n')

