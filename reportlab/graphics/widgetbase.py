#widgets.py
import string

from reportlab.graphics import shapes
from reportlab import config
from reportlab.lib import colors

class Widget(shapes.UserNode):
    """Base for all user-defined widgets.  Keep as simple as possible. Does
    not inherit from Shape so that we can rewrite shapes without breaking
    widgets and vice versa."""
    _attrMap = None

    
    def verify(self):
        """If the _attrMap attribute is not None, this
        checks all expected attributes are present; no
        unwanted attributes are present; and (if a
        checking function is found) checks each
        attribute has a valid value.  Either succeeds
        or raises an informative exception."""
        if self._attrMap is not None:
            for key in self.__dict__.keys():
                if key[0] <> '_':
                    assert self._attrMap.has_key(key), "Unexpected attribute %s found in %s" % (key, self)
            for (attr, checkerFunc) in self._attrMap.items():
                assert hasattr(self, attr), "Missing attribute %s from %s" % (key, self)
                if checkerFunc:
                    value = getattr(self, attr)
                    assert checkerFunc(value), "Invalid value %s for attribute %s in class %s" % (value, attr, self.__class__.__name__)
                    
    if config.shapeChecking:
        """This adds the ability to check every attribite assignment as it is made.
        It slows down shapes but is a big help when developing. It does not
        get defined if config.shapeChecking = 0"""
        def __setattr__(self, attr, value):
            """By default we verify.  This could be off
            in some parallel base classes."""
            if self._attrMap is not None:
                if attr[0:1] <> '_':
                    try:
                        checker = self._attrMap[attr]
                        if checker:
                            if not checker(value):
                                raise AttributeError, "Illegal assignment of '%s' to '%s' in class %s" % (value, attr, self.__class__.__name__)
                    except KeyError:
                        raise AttributeError, "Illegal attribute '%s' in class %s" % (attr, self.__class__.__name__)
            #if we are still here, set it.
            self.__dict__[attr] = value
            #print 'set %s.%s = %s' % (self.__class__.__name__, attr, value)

    def draw(self):
        raise shapes.NotImplementedError, "draw() must be implemented for each Widget!"
    
    def demo(self):
        raise shapes.NotImplementedError, "demo() must be implemented for each Widget!"

    def provideNode(self):
        return self.draw()

    def getProperties(self):
        """Returns a list of all properties which can be edited and
        which are not marked as private. This may include 'child
        widgets' or 'primitive shapes'.  You are free to override
        this and provide alternative implementations; the default
        one simply returns everything without a leading underscore."""
        # TODO when we need it, but not before -
        # expose sequence contents?
        props = {}
        for name in self.__dict__.keys():
            if name[0:1] <> '_':
                component = getattr(self, name)
                
                if shapes.isValidChild(component):
                    # child object, get its properties too
                    childProps = component.getProperties()
                    for (childKey, childValue) in childProps.items():
                        props['%s.%s' % (name, childKey)] = childValue
                else:
                    props[name] = component
               
        return props

    def setProperties(self, propDict):
        """Permits bulk setting of properties.  These may include
        child objects e.g. "chart.legend.width = 200".
        
        All assignments will be validated by the object as if they
        were set individually in python code.

        All properties of a top-level object are guaranteed to be
        set before any of the children, which may be helpful to
        widget designers."""
        
        childPropDicts = {}
        for (name, value) in propDict.items():
            parts = string.split(name, '.', 1)
            if len(parts) == 1:
                #simple attribute, set it now
                setattr(self, name, value)
            else:
                (childName, remains) = parts
                try:
                    childPropDicts[childName][remains] = value
                except KeyError:
                    childPropDicts[childName] = {remains: value}
        # now assign to children
        for (childName, childPropDict) in childPropDicts.items():
            child = getattr(self, childName)
            child.setProperties(childPropDict)
            
            
        
    def dumpProperties(self, prefix=""):
        """Convenience. Lists them on standard output.  You
        may provide a prefix - mostly helps to generate code
        samples for documentation."""
        propList = self.getProperties().items()
        propList.sort()
        if prefix:
            prefix = prefix + '.'
        for (name, value) in propList:
            print '%s%s = %s' % (prefix, name, value)
                    
                
                        

class TwoCircles(Widget):
    def __init__(self):
        self.leftCircle = shapes.Circle(100,100,20, fillColor=colors.red)
        self.rightCircle = shapes.Circle(300,100,20, fillColor=colors.red)

    def draw(self):
        return shapes.Group(self.leftCircle, self.rightCircle)

class Face(Widget):
    """This draws a face with two eyes.  It exposes a couple of properties
    to configure itself and hides all other details"""
    def checkMood(moodName):
        return (moodName in ('happy','sad','ok'))
    _attrMap = {
        'x': shapes.isNumber,
        'y': shapes.isNumber,
        'size': shapes.isNumber,
        'skinColor':shapes.isColorOrNone,
        'eyeColor': shapes.isColorOrNone,
        'mood': checkMood 
        }

        
    def __init__(self):
        self.x = 10
        self.y = 10
        self.size = 80
        self.skinColor = None
        self.eyeColor = colors.blue
        self.mood = 'happy'

    def demo(self):
        pass
    
    def draw(self):
        s = self.size  # abbreviate as we will use this a lot
        g = shapes.Group()
        g.transform = [1,0,0,1,self.x, self.y]
        # background
        g.add(shapes.Circle(s * 0.5, s * 0.5, s * 0.5, fillColor=self.skinColor))
        

        # left eye
        g.add(shapes.Circle(s * 0.35, s * 0.65, s * 0.1, fillColor=colors.white))
        g.add(shapes.Circle(s * 0.35, s * 0.65, s * 0.05, fillColor=self.eyeColor))
        
        # right eye
        g.add(shapes.Circle(s * 0.65, s * 0.65, s * 0.1, fillColor=colors.white))
        g.add(shapes.Circle(s * 0.65, s * 0.65, s * 0.05, fillColor=self.eyeColor))

        # nose
        g.add(shapes.Polygon(points=[s * 0.5, s * 0.6, s * 0.4, s * 0.3, s * 0.6, s * 0.3],
                             fillColor=None))

        # mouth
        if self.mood == 'happy':
            offset = -0.05
        elif self.mood == 'sad':
            offset = +0.05
        else:
            offset = 0
            
        g.add(shapes.Polygon(points = [
                                s * 0.3, s * 0.2, #left of mouth
                                s * 0.7, s * 0.2, #right of mouth
                                s * 0.6, s * (0.2 + offset), # the bit going up or down
                                s * 0.4, s * (0.2 + offset) # the bit going up or down
                                
                                ],
                             fillColor = colors.pink,
                             strokeColor = colors.red,
                             strokeWidth = s * 0.03
                             ))
        
        return g

class TwoFaces(Widget):
    def __init__(self):
        self.faceOne = Face()
        self.faceOne.mood = "happy"
        self.faceTwo = Face()
        self.faceTwo.x = 100
        self.faceTwo.mood = "sad"
        
    def draw(self):
        """Just return a group"""
        return shapes.Group(self.faceOne, self.faceTwo)

    def demo(self):
        """The default case already looks good enough,
        no implementation needed here"""
        pass
    
def test():
    d = shapes.Drawing(400, 200)
    tc = TwoCircles()
    d.add(tc)
    import renderPDF
    renderPDF.drawToFile(d, 'sample_widget.pdf', 'A Sample Widget')
    print 'saved sample_widget.pdf'

    d = shapes.Drawing(400, 200)
    f = Face()
    f.skinColor = colors.yellow
    f.mood = "sad"
    d.add(f)
    renderPDF.drawToFile(d, 'face.pdf', 'A Sample Widget')
    print 'saved face.pdf'

    tf = TwoFaces()
    

if __name__=='__main__':
    test()
    
    