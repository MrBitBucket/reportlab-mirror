#copyright ReportLab Inc. 2000
#see license.txt for license details
#history http://cvs.sourceforge.net/cgi-bin/cvsweb.cgi/reportlab/lib/abag.py?cvsroot=reportlab
#$Header: /tmp/reportlab/reportlab/lib/abag.py,v 1.1 2000/11/29 16:16:33 rgbecker Exp $
class ABag:
	"""
	A trivial BAG class for holding attributes
	"""
	def __init__(self,**attr):
		for k,v in attr.items():
			setattr(self,k,v)

	def clone(self,**attr):
		n = apply(ABag,(),self.__dict__)
		if attr != {}: apply(ABag.__init__,(n,),attr)
		return n
