#!/usr/bin/env python
'''
$Id: test_xmltestsuite.py,v 1.2 2003/04/13 16:04:04 rgbecker Exp $
Test parsing and validation against James Clark's test cases,
as downloaded from http://www.jclark.com/xml/
The .zip file should be in the same directory as this script.
Note that the .zip file can be freely distributed in unmodified form
so it could be added to the pyRXP distribution.
'''
__rcs_id__	= '$Id: test_xmltestsuite.py,v 1.2 2003/04/13 16:04:04 rgbecker Exp $'
__version__ = '$Revision: 1.2 $'[11:-2]
__author__ = 'Stuart Bishop <stuart@stuartbishop.net>'

import unittest, zipfile, sys, os, os.path, codecs
debug = int(os.environ.get('RL_DEBUG','0'))

# Debug is to help me trace down memory bugs
if debug: import time

# 2.2 compatibility - sort of
try:
	__file__
except NameError:
	__file__ = os.path.join(os.getcwd(),'oops')

class test_pyRXPU(unittest.TestCase):
	mod = None
	
	def parse(self,filename,**kw):
		if debug: print >> sys.stderr,'About to parse %s' % filename
		kw = kw.copy()
		kw['ReturnComments'] = 0
		kw['ExpandEmpty'] = 1
		kw['XMLLessThan'] = 1
		kw['ReturnProcessingInstructions'] = 1
		kw['ReturnList'] = 1
		parser = self.mod.Parser(**kw)
		# Change directory in case we are loading entities from cwd
		retdir = os.getcwd()
		d,n = os.path.split(filename)
		os.chdir(d)
		try:
			f = open(n)
			xml = f.read()
			return parser.parse(xml)
		finally:
			try:
				f.close()
			except:
				pass
			os.chdir(retdir)
			if debug: print >> sys.stderr,'Done parsing   %s' % filename
			if debug: print >> sys.stderr,'='*60
			if debug==1: time.sleep(1)

	def getcanonical(self,filename):
		''' Parse in the named file, and return it as canonical XML '''
		return self._getcan(self.parse(filename))

	def _getcan(self,node):
		if type(node) is type([]): return ''.join(map(self._getcan, node))
		if type(node) in (type(''),type(u'')):
			return self._quote(node)

		tag,attrs,kids,junk = node

		if tag == self.mod.commentTagName:
			return u'<!--%s-->' % (kids[0])
		elif tag == self.mod.piTagName:
			return u'<?%s %s?>' % (attrs['name'],kids[0])

		if attrs is None:
			attrs = ''
		else:
			keys = attrs.keys()
			keys.sort() # Attributes in lexical order
			attrs = ' '.join(
				['%s="%s"' % (k,self._quote(attrs[k])) for k in keys]
				)
			if attrs:
				attrs = ' ' + attrs

		text = ''.join([self._getcan(kid) for kid in kids])

		return '<%s%s>%s</%s>' % (tag,attrs,text,tag)

	def _quote(self,txt):
		txt = txt.replace('&','&amp;')
		txt = txt.replace('<','&lt;')
		txt = txt.replace('>','&gt;')
		txt = txt.replace('"','&quot;')
		txt = txt.replace('\x09','&#9;')
		txt = txt.replace('\x0a','&#10;')
		txt = txt.replace('\x0d','&#13;')
		return txt

	def _test_valid(self,inname,outname):
		inxml = self.getcanonical(inname)
		f = codecs.open(outname,mode='r',encoding='utf8')
		outxml = f.read()
		f.close()
		self.assertEqual(inxml,outxml)

	def _test_invalid_parse(self,inname):
		try:
			self.parse(inname,Validate=0)
		except self.mod.error,x:
			self.fail('Failed to parse %r in non-validating mode' % inname)

	def _test_invalid_validate(self,inname):
		try:
			self.parse(inname,Validate=1)
			self.fail('Failed to detect validity error in %r' % inname)
		except self.mod.error:
			pass

	def _test_notwf(self,inname):
		try:
			self.parse(inname,Validate=0)
			self.fail(
				'Failed to detect that %r was not well formed' % inname
				)
		except self.mod.error:
			pass

def buildup_test(cls=test_pyRXPU,I=[]):
	''' Add test methods to the TestCase '''
	cls.valid = []
	cls.invalid = []
	cls.notwf = []
	testdir = os.path.dirname(__file__)
	try:
		zipf = zipfile.ZipFile(os.path.join(testdir,'xmltest.zip'))
	except:
		print >> sys.stderr, "Can't locate file xmltest.zip\nPerhaps it should be downloaded from\nhttp://www.reportlab.com/ftp/xmltest.zip\nor\nftp://ftp.jclark.com/pub/xml/xmltest.zip\n"
		raise
	for zipname in zipf.namelist():

		# Extract the files if they don't alrady exist
		osname = os.path.join(*zipname.split('/')) # For non-unixes
		osname = os.path.join(testdir,osname)
		dir = os.path.dirname(osname)
		if not os.path.isdir(dir):
			os.makedirs(dir)
		if not os.path.isfile(osname):
			f = open(osname,'wb')
			f.write(zipf.read(zipname))
			f.close()
		if I and zipname not in I: continue

		# Add input files to our lists
		if os.path.splitext(osname)[1] == '.xml' and zipname.find('out') == -1:
			if zipname.find('invalid') != -1:
				cls.invalid.append(osname)
			elif zipname.find('not-wf') != -1:
				cls.notwf.append(osname)
			elif zipname.find('valid') != -1:
				outname = os.path.join(dir,'out',os.path.basename(osname))
				cls.valid.append( (osname,outname) )

	# Add 'valid' tests
	for inname,outname in cls.valid:
		num = int(os.path.splitext(os.path.basename(inname))[0])
		dir = os.path.split(os.path.split(inname)[0])[1]
		mname = 'test_Valid_%s_%03d' % (dir,num)
		def doTest(self,inname=inname,outname=outname):
			self._test_valid(inname,outname)
		setattr(cls,mname,doTest)

	# Add 'invalid' tests
	for inname in cls.invalid:
		num = int(os.path.splitext(os.path.basename(inname))[0])
		mname = 'test_InvalidParse_%03d' % (num)
		def doTest(self,inname=inname):
			self._test_invalid_parse(inname)
		setattr(cls,mname,doTest)
		mname = 'test_InvalidValidate_%03d' % (num)
		def doTest(self,inname=inname):
			self._test_invalid_validate(inname)
		setattr(cls,mname,doTest)

	# Add 'not wellformed' tests
	for inname in cls.notwf:
		num = int(os.path.splitext(os.path.basename(inname))[0])
		dir = os.path.split(os.path.split(inname)[0])[1]
		mname = 'test_NotWellFormed_%s_%03d' % (dir,num)
		def doTest(self,inname=inname):
			self._test_notwf(inname)
		setattr(cls,mname,doTest)
	import pyRXPU
	cls.mod = pyRXPU

if __name__ == '__main__':
	I = filter(lambda a: a[:2]=='-I',sys.argv)
	map(sys.argv.remove,I)
	I = map(lambda x: x[2:],I)
	buildup_test(I=I)
	unittest.main()
