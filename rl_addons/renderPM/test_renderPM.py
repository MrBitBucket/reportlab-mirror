if	__name__=='__main__':
	import sys, os, traceback
	import _renderPM
	from reportlab.graphics import shapes, renderPM

	def test_base():
		class dummy:
			pass
		g=_renderPM.gstate(1,1)
		try:
			g.aaa = 3
			print 'Wrong handling of bad attribute'
		except AttributeError:
			pass

		for fontName, fontSize in (('aaa',10),('Times-Roman','10'),('Times-Roman',-10),(1,10)):
			try:
				g.setFont(fontName,fontSize)
				print 'Wrong handling of setFont(%s,%s)' % (fontName,fontSize)
			except _renderPM.Error:
				pass
			except TypeError:
				pass

		for a in ('strokeColor','fillColor'):
			try:
				setattr(g,a,(1,2,3))
				print 'Wrong handling of bad '+a
			except ValueError:
				pass

			try:
				c=dummy()
				c.red=0xff/255.
				c.green=0xaf/255.
				c.blue=0xbf/255.
				for v,r in ((None,None),(0xfffafb,0xfffafb),(c,0xffafbf)):
					setattr(g,a,v)
					assert getattr(g,a)==r, "%s should be %s" % (a,hex(r))
			except:
				print 'wrong handling of good %s' % a
				traceback.print_exc()
				print hex(getattr(g,a))

		for v in ('a',1,(1,'a'),('a',1),(1,()),(1,('a',2))):
			try:
				g.dashArray=v
				print 'Wrong handling of dashArray %s' % v
			except ValueError:
				pass
		try:
			g.dashArray=7,(1,2,3)
			assert g.dashArray==(7.0,(1.0,2.0,3.0)), "should be (7.0,(1.0,2.0,3.0))"
		except:
			print 'wrong handling of dashArray'
			traceback.print_exc()
			print g.dashArray

		try:
			g.pathBegin()
			g.moveTo(0,0)
			g.lineTo(1,0)
			g.lineTo(1,1)
			g.lineTo(0,1)
			g.pathClose()
			good = (('moveToClosed', 0.0, 0.0), ('lineTo', 1.0, 0.0), ('lineTo', 1.0, 1.0), ('lineTo', 0.0, 1.0), ('lineTo', 0.0, 0.0))
			assert good==g.path, 'Wrong path should be %s' % str(good)
		except:
			print 'wrong handling of path'
			traceback.print_exc()
			print g.path

	if len(sys.argv)==1:
		test_base()
	else:
		def do_save(c,n,txt=0,pil=0):
			DIR='pmout'
			if not os.path.isdir(DIR): os.mkdir(DIR)
			c.saveToFile(os.path.join(DIR,"test_renderPM_%03d.gif"%n))
			if txt:
				f = open(os.path.join(DIR,"test_renderPM_%03d.txt"%n),'w')
				b = c.pixBuf
				w = c.width
				h = c.height
				k = 0
				for i in xrange(h):
					f.write('%6.6x: '% i );
					for j in xrange(w):
						v = (ord(b[k])<<16) | (ord(b[k+1])<<8) | ord(b[k+2])
						k = k + 3
						f.write(' %6.6x'%v)
					f.write('\n')

				if pil:
					from PIL import Image
					im = Image.new('RGB', size=(w, h))
					im.fromstring(b)
					f.write('PIL\n')
					for i in xrange(h):
						f.write('%6.6x: '% i );
						for j in xrange(w):
							v = im.getpixel((i,j))
							f.write(' %2.2x%2.2x%2.2x'%v)
						f.write('\n')
					im.save(os.path.join(DIR,"test_renderPM_%03dx.jpg"%n),'JPEG')
					im.save(os.path.join(DIR,"test_renderPM_%03dx.bmp"%n),'BMP')
					im.save(os.path.join(DIR,"test_renderPM_%03dx.tif"%n),'TIFF')
					im = im.convert("P", dither=Image.NONE, palette=Image.ADAPTIVE)
					im.save(os.path.join(DIR,"test_renderPM_%03dx.gif"%n),'GIF')

		def flagged(n):
			return str(n) in sys.argv or 'all' in sys.argv

		def doVPath(c, S,x0=0,y0=0):
			c.pathBegin()
			for P in S:
				c.moveTo(P[0][0]-x0,P[0][1]-y0)
				for p in P[1:]:
					c.lineTo(p[0]-x0,p[1]-y0)
				c.pathClose()
			c.pathFill()

		def doCTest(f, c, x, y, c0=0x8000,c1=0xff0000):
			c.ctm=(1,0,0,1,x,y)
			c.fillColor = c0
			c.strokeColor = c1
			f(c)

		if flagged(0):
			vp=[[(136.262,131.996), (136.91,130.502), (137.038,130.192), (137.18,129.832), (137.243,129.646), (137.295,129.464), (137.329,129.292), (137.342,129.134), (137.337,129.021), (137.321,128.92), (137.295,128.828), (137.26,128.747), (137.214,128.674), (137.159,128.61), (137.094,128.555), (137.02,128.506), (136.937,128.465), (136.845,128.43), (136.745,128.401), (136.636,128.377), (136.393,128.343), (136.118,128.324), (136.118,128), (140.816,128), (140.816,128.324), (140.578,128.345), (140.361,128.387), (140.164,128.449), (139.985,128.53), (139.824,128.627), (139.677,128.741), (139.544,128.869), (139.423,129.01), (139.313,129.164), (139.211,129.328), (139.116,129.502), (139.026,129.683), (138.858,130.066), (138.692,130.466), (134.642,140.186), (134.318,140.186), (130.034,130.142), (129.838,129.706), (129.743,129.514), (129.648,129.339), (129.553,129.18), (129.457,129.037), (129.358,128.908), (129.256,128.794), (129.148,128.694), (129.036,128.607), (128.916,128.532), (128.789,128.469), (128.652,128.417), (128.506,128.376), (128.349,128.345), (128.18,128.324), (128.18,128), (131.924,128), (131.924,128.324), (131.673,128.346), (131.426,128.377), (131.193,128.423), (131.084,128.453), (130.981,128.491), (130.887,128.535), (130.801,128.587), (130.725,128.648), (130.661,128.719), (130.609,128.8), (130.57,128.893), (130.546,128.998), (130.538,129.116), (130.549,129.253), (130.58,129.406), (130.625,129.567), (130.682,129.732), (130.811,130.053), (130.934,130.322), (131.654,131.996), (136.262,131.996)],
				[(136.028,132.644), (131.924,132.644), (133.994,137.45), (136.028,132.644)]]

			def doTest0(c, vp, x, y, c0=0x0,c1=0xff0000, angle=0, c2=0xff00ff):
				c.ctm=(1,0,0,1,x,y)
				c.fillColor = c0
				doVPath(c,vp,128,128)
				c.ctm = shapes.mmult(c.ctm, shapes.rotate(180))
				c.fillColor = c1
				doVPath(c,vp,128,128)
				c.ctm=(1,0,0,1,x,y)
				c.pathBegin()
				c.ctm=(1,0,0,1,x+20,y)
				c.ctm = shapes.mmult(c.ctm, shapes.rotate(angle))
				c.moveTo(0,0)
				c.lineTo(20,0)
				c.strokeColor = c2
				c.pathStroke()
				c.ctm=(1,0,0,1,x+20,y-20)
				c.drawString(0,0,"Robin")

			c = renderPM.PMCanvas(256, 256, bg=0xffffff)
			c.fillColor = 0x000000
			c.setFont('Times-Roman',18)

			doTest0(c,vp, 128, 128 )
			vp[0].reverse()
			vp[1].reverse()
			doTest0(c,vp, 168, 168, c0=0xff00, c1=0xff, angle=45)
			do_save(c,0)

		def doCPath1(c):
			c.pathBegin()
			c.moveTo(110-85,100-85)
			c.curveTo(110-85,94.477152501999996-85, 105.522847498-85,90-85, 100-85,90-85)
			c.curveTo(94.477152501999996-85,90-85, 90-85,94.477152501999996-85, 90-85,100-85)
			c.curveTo(90-85,105.522847498-85, 94.477152501999996-85,110-85, 100-85,110-85)
			c.curveTo(105.522847498-85,110-85, 110-85,105.522847498-85, 110-85,100-85)
			c.pathClose()
			c.pathFill()
			c.pathStroke()

		def doCPath2(c):
			c.pathBegin()
			c.moveTo(5,5)
			c.lineTo(5,20)
			c.lineTo(20,20)
			c.lineTo(20,5)
			c.pathClose()
			c.pathFill()

		def rotate_alpha_blend_text(can,off_x, text, dw, n, end_alpha):
			"decrease alpha linearly over the range of n points"
			dalpha = end_alpha/n
			for ii in range(n):
				can.gsave()
				can.rotate(dw*ii)
				# print dw*ii
				can.gstate.fill_opacity = end_alpha-ii*dalpha
				print "alpha = ", can.gstate.fill_opacity
				can.drawString(off_x,0, text)
				can.grestore()

		def doCPath4(c,doStroke=1,doFill=1):
			c.pathBegin()
			c.moveTo(5,5)
			c.lineTo(5,20)
			c.lineTo(20,20)
			c.lineTo(20,5)
			c.pathClose()
			if doFill: c.pathFill()
			if doStroke: c.pathStroke()

		def doCPath5(c,doStroke=1):
			c.pathBegin()
			c.moveTo(5,5)
			c.lineTo(5,20)
			c.lineTo(20,20)
			c.lineTo(20,5)
			c.pathClose()
			if doStroke: c.pathStroke()

		def doCPath6(c,doStroke=1):
			c.pathBegin()
			c.moveTo(5,10)
			c.lineTo(5,20)
			c.lineTo(20,20)
			c.lineTo(20,10)
			c.pathClose()
			if doStroke: c.pathStroke()

		if flagged(1):
			c = renderPM.PMCanvas(25, 25, bg=0xffffff)
			c.setFont('Times-Roman',18)
			doCTest(doCPath1, c, 0, 0 )
			do_save(c,1)

		if flagged(2):
			c = renderPM.PMCanvas(25, 25, bg=0xffffff)
			doCTest(doCPath2, c, 0, 0 )
			do_save(c,2,txt=1,pil=1)

		if flagged(3):
			c = renderPM.PMCanvas(256, 256, bg=0xffffff)
			c.fillColor = 0x000000
			c.setFont('Times-Roman',18)
			text = "ABC"
			c.ctm=(1,0,0,("invert" in sys.argv) and -1 or 1, 127.5,127.5)
			c.drawString(0, 0, text)
			c.ctm = shapes.mmult(c.ctm, shapes.rotate(180))
			c.fillColor = 0xff0000
			c.drawString(0, 0, text)
			do_save(c,3)

		if flagged(4):
			c = renderPM.PMCanvas(25, 25, bg=0xffffff)
			doCTest(doCPath4, c, 0, 0, c0=0x8000, c1=0xff0000)
			do_save(c,4)

		if flagged(5):
			c = renderPM.PMCanvas(25, 25, bg=0xffffff)
			doCTest(doCPath5, c, 0, 0 )
			do_save(c,5)

		if flagged(6):
			c = renderPM.PMCanvas(25, 25, bg=0xffffff)
			doCPath6(c,doStroke=1)
			print 'Clip',c.path
			c.clipPathSet()
			doCTest(doCPath4, c, 0, 0, c0=0x8000, c1=0xff0000)
			print 'Draw',c.path
			c.clipPathClear()
			do_save(c,6)
