from reportlab.lib import colors
from reportlab.lib.attrmap import *
from reportlab.pdfgen.canvas import Canvas
from reportlab.graphics.shapes import Group, Drawing, Ellipse, Wedge, String, STATE_DEFAULTS, Polygon, Line

def _getShaded(col,shd=None,shading=0.1):
    if shd is None:
        from reportlab.lib.colors import Blacker
        if col: shd = Blacker(col,1-shading)
    return shd

def _draw_3d_bar(G, x1, x2, y0, yhigh, xdepth, ydepth,
                fillColor=None, fillColorShaded=None,
                strokeColor=None, strokeWidth=1, shading=0.1):
    fillColorShaded = _getShaded(fillColor,fillColorShaded,shading)

    def _add_3d_bar(x1, x2, y1, y2, xoff, yoff,
                    G=G,strokeColor=strokeColor, strokeWidth=strokeWidth, fillColor=fillColor):
        G.add(Polygon((x1,y1,x1+xoff, y1+yoff,x2+xoff, y2+yoff,x2,y2),
            strokeWidth=strokeWidth, strokeColor=strokeColor, fillColor=fillColor))

    usd = max(y0, yhigh)
    if xdepth or ydepth:
        if y0!=yhigh:   #non-zero height
            _add_3d_bar( x2, x2, y0, yhigh, xdepth, ydepth,fillColor=fillColorShaded) #side

        _add_3d_bar(x1, x2, usd, usd, xdepth, ydepth)   #top

    G.add(Polygon((x1,y0,x2,y0,x2,yhigh,x1,yhigh),
        strokeColor=strokeColor, strokeWidth=strokeWidth, fillColor=fillColor)) #front

    if xdepth or ydepth:
        G.add(Line( x1, usd, x2, usd, strokeWidth=strokeWidth, strokeColor=strokeColor or fillColorShaded))

class _YStrip:
    def __init__(self,y0,y1, slope, fillColor, fillColorShaded, shading=0.1):
        self.y0 = y0
        self.y1 = y1
        self.slope = slope
        self.fillColor = fillColor
        self.fillColorShaded = _getShaded(fillColor,fillColorShaded,shading)

def _ystrip_cmp(a,b):
    return cmp(a.y1,b.y1)

def _ystrip_poly( x0, x1, y0, y1, xoff, yoff):
    return [x0,y0,x0+xoff,y0+yoff,x1+xoff,y1+yoff,x1,y1]

def _draw_3d_line( G, x0, x1, y0, y1,
                    xdepth, ydepth,
                    fillColor, fillColorShaded=None, xdelta=1, shading=0.1):
    depth_slope  = xdepth==0 and 1e150 or -ydepth/float(xdepth)
    if not hasattr(y0,'__getitem__'): y0 = (y0,)
    n = len(y0)
    if not hasattr(y1,'__getitem__'): y1 = (y1,)
    if not hasattr(fillColor,'__getitem__'): fillColor = (fillColor,)
    if fillColorShaded is None: fillColorShaded = n*[None]
    elif not hasattr(fillColorShaded,'__getitem__'): fillColorShaded = (fillColorShaded,)

    I = xrange(n)
    x = float(x1-x0)
    slope = x==0 and n*[1e150] or map(lambda y1,y0,x=x: (y1-y0)/x,y1,y0)

    def F(x,i, slope=slope, y0=y0, x0=x0):
        return float((x-x0)*slope[i]+y0[i])
    if x0>=x1: X=[(x0,x0)]
    else:
        x = x0
        X = []
        while x<=x1:
            xn = x+xdelta
            X.append((x,xn))
            x = xn
        if X[-1][0]==x1: del X[-1]
        else: X[-1][1] = x1
    Y = n*[None]
    for x in X:
        for i in I:
            Y[i] = _YStrip(F(x[0],i),F(x[1],i),slope[i],fillColor[i],fillColorShaded[i],shading)
        Y.sort(_ystrip_cmp)
        for y in Y:
            c = y.slope>depth_slope and y.fillColorShaded or y.fillColor
            print 'Poly([%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f])'% tuple(_ystrip_poly(x[0], x[1], y.y0, y.y1, xdepth, -ydepth))
            G.add(Polygon(_ystrip_poly(x[0], x[1], y.y0, y.y1, xdepth, ydepth),
                fillColor = c, strokeColor=c, strokeWidth=xdelta*0.6))

from math import pi, sin, cos
_pi_2 = pi*0.5
_2pi = 2*pi
_180_pi=180./pi

def _2rad(angle):
    return (angle*pi)/180

def mod_2pi(radians):
    radians = radians % _2pi
    if radians<-1e-6: radians += _2pi
    return radians

def _2deg(o):
    return o*_180_pi

def _360(a):
    a %= 360
    if a<-1e-6: a += 360
    return a

if __name__=='__main__':
    from reportlab.graphics.shapes import Drawing
    from reportlab.lib.colors import lightgrey, pink
    D = Drawing(300,200)
    _draw_3d_bar(D, 10, 20, 10, 50, 5, 5, fillColor=lightgrey, strokeColor=pink)
    _draw_3d_bar(D, 30, 40, 10, 45, 5, 5, fillColor=lightgrey, strokeColor=pink)

    _draw_3d_line(D, 50, 55, 10, 45, 5, 5, fillColor=lightgrey)
    _draw_3d_line(D, 55, 60, 45, 10, 5, 5, fillColor=lightgrey)
    D.save(formats=['pdf'],outDir='.',fnRoot='_draw_3d_bar')
