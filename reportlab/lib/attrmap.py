#copyright ReportLab Inc. 2000
#see license.txt for license details
#history http://cvs.sourceforge.net/cgi-bin/cvsweb.cgi/reportlab/lib/attrmap.py?cvsroot=reportlab
#$Header: /tmp/reportlab/reportlab/lib/attrmap.py,v 1.2 2001/05/17 16:21:33 rgbecker Exp $
from UserDict import UserDict
from reportlab.lib.validators import isAnything

class CallableValue:
	'''a class to allow callable initial values'''
	def __init__(self,func,*args,**kw):
		#assert iscallable(func)
		self.func = func
		self.args = args
		self.kw = kw

	def __call__(self):
		return apply(self.func,self.args,self.kw)
		
class AttrMapValue:
	'''Simple multi-value holder for attribute maps'''
	def __init__(self,validate=None,desc=None,initial=None, **kw):
		self.validate = validate or isAnything
		self.desc = desc
		self._initial = initial
		for k,v in kw.items():
			setattr(self,k,v)

	def __getattr__(self,name):
		#hack to allow callable initial values
		if name=='initial' and isinstance(self._initial,CallableValue): return self._initial()
		raise AttributeError, name

class AttrMap(UserDict):
	def __init__(self,BASE=None,UNWANTED=[],**kw):
		if BASE:
			if isinstance(BASE,AttrMap):
				data = BASE.data						#they used BASECLASS._attrMap
			elif hasattr(BASE,'_attrMap'):
				data = getattr(BASE._attrMap,'data',{})	#they gave us the BASECLASS
			else:
				raise ValueError, 'BASE=%s has wrong kind of value' % str(BASE)
		else:
			data = {}

		UserDict.__init__(self,data)
		self.remove(UNWANTED)
		self.data.update(kw)

	def update(self,kw):
		if isinstance(kw,AttrMap): kw = kw.data
		self.data.update(kw)

	def remove(self,unwanted):
		for k in unwanted:
			try:
				del self[k]
			except KeyError:
				pass

	def clone(self,UNWANTED=[],**kw):
		c = AttrMap(BASE=self,UNWANTED=UNWANTED)
		c.update(kw)
		return c

def validateSetattr(obj,name,value):
	'''validate setattr(obj,name,value)'''
	map = obj._attrMap
	if map and name[0]!= '_':
		try:
			validate = map[name].validate
			if not validate(value):
				raise AttributeError, "Illegal assignment of '%s' to '%s' in class %s" % (value, name, obj.__class__.__name__)
		except KeyError:
			raise AttributeError, "Illegal attribute '%s' in class %s" % (name, obj.__class__.__name__)
	obj.__dict__[name] = value
