#include "Python.h"
#ifndef PyMem_New
	/*Niki Spahiev <niki@vintech.bg> suggests this is required for 1.5.2*/
#	define PyMem_New(type, n) ( (type *) PyMem_Malloc((n) * sizeof(type)) )
#endif
#include <string.h>
#include "libart_lgpl/libart.h"
#include "gt1/gt1-parset1.h"

#if defined(macintosh)
#	include <extras.h>
#	define strdup _strdup
#endif


#define VERSION "0.95"
#define MODULE "_renderPM"
static PyObject *moduleError;
static PyObject *_version;
#ifndef LIBART_VERSION
#	define LIBART_VERSION "?.?.?"
#endif
static PyObject *_libart_version;
static char *moduleDoc =
"Helper extension module for renderPM.\n\
\n\
Interface summary:\n\
\n\
	import _render\n\
	gstate(width,height[,depth=3,bg=0xffffff])		#create an initialised graphics state\n\
	makeT1Font(fontName,pfbPath,names)				#make a T1 font\n\
	delCache()										#delete all font info\n\
\n\
	Error			# module level error\n\
	error			# alias for Error\n\
	_libart_version	# base library version string\n\
	_version		# module version string\n\
";


typedef struct {
  int format;
  art_u8 * buf;
  int width;
  int height;
  int nchan;
  int rowstride;
} pixBufT;

typedef	struct {
		size_t	width;
		size_t	height;
		size_t	stride;
		art_u8	*buf;
		} gstateColorX;

static pixBufT* pixBufAlloc(int w, int h, int nchan, gstateColorX bg)
{
	pixBufT* p = PyMem_Malloc(sizeof(pixBufT));
	if(p){
		size_t	n;
		p->format = 0; /* RGB */
		p->buf = PyMem_Malloc(n=w*h*nchan); /* start with white background by default */
		if(p->buf){
			/*initialise the pixmap pixels*/
			art_u8	*b, *lim = p->buf+n;
			size_t	stride = w*nchan, i;
			p->width = w;
			p->height = h;
			p->nchan = nchan;
			p->rowstride = stride;

			/*set up the background*/
			if(bg.stride==0){	/*simple color case*/
				art_u32	bgv = (bg.buf[0]<<16) | (bg.buf[1]<<8) | bg.buf[2];
				for(i=0;i<(size_t)nchan;i++){
					art_u8 	c= (bgv>>(8*(nchan-i-1)))&0xff;
					b = p->buf+i;
					while(b<lim){
						*b = c;
						b += nchan;
						}
					}
				}
			else{	/*image case*/
				size_t	j = 0;
				art_u8	*r = bg.buf;
				b = p->buf;
				i = 0;
				while(b<lim){
					*b++ = r[j++ % bg.stride];
					if(j==stride){
						r += bg.stride;
						j = 0;
						i++;
						if(i==bg.height) r = bg.buf;
						}
					}
				}
			}
		else {
			PyMem_Free(p);
			p = NULL;
			}
		}

	return p;
}

static void pixBufFree(pixBufT** pp)
{
	pixBufT*	p = *pp;
	if(p){
		PyMem_Free(p->buf);
		PyMem_Free(p);
		*pp = 0;
		}
}

typedef	double	A2DMX[6];		/*Affine transforms*/
typedef	struct {
		art_u32	value;				/*the color value*/
		int		valid;				/*if it's valid*/
		} gstateColor;

typedef struct {
	PyObject_HEAD
	A2DMX		ctm;
	gstateColor	strokeColor;			/*strokeColor*/
	double		strokeWidth;
	int			lineCap;
	int			lineJoin;
	double		strokeOpacity;
	gstateColor	fillColor;			/*fill color*/
	int			fillRule;
	double		fillOpacity;
	double		fontSize;
	ArtSVP*		clipSVP;
	pixBufT*	pixBuf;
	int			pathLen, pathMax;	/*current and maximum sizes*/
	ArtBpath*	path;				/*the vector path data*/
	ArtVpathDash	dash;			/*for doing dashes*/
	Gt1EncodedFont*		font;		/*the currently set external font or NULL*/
	} gstateObject;

#ifdef	ROBIN_DEBUG
#define	GFMT	"%.17g"
#define PATHCODENAME(c) (c==ART_MOVETO_OPEN?"MOVETO":(c==ART_MOVETO?"MOVETO_C":(c==ART_LINETO?"LINETO":(c==ART_CURVETO?"CURVETO":(c==ART_END?"END":"????")))))
static	void dump_path(gstateObject* self)
{
	ArtBpath	*q = self->path;
	size_t		i;
	printf("strokeColor=%8.8xX%s strokeWidth=%g fillColor=%8.8xX%s\n", self->strokeColor.value,
			self->strokeColor.valid ? "valid":"invalid", self->strokeWidth,
			self->fillColor.value,
			self->fillColor.valid ? "valid":"invalid"
			);
	printf("ctm: " GFMT " " GFMT " " GFMT " " GFMT " " GFMT " " GFMT " det: " GFMT "\n", self->ctm[0], self->ctm[1], self->ctm[2], self->ctm[3], self->ctm[4], self->ctm[5],
		self->ctm[0]*self->ctm[3] - self->ctm[1]*self->ctm[2]);
	printf("path: pathLen=%d pathMax=%d\n",self->pathLen, self->pathMax);
	for(i=0;i<(size_t)self->pathLen;i++){
		char	*s;
		printf("%3d: %-8s, (" GFMT "," GFMT "), (" GFMT "," GFMT "), (" GFMT "," GFMT ")\n",
				i, s=PATHCODENAME(q->code),
				q->x1,q->y1,q->x2,q->y2,q->x3,q->y3);
		if((q++)->code==ART_END || s[0]=='?') break;
		}
	fflush(stdout);
}

void dump_vpath(char* msg, ArtVpath* q)
{
	size_t		i;
	printf("%s vpath:\n",msg);
	for(i=0;i<10000;i++){
		char	*s;
		printf("%3d: %-8s, (" GFMT "," GFMT ")\n",
				i, s=PATHCODENAME(q->code),
				q->x,q->y);
		if((q++)->code==ART_END || s[0]=='?') break;
		}
	fflush(stdout);
}

void dump_svp(char* msg, ArtSVP* svp)
{
	int	i, j;
	printf("%s svp:\n",msg);
	for(i=0;i<svp->n_segs;i++){
		ArtSVPSeg *s=svp->segs+i;
		printf("seg%3d: n_points=%d dir=%s box=(" GFMT "," GFMT ") (" GFMT "," GFMT ")\n", i, s->n_points, s->dir?"dn":"up",s->bbox.x0,s->bbox.y0,s->bbox.x1,s->bbox.y1);
		for(j=0;j<s->n_points;j++) printf("    (" GFMT "," GFMT ")\n",s->points[j].x, s->points[j].y);
		}
	fflush(stdout);
}
#else
#define dump_path(p)
#define dump_vpath(m,p)
#define dump_svp(m,p)
#endif

static	void bpath_add_point(ArtBpath** pp, int* pn, int *pm, int code, double x[3], double y[3])
{
	int i = (*pn)++;
	if(i == *pm) art_expand(*pp, ArtBpath, *pm);
	(*pp)[i].code = code;
	(*pp)[i].x1 = x[0];
	(*pp)[i].y1 = y[0];
	(*pp)[i].x2 = x[1];
	(*pp)[i].y2 = y[1];
	(*pp)[i].x3 = x[2];
	(*pp)[i].y3 = y[2];
}

static	PyObject*	_gstate_bpath_add(int c, char* fmt, gstateObject* self, PyObject* args)
{
	double			x[3], y[3];

	if(!PyArg_ParseTuple(args,fmt,x+2,y+2)) return NULL;
	x[0] = x[1] = y[0] = y[1] = 0;
	bpath_add_point(&(self->path), &(self->pathLen), &(self->pathMax), c, x, y);
	Py_INCREF(Py_None);
	return Py_None;
}

static	void gstate_pathEnd(gstateObject* self)
{
	double			x[3];
	x[0] = x[1] = x[2] = 0;
	bpath_add_point(&(self->path), &(self->pathLen), &(self->pathMax), ART_END, x, x);
	self->pathLen--;
}

static	PyObject*	gstate_moveTo(gstateObject* self, PyObject* args)
{
	return _gstate_bpath_add(ART_MOVETO_OPEN,"dd:moveTo",self,args);
}

static	PyObject*	gstate_moveToClosed(gstateObject* self, PyObject* args)
{
	return _gstate_bpath_add(ART_MOVETO,"dd:moveToClosed",self,args);
}

static	gstateObject*	_gstate_pathLenCheck(gstateObject* self)
{
	if(!self->pathLen){
		PyErr_SetString(moduleError, "path must begin with a moveTo");
		return NULL;
		}
	return self;
}

static	PyObject*	gstate_lineTo(gstateObject* self, PyObject* args)
{
	if(!_gstate_pathLenCheck(self)) return NULL;
	return _gstate_bpath_add(ART_LINETO,"dd:lineTo",self,args);
}

static	PyObject*	gstate_curveTo(gstateObject* self, PyObject* args)
{
	double			x[3], y[3];
	if(!_gstate_pathLenCheck(self)) return NULL;
	if(!PyArg_ParseTuple(args,"dddddd:curveTo",x+0,y+0,x+1,y+1,x+2,y+2)) return NULL;
	bpath_add_point(&(self->path), &(self->pathLen), &(self->pathMax), ART_CURVETO, x, y);
	Py_INCREF(Py_None);
	return Py_None;
}

static	PyObject*	gstate_pathBegin(gstateObject* self, PyObject* args)
{
	if(!PyArg_ParseTuple(args,":pathBegin")) return NULL;
	self->pathLen = 0;
	Py_INCREF(Py_None);
	return Py_None;
}

static	double _norm1diff(ArtBpath *p, ArtBpath *q)
{
	double rx = p->x3-q->x3;
	double ry = p->y3-q->y3;
	if(rx<0) rx = -rx;
	if(ry<0) ry = -ry;
	if(rx<=ry) return ry;
	return rx;
}

static	PyObject*	gstate_pathClose(gstateObject* self, PyObject* args)
{
	int	c;
	ArtBpath	*p, *q, *q0;
	double		x[3], y[3];
	if(!PyArg_ParseTuple(args,":pathClose")) return NULL;
	p = self->path;
	for(q0 = q = p + self->pathLen-1;q>=p;q--){
		c = q->code;
		if(c==ART_MOVETO_OPEN){
			q->code = ART_MOVETO;	/*this closes it*/
			if(_norm1diff(q,q0)>1e-8){
				x[0] = x[1] = y[0] = y[1] = 0.0;
				x[2] = q->x3;
				y[2] = q->y3;
				bpath_add_point(&self->path,&self->pathLen,&self->pathMax,ART_LINETO,x,y);
				}
			break;
			}
		else if(c==ART_MOVETO){
			PyErr_SetString(moduleError, "path already closed");
			return NULL;
			}
		}

	if(q<p){
		PyErr_SetString(moduleError, "bpath has no MOVETO");
		return NULL;
		}

	Py_INCREF(Py_None);
	return Py_None;
}

static	PyObject* gstate_clipPathClear(gstateObject* self, PyObject* args)
{
	if(!PyArg_ParseTuple(args,":clipPathClear")) return NULL;
	if(self->clipSVP){
		art_svp_free(self->clipSVP);
		self->clipSVP = NULL;
		}
	Py_INCREF(Py_None);
	return Py_None;
}

static art_u32 _RGBA(art_u32 rgb, double alpha)
{
	art_u32 tmp = ((int)(0xFF * alpha))&0xFF;
	return (rgb << 8) | tmp;
}

static void _vpath_segment_reverse(ArtVpath *p, ArtVpath *q)
{
	if(p<q){
		ArtPathcode c;
		ArtVpath *b= p, *e = q;
		while(b<e){
			ArtVpath s = *b;
			*b++ = *e;
			*e-- = s;
			}
		c = p->code;
		p->code = q->code;
		q->code = c;
		}
}

static	void _vpath_reverse(ArtVpath *p)
{
	ArtVpath	*q = p;
	while(q->code!=ART_END){
		while((++p)->code==ART_LINETO);
		_vpath_segment_reverse( q, p-1 );
		q = p;
		}
}

static double _vpath_segment_area(ArtVpath *p, ArtVpath *q)
{
	double a=0.0, x0,y0, x1,y1;
	if(p->code==ART_MOVETO){
		ArtVpath* p0 = p;
		while(p<q){
			x0 = p->x;
			y0 = (p++)->y;
			if(p==q){
				x1 = p0->x;
				y1 = p0->y;
				}
			else{
				x1 = p->x;
				y1 = p->y;
				}
			a += x1*y0 - x0*y1;
			}
		}
	return a;
}

static double _vpath_area(ArtVpath *p)
{
	double a=0.0, t;
	ArtVpath	*q = p, *p0=p;
	while(q->code!=ART_END){
		while((++p)->code==ART_LINETO);
		t = _vpath_segment_area( q, p);
#ifdef	ROBIN_DEBUG
		printf("	closed segment area=%g\n", t );
#endif
		a += t;
		q = p;
		}
	if(a<=-1e-8) _vpath_reverse( p0 );
	return a;
}

static	PyObject* gstate_clipPathSet(gstateObject* self, PyObject* args)
{
	ArtVpath	*vpath;
	ArtVpath	*trVpath;

	if(!PyArg_ParseTuple(args,":clipPathSet")) return NULL;
	gstate_pathEnd(self);
	dump_path(self);
	vpath = art_bez_path_to_vec(self->path, 0.25);
	dump_vpath("after -->vec",vpath);
	trVpath = art_vpath_affine_transform (vpath, self->ctm);
	_vpath_area(trVpath);
	if(self->clipSVP) art_svp_free(self->clipSVP);
	self->clipSVP = art_svp_from_vpath(trVpath);
	art_free(trVpath);
	art_free(vpath);
	Py_INCREF(Py_None);
	return Py_None;
}

static void _gstate_pathFill(gstateObject* self,int endIt, int vpReverse)
{

	if(self->fillColor.valid){
		ArtVpath	*vpath, *trVpath;
		ArtSVP		*svp, *tmp_svp;
		pixBufT*	p;
		double		a;
		if(endIt) gstate_pathEnd(self);
		dump_path(self);
		vpath = art_bez_path_to_vec(self->path, 0.25);
		if(0 && vpReverse) _vpath_reverse(vpath);
		trVpath =  art_vpath_affine_transform(vpath, self->ctm);
		a = _vpath_area(trVpath);
		if(fabs(a)>1e-7){
			/*fill only larger things*/
			svp = art_svp_from_vpath(trVpath);
			if(self->clipSVP) {
				tmp_svp = svp;
				dump_svp("fill clip svp path",self->clipSVP);
				dump_svp("fill svp orig",svp);
				svp = art_svp_intersect(tmp_svp, self->clipSVP);
				art_svp_free(tmp_svp);
				}

#ifdef	ROBIN_DEBUG
			printf("fillColor=0x%8.8x, opacity=" GFMT " -->0x%8.8x\n",self->fillColor.value, self->fillOpacity, _RGBA(self->fillColor.value, self->fillOpacity));
			dump_vpath("fill vpath", vpath);
			dump_vpath("fill trVpath", trVpath);
			dump_svp("fill svp",svp);
#endif
			p = self->pixBuf;
			art_rgb_svp_alpha(svp,
							 0,0,
							 p->width, p->height,
							 _RGBA(self->fillColor.value, self->fillOpacity),
							 p->buf,
							 p->rowstride,
							 NULL);

			art_svp_free(svp);
			}
		PyMem_Free(trVpath);
		PyMem_Free(vpath);
		}
}

static PyObject* gstate_pathFill(gstateObject* self, PyObject* args)
{
	if(!PyArg_ParseTuple(args,":pathFill")) return NULL;
	_gstate_pathFill(self,1,0);
	Py_INCREF(Py_None);
	return Py_None;
}

static PyObject* gstate_pathStroke(gstateObject* self, PyObject* args)
{
	ArtVpath	*vpath=NULL, *trVpath;
	ArtSVP*		svp=NULL;
	ArtSVP*		tmp_svp=NULL;
	pixBufT*	p;

	if(!PyArg_ParseTuple(args,":pathStroke")) return NULL;
	if(self->strokeColor.valid && self->strokeWidth>0){
		gstate_pathEnd(self);
		dump_path(self);
		vpath = art_bez_path_to_vec(self->path, 0.25);

		if(self->dash.dash){
			ArtVpath*	tvpath=vpath;
			vpath = art_vpath_dash(tvpath, &self->dash);
			PyMem_Free(tvpath);
			}
		dump_vpath("stroke vpath", vpath);
		trVpath = art_vpath_affine_transform(vpath, self->ctm);
		_vpath_area(trVpath);
		svp = art_svp_vpath_stroke(trVpath, self->lineJoin, self->lineCap, self->strokeWidth, 4, 0.5);
		art_free(trVpath);
		if(self->clipSVP){
			tmp_svp = svp;
			dump_svp("stroke clip svp path",self->clipSVP);
			dump_svp("stroke svp orig",svp);
			svp = art_svp_intersect(tmp_svp, self->clipSVP);
			art_svp_free(tmp_svp);
			}

		dump_svp("stroke svp",svp);
		p = self->pixBuf;
		art_rgb_svp_alpha(svp,
						 0,0,
						 p->width, p->height,
						 _RGBA(self->strokeColor.value, self->strokeOpacity),
						 p->buf,
						 p->rowstride,
						 NULL);
		art_svp_free(svp);
		PyMem_Free(vpath);
		}
	Py_INCREF(Py_None);
	return Py_None;
}

static PyObject* gstate_drawString(gstateObject* self, PyObject* args)
{
	A2DMX	orig, trans = {1,0,0,1,0,0}, scaleMat = {1,0,0,1,0,0};
	double	scaleFactor, x, y, gw;
	char*	text;
	ArtBpath	*saved_path;
	if(!self->font){
		PyErr_SetString(moduleError, "No font set!");
		return NULL;
		}
	if(!PyArg_ParseTuple(args,"dds:drawString", &x, &y, &text)) return NULL;

	/*save ctm*/
	memcpy(orig, self->ctm, sizeof(A2DMX));
	saved_path = self->path;

	/* translate to x, y */
	trans[4] = x;
	trans[5] = y;
	art_affine_multiply(self->ctm,trans,self->ctm);
	scaleFactor = self->fontSize/1000.0; /* apply font scaling */
	scaleMat[0] = scaleFactor;
#ifdef FLIPY
	scaleMat[3] = -scaleFactor;
#else
	scaleMat[3] = scaleFactor;
#endif
	art_affine_multiply(self->ctm, scaleMat, self->ctm);

	/*here we render each character one by one, lacks efficiency once again*/
	trans[5] = 0;
	while(*text){
		int	c = (*text++)&0xff;
		self->path = gt1_get_glyph_outline(self->font, c, &gw);	/*ascii encoding for the moment*/
		if(self->path){
			_gstate_pathFill(self,0,1);
			PyMem_Free(self->path);
			}
		else {
			fprintf(stderr, "No glyph outline for code %d!\n", c);
			gw = 1000;
			}

		/*move to right, scaling width by xscale and don't allow rotations or skew in CTM */
		trans[4] = gw;	/*units are em units right?*/
		art_affine_multiply(self->ctm, trans, self->ctm);
		}

	/*restore original ctm*/
	memcpy(self->ctm, orig, sizeof(A2DMX));
	self->path = saved_path;
	Py_INCREF(Py_None);
	return Py_None;
}

static PyObject* _fmtPathElement(ArtBpath *p, char* name, int n)
{
	PyObject	*P = PyTuple_New(n+1);
	PyTuple_SET_ITEM(P, 0, PyString_FromString(name));
	if(n==6){
		PyTuple_SET_ITEM(P, 1, PyFloat_FromDouble(p->x1));
		PyTuple_SET_ITEM(P, 2, PyFloat_FromDouble(p->y1));
		PyTuple_SET_ITEM(P, 3, PyFloat_FromDouble(p->x2));
		PyTuple_SET_ITEM(P, 4, PyFloat_FromDouble(p->y2));
		PyTuple_SET_ITEM(P, 5, PyFloat_FromDouble(p->x3));
		PyTuple_SET_ITEM(P, 6, PyFloat_FromDouble(p->y3));
		}
	else {
		PyTuple_SET_ITEM(P, 1, PyFloat_FromDouble(p->x3));
		PyTuple_SET_ITEM(P, 2, PyFloat_FromDouble(p->y3));
		}
	return P;
}

static PyObject* _get_gstatePath(int n, ArtBpath* path)
{
	PyObject	*P = PyTuple_New(n);
	PyObject	*e;
	ArtBpath	*p;
	int			i;
	for(i=0;i<n;i++){
		p = path+i;
		switch(p->code){
			case ART_MOVETO_OPEN:
				e = _fmtPathElement(p,"moveTo",2);
				break;
			case ART_MOVETO:
				e = _fmtPathElement(p,"moveToClosed",2);
				break;
			case ART_LINETO:
				e = _fmtPathElement(p,"lineTo",2);
				break;
			case ART_CURVETO:
				e = _fmtPathElement(p,"curveTo",6);
				break;
			}
		PyTuple_SET_ITEM(P, i, e);
		}
	return P;
}

static PyObject* gstate__stringPath(gstateObject* self, PyObject* args)
{
	double	w, x=0, y=0, s;
	char*	text;
	PyObject *P, *p;
	ArtBpath	*path, *pp;
	int		n, i, c;
	if(!self->font){
		PyErr_SetString(moduleError, "No font set!");
		return NULL;
		}
	if(!PyArg_ParseTuple(args,"s|dd:_stringPath", &text, &x, &y)) return NULL;

	s = self->fontSize/1000;
	n = strlen(text);
	P = PyTuple_New(n);
	for(i=0;i<n;i++){
		c = text[i]&0xff;
		path = gt1_get_glyph_outline(self->font, c, &w);	/*ascii encoding for the moment*/
		if(path){
			pp = path;
			while(pp->code!=ART_END){
				if(pp->code==ART_CURVETO){
					pp->x1= pp->x1*s+x;
					pp->y1= pp->y1*s+y;
					pp->x2= pp->x2*s+x;
					pp->y2= pp->y2*s+y;
					}
				pp->x3 = pp->x3*s+x;
				pp->y3 = pp->y3*s+y;
				pp++;
				}
			p = _get_gstatePath(pp-path,path);
			PyMem_Free(path);
			}
		else {
			fprintf(stderr, "No glyph outline for code %d!\n", c);
			w = 1000;
			Py_INCREF(Py_None);
			p = Py_None;
			}
		PyTuple_SET_ITEM(P, i, p);
		x += w*s;
		}
	return P;
}

static PyObject* gstate_setFont(gstateObject* self, PyObject* args)
{
	char	*fontName;
	Gt1EncodedFont*	f;
	double	fontSize;

	if(!PyArg_ParseTuple(args,"sd:setFont", &fontName, &fontSize)) return NULL;
	if(fontSize<0){
		PyErr_SetString(moduleError, "Invalid fontSize");
		return NULL;
		}
	f=gt1_get_encoded_font(fontName);
	if(f){
		self->font = f;
		self->fontSize = fontSize;
		Py_INCREF(Py_None);
		return Py_None;
		}

	PyErr_SetString(moduleError, "Can't find font!");
	return NULL;
}

static	void _dashFree(gstateObject* self)
{
	if(self->dash.dash){
		PyMem_Free(self->dash.dash);
		self->dash.dash = NULL;
		}
}

static	PyObject* _getA2DMX(double* ctm)
{
	return Py_BuildValue("(dddddd)",ctm[0],ctm[1],ctm[2],ctm[3],ctm[4],ctm[5]);
}

static int _setA2DMX(PyObject* value, double* ctm)
{
	int		i;
	A2DMX	m;
	if(value==Py_None){
		ctm[0] = ctm[3] = 1;
		ctm[1] = ctm[2] = ctm[4] = ctm[5] = 0;
		return 1;
		}
	if(!(i=PyArg_Parse(value,"(dddddd)",m+0,m+1,m+2,m+3,m+4,m+5))){
		PyErr_Clear();
		i=PyArg_Parse(value,"[dddddd]",m+0,m+1,m+2,m+3,m+4,m+5);
		}
	if(i){
		ctm[0] = m[0];
		ctm[1] = m[1];
		ctm[2] = m[2];
		ctm[3] = m[3];
		ctm[4] = m[4];
		ctm[5] = m[5];
		}
	return i;
}

#if 0
static	void _reverse_rows_inplace( char *buf, int nrows, int stride)
{
	char	*rbuf=buf+(nrows-1)*stride, tmp, *lim;
	int		stride2 = stride*2;
	while(buf<rbuf){
		lim = buf+stride;
		while(buf<lim){
			tmp = *buf;
			*buf++ = *rbuf;
			*rbuf++ = tmp;
			}
		rbuf -= stride2;
		}
}
#endif

static PyObject* gstate__aapixbuf(gstateObject* self, PyObject* args)
{
	int			dstX, dstY, dstW, dstH, srclen;
	double		ctm[6];
	ArtPixBuf	src;

	src.n_channels = 3;

	/*(dstX,dstY,dstW,dstH,src,srcW,srcH[,srcD[,aff]])*/
	if(!PyArg_ParseTuple(args,"iiiit#ii|i:_aapixbuf",
				&dstX, &dstY, &dstW, &dstH,
				&src.pixels,&srclen,&src.width,&src.height,&src.n_channels)) return NULL;
	ctm[0] = ((float)dstW)/src.width;
	ctm[1] = ctm[2] = 0;
	ctm[3] = -((float)dstH)/src.height;
	ctm[4] = dstX;
	ctm[5] = dstY+dstH;
	art_affine_multiply(ctm,ctm,self->ctm);
	src.format = ART_PIX_RGB;
	src.destroy_data = src.destroy = NULL;
	src.rowstride = src.width*src.n_channels;
	src.has_alpha = src.n_channels==4;
	src.bits_per_sample = 8;
	art_rgb_pixbuf_affine(self->pixBuf->buf,0,0,self->pixBuf->width,self->pixBuf->height,self->pixBuf->rowstride,
			(const ArtPixBuf*)&src,ctm,ART_FILTER_NEAREST,NULL);
	Py_INCREF(Py_None);
	return Py_None;
}

static	void _safeDecr(PyObject** p)
{
	if(*p){
		Py_DECREF(*p);
		*p = NULL;
		}
}

static	int _set_gstateDashArray(PyObject* value, gstateObject* self)
{
	if(value==Py_None){
		_dashFree(self);
		return 1;
		}
	else {
		int	n_dash, i, r=0;
		PyObject	*v=NULL, *pDash=NULL;
		double		offset, *dash=NULL;
		if(!PySequence_Check(value) || PySequence_Length(value)!=2){
L0:			PyErr_SetString(PyExc_ValueError, "dashArray should be None or (offset,(dashlen,....,dashlen,...))");
			if(dash) PyMem_Free(dash);
L1:			_safeDecr(&v);
			_safeDecr(&pDash);
			return r;
			}
		v = PySequence_GetItem(value,0);
		if(!PyArg_Parse(v,"d",&offset)) goto L0;
		pDash = PySequence_GetItem(value,1);
		if(!PySequence_Check(pDash) || (n_dash=PySequence_Length(pDash))<1) goto L0;
		dash = PyMem_Malloc(sizeof(double)*n_dash);
		for(i=0;i<n_dash;i++){
			_safeDecr(&v);
			v = PySequence_GetItem(pDash,i);
			if(!PyArg_Parse(v,"d",dash+i)) goto L0;
			}

		/*everything checks out release current thing and set new one*/
		_dashFree(self);
		self->dash.n_dash = n_dash;
		self->dash.offset = offset;
		self->dash.dash = dash;
		r = 1;
		goto L1;
		}
}

static	PyObject*  _get_gstateDashArray(gstateObject* self)
{
	PyObject	*r=NULL, *pDash=NULL, *v=NULL;
	int			n_dash, i;
	double		*dash;

	if(!self->dash.dash){
		Py_INCREF(Py_None);
		return Py_None;
		}

	if(!(r=PyTuple_New(2))) goto L0;
	if(!(pDash=PyTuple_New(n_dash=self->dash.n_dash))) goto L0;
	if(!(v = PyFloat_FromDouble(self->dash.offset))) goto L0;
	PyTuple_SET_ITEM(r,0,v);
	PyTuple_SET_ITEM(r,1,pDash);
	for(dash=self->dash.dash,i=0;i<n_dash;i++){
		if(!(v = PyFloat_FromDouble(dash[i]))) goto L0;
		PyTuple_SET_ITEM(pDash,i,v);
		}
	return r;
L0:
	_safeDecr(&r);
	_safeDecr(&pDash);
	_safeDecr(&v);
	return NULL;
}

static	int _set_gstateColor(PyObject* value, gstateColor* c)
{
	art_u32		cv;
	int			i;
	if(value==Py_None){
		c->valid = 0;
		return 1;
		}
	if((i = PyArg_Parse(value,"i",&cv))){
L0:		c->value = cv;
		c->valid = 1;
		return 1;
		}
	else if(PyObject_HasAttrString(value,"red")
			&& PyObject_HasAttrString(value,"green")
			&& PyObject_HasAttrString(value,"blue")){
		double	r, g, b;
		PyObject *v;
		PyErr_Clear();
		v = PyObject_GetAttrString(value,"red");
		i = PyArg_Parse(v,"d",&r);
		Py_DECREF(v);
		if(!i) goto L1;
		v = PyObject_GetAttrString(value,"green");
		i = PyArg_Parse(v,"d",&g);
		Py_DECREF(v);
		if(!i) goto L1;
		v = PyObject_GetAttrString(value,"blue");
		i = PyArg_Parse(v,"d",&b);
		Py_DECREF(v);
		if(!i) goto L1;
		cv = ((((int)(r*255))&0xFF)<<16) | ((((int)(g*255))&0xFF)<<8) | (((int)(b*255))&0xFF);
		goto L0;
		}
L1:
	PyErr_SetString(PyExc_ValueError, "bad color value");
	return 0;
}

static	int _set_gstateColorX(PyObject* value, gstateColorX* c)
{
	int	i;
	if(PySequence_Check(value)){
		size_t	len;
		i = PyArg_Parse(value,"(iis#)",&c->width,&c->height,&c->buf,&len);
		if(i){
			/*we assume depth 3*/
			if(len!=3*c->width*c->height){
				PyErr_SetString(PyExc_ValueError, "bad bg image length");
				i = 0;
				}
			else{
				c->stride = c->width*3;
				}
			}
		}
	else {
		gstateColor	bg = {0xffffffff,1};
		i = _set_gstateColor(value,&bg);
		if(i){
			c->buf[0] = (bg.value>>16)&0xff;
			c->buf[1] = (bg.value>>8)&0xff;
			c->buf[2] = bg.value&0xff;
			}
		}
	return i;
}

static PyObject* _get_gstateColor(gstateColor* c)
{
	if(c->valid) return PyInt_FromLong(c->value);
	Py_INCREF(Py_None);
	return Py_None;
}

static PyObject* _get_gstateFontName(Gt1EncodedFont *f)
{
	if(f) return PyString_FromString(gt1_encoded_font_name(f));
	Py_INCREF(Py_None);
	return Py_None;
}

static struct PyMethodDef gstate_methods[] = {
	{"clipPathClear", (PyCFunction)gstate_clipPathClear, METH_VARARGS, "clipPathClear()"},
	{"clipPathSet", (PyCFunction)gstate_clipPathSet, METH_VARARGS, "clipPathSet()"},
	{"curveTo", (PyCFunction)gstate_curveTo, METH_VARARGS, "curveTo(x1,y1,x2,y2,x3,y3)"},
	{"drawString", (PyCFunction)gstate_drawString, METH_VARARGS, "drawString(x,y,text)"},
	{"lineTo", (PyCFunction)gstate_lineTo, METH_VARARGS, "lineTo(x,y)"},
	{"moveTo", (PyCFunction)gstate_moveTo, METH_VARARGS, "moveTo(x,y)"},
	{"moveToClosed", (PyCFunction)gstate_moveToClosed, METH_VARARGS, "moveToClosed(x,y)"},
	{"pathBegin", (PyCFunction)gstate_pathBegin, METH_VARARGS, "pathBegin()"},
	{"pathClose", (PyCFunction)gstate_pathClose, METH_VARARGS, "pathClose()"},
	{"pathFill", (PyCFunction)gstate_pathFill, METH_VARARGS, "pathFill()"},
	{"pathStroke", (PyCFunction)gstate_pathStroke, METH_VARARGS, "pathStroke()"},
	{"setFont", (PyCFunction)gstate_setFont, METH_VARARGS, "setFont(fontName,fontSize)"},
	{"_stringPath", (PyCFunction)gstate__stringPath, METH_VARARGS, "_stringPath(text[,x=0,y=0])"},
	{"_aapixbuf", (PyCFunction)gstate__aapixbuf, METH_VARARGS, "_aapixbuf(dstX,dstY,dstW,dstH,src,srcW,srcH[,srcD]])"},
	{NULL, NULL}		/* sentinel */
};

static PyObject* gstate_getattr(gstateObject *self, char *name)
{
#ifdef	ROBIN_DEBUG
	printf("getattr(%s)\n", name);
#endif
	if(!strcmp(name,"ctm")) return _getA2DMX(self->ctm);
	else if(!strcmp(name,"strokeColor")) return _get_gstateColor(&self->strokeColor);
	else if(!strcmp(name,"fillColor")) return _get_gstateColor(&self->fillColor);
	else if(!strcmp(name,"fillRule")) return PyInt_FromLong(self->fillRule);
	else if(!strcmp(name,"lineCap")) return PyInt_FromLong(self->lineCap);
	else if(!strcmp(name,"lineJoin")) return PyInt_FromLong(self->lineJoin);
	else if(!strcmp(name,"hasClipPath")) return PyInt_FromLong(self->clipSVP!=NULL);
	else if(!strcmp(name,"strokeWidth")) return PyFloat_FromDouble(self->strokeWidth);
	else if(!strcmp(name,"strokeOpacity")) return PyFloat_FromDouble(self->strokeOpacity);
	else if(!strcmp(name,"fillOpacity")) return PyFloat_FromDouble(self->fillOpacity);
	else if(!strcmp(name,"width")) return PyInt_FromLong(self->pixBuf->width);
	else if(!strcmp(name,"height")) return PyInt_FromLong(self->pixBuf->height);
	else if(!strcmp(name,"depth")) return PyInt_FromLong(self->pixBuf->nchan);
	else if(!strcmp(name,"path")) return _get_gstatePath(self->pathLen,self->path);
	else if(!strcmp(name,"pathLen")) return PyInt_FromLong(self->pathLen);
	else if(!strcmp(name,"fontSize")) return PyFloat_FromDouble(self->fontSize);
	else if(!strcmp(name,"fontName")) return _get_gstateFontName(self->font);
	else if(!strcmp(name,"dashArray")) return _get_gstateDashArray(self);
	else if(!strcmp(name,"pixBuf")){
		pixBufT* p = self->pixBuf;
		int	nw = p->width*p->nchan;
		PyObject *v = PyString_FromStringAndSize((char *)p->buf, p->height*nw);
		char	*r1 = PyString_AS_STRING(v);
		char	*r2 = r1 + (p->height-1)*p->rowstride;
		while(r1<r2){
			int	i;
			for(i=0;i<nw;i++){
				char c;
				c = r2[i];
				r2[i] = r1[i];
				r1[i] = c;
				}
			r1 += nw;
			r2 -= nw;
			}
		return v;
		}
	return Py_FindMethod(gstate_methods, (PyObject *)self, name);
}

static int gstate_setattr(gstateObject *self, char *name, PyObject* value)
{
	int	i;
#ifdef	ROBIN_DEBUG
	printf("setattr(%s)\n", name);
#endif
	if(!strcmp(name,"ctm")) i = _setA2DMX(value,self->ctm);
	else if(!strcmp(name,"strokeColor")) i = _set_gstateColor(value,&self->strokeColor);
	else if(!strcmp(name,"fillColor")) i = _set_gstateColor(value,&self->fillColor);
	else if(!strcmp(name,"fillRule")) i = PyArg_Parse(value,"i",&self->fillRule);
	else if(!strcmp(name,"lineCap")) i = PyArg_Parse(value,"i",&self->lineCap);
	else if(!strcmp(name,"lineJoin")) i = PyArg_Parse(value,"i",&self->lineJoin);
	else if(!strcmp(name,"strokeWidth")) i = PyArg_Parse(value,"d",&self->strokeWidth);
	else if(!strcmp(name,"strokeOpacity")) i = PyArg_Parse(value,"d",&self->strokeOpacity);
	else if(!strcmp(name,"fillOpacity")) i = PyArg_Parse(value,"d",&self->fillOpacity);
	else if(!strcmp(name,"dashArray")) i = _set_gstateDashArray(value,self);
	else {
		PyErr_SetString(PyExc_AttributeError, name);
		i = 0;
		}

	if(i && !PyErr_Occurred()) i = 0;
	else {
		i = -1;
		if(!PyErr_Occurred()) PyErr_SetString(PyExc_ValueError, name);
		}
	return i;
}

static	void gstateFree(gstateObject* self)
{
	pixBufFree(&self->pixBuf);
	_dashFree(self);
	if(self->path){
		PyMem_Free(self->path);
		}
	if(self->clipSVP){
		PyMem_Free(self->clipSVP);
		}
	PyMem_DEL(self);
}

static PyTypeObject gstateType = {
	PyObject_HEAD_INIT(0)
	0,								/*ob_size*/
	"gstate",						/*tp_name*/
	sizeof(gstateObject),			/*tp_basicsize*/
	0,								/*tp_itemsize*/
	/* methods */
	(destructor)gstateFree,			/*tp_dealloc*/
	(printfunc)0,					/*tp_print*/
	(getattrfunc)gstate_getattr,	/*tp_getattr*/
	(setattrfunc)gstate_setattr,	/*tp_setattr*/
	(cmpfunc)0,						/*tp_compare*/
	(reprfunc)0,					/*tp_repr*/
	0,								/*tp_as_number*/
	0,								/*tp_as_sequence*/
	0,								/*tp_as_mapping*/
	(hashfunc)0,					/*tp_hash*/
	(ternaryfunc)0,					/*tp_call*/
	(reprfunc)0,					/*tp_str*/

	/* Space for future expansion */
	0L,0L,0L,0L,
	/* Documentation string */
	"gstate instance\n\
\n\
gstates have the following methods\n\
 clipPathClear() clear clipPath\n\
 clipPathSet() move current path into clipPath\n\
 curveTo(x1,y1,x2,y2,x3,y3)  #add a curveTo type segment\n\
 drawString(x,y,text)\n\
 moveTo(x,y) start a segment\n\
 moveToClosed(x,y) start a closed segment\n\
 lineTo(x,y) add a line segment\n\
 pathBegin() initialise\n\
 pathClose() close path with LINETO to preceding  MOVETO\n\
 pathFill()  fill current path\n\
 pathStroke() stroke current path\n\
 setFont(fontName,fontSize) set the font from the gt1 cache\n\
 _stringPath(text) return path dump of text\n\
 _aapixbuf(dstX,dstY,dstW,dstH,src,srcW,srcH[,srcD]) composite\n\
      srcW by srcY depth srcD(=3) image to dst Rect(dstX,dstY,dstW,dstH)\n\
	  src is string bytes in rgb order\n\
\n\
gstates have the following attributes\n\
ctm			6vec float transformation matrix\n\
strokeColor 32bit stroke colour\n\
fillColor	32bit fill colour\n\
fillRule	int fill rule\n\
lineCap		int\n\
lineJoin	int\n\
hasClipPath readonly int\n\
strokeWidth float\n\
strokeOpacity float\n\
fillOpacity float\n\
dashArray	[floatOffset, [floatdash array]]\n\
fontName	string readonly\n\
fontSize	float readonly\n\
width		int	readonly pixBuf width\n\
height		int readonly pixBuf height\n\
depth		int readonly pixBuf depth\n\
path		readonly tuple describing the path\n\
pathLen		int readonly number of path segments\n\
pixBuf		str readonly the pixBuf\n\
"
};


static  art_u32			bgv = 0xffffffff;

static	gstateObject* gstate(PyObject* module, PyObject* args, PyObject* keywds)
{
	gstateObject*		self=NULL;
	int					w, h, d=3, m=12;
	char				*kwlist[] = {"w","h","depth","bg",NULL};
	PyObject			*pbg=NULL;
	gstateColorX		bg = {1,1,0,(art_u8*)&bgv};	/*default white background*/

	if(!PyArg_ParseTupleAndKeywords(args,keywds,"ii|iO:gstate",kwlist,&w,&h,&d,&pbg)) return NULL;
	if(pbg){
		if(!_set_gstateColorX(pbg,&bg)){
			PyErr_SetString(moduleError, "invalid value for bg");
			return NULL;
			}
		}

	if((self = PyObject_NEW(gstateObject, &gstateType))){
		self->pixBuf = pixBufAlloc(w,h,d,bg);
		self->path = PyMem_New(ArtBpath,m);
		if(!self->pixBuf){
			PyErr_SetString(moduleError, "no memory");
			gstateFree(self);
			self = NULL;
			}
		else {
			self->ctm[0] = self->ctm[3] = 1.0;
			self->ctm[1] = self->ctm[2] = self->ctm[4] = self->ctm[5] = 0.0;
			self->strokeColor.valid = self->fillColor.valid = 0;
			self->fillRule = self->lineCap = self->lineJoin = 0;
			self->strokeOpacity = self->strokeWidth = self->fillOpacity = 1.0;
			self->pathLen = 0;
			self->pathMax = m;
			self->clipSVP = NULL;
			self->font = NULL;
			self->fontSize = 10;
			self->dash.n_dash = 0;
			self->dash.dash = NULL;
			}
		}

	return self;
}

static	PyObject*	makeT1Font(PyObject* self, PyObject* args)
{
	char	*name, *pfbPath, **names;
	size_t	N, i;
	int		ok;
	PyObject*	L;
	char	*s, *_notdef = ".notdef";

	if(!PyArg_ParseTuple(args,"ssO:makeT1Font", &name, &pfbPath, &L)) return NULL;
	if(!PySequence_Check(L)){
		PyErr_SetString(moduleError, "names should be a sequence object returning strings");
		return NULL;
		}
	N = PySequence_Length(L);
	names = PyMem_Malloc(N*sizeof(*names));
	for(i=0;i<N;i++){
		PyObject*	v = PySequence_GetItem(L,i);
		if(v==Py_None){
			s = _notdef;
			}
		else if(PyString_Check(v)){
			s = strdup(PyString_AsString(v));
			}
		else {
			PyErr_SetString(moduleError, "names should all be strings");
			Py_DECREF(v);
			break;
			}
		names[i] = s;
		Py_DECREF(v);
		}
	if((ok=(i==N))){
		if(!gt1_create_encoded_font(name,pfbPath,names,N)){
			PyErr_SetString(moduleError, "can't make font");
			ok = 0;
			}
		}
	while(i--){
		s = names[i];
		if(s!=_notdef) PyMem_Free(s);
		}
	PyMem_Free(names);
	if(!ok) return NULL;
	Py_INCREF(Py_None);
	return Py_None;
}

static PyObject* delCache(PyObject* self, PyObject* args)
{
	if(!PyArg_ParseTuple(args,":delCache")) return NULL;
	gt1_del_cache();
	Py_INCREF(Py_None);
	return Py_None;
}

#define HEADER_SIZE		512

#define	RUN_THRESH		3
#define	MAX_RUN			128		/* 0xff = 2, 0xfe = 3, etc */
#define	MAX_COUNT		128		/* 0x00 = 1, 0x01 = 2, etc */

/* Opcodes */
#define PICT_picVersion		0x11
#define PICT_background		0x1b
#define	PICT_headerOp		0x0C00
#define PICT_clipRgn		0x01
#define PICT_PackBitsRect	0x98
#define PICT_EndOfPicture	0xFF
#define PICT_MAXCOLORS 256

typedef unsigned char pixel;
typedef struct {pixel *p, *buf;} BYTE_STREAM;
void pict_putc(unsigned c, BYTE_STREAM* bs)
{
	*bs->p++ = c;
}

static void pict_putFill(BYTE_STREAM* fd, int n)
{
	register int i;

	for (i = 0; i < n; i++)
		(void) pict_putc(0, fd);
}

static void pict_putShort(BYTE_STREAM* fd, int i)
{
	(void) pict_putc((i >> 8) & 0xff, fd);
	(void) pict_putc(i & 0xff, fd);
}

static void pict_putLong( BYTE_STREAM *fd, long i )
{
	(void) pict_putc((int)((i >> 24) & 0xff), fd);
	(void) pict_putc(((int)(i >> 16) & 0xff), fd);
	(void) pict_putc(((int)(i >> 8) & 0xff), fd);
	(void) pict_putc((int)(i & 0xff), fd);
}

static void pict_putRect(BYTE_STREAM* fd, int s0, int s1, int s2, int s3)
{
	pict_putShort(fd, s0);
	pict_putShort(fd, s1);
	pict_putShort(fd, s2);
	pict_putShort(fd, s3);
}

#define		runtochar(c)	(257-(c))
#define		counttochar(c)	((c)-1)
static int pict_putRow(BYTE_STREAM* fd, int row, int cols, pixel* rowpixels, char* packed)
{
	register int i;
	int packcols, count, run, rep, oc;
	register pixel *pP;
	pixel lastp;
	register char *p;

	run = count = 0;
	for (cols--, i = cols, pP = rowpixels + cols, p = packed, lastp = *pP;
		i >= 0; i--, lastp = *pP, pP--){
		if (lastp == *pP) run++;
		else if (run < RUN_THRESH){
			while (run > 0){
				*p++ = lastp;
				run--;
				count++;
				if (count == MAX_COUNT){
					*p++ = counttochar(MAX_COUNT);
					count -= MAX_COUNT;
					}
				}
			run = 1;
			}
		else{
			if (count > 0) *p++ = counttochar(count);
			count = 0;
			while (run > 0){
				rep = run > MAX_RUN ? MAX_RUN : run;
				*p++ = lastp;
				*p++ = runtochar(rep);
				run -= rep;
				}
			run = 1;
			}
		}
	if (run < RUN_THRESH){
		while (run > 0){
			*p++ = lastp;
			run--;
			count++;
			if (count == MAX_COUNT){
				*p++ = counttochar(MAX_COUNT);
				count -= MAX_COUNT;
				}
			}
		}
	else{
		if (count > 0) *p++ = counttochar(count);
		count = 0;
		while (run > 0){
			rep = run > MAX_RUN ? MAX_RUN : run;
			*p++ = lastp;
			*p++ = runtochar(rep);
				run -= rep;
			}
		run = 1;
		}
	if (count > 0) *p++ = counttochar(count);

	packcols = p - packed;		/* how many did we write? */
	if (cols > 250){
		pict_putShort(fd, packcols);
		oc = packcols + 2;
		}
	else{
		(void) pict_putc(packcols, fd);
		oc = packcols + 1;
		}

	/* now write out the packed row */
	while(p != packed){
		--p;
		(void) pict_putc(*p, fd);
		}

	return (oc);
}

static PyObject* pil2pict(PyObject* self, PyObject* args)
{
	PyObject *result;
	int		rows, cols, colors, i, row, oc, len, npixels, tc=-1;
	char	*packed;
	long	lpos;
	pixel	*palette, *pixels;
	BYTE_STREAM	OBS;
	BYTE_STREAM	*obs = &OBS;

	if(!PyArg_ParseTuple(args,"iis#s#|i:pil2pict",&cols,&rows,&pixels,&npixels,&palette,&colors,&tc)) return NULL;

	colors /= 3;
	len = HEADER_SIZE*4+colors*4*sizeof(short)+cols*rows*sizeof(pixel);	/*generous estimate of maximum size*/
	obs->buf = obs->p = (pixel*)malloc(len);

	/* write the header */
	pict_putFill(obs, HEADER_SIZE);

	/* write picSize and picFrame */
	pict_putShort(obs, 0);
	pict_putRect(obs, 0, 0, rows, cols);

	/* write version op and version */
	pict_putShort(obs, PICT_picVersion);
	pict_putShort(obs, 0x02FF);
	pict_putShort(obs, PICT_headerOp);
	pict_putShort(obs, 0xFFFE);
	pict_putShort(obs, 0);

	pict_putRect(obs, 72, 0, 72, 0);	/*h/v resolutions*/
	pict_putRect(obs, 0,0, cols,rows);
	pict_putFill(obs, 4);


	/* seems to be needed by many PICT2 programs */
	pict_putShort(obs, 0x1e);	/*DefHilite*/
	pict_putShort(obs, PICT_clipRgn);
	pict_putShort(obs, 10);
	pict_putRect(obs, 0, 0, rows, cols);
	if(tc!=-1){
		pict_putShort(obs, PICT_background);
		pict_putShort(obs, (short)(((unsigned long)((tc>>16)&0xFF)*65535L)/255L));
		pict_putShort(obs, (short)(((unsigned long)((tc>>8)&0xFF)*65535L)/255L));
		pict_putShort(obs, (short)(((unsigned long)(tc&0xFF)*65535L)/255L));
#if 0
		pict_putShort(obs, 0x0f);				/*bkcolor*/
		pict_putLong(obs, (unsigned long)tc);
#endif
		pict_putShort(obs,5);					/*src mode*/
		pict_putShort(obs,36|64);
		pict_putShort(obs,8);					/*src mode*/
		pict_putShort(obs,36|64);
		}

	/* write picture */
	pict_putShort(obs, PICT_PackBitsRect);
	pict_putShort(obs, cols | 0x8000);
	pict_putRect(obs, 0, 0, rows, cols);
	pict_putShort(obs, 0);	/* pmVersion */
	pict_putShort(obs, 0);	/* packType */
	pict_putLong(obs, 0L);	/* packSize */
	pict_putRect(obs, 72, 0, 72, 0);	/* hRes/vRes */
	pict_putShort(obs, 0);	/* pixelType */
	pict_putShort(obs, 8);	/* pixelSize */
	pict_putShort(obs, 1);	/* cmpCount */
	pict_putShort(obs, 8);	/* cmpSize */
	pict_putLong(obs, 0L);	/* planeBytes */
	pict_putLong(obs, 0L);	/* pmTable */
	pict_putLong(obs, 0L);	/* pmReserved */
	pict_putLong(obs, 0L);	/* ctSeed */
	pict_putShort(obs, 0);	/* ctFlags */
	pict_putShort(obs, colors-1);	/* ctSize */

	/*Write out the colormap*/
	for (i = 0; i < colors; i++){
		pict_putShort(obs, i);
		pict_putShort(obs, (short)(((unsigned long)palette[3*i]*65535L)/255L));
		pict_putShort(obs, (short)(((unsigned long)palette[3*i+1]*65535L)/255L));
		pict_putShort(obs, (short)(((unsigned long)palette[3*i+2]*65535L)/255L));
		}

	pict_putRect(obs, 0, 0, rows, cols);		/*srcRect*/
	pict_putRect(obs, 0, 0, rows, cols);		/*dstRect*/
	pict_putShort(obs,tc!=-1 ? 36|64 : 0);			/*transfer mode*/

	/*write out the pixel data.*/
	packed = (char*) malloc((unsigned)(cols+cols/MAX_COUNT+1));
	oc = 0;
	for(row=0; row<rows; row++) oc += pict_putRow(obs, row, cols, pixels+row*cols, packed);
	free(packed);

	/*pad to even number of bytes*/
	if (oc & 1) (void)pict_putc(0, obs);
	pict_putShort(obs, PICT_EndOfPicture);

	len = obs->p-obs->buf;
	lpos = (obs->p-obs->buf) - HEADER_SIZE;
	obs->p = obs->buf + HEADER_SIZE;
	pict_putShort(obs, (short)(lpos & 0xffff));
	result = PyString_FromStringAndSize((const char *)obs->buf,len);
	free(obs->buf);
	return result;
}

static struct PyMethodDef moduleMethods[] = {
	{"gstate", (PyCFunction)gstate, METH_VARARGS|METH_KEYWORDS, "gstate(width,height[,depth=3][,bg=0xffffff]) create an initialised graphics state"},
	{"makeT1Font", (PyCFunction)makeT1Font, METH_VARARGS, "makeT1Font(fontName,pfbPath,names)"},
	{"delCache", (PyCFunction)delCache, METH_VARARGS, "delCache()"},
	{"pil2pict", (PyCFunction)pil2pict, METH_VARARGS, "pil2pict(cols,rows,datastr,palette) return PICT version of im as a string"},
	{NULL,	NULL}			/*sentinel*/
	};

void init_renderPM(void)
{
	PyObject *m, *d;

	/*set up the types by hand*/
	gstateType.ob_type = &PyType_Type;

	/* Create the module and add the functions */
	m = Py_InitModule(MODULE, moduleMethods);

	/* Add some symbolic constants to the module */
	d = PyModule_GetDict(m);
	_version = PyString_FromString(VERSION);
	PyDict_SetItemString(d, "_version", _version );
	_libart_version = PyString_FromString(LIBART_VERSION);
	PyDict_SetItemString(d, "_libart_version", _libart_version );
	moduleError = PyErr_NewException(MODULE ".Error",NULL,NULL);
	PyDict_SetItemString(d, "Error", moduleError);

	/*add in the docstring*/
	PyDict_SetItemString(d, "__doc__",	PyString_FromString(moduleDoc));
	PyDict_SetItemString(d, "__file__", PyString_FromString(__FILE__));
}
