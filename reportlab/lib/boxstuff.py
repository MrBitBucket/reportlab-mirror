#Copyright ReportLab Europe Ltd. 2000-2006
#see license.txt for license details
__version__=''' $Id$ '''
def anchorAdjustXY(anchor,x,y,width,height):
    if anchor not in ('sw','s','se'):
        if anchor in ('e','c','w'):
            y -= height/2.
        else:
            y -= height
    if anchor not in ('nw','w','sw'):
        if anchor in ('n','c','s'):
            x -= width/2.
        else:
            x -= width
    return x,y

def aspectRatioFix(preserve,anchor,x,y,width,height,imWidth,imHeight):
    scale = 1.0
    if width is None:
        width = imWidth
    if height is None:
        height = imHeight
    if width<0:
        width = -width
        x -= width
    if height<0:
        height = -height
        y -= height
    if preserve:
        imWidth = abs(imWidth)
        imHeight = abs(imHeight)
        scale = min(width/float(imWidth),height/float(imHeight))
        owidth = width
        oheight = height
        width = scale*imWidth-1e-8
        height = scale*imHeight-1e-8
        if anchor not in ('n','c','s'):
            dx = 0.5*(owidth-width)
            if anchor in ('ne','e','se'):
                x -= dx
            else:
                x += dx
        if anchor not in ('e','c','w'):
            dy = 0.5*(oheight-height)
            if anchor in ('nw','n','ne'):
                y -= dy
            else:
                y += dy
    return x,y, width, height, scale
