#copyright ReportLab Inc. 2000
#see license.txt for license details
#history http://cvs.sourceforge.net/cgi-bin/cvsweb.cgi/reportlab/lib/attrmap.py?cvsroot=reportlab
#$Header: /tmp/reportlab/reportlab/lib/attrmap.py,v 1.1 2001/05/17 11:15:15 rgbecker Exp $
from UserDict import UserDict

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
		self.validate = validate
		self.desc = desc
		self._initial = initial
		for k,v in kw.items():
			setattr(self,k,v)

	def __getattr__(self,name):
		#hack to allow callable initial values
		if name=='initial': if isinstance(CallableValue,self._initial): return self._initial()
		raise AttributeError, name

class AttrMap(UserDict):
	def __init__(self,BASE=None,UNWANTED=[],**kw):
		if BASE:
			if isinstance(BASE,AttrMap):
				UserDict.__init__(self,BASE.data)		#they used BASECLASS._attrMap
			elif hasattr(BASE,'_attrMap'):
				UserDict.__init__(self,BASE._attrMap)	#they gave us the BASECLASS

		self.remove(UNWANTED)
		self.update(kw)

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
