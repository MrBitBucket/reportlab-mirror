#copyright ReportLab Inc. 2000-2001
#see license.txt for license details
#history http://cvs.sourceforge.net/cgi-bin/cvsweb.cgi/reportlab/graphics/widgetbase.py?cvsroot=reportlab
#$Header: /tmp/reportlab/reportlab/graphics/widgetbase.py,v 1.20 2001/05/21 11:46:30 rgbecker Exp $
import string

from reportlab.graphics import shapes
from reportlab import rl_config
from reportlab.lib import colors
from reportlab.lib.validators import *
from reportlab.lib.attrmap import *


class PropHolder:
	'''Base for property holders'''

	_attrMap = None

	def verify(self):
		"""If the _attrMap attribute is not None, this
		checks all expected attributes are present; no
		unwanted attributes are present; and (if a
		checking function is found) checks each
		attribute has a valid value.  Either succeeds
		or raises an informative exception.
		"""

		if self._attrMap is not None:
			for key in self.__dict__.keys():
				if key[0] <> '_':
					msg = "Unexpected attribute %s found in %s" % (key, self)
					assert self._attrMap.has_key(key), msg
			for (attr, metavalue) in self._attrMap.items():
				msg = "Missing attribute %s from %s" % (key, self)
				assert hasattr(self, attr), msg
				value = getattr(self, attr)
				args = (value, attr, self.__class__.__name__)
				assert metavalue.validate(value), "Invalid value %s for attribute %s in class %s" % args


	if rl_config.shapeChecking:
		"""This adds the ability to check every attribute assignment
		as it is made. It slows down shapes but is a big help when
		developing. It does not get defined if rl_config.shapeChecking = 0.
		"""

		def __setattr__(self, name, value):
			"""By default we verify.  This could be off
			in some parallel base classes."""
			validateSetattr(self,name,value)


	def getProperties(self):
		"""Returns a list of all properties which can be edited and
		which are not marked as private. This may include 'child
		widgets' or 'primitive shapes'.  You are free to override
		this and provide alternative implementations; the default
		one simply returns everything without a leading underscore.
		"""

		from reportlab.lib.validators import isValidChild

		# TODO when we need it, but not before -
		# expose sequence contents?

		props = {}
		for name in self.__dict__.keys():
			if name[0:1] <> '_':
				component = getattr(self, name)

				if isValidChild(component):
					# child object, get its properties too
					childProps = component.getProperties()
					for (childKey, childValue) in childProps.items():
						#key might be something indexed like '[2].fillColor'
						#or simple like 'fillColor'; in the former case we
						#don't need a '.' between me and my child.
						if childKey[0] == '[':
							props['%s%s' % (name, childKey)] = childValue
						else:
							props['%s.%s' % (name, childKey)] = childValue
				else:
					props[name] = component

		return props


	def setProperties(self, propDict):
		"""Permits bulk setting of properties.	These may include
		child objects e.g. "chart.legend.width = 200".

		All assignments will be validated by the object as if they
		were set individually in python code.

		All properties of a top-level object are guaranteed to be
		set before any of the children, which may be helpful to
		widget designers.
		"""

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
		"""Convenience. Lists them on standard output.	You
		may provide a prefix - mostly helps to generate code
		samples for documentation.
		"""

		propList = self.getProperties().items()
		propList.sort()
		if prefix:
			prefix = prefix + '.'
		for (name, value) in propList:
			print '%s%s = %s' % (prefix, name, value)


class Widget(PropHolder, shapes.UserNode):
	"""Base for all user-defined widgets.  Keep as simple as possible. Does
	not inherit from Shape so that we can rewrite shapes without breaking
	widgets and vice versa."""

	def draw(self):
		msg = "draw() must be implemented for each Widget!"
		raise shapes.NotImplementedError, msg

	def demo(self):
		msg = "demo() must be implemented for each Widget!"
		raise shapes.NotImplementedError, msg

	def provideNode(self):
		return self.draw()

		
_ItemWrapper={}

class TypedPropertyCollection(PropHolder):
	"""A container with properties for objects of the same kind.

	This makes it easy to create lists of objects. You initialize
	it with a class of what it is to contain, and that is all you
	can add to it.	You can assign properties to the collection
	as a whole, or to a numeric index within it; if so it creates
	a new child object to hold that data.

	So:
		wedges = TypedPropertyCollection(WedgeProperties)
		wedges.strokeWidth = 2				  # applies to all
		wedges.strokeColor = colors.red		  # applies to all
		wedges[3].strokeColor = colors.blue   # only to one

	The last line should be taken as a prescription of how to
	create wedge no. 3 if one is needed; no error is raised if
	there are only two data points.
	"""

	def __init__(self, exampleClass):
		#give it same validation rules as what it holds
		self._prototype = exampleClass
		example = exampleClass()
		self._attrMap = example._attrMap.clone()
		#give it same default values as whhat it holds
		self.setProperties(example.getProperties())
		self._children = {}

	def __getitem__(self, index):
		try:
			return self._children[index]
		except KeyError:
			Klass = self._prototype
			if Klass in _ItemWrapper.keys():
				WKlass = _ItemWrapper[Klass]
			else:
				class WKlass(Klass):
					def __getattr__(self,name):
						try:
							return Klass.__getattr__(self,name)
						except:
							return getattr(self._parent,name)
				_ItemWrapper[Klass] = WKlass

			child = WKlass()
			child._parent = self
			for i in filter(lambda x,K=child.__dict__.keys(): x in K,child._attrMap.keys()):
				del child.__dict__[i]

			self._children[index] = child
			return child

	def __setitem__(self, key, value):
		msg = "This collection can only hold objects of type %s" % self._prototype.__name__
		assert isinstance(value, self._prototype), msg

	def __len__(self):
		return len(self._children.keys())
		
	def getProperties(self):
		# return any children which are defined and whatever
		# differs from the parent
		props = {}

		for (key, value) in Widget.getProperties(self).items():
			props['%s' % key] = value

		for idx in self._children.keys():
			childProps = self._children[idx].getProperties()
			for (key, value) in childProps.items():
				parentValue = getattr(self, key)
				if parentValue <> value:
					newKey = '[%s].%s' % (idx, key)
					props[newKey] = value

		return props

	def setVector(self,**kw):
		for name, value in kw.items():
			for i in xrange(len(value)):
				setattr(self[i],name,value[i])

## No longer needed!
class StyleProperties(PropHolder):
	"""A container class for attributes used in charts and legends.

	Attributes contained can be those for any graphical element
	(shape?) in the ReportLab graphics package. The idea for this
	container class is to be useful in combination with legends
	and/or the individual appearance of data series in charts.

	A legend could be as simple as a wrapper around a list of style
	properties, where the 'desc' attribute contains a descriptive
	string and the rest could be used by the legend e.g. to draw 
	something like a color swatch. The graphical presentation of
	the legend would be its own business, though.

	A chart could be inspecting a legend or, more directly, a list
	of style properties to pick individual attributes that it knows
	about in order to render a particular row of the data. A bar
	chart e.g. could simply use 'strokeColor' and 'fillColor' for
	drawing the bars while a line chart could also use additional
	ones like strokeWidth.
	"""
	
	_attrMap = AttrMap(
		strokeWidth = AttrMapValue(isNumber),
		strokeLineCap = AttrMapValue(isNumber),
		strokeLineJoin = AttrMapValue(isNumber),
		strokeMiterLimit = AttrMapValue(None),
		strokeDashArray = AttrMapValue(isListOfNumbersOrNone),
		strokeOpacity = AttrMapValue(isNumber),
		strokeColor = AttrMapValue(isColorOrNone),
		fillColor = AttrMapValue(isColorOrNone),
		desc = AttrMapValue(isString),
		)

	def __init__(self, **kwargs):
		"Initialize with attributes if any."

		for k, v in kwargs.items():
			setattr(self, k, v)
			

	def __setattr__(self, name, value):
		"Verify attribute name and value, before setting it."
		validateSetattr(self,name,value)


class TwoCircles(Widget):
	def __init__(self):
		self.leftCircle = shapes.Circle(100,100,20, fillColor=colors.red)
		self.rightCircle = shapes.Circle(300,100,20, fillColor=colors.red)

	def draw(self):
		return shapes.Group(self.leftCircle, self.rightCircle)


class Face(Widget):
	"""This draws a face with two eyes.

	It exposes a couple of properties
	to configure itself and hides all other details.
	"""

	_attrMap = AttrMap(
		x = AttrMapValue(isNumber),
		y = AttrMapValue(isNumber),
		size = AttrMapValue(isNumber),
		skinColor = AttrMapValue(isColorOrNone),
		eyeColor = AttrMapValue(isColorOrNone),
		mood = AttrMapValue(OneOf(('happy','sad','ok'))),
		)

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
		g.add(shapes.Polygon(
			points=[s * 0.5, s * 0.6, s * 0.4, s * 0.3, s * 0.6, s * 0.3],
			fillColor=None))

		# mouth
		if self.mood == 'happy':
			offset = -0.05
		elif self.mood == 'sad':
			offset = +0.05
		else:
			offset = 0

		g.add(shapes.Polygon(
			points = [
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
	from reportlab.graphics.charts.piecharts import WedgeProperties
	wedges = TypedPropertyCollection(WedgeProperties)
	wedges.fillColor = colors.red
	wedges.setVector(fillColor=(colors.blue,colors.green,colors.white))
	print len(_ItemWrapper)

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
	d.add(f, name='theFace')
	print 'drawing 1 properties:'
	d.dumpProperties()
	renderPDF.drawToFile(d, 'face.pdf', 'A Sample Widget')
	print 'saved face.pdf'

	d2 = d.expandUserNodes0()
	renderPDF.drawToFile(d2, 'face_copy.pdf', 'An expanded drawing')
	print 'saved face_copy.pdf'
	print 'drawing 2 properties:'
	d2.dumpProperties()


if __name__=='__main__':
	test()
