#copyright ReportLab Inc. 2001
#see license.txt for license details
#history http://cvs.sourceforge.net/cgi-bin/cvsweb.cgi/reportlab/graphics/shapes.py?cvsroot=reportlab
#$Header: /tmp/reportlab/reportlab/graphics/shapes.py,v 1.59 2001/10/09 15:00:50 rgbecker Exp $
# core of the graphics library - defines Drawing and Shapes
"""
"""

import string, os, sys
from math import pi, cos, sin, tan
from types import FloatType, IntType, ListType, TupleType, StringType
from pprint import pprint

from reportlab.platypus import Flowable
from reportlab.rl_config import shapeChecking, _verbose
from reportlab.lib import logger
from reportlab.lib import colors
from reportlab.lib.validators import *
from reportlab.lib.attrmap import *
from reportlab.pdfbase.pdfmetrics import stringWidth

class NotImplementedError(Exception):
	pass

# two constants for filling rules
NON_ZERO_WINDING = 'Non-Zero Winding'
EVEN_ODD = 'Even-Odd'

## these can be overridden at module level before you start
#creating shapes.  So, if using a special color model,
#this provides support for the rendering mechanism.
#you can change defaults globally before you start
#making shapes; one use is to substitute another
#color model cleanly throughout the drawing.

STATE_DEFAULTS = {	 # sensible defaults for all
	'transform': (1,0,0,1,0,0),

	# styles follow SVG naming
	'strokeColor': colors.black,
	'strokeWidth': 1,
	'strokeLineCap': 0,
	'strokeLineJoin': 0,
	'strokeMiterLimit' : 'TBA',  # don't know yet so let bomb here
	'strokeDashArray': None,
	'strokeOpacity': 1.0,  #100%

	'fillColor': colors.black,	 #...or text will be invisible
	#'fillRule': NON_ZERO_WINDING, - these can be done later
	#'fillOpacity': 1.0,  #100% - can be done later

	'fontSize': 10,
	'fontName': 'Times-Roman',
	'textAnchor':  'start' # can be start, middle, end, inherited
	}


####################################################################
# math utilities.  These could probably be moved into lib
# somewhere.
####################################################################

# constructors for matrices:
def nullTransform():
	return (1, 0, 0, 1, 0, 0)

def translate(dx, dy):
	return (1, 0, 0, 1, dx, dy)

def scale(sx, sy):
	return (sx, 0, 0, sy, 0, 0)

def rotate(angle):
	a = angle * pi/180
	return (cos(a), sin(a), -sin(a), cos(a), 0, 0)

def skewX(angle):
	a = angle * pi/180
	return (1, 0, tan(a), 1, 0, 0)

def skewY(angle):
	a = angle * pi/180
	return (1, tan(a), 0, 1, 0, 0)

def mmult(A, B):
	"A postmultiplied by B"
	# I checked this RGB
	# [a0 a2 a4]	[b0 b2 b4]
	# [a1 a3 a5] *	[b1 b3 b5]
	# [		 1 ]	[	   1 ]
	#
	return (A[0]*B[0] + A[2]*B[1],
			A[1]*B[0] + A[3]*B[1],
			A[0]*B[2] + A[2]*B[3],
			A[1]*B[2] + A[3]*B[3],
			A[0]*B[4] + A[2]*B[5] + A[4],
			A[1]*B[4] + A[3]*B[5] + A[5])

def inverse(A):
	"For A affine 2D represented as 6vec return 6vec version of A**(-1)"
	# I checked this RGB
	det = float(A[0]*A[3] - A[2]*A[1])
	R = [A[3]/det, -A[1]/det, -A[2]/det, A[0]/det]
	return tuple(R+[-R[0]*A[4]-R[2]*A[5],-R[1]*A[4]-R[3]*A[5]])

def zTransformPoint(A,v):
	"Apply the homogenous part of atransformation a to vector v --> A*v"
	return (A[0]*v[0]+A[2]*v[1],A[1]*v[0]+A[3]*v[1])

def transformPoint(A,v):
	"Apply transformation a to vector v --> A*v"
	return (A[0]*v[0]+A[2]*v[1]+A[4],A[1]*v[0]+A[3]*v[1]+A[5])

def transformPoints(matrix, V):
	return map(transformPoint, V)

def zTransformPoints(matrix, V):
	return map(lambda x,matrix=matrix: zTransformPoint(matrix,x), V)

def _textBoxLimits(text, font, fontSize, leading, textAnchor, boxAnchor):
	w = 0
	for t in text:
		w = max(w,stringWidth(t,font, fontSize))

	h = len(text)*leading
	yt = fontSize
	if boxAnchor[0]=='s':
		yb = -h
		yt = yt - h
	elif boxAnchor[0]=='n':
		yb = 0
	else:
		yb = -h/2.0
		yt = yt + yb

	if boxAnchor[-1]=='e':
		xb = -w
		if textAnchor=='end': xt = 0
		elif textAnchor=='start': xt = -w
		else: xt = -w/2.0
	elif boxAnchor[-1]=='w':
		xb = 0
		if textAnchor=='end': xt = w
		elif textAnchor=='start': xt = 0
		else: xt = w/2.0
	else:
		xb = -w/2.0
		if textAnchor=='end': xt = -xb
		elif textAnchor=='start': xt = xb
		else: xt = 0

	return xb, yb, w, h, xt, yt

def _rotatedBoxLimits( x, y, w, h, angle):
	'''
	Find the corner points of the rotated w x h sized box at x,y
	return the corner points and the min max points in the original space
	'''
	C = zTransformPoints(rotate(angle),((x,y),(x+w,y),(x+w,y+h),(x,y+h)))
	X = map(lambda x: x[0], C)
	Y = map(lambda x: x[1], C)
	return min(X), max(X), min(Y), max(Y), C


	#################################################################
	#
	#	 And now the shapes themselves....
	#
	#################################################################

class Shape:
	"""Base class for all nodes in the tree. Nodes are simply
	packets of data to be created, stored, and ultimately
	rendered - they don't do anything active.  They provide
	convenience methods for verification but do not
	check attribiute assignments or use any clever setattr
	tricks this time."""

	_attrMap = AttrMap()

	def __init__(self, keywords={}):
		"""In general properties may be supplied to the
		constructor."""

		for key, value in keywords.items():
			#print 'setting keyword %s.%s = %s' % (self, key, value)
			setattr(self, key, value)

	def copy(self):
		"""Return a clone of this shape."""

		# implement this in the descendants as they need the right init methods.
		raise NotImplementedError, "No copy method implemented for %s" % self.__class__.__name__

	def getProperties(self,recur=1):
		"""Interface to make it easy to extract automatic
		documentation"""

		#basic nodes have no children so this is easy.
		#for more complex objects like widgets you
		#may need to override this.
		props = {}
		for key, value in self.__dict__.items():
			if key[0:1] <> '_':
				props[key] = value
		return props

	def setProperties(self, props):
		"""Supports the bulk setting if properties from,
		for example, a GUI application or a config file."""

		self.__dict__.update(props)
		#self.verify()

	def dumpProperties(self, prefix=""):
		"""Convenience. Lists them on standard output.	You
		may provide a prefix - mostly helps to generate code
		samples for documentation."""

		propList = self.getProperties().items()
		propList.sort()
		if prefix:
			prefix = prefix + '.'
		for (name, value) in propList:
			print '%s%s = %s' % (prefix, name, value)

	def verify(self):
		"""If the programmer has provided the optional
		_attrMap attribute, this checks all expected
		attributes are present; no unwanted attributes
		are present; and (if a checking function is found)
		checks each attribute.	Either succeeds or raises
		an informative exception."""

		if self._attrMap is not None:
			for key in self.__dict__.keys():
				if key[0] <> '_':
					assert self._attrMap.has_key(key), "Unexpected attribute %s found in %s" % (key, self)
			for (attr, metavalue) in self._attrMap.items():
				assert hasattr(self, attr), "Missing attribute %s from %s" % (attr, self)
				value = getattr(self, attr)
				assert metavalue.validate(value), "Invalid value %s for attribute %s in class %s" % (value, attr, self.__class__.__name__)

	if shapeChecking:
		"""This adds the ability to check every attribute assignment as it is made.
		It slows down shapes but is a big help when developing. It does not
		get defined if rl_config.shapeChecking = 0"""
		def __setattr__(self, attr, value):
			"""By default we verify.  This could be off
			in some parallel base classes."""
			validateSetattr(self,attr,value)	#from reportlab.lib.attrmap

class Group(Shape):
	"""Groups elements together.  May apply a transform
	to its contents.  Has a publicly accessible property
	'contents' which may be used to iterate over contents.
	In addition, child nodes may be given a name in which
	case they are subsequently accessible as properties."""

	_attrMap = AttrMap(
		transform = AttrMapValue(isTransform,desc="Coordinate transformation to apply"),
		contents = AttrMapValue(isListOfShapes,desc="Contained drawable elements"),
		)

	def __init__(self, *elements, **keywords):
		"""Initial lists of elements may be provided to allow
		compact definitions in literal Python code.  May or
		may not be useful."""

		# Groups need _attrMap to be an instance rather than
		# a class attribute, as it may be extended at run time.
		self._attrMap = self._attrMap.clone()
		self.contents = []
		self.transform = (1,0,0,1,0,0)
		for elt in elements:
			self.add(elt)
		# this just applies keywords; do it at the end so they
		#don;t get overwritten
		Shape.__init__(self, keywords)

	def _addNamedNode(self,name,node):
		'if name is not None add an attribute pointing to node and add to the attrMap'
		if name:
			if name not in self._attrMap.keys():
				self._attrMap[name] = AttrMapValue(isValidChild)
			setattr(self, name, node)

	def add(self, node, name=None):
		"""Appends child node to the 'contents' attribute.	In addition,
		if a name is provided, it is subsequently accessible by name"""

		# propagates properties down
		assert isValidChild(node), "Can only add Shape or UserNode objects to a Group"
		self.contents.append(node)
		self._addNamedNode(name,node)

	def insert(self, i, n, name=None):
		'Inserts sub-node n in contents at specified location'
		assert isValidChild(n), "Can only insert Shape or UserNode objects in a Group"
		if i<0:
			self.contents[i:i] =[n]
		else:
			self.contents.insert(i,n)
		self._addNamedNode(name,n)

	def expandUserNodes(self):
		"""Return a new object which only contains primitive shapes."""

		# many limitations - shared nodes become multiple ones,
		obj = self.__class__()
		obj._attrMap = self._attrMap.clone()
		if hasattr(obj,'transform'): obj.transform = self.transform[:]

		self_contents = self.contents
		for child in self_contents:
			if isinstance(child, UserNode):
				newChild = child.provideNode()
			elif isinstance(child, Group):
				newChild = child.expandUserNodes()
			else:
				newChild = child.copy()
			obj.contents.append(newChild)

		self._copyNamedContents(obj)
		return obj

	def _explode(self):
		''' return a fully expanded object'''
		obj = self.__class__()

	def _copyContents(self,obj):
		for child in self.contents:
			obj.contents.append(child)

	def _copyNamedContents(self,obj,aKeys=None,noCopy=('contents',)):
		from copy import copy
		self_contents = self.contents
		if not aKeys: aKeys = self._attrMap.keys()
		for (k, v) in self.__dict__.items():
			if k in self_contents:
				pos = self_contents.index(v)
				setattr(obj, oldKey, obj.contents[pos])
			elif k in aKeys and k not in noCopy:
				setattr(obj, k, copy(v))

	def _copy(self,obj):
		"""copies to obj"""
		obj._attrMap = self._attrMap.clone()
		self._copyContents(obj)
		self._copyNamedContents(obj)
		return obj

	def copy(self):
		"""returns a copy"""
		return self._copy(self.__class__())

	def rotate(self, theta):
		"""Convenience to help you set transforms"""
		self.transform = mmult(self.transform, rotate(theta))

	def translate(self, dx, dy):
		"""Convenience to help you set transforms"""
		self.transform = mmult(self.transform, translate(dx, dy))

	def scale(self, sx, sy):
		"""Convenience to help you set transforms"""
		self.transform = mmult(self.transform, scale(sx, sy))


	def skew(self, kx, ky):
		"""Convenience to help you set transforms"""
		self.transform = mmult(mmult(self.transform, skewX(kx)),skewY(ky))

	def shift(self, x, y):
		'''Convenience function to set the origin arbitrarily'''
		self.transform = self.transform[:-2]+(x,y)

	def asDrawing(self, width, height):
		"""	Convenience function to make a drawing from a group
			After calling this the instance will be a drawing!
		"""
		self.__class__ = Drawing
		self._attrMap.update(self._xtraAttrMap)
		self.width = width
		self.height = height

	def getContents(self):
		'''Return the list of things to be rendered
		override to get more complicated behaviour'''
		b = getattr(self,'background',None)
		C = self.contents
		if b and b not in C: C = [b]+C
		return C

class Drawing(Group, Flowable):
	"""Outermost container; the thing a renderer works on.
	This has no properties except a height, width and list
	of contents."""

	_xtraAttrMap = AttrMap(
		width = AttrMapValue(isNumber,desc="Drawing width in points."),
		height = AttrMapValue(isNumber,desc="Drawing height in points."),
		canv = AttrMapValue(None),
		background = AttrMapValue(isValidChildOrNone,desc="Background widget for the drawing"),
		hAlign = AttrMapValue(OneOf("LEFT", "RIGHT", "CENTER", "CENTRE"), desc="Alignment within parent document"),
		vAlign = AttrMapValue(OneOf("TOP", "BOTTOM", "CENTER", "CENTRE"), desc="Alignment within parent document")
		)

	_attrMap = AttrMap(BASE=Group)
	_attrMap.update(_xtraAttrMap)

	def __init__(self, width=400, height=200, *nodes, **keywords):
		self.background = None
		apply(Group.__init__,(self,)+nodes,keywords)
		self.width = width
		self.height = height
		self.hAlign = 'LEFT'
		self.vAlign = 'BOTTOM'

	def draw(self):
		"""This is used by the Platypus framework to let the document
		draw itself in a story.  It is specific to PDF and should not
		be used directly."""

		import renderPDF
		R = renderPDF._PDFRenderer()
		R.draw(self, self.canv, 0, 0)

	def expandUserNodes(self):
		"""Return a new drawing which only contains primitive shapes."""
		obj = Group.expandUserNodes(self)
		obj.width = self.width
		obj.height = self.height
		return obj


	def copy(self,obj):
		"""Returns a copy"""
		return self._copy(Drawing(self.width, self.height))

	def asGroup(self,*args,**kw):
		return self._copy(apply(Group,args,kw))

	def save(self, formats=None, verbose=None, fnRoot=None, outDir=None):
		from reportlab import rl_config
		"Saves copies of self in desired location and formats"
		ext = ''
		if not fnRoot:
			fnRoot = getattr(self,'fileNamePattern',(self.__class__.__name__+'%03d'))
			try:
				fnRoot = fnRoot % getattr(self,'chartId',0)
			except TypeError, err:
				if str(err) != 'not all arguments converted': raise

		if os.path.isabs(fnRoot):
			outDir, fnRoot = os.path.split(fnRoot)
		else:
			outDir = outDir or getattr(self,'outDir','.')
		if not os.path.isabs(outDir): outDir = os.path.join(os.path.dirname(sys.argv[0]),outDir)
		if not os.path.isdir(outDir): os.makedirs(outDir)
		fnroot = os.path.normpath(os.path.join(outDir,fnRoot))
		plotMode = os.path.splitext(fnroot)
		if string.lower(plotMode[1][1:]) in ['pdf','eps','gif','png','jpg','jpeg','tiff','tif']:
			fnroot = plotMode[0]

		plotMode, verbose = formats or getattr(self,'formats',['pdf']), verbose or getattr(self,'verbose',_verbose)
		_saved = logger.warnOnce.enabled, logger.infoOnce.enabled
		logger.warnOnce.enabled = logger.infoOnce.enabled = verbose
		if 'pdf' in plotMode:
			from reportlab.graphics import renderPDF
			filename = fnroot+'.pdf'
			if verbose: print "generating PDF file %s" % filename
			renderPDF.drawToFile(self, filename, fnroot,showBoundary=getattr(self,'showBorder',rl_config.showBoundary))
			ext = ext +  '/.pdf'

		if 'gif' in plotMode:
			from reportlab.graphics import renderPM
			filename = fnroot+'.gif'
			if verbose: print "generating GIF file %s" % filename
			renderPM.drawToFile(self, filename,fmt='GIF',showBoundary=getattr(self,'showBorder',rl_config.showBoundary))
			ext = ext +  '/.gif'

		if 'png' in plotMode:
			from reportlab.graphics import renderPM
			filename = fnroot+'.png'
			if verbose: print "generating PNG file %s" % filename
			renderPM.drawToFile(self, filename,fmt='PNG',showBoundary=getattr(self,'showBorder',rl_config.showBoundary))
			ext = ext +  '/.png'

		if 'tif' in plotMode:
			from reportlab.graphics import renderPM
			filename = fnroot+'.tif'
			if verbose: print "generating TIFF file %s" % filename
			renderPM.drawToFile(self, filename,fmt='TIFF',showBoundary=getattr(self,'showBorder',rl_config.showBoundary))
			ext = ext +  '/.tif'

		if 'jpg' in plotMode:
			from reportlab.graphics import renderPM
			filename = fnroot+'.jpg'
			if verbose: print "generating JPG file %s" % filename
			renderPM.drawToFile(self, filename,fmt='JPEG',showBoundary=getattr(self,'showBorder',rl_config.showBoundary))
			ext = ext +  '/.jpg'

		if 'eps' in plotMode:
			from fidelity.epscharts import renderPS_SEP
			filename = fnroot+'.eps'
			if verbose: print "generating EPS file %s" % filename
			renderPS_SEP.drawToFile(self,
								filename,
								title = fnroot,
								dept = getattr(self,'EPS_info',['Testing'])[0],
								company = getattr(self,'EPS_info',['','ReportLab'])[1],
								preview = getattr(self,'preview',1),
								showBoundary=getattr(self,'showBorder',rl_config.showBoundary))

			ext = ext +  '/.eps'

		logger.warnOnce.enabled, logger.infoOnce.enabled = _saved
		return ext and fnroot+ext[1:] or ''

class _DrawingEditorMixin:
	'''This is a mixin to provide functionality for edited drawings'''
	def _add(self,obj,value,name=None,validate=None,desc=None,pos=None):
		'''
		effectively setattr(obj,name,value), but takes care of things with _attrMaps etc
		'''
		ivc = isValidChild(value)
		if name and hasattr(obj,'_attrMap'):
			if not obj.__dict__.has_key('_attrMap'):
				obj._attrMap = obj._attrMap.clone()
			if ivc and validate is None: validate = isValidChild
			obj._attrMap[name] = AttrMapValue(validate,desc)
		if hasattr(obj,'add') and ivc:
			if pos:
				obj.insert(pos,value,name)
			else:
				obj.add(value,name)
		elif name:
			setattr(obj,name,value)
		else:
			raise ValueError, "Can't add, need name"

class LineShape(Shape):
	# base for types of lines

	_attrMap = AttrMap(
		strokeColor = AttrMapValue(isColorOrNone),
		strokeWidth = AttrMapValue(isNumber),
		strokeLineCap = AttrMapValue(None),
		strokeLineJoin = AttrMapValue(None),
		strokeMiterLimit = AttrMapValue(isNumber),
		strokeDashArray = AttrMapValue(isListOfNumbersOrNone),
		)

	def __init__(self, kw):
		self.strokeColor = STATE_DEFAULTS['strokeColor']
		self.strokeWidth = 1
		self.strokeLineCap = 0
		self.strokeLineJoin = 0
		self.strokeMiterLimit = 0
		self.strokeDashArray = None
		self.setProperties(kw)


class Line(LineShape):
	_attrMap = AttrMap(
		strokeColor = AttrMapValue(isColorOrNone),
		strokeWidth = AttrMapValue(isNumber),
		strokeLineCap = AttrMapValue(None),
		strokeLineJoin = AttrMapValue(None),
		strokeMiterLimit = AttrMapValue(isNumber),
		strokeDashArray = AttrMapValue(isListOfNumbersOrNone),
		x1 = AttrMapValue(isNumber),
		y1 = AttrMapValue(isNumber),
		x2 = AttrMapValue(isNumber),
		y2 = AttrMapValue(isNumber),
		)

	def __init__(self, x1, y1, x2, y2, **kw):
		LineShape.__init__(self, kw)
		self.x1 = x1
		self.y1 = y1
		self.x2 = x2
		self.y2 = y2


class SolidShape(Shape):
	# base for anything with outline and content

	_attrMap = AttrMap(
		strokeColor = AttrMapValue(isColorOrNone),
		strokeWidth = AttrMapValue(isNumber),
		strokeLineCap = AttrMapValue(None),
		strokeLineJoin = AttrMapValue(None),
		strokeMiterLimit = AttrMapValue(isNumber),
		strokeDashArray = AttrMapValue(None),
		fillColor = AttrMapValue(isColorOrNone),
		)

	def __init__(self, kw):
		self.strokeColor = STATE_DEFAULTS['strokeColor']
		self.strokeWidth = 1
		self.strokeLineCap = 0
		self.strokeLineJoin = 0
		self.strokeMiterLimit = 0
		self.strokeDashArray = None
		self.fillColor = STATE_DEFAULTS['fillColor']
		# do this at the end so keywords overwrite
		#the above settings
		Shape.__init__(self, kw)


# path operator  constants
_MOVETO, _LINETO, _CURVETO, _CLOSEPATH = range(4)
_PATH_OP_ARG_COUNT = (2, 2, 6, 0)  # [moveTo, lineTo, curveTo, closePath]
_PATH_OP_NAMES=['moveTo','lineTo','curveTo','closePath']

def _renderPath(path, drawFuncs):
	"""Helper function for renderers."""
	# this could be a method of Path...
	points = path.points
	i = 0
	hadClosePath = 0
	hadMoveTo = 0
	for op in path.operators:
		nArgs = _PATH_OP_ARG_COUNT[op]
		func = drawFuncs[op]
		j = i + nArgs
		apply(func, points[i:j])
		i = j
		if op == _CLOSEPATH:
			hadClosePath = hadClosePath + 1
		if op == _MOVETO:
			hadMoveTo = hadMoveTo + 1
	return hadMoveTo == hadClosePath


class Path(SolidShape):
	"""Path, made up of straight lines and bezier curves."""
	
	_attrMap = AttrMap(
		strokeColor = AttrMapValue(None),
		strokeWidth = AttrMapValue(isNumber),
		strokeLineCap = AttrMapValue(None),
		strokeLineJoin = AttrMapValue(None),
		strokeMiterLimit = AttrMapValue(None),
		strokeDashArray = AttrMapValue(isListOfNumbersOrNone),
		fillColor = AttrMapValue(None),
		points = AttrMapValue(isListOfNumbers),
		operators = AttrMapValue(isListOfNumbers),
		isClipPath = AttrMapValue(isBoolean),
		)

	def __init__(self, points=None, operators=None, isClipPath=0, **kw):
		SolidShape.__init__(self, kw)
		if points is None:
			points = []
		if operators is None:
			operators = []
		assert len(points) % 2 == 0, 'Point list must have even number of elements!'
		self.points = points
		self.operators = operators
		self.isClipPath = isClipPath

	def copy(self):
		new = Path(self.points[:], self.operators[:])
		new.setProperties(self.getProperties())
		return new

	def moveTo(self, x, y):
		self.points.extend([x, y])
		self.operators.append(_MOVETO)

	def lineTo(self, x, y):
		self.points.extend([x, y])
		self.operators.append(_LINETO)

	def curveTo(self, x1, y1, x2, y2, x3, y3):
		self.points.extend([x1, y1, x2, y2, x3, y3])
		self.operators.append(_CURVETO)

	def closePath(self):
		self.operators.append(_CLOSEPATH)

def definePath(pathSegs=[],isClipPath=0,**kw):
	O = []
	P = []
	for seg in pathSegs:
		if type(seg) not in [ListType,TupleType]: 
			opName = seg
			args = []
		else:
			opName = seg[0]
			args = seg[1:]
		if opName not in _PATH_OP_NAMES:
			raise ValueError, 'bad operator name %s' % opName
		op = _PATH_OP_NAMES.index(opName)
		if len(args)!=_PATH_OP_ARG_COUNT[op]:
			raise ValueError, '%s bad arguments %s' % (opName,str(args))
		O.append(op)
		P.extend(args)
	return apply(Path,(P,O,isClipPath),kw)

class Rect(SolidShape):
	"""Rectangle, possibly with rounded corners."""

	_attrMap = AttrMap(
		strokeColor = AttrMapValue(isColorOrNone),
		strokeWidth = AttrMapValue(isNumber),
		strokeLineCap = AttrMapValue(None),
		strokeLineJoin = AttrMapValue(None),
		strokeMiterLimit = AttrMapValue(None),
		strokeDashArray = AttrMapValue(isListOfNumbersOrNone),
		fillColor = AttrMapValue(isColorOrNone),
		x = AttrMapValue(isNumber),
		y = AttrMapValue(isNumber),
		width = AttrMapValue(isNumber),
		height = AttrMapValue(isNumber),
		rx = AttrMapValue(isNumber),
		ry = AttrMapValue(isNumber),
		)

	def __init__(self, x, y, width, height, rx=0, ry=0, **kw):
		SolidShape.__init__(self, kw)
		self.x = x
		self.y = y
		self.width = width
		self.height = height
		self.rx = rx
		self.ry = ry

	def copy(self):
		new = Rect(self.x, self.y, self.width, self.height)
		new.setProperties(self.getProperties())
		return new


class Circle(SolidShape):

	_attrMap = AttrMap(
		strokeColor = AttrMapValue(None),
		strokeWidth = AttrMapValue(isNumber),
		strokeLineCap = AttrMapValue(None),
		strokeLineJoin = AttrMapValue(None),
		strokeMiterLimit = AttrMapValue(None),
		strokeDashArray = AttrMapValue(isListOfNumbersOrNone),
		fillColor = AttrMapValue(None),
		cx = AttrMapValue(isNumber),
		cy = AttrMapValue(isNumber),
		r = AttrMapValue(isNumber),
		)

	def __init__(self, cx, cy, r, **kw):
		SolidShape.__init__(self, kw)
		self.cx = cx
		self.cy = cy
		self.r = r

	def copy(self):
		new = Circle(self.cx, self.cy, self.r)
		new.setProperties(self.getProperties())
		return new


class Ellipse(SolidShape):

	_attrMap = AttrMap(
		strokeColor = AttrMapValue(None),
		strokeWidth = AttrMapValue(isNumber),
		strokeLineCap = AttrMapValue(None),
		strokeLineJoin = AttrMapValue(None),
		strokeMiterLimit = AttrMapValue(None),
		strokeDashArray = AttrMapValue(isListOfNumbersOrNone),
		fillColor = AttrMapValue(None),
		cx = AttrMapValue(isNumber),
		cy = AttrMapValue(isNumber),
		rx = AttrMapValue(isNumber),
		ry = AttrMapValue(isNumber),
		)

	def __init__(self, cx, cy, rx, ry, **kw):
		SolidShape.__init__(self, kw)
		self.cx = cx
		self.cy = cy
		self.rx = rx
		self.ry = ry

	def copy(self):
		new = Ellipse(self.cx, self.cy, self.rx, self.ry)
		new.setProperties(self.getProperties())
		return new


class Wedge(SolidShape):
	"""A "slice of a pie" by default translates to a polygon moves anticlockwise
	   from start angle to end angle"""

	_attrMap = AttrMap(
		strokeColor = AttrMapValue(None),
		strokeWidth = AttrMapValue(isNumber),
		strokeLineCap = AttrMapValue(None),
		strokeLineJoin = AttrMapValue(None),
		strokeMiterLimit = AttrMapValue(None),
		strokeDashArray = AttrMapValue(isListOfNumbersOrNone),
		fillColor = AttrMapValue(None),
		centerx = AttrMapValue(isNumber),
		centery = AttrMapValue(isNumber),
		radius = AttrMapValue(isNumber),
		startangledegrees = AttrMapValue(isNumber),
		endangledegrees = AttrMapValue(isNumber),
		yradius = AttrMapValue(isNumberOrNone),
		)

	degreedelta = 1 # jump every 1 degrees

	def __init__(self, centerx, centery, radius, startangledegrees, endangledegrees, yradius=None, **kw):
		if yradius is None: yradius = radius
		SolidShape.__init__(self, kw)
		while endangledegrees<startangledegrees:
			endangledegrees = endangledegrees+360
		#print "__init__"
		self.centerx, self.centery, self.radius, self.startangledegrees, self.endangledegrees = \
			centerx, centery, radius, startangledegrees, endangledegrees
		self.yradius = yradius

	#def __repr__(self):
	#		 return "Wedge"+repr((self.centerx, self.centery, self.radius, self.startangledegrees, self.endangledegrees ))
	#__str__ = __repr__

	def asPolygon(self):
		#print "asPolygon"
		centerx, centery, radius, startangledegrees, endangledegrees = \
			self.centerx, self.centery, self.radius, self.startangledegrees, self.endangledegrees
		yradius = self.yradius
		degreedelta = self.degreedelta
		points = []
		a = points.append
		a(centerx); a(centery)
		from math import sin, cos, pi
		degreestoradians = pi/180.0
		radiansdelta = degreedelta*degreestoradians
		startangle = startangledegrees*degreestoradians
		endangle = endangledegrees*degreestoradians
		while endangle<startangle:
			#print "endangle", endangle
			endangle = endangle+2*pi
		angle = startangle
		#print "start", startangle, "end", endangle
		while angle<endangle:
			#print angle
			x = centerx + cos(angle)*radius
			y = centery + sin(angle)*yradius
			a(x); a(y)
			angle = angle+radiansdelta
		#print "done"
		x = centerx + cos(endangle)*radius
		y = centery + sin(endangle)*yradius
		a(x); a(y)
		return Polygon(points)

	def copy(self):
		new = Wedge(self.centerx,
					self.centery,
					self.radius,
					self.startangledegrees,
					self.endangledegrees)
		new.setProperties(self.getProperties())
		return new


class Polygon(SolidShape):
	"""Defines a closed shape; Is implicitly
	joined back to the start for you."""

	_attrMap = AttrMap(
		strokeColor = AttrMapValue(None),
		strokeWidth = AttrMapValue(isNumber),
		strokeLineCap = AttrMapValue(None),
		strokeLineJoin = AttrMapValue(None),
		strokeMiterLimit = AttrMapValue(None),
		strokeDashArray = AttrMapValue(isListOfNumbersOrNone),
		fillColor = AttrMapValue(None),
		points = AttrMapValue(isListOfNumbers),
		)

	def __init__(self, points=[], **kw):
		SolidShape.__init__(self, kw)
		assert len(points) % 2 == 0, 'Point list must have even number of elements!'
		self.points = points

	def copy(self):
		new = Polygon(self.points)
		new.setProperties(self.getProperties())
		return new


class PolyLine(LineShape):
	"""Series of line segments.  Does not define a
	closed shape; never filled even if apparently joined.
	Put the numbers in the list, not two-tuples."""

	_attrMap = AttrMap(
		strokeColor = AttrMapValue(isColorOrNone),
		strokeWidth = AttrMapValue(isNumber),
		strokeLineCap = AttrMapValue(None),
		strokeLineJoin = AttrMapValue(None),
		strokeMiterLimit = AttrMapValue(isNumber),
		strokeDashArray = AttrMapValue(isListOfNumbersOrNone),
		points = AttrMapValue(isListOfNumbers),
		)

	def __init__(self, points=[], **kw):
		LineShape.__init__(self, kw)
		lenPoints = len(points)
		if lenPoints:
			if type(points[0]) in (ListType,TupleType):
				L = []
				for (x,y) in points:
					L.append(x)
					L.append(y)
				points = L
			else:
				assert len(points) % 2 == 0, 'Point list must have even number of elements!'
		self.points = points

	def copy(self):
		new = PolyLine(self.points)
		new.setProperties(self.getProperties())
		return new


class String(Shape):
	"""Not checked against the spec, just a way to make something work.
	Can be anchored left, middle or end."""

	# to do.
	_attrMap = AttrMap(
		x = AttrMapValue(isNumber),
		y = AttrMapValue(isNumber),
		text = AttrMapValue(isString),
		fontName = AttrMapValue(None),
		fontSize = AttrMapValue(isNumber),
		fillColor = AttrMapValue(isColorOrNone),
		textAnchor = AttrMapValue(isTextAnchor),
		)

	def __init__(self, x, y, text, **kw):
		self.x = x
		self.y = y
		self.text = text
		self.textAnchor = 'start'
		self.fontName = STATE_DEFAULTS['fontName']
		self.fontSize = STATE_DEFAULTS['fontSize']
		self.fillColor = STATE_DEFAULTS['fillColor']
		self.setProperties(kw)

	def copy(self):
		new = String(self.x, self.y, self.text)
		new.setProperties(self.getProperties())
		return new


class UserNode:
	"""A simple template for creating a new node.  The user (Python
	programmer) may subclasses this.  provideNode() must be defined to
	provide a Shape primitive when called by a renderer.  It does
	NOT inherit from Shape, as the renderer always replaces it, and
	your own classes can safely inherit from it without getting
	lots of unintended behaviour."""

	def provideNode(self):
		"""Override this to create your own node. This lets widgets be
		added to drawings; they must create a shape (typically a group)
		so that the renderer can draw the custom node."""

		raise NotImplementedError, "this method must be redefined by the user/programmer"


def test():
	r = Rect(10,10,200,50)
	import pprint
	pp = pprint.pprint
	print 'a Rectangle:'
	pp(r.getProperties())
	print
	print 'verifying...',
	r.verify()
	print 'OK'
	#print 'setting rect.z = "spam"'
	#r.z = 'spam'
	print 'deleting rect.width'
	del r.width
	print 'verifying...',
	r.verify()


if __name__=='__main__':
	test()
