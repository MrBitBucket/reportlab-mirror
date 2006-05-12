/****************************************************************************
#Copyright ReportLab Europe Ltd. 2000-2004
#see license.txt for license details
#history http://www.reportlab.co.uk/cgi-bin/viewcvs.cgi/public/reportlab/trunk/reportlab/lib/_rl_accel.c
 ****************************************************************************/
#if 0
static __version__=" $Id$ "
#endif
#include "Python.h"
#include <stdlib.h>
#include <math.h>
#define DEFERRED_ADDRESS(A) 0
#if defined(__GNUC__) || defined(sun) || defined(_AIX) || defined(__hpux)
#	define STRICMP strcasecmp
#elif defined(_MSC_VER)
#	define STRICMP stricmp
#elif defined(macintosh)
# include <extras.h>
# define strdup _strdup
# define STRICMP _stricmp
#else
#	error "Don't know how to define STRICMP"
#endif
#ifndef max
#	define max(a,b) ((a)>(b)?(a):(b))
#endif
#ifndef min
#	define min(a,b) ((a)<(b)?(a):(b))
#endif
#define VERSION "0.53"
#define MODULE "_rl_accel"


static PyObject *moduleVersion;
typedef struct _fI_t {
		char*			name;
		int				ascent, descent;
		int				widths[256];
		struct _fI_t*	next;
		} fI_t;

typedef struct _eI_t {
		char*			name;
		fI_t*			fonts;
		struct _eI_t*	next;
		} eI_t;

eI_t		*Encodings=NULL;
eI_t		*defaultEncoding = NULL;
PyObject	*_SWRecover=NULL;

static PyObject *ErrorObject;

static	eI_t*	find_encoding(char* name)
{
	eI_t*	e = Encodings;
	for(;e;e=e->next) if(!STRICMP(name,e->name)) return e;
	return (eI_t*)0;
}

static	fI_t* find_font(char* name, fI_t* f)
{
	for(;f;f=f->next) if(!STRICMP(name,f->name)) return f;
	return (fI_t*)0;
}

static	int _parseSequenceInt(PyObject* e, int i, int *x)
{
	PyObject	*p;
	if((p = PySequence_GetItem(e,i)) && (p = PyNumber_Int(p))){
		*x=PyInt_AS_LONG(p);
		return 1;
		}
	return 0;
}

static PyObject *_pdfmetrics__SWRecover(PyObject* dummy, PyObject* args)
{
	PyObject *result = NULL;
	PyObject *temp=NULL;

	if (PyArg_ParseTuple(args, "|O:_SWRecover", &temp)) {
		if(temp){
			if (!PyCallable_Check(temp)) {
				PyErr_SetString(PyExc_TypeError, "parameter must be callable");
				return NULL;
				}
			Py_INCREF(temp);					/* Add a reference to new callback */
			Py_XDECREF(_SWRecover);	/* Dispose of previous callback */
			_SWRecover = temp;				/* Remember new callback */
			}
		else if(_SWRecover){
			Py_INCREF(_SWRecover);
			return _SWRecover;
			}
		/* Boilerplate to return "None" */
		Py_INCREF(Py_None);
		result = Py_None;
		}
	return result;
}

static PyObject *_pdfmetrics_defaultEncoding(PyObject *self, PyObject* args)
{
	char*	encoding=NULL;
	eI_t*	e;
	if (!PyArg_ParseTuple(args, "|s", &encoding)) return NULL;
	if(encoding){
		if(!(e= find_encoding(encoding))){
			e = (eI_t*)malloc(sizeof(eI_t));
			e->name = strdup(encoding);
			e->next = Encodings;
			e->fonts = NULL;
			Encodings = e;
			}
		defaultEncoding = e;
		}
	else if(defaultEncoding) return Py_BuildValue("s",defaultEncoding->name);
	Py_INCREF(Py_None);
	return Py_None;
}

static PyObject *_pdfmetrics_setFontInfo(PyObject *self, PyObject* args)
{
	char		*fontName, *encoding;
	int			ascent, descent;
	PyObject	*pW;
	int			i;
	eI_t*		e;
	fI_t*		f;

	if (!PyArg_ParseTuple(args, "ssiiO", &fontName, &encoding, &ascent, &descent,&pW)) return NULL;
	i = PySequence_Length(pW);
	if(i!=256){
badSeq:	PyErr_SetString(ErrorObject,"widths should be a length 256 sequence of integers");
		return NULL;
		}
	e = find_encoding(encoding);
	if(!e){
		e = (eI_t*)malloc(sizeof(eI_t));
		e->name = strdup(encoding);
		e->next = Encodings;
		e->fonts = NULL;
		Encodings = e;
		f = NULL;
		}
	else
		f = find_font(fontName,e->fonts);

	if(!f){
		f = (fI_t*)malloc(sizeof(fI_t));
		f->name = strdup(fontName);
		f->next = e->fonts;
		e->fonts = f;
		}
	f->ascent = ascent;
	f->descent = descent;
	for(i=0;i<256;i++)
		if(!_parseSequenceInt(pW,i,&f->widths[i])) goto badSeq;

	Py_INCREF(Py_None);
	return Py_None;
}

static PyObject *_pdfmetrics_getFonts(PyObject *self, PyObject *args)
{
	char		*encoding=0;
	fI_t*		f;
	eI_t*		e;
	int			nf;
	PyObject	*r;
	if (!PyArg_ParseTuple(args, "|s:getFonts", &encoding)) return NULL;
	if(!(e=encoding?find_encoding(encoding):defaultEncoding)){
		PyErr_SetString(ErrorObject,"unknown encoding");
		return NULL;
		}

	for(nf=0,f=e->fonts;f;f=f->next) nf++;

	r = PyList_New(nf);
	for(nf=0,f=e->fonts;f;f=f->next) PyList_SetItem(r,nf++,PyString_FromString(f->name));

	return r;
}

static PyObject *_pdfmetrics_getFontInfo(PyObject *self, PyObject* args)
{
	char		*fontName, *encoding=0;
	eI_t*		e;
	fI_t*		f;
	int			i;
	PyObject	*r, *t;

	if (!PyArg_ParseTuple(args, "s|s", &fontName, &encoding)) return NULL;
	if(!(e=encoding?find_encoding(encoding):defaultEncoding)){
		PyErr_SetString(ErrorObject,"unknown encoding");
		return NULL;
		}

	if(!(f = find_font(fontName,e->fonts))){
		PyErr_SetString(ErrorObject,"unknown font");
		return NULL;
		}

	t = PyList_New(256);
	for(i=0;i<256;i++){
		PyList_SetItem(t,i,PyInt_FromLong(f->widths[i]));
		}
	r = PyTuple_New(3);
	PyTuple_SetItem(r,0,t);
	PyTuple_SetItem(r,1,PyInt_FromLong(f->ascent));
	PyTuple_SetItem(r,2,PyInt_FromLong(f->descent));
	return r;
}

static PyObject *_pdfmetrics_stringWidth(PyObject *self, PyObject* args)
{
	char		*fontName, *encoding=NULL;
	unsigned char *text;
	double		fontSize;
	fI_t		*fI;
	eI_t		*e;
	int			w, *width, i, textLen;
	static int	recover=1;

	if (!PyArg_ParseTuple(args, "s#sd|s", &text, &textLen, &fontName, &fontSize, &encoding)) return NULL;
	if(fontSize<=0){
		PyErr_SetString(ErrorObject,"bad fontSize");
		return NULL;
		}

	if(!(e=encoding?find_encoding(encoding):defaultEncoding)){
		PyErr_SetString(ErrorObject,"unknown encoding");
		return NULL;
		}

	if(!(fI=find_font(fontName,e->fonts))){
		if(_SWRecover && recover){
			PyObject *arglist = Py_BuildValue("(s#sds)",text,textLen,fontName,fontSize,e->name);
			PyObject *result;
			if(!arglist){
				PyErr_SetString(ErrorObject,"recovery failed!");
				return NULL;
				}
			recover = 0;
			result = PyEval_CallObject(_SWRecover, arglist);
			recover = 1;
			Py_DECREF(arglist);
			if(!result) return NULL;
			if(result!=Py_None) return result;
			Py_DECREF(result);
			if((fI=find_font(fontName,e->fonts))) goto L2;
			}
		PyErr_SetString(ErrorObject,"unknown font");
		return NULL;
		}

L2:
	width = fI->widths;
	for(i=w=0;i<textLen;i++)
		w += width[text[i]];

	return Py_BuildValue("f",0.001*fontSize*w);
}

static PyObject *_pdfmetrics_instanceStringWidth(PyObject *unused, PyObject* args)
{
	PyObject	*pfontName, *self;
	char		*fontName;
	unsigned char *text;
	double		fontSize;
	fI_t		*fI;
	eI_t		*e;
	int			w, *width, i, textLen;
	static int	recover=1;

	if (!PyArg_ParseTuple(args, "Os#d", &self, &text, &textLen, &fontSize)) return NULL;
	if(fontSize<=0){
		PyErr_SetString(ErrorObject,"bad fontSize");
		return NULL;
		}

	pfontName = PyObject_GetAttrString(self,"fontName");
	if(!pfontName){
		PyErr_SetString(PyExc_AttributeError,"No attribute fontName");
		return NULL;
		}

	if(!PyString_Check(pfontName)){
		Py_DECREF(pfontName);
		PyErr_SetString(PyExc_TypeError,"Attribute fontName is not a string");
		return NULL;
		}
	fontName = PyString_AsString(pfontName);

	e = defaultEncoding;

	if(!(fI=find_font(fontName,e->fonts))){
		if(_SWRecover && recover){
			PyObject *arglist = Py_BuildValue("(s#sds)",text,textLen,fontName,fontSize,e->name);
			PyObject *result;
			if(!arglist){
				PyErr_SetString(ErrorObject,"recovery failed!");
				goto L1;
				}
			recover = 0;
			result = PyEval_CallObject(_SWRecover, arglist);
			recover = 1;
			Py_DECREF(arglist);
			if(!result) goto L1;
			if(result!=Py_None) return result;
			Py_DECREF(result);
			if((fI=find_font(fontName,e->fonts))) goto L2;
			}
		PyErr_SetString(ErrorObject,"unknown font");
L1:		Py_DECREF(pfontName);
		return NULL;
		}

L2:	Py_DECREF(pfontName);
	width = fI->widths;
	for(i=w=0;i<textLen;i++)
		w += width[text[i]];

	return Py_BuildValue("f",0.001*fontSize*w);
}

#define a85_0		   1L
#define a85_1		   85L
#define a85_2		 7225L
#define a85_3	   614125L
#define a85_4	 52200625L

PyObject *_a85_encode(PyObject *self, PyObject *args)
{
	unsigned char	*inData;
	int				length, blocks, extra, i, k, lim;
	unsigned long	block, res;
	char			*buf;
	PyObject		*retVal;

	if (!PyArg_ParseTuple(args, "z#", &inData, &length)) return NULL;

	blocks = length / 4;
	extra = length % 4;

	buf = (char*)malloc((blocks+1)*5+3);
	lim = 4*blocks;

	for(k=i=0; i<lim; i += 4){
		/*
		 * If you evere have trouble with this consider using masking to ensure
		 * that the shifted quantity is only 8 bits long
		 */
		block = ((unsigned long)inData[i]<<24)|((unsigned long)inData[i+1]<<16)
				|((unsigned long)inData[i+2]<<8)|((unsigned long)inData[i+3]);
		if (block == 0) buf[k++] = 'z';
		else {
			res = block/a85_4;
			buf[k++] = (char)(res+33);
			block -= res*a85_4;

			res = block/a85_3;
			buf[k++] = (char)(res+33);
			block -= res*a85_3;

			res = block/a85_2;
			buf[k++] = (char)(res+33);
			block -= res*a85_2;

			res = block / a85_1;
			buf[k++] = (char)(res+33);

			buf[k++] = (char)(block-res*a85_1+33);
			}
		}

	if(extra>0){
		block = 0L;

		for (i=0; i<extra; i++)
			block += (unsigned long)inData[length-extra+i] << (24-8*i);

		res = block/a85_4;
		buf[k++] = (char)(res+33);
		if(extra>=1){
			block -= res*a85_4;

			res = block/a85_3;
			buf[k++] = (char)(res+33);
			if(extra>=2){
				block -= res*a85_3;

				res = block/a85_2;
				buf[k++] = (char)(res+33);
				if(extra>=3) buf[k++] = (char)((block-res*a85_2)/a85_1+33);
				}
			}
		}

	buf[k++] = '~';
	buf[k++] = '>';
	retVal = PyString_FromStringAndSize(buf, k);
	free(buf);
	return retVal;
}

PyObject *_a85_decode(PyObject *self, PyObject *args)
{
	unsigned char	*inData, *p, *q, *tmp, *buf;
	unsigned int	length, blocks, extra, k, num, c1, c2, c3, c4, c5;
	static unsigned pad[] = {0,0,0xffffff,0xffff,0xff};
	PyObject		*retVal;

	if (!PyArg_ParseTuple(args, "z#", &inData, &length)) return NULL;
	for(k=0,q=inData, p=q+length;q<p && (q=(unsigned char*)strchr((const char*)q,'z'));k++, q++);	/*count 'z'*/
	length += k*4;
	tmp = q = (unsigned char*)malloc(length+1);
	while(inData<p && (k = *inData++)){
		if(isspace(k)) continue;
		if(k=='z'){
			/*turn 'z' into '!!!!!'*/
			memcpy(q,"!!!!!",5);
			q += 5;
			}
		else
			*q++ = k;
		}
	inData = tmp;
	length = q - inData;
	buf = inData+length-2;
	if(buf[0]!='~' || buf[1]!='>'){
		PyErr_SetString(ErrorObject, "Invalid terminator for Ascii Base 85 Stream");
		free(inData);
		return NULL;
		}
	length -= 2;
	buf[0] = 0;

	blocks = length / 5;
	extra = length % 5;

	buf = (unsigned char*)malloc((blocks+1)*4);
	q = inData+blocks*5;
	for(k=0;inData<q;inData+=5){
		c1 = inData[0]-33;
		c2 = inData[1]-33;
		c3 = inData[2]-33;
		c4 = inData[3]-33;
		c5 = inData[4]-33;
		num = (((c1*85+c2)*85+c3)*85+c4)*85+c5;
		buf[k++] = num>>24;
		buf[k++] = num>>16;
		buf[k++] = num>>8;
		buf[k++] = num;
		}
	if(extra>1){
		c1 = inData[0]-33;
		c2 = extra>=2 ? inData[1]-33: 0;
		c3 = extra>=3 ? inData[2]-33: 0;
		c4 = extra>=4 ? inData[3]-33: 0;
		c5 = 0;
		num = (((c1*85+c2)*85+c3)*85+c4)*85+c5 + pad[extra];
		if(extra>1){
			buf[k++] = num>>24;
			if(extra>2){
				buf[k++] = num>>16;
				if(extra>3){
					buf[k++] = num>>8;
					}
				}
			}
		}
	retVal = PyString_FromStringAndSize((const char*)buf, k);
	free(buf);
	free(tmp);
	return retVal;
}

static	char* _fp_fmts[]={"%.0f", "%.1f", "%.2f", "%.3f", "%.4f", "%.5f", "%.6f"};
static	char *_fp_one(PyObject *pD)
{
	double	d, ad;
	static	char s[30];
	int l;
	char*	dot;
	if((pD=PyNumber_Float(pD))){
		d = PyFloat_AS_DOUBLE(pD);
		Py_DECREF(pD);
		}
	else {
		PyErr_SetString(ErrorObject, "bad numeric value");
		return NULL;
		}
	ad = fabs(d);
	if(ad<=1.0e-7){
		s[0]='0';
		s[1]=0;
		}
	else{
		if(ad>1e20){
			PyErr_SetString(ErrorObject, "number too large");
			return NULL;
			}
		if(ad>1) l = min(max(0,6-(int)log10(ad)),6);
		else l = 6;
		sprintf(s,_fp_fmts[l], d);
		if(l){
			l = strlen(s)-1;
			while(l && s[l]=='0') l--;
			if(s[l]=='.' || s[l]==',') s[l]=0;
			else {
				s[l+1]=0;
				if(s[0]=='0' && (s[1]=='.'||s[1]==',')){
					if(s[1]==',') s[1] = '.';
					return s+1;
					}
				}
			if((dot=strchr(s,','))) *dot = '.';
			}
		}
	return s;
}

PyObject *_fp_str(PyObject *self, PyObject *args)
{
	int				aL;
	PyObject		*retVal;
	char			*pD;
	char			*buf, *pB;
	int				i;

	if((aL=PySequence_Length(args))>=0){
		if(aL==1){
			retVal = PySequence_GetItem(args,0);
			if((i=PySequence_Length(retVal))>=0){
				aL = i;
				args = retVal;
				}
			else PyErr_Clear();
			Py_DECREF(retVal);
			}
		buf=malloc(31*aL);
		pB = buf;
		for(i=0;i<aL;i++){
			retVal = PySequence_GetItem(args,i);
			if(retVal){
				pD = _fp_one(retVal);
				Py_DECREF(retVal);
				}
			else pD = NULL;
			if(!pD){
				free(buf);
				return NULL;
				}
			if(pB!=buf){
				*pB++ = ' ';
				}
			strcpy(pB,pD);
			pB = pB + strlen(pB);
			}
		*pB = 0;
		retVal = PyString_FromString(buf);
		free(buf);
		return retVal;
		}
	else {
		PyErr_Clear();
		PyArg_ParseTuple(args, "O:_fp_str", &retVal);
		return NULL;
		}
}

static PyObject *_escapePDF(unsigned char* text, int textlen)
{
	unsigned char*	out = PyMem_Malloc((textlen<<2)+1);
	int				j=0, i=0;
	char			buf[4];
	PyObject*		ret;

	while(i<textlen){
		unsigned char c = text[i++];
		if(c<32 || c>=127){
			sprintf(buf,"%03o",c);
			out[j++] = '\\';
			out[j++] = buf[0];
			out[j++] = buf[1];
			out[j++] = buf[2];
			}
		else {
			if(c=='\\' || c=='(' || c==')') out[j++] = '\\';
			out[j++] = c;
			}
		}
	ret = PyString_FromStringAndSize((const char *)out,j);
	PyMem_Free(out);
	return ret;
}

static PyObject *escapePDF(PyObject *self, PyObject* args)
{
	unsigned char	*text;
	int				textLen;

	if (!PyArg_ParseTuple(args, "s#:escapePDF", &text, &textLen)) return NULL;
	return _escapePDF(text,textLen);
}

static PyObject *_instanceEscapePDF(PyObject *unused, PyObject* args)
{
	PyObject		*self;
	unsigned char	*text;
	int				textLen;

	if (!PyArg_ParseTuple(args, "Os#:_instanceEscapePDF", &self, &text, &textLen)) return NULL;
	return _escapePDF(text,textLen);
}

static PyObject *_sameFrag(PyObject *self, PyObject* args)
{
	PyObject *f, *g;
	static char *names[] = {"fontName", "fontSize", "textColor", "rise", "underline", NULL};
	int	r=0, t;
	char **p;
	if (!PyArg_ParseTuple(args, "OO:_sameFrag", &f, &g)) return NULL;
	if(PyObject_HasAttrString(f,"cbDefn")||PyObject_HasAttrString(g,"cbDefn")) goto L0;
	for(p=names;*p;p++){
		PyObject *fa, *ga;
		fa = PyObject_GetAttrString(f,*p);
		if(!fa){
L1:			return NULL;
			}
		ga = PyObject_GetAttrString(g,*p);
		if(!ga){
			Py_DECREF(fa);
			goto L1;
			}
		t = PyObject_Compare(fa,ga);
		Py_DECREF(fa);
		Py_DECREF(ga);
		if(PyErr_Occurred()) goto L1;
		if(t) goto L0;
		}
	r = 1;
L0:	return PyInt_FromLong((long)r);
}

static PyObject *ttfonts_calcChecksum(PyObject *self, PyObject* args)
{
	unsigned char	*data;
	int				dataLen;
	unsigned long	Sum = 0L;
	unsigned char	*EndPtr;
	unsigned long n;
	int leftover;


	if (!PyArg_ParseTuple(args, "s#:calcChecksum", &data, &dataLen)) return NULL;
	EndPtr = data + (dataLen & ~3);

	/*full ULONGs*/
	while(data < EndPtr){
		n = ((*data++) << 24);
		n += ((*data++) << 16);
		n += ((*data++) << 8);
		n += ((*data++));
		Sum += n;
		}

	/*pad with zeros*/
	leftover = dataLen & 3;
	if(leftover){
		n = ((*data++) << 24);
		if (leftover>1) n += ((*data++) << 16);
		if (leftover>2) n += ((*data++) << 8);
		Sum += n;
		}

	return PyInt_FromLong(Sum);
}

static PyObject *ttfonts_add32(PyObject *self, PyObject* args)
{
	unsigned long x, y;
#if PY_VERSION_HEX>=0x02030000
	PyObject	*ox, *oy;
	if(!PyArg_ParseTuple(args, "OO:add32", &ox, &oy)) return NULL;
	if(PyLong_Check(ox)){
		x = PyLong_AsUnsignedLongMask(ox);
		}
	else{
		x = PyInt_AsLong(ox);
		if(PyErr_Occurred()) return NULL;
		}
	if(PyLong_Check(oy)){
		y = PyLong_AsUnsignedLongMask(oy);
		}
	else{
		y = PyInt_AsLong(oy);
		if(PyErr_Occurred()) return NULL;
		}
#else
	if(!PyArg_ParseTuple(args, "ii:add32", &x, &y)) return NULL;
#endif
	x += y;
	return PyInt_FromLong(x);
}

static PyObject *hex32(PyObject *self, PyObject* args)
{
	unsigned long x;
	char	buf[20];
#if PY_VERSION_HEX>=0x02030000
	PyObject	*ox;
	if(!PyArg_ParseTuple(args, "O:hex32", &ox)) return NULL;
	if(PyLong_Check(ox)){
		x = PyLong_AsUnsignedLongMask(ox);
		}
	else{
		x = PyInt_AsLong(ox);
		if(PyErr_Occurred()) return NULL;
		}
#else
	if(!PyArg_ParseTuple(args, "i:hex32", &x)) return NULL;
#endif
	sprintf(buf,"0X%8.8X",x);
	return PyString_FromString(buf);
}

#if PY_VERSION_HEX>=0x02040000
static PyObject *_notdefFont=NULL;
static PyObject *_notdefChar=NULL;
static PyObject *_k_UCS_2 = NULL;

static PyObject *_GetExcValue(void){
	PyObject *type = NULL, *value = NULL, *tb = NULL;
	PyObject *result = NULL;
	PyThreadState *tstate = PyThreadState_Get();
	PyErr_Fetch(&type, &value, &tb);
	PyErr_NormalizeException(&type, &value, &tb);
	if(PyErr_Occurred()) goto L_BAD;
	if(!value){
		value = Py_None;
		Py_INCREF(value);
		}
	Py_XDECREF(tstate->exc_type);
	Py_XDECREF(tstate->exc_value);
	Py_XDECREF(tstate->exc_traceback);
	tstate->exc_type = type;
	tstate->exc_value = value;
	tstate->exc_traceback = tb;
	result = value;
	Py_XINCREF(result);
	type = 0;
	value = 0;
	tb = 0;
L_BAD:
	Py_XDECREF(type);
	Py_XDECREF(value);
	Py_XDECREF(tb);
	return result;
	}
static PyObject *unicode2T1(PyObject *self, PyObject *args, PyObject *kwds){
	int			i, j, _i1, _i2;
	PyObject	*R, *font, *enc, *e, *res, *utext=NULL, *fonts=NULL,
				*_o1 = NULL, *_o2 = NULL, *_o3 = NULL, *_o4 = NULL;
	static char *argnames[] = {"utext","fonts",NULL};
	if (!PyArg_ParseTupleAndKeywords(args, kwds, "OO", argnames, &utext, &fonts)) return NULL;
	Py_INCREF(utext);
	Py_INCREF(fonts);
	R = Py_None; Py_INCREF(Py_None);
	font = Py_None; Py_INCREF(Py_None);
	enc = Py_None; Py_INCREF(Py_None);
	e = Py_None; Py_INCREF(Py_None);

	if(!_notdefFont){
		_o1 = PyImport_ImportModule("reportlab.pdfbase.pdfmetrics"); if(!_o1) goto L_ERR;
		_o2 = PyObject_GetAttrString(_o1,"_notdefFont");
		_o3 = PyObject_GetAttrString(_o1,"_notdefChar");
		_o4 = PyString_FromString("UCS-2");
		if(!_o2 || !_o3 || !_o3) goto L_ERR;
		_notdefFont = _o2;
		_notdefChar = _o3;
		_k_UCS_2 = _o4;
		Py_DECREF(_o1);
		_o1 = _o2 = _o3 = _o4 = NULL;
		}

	_o2 = PyList_New(0); if(!_o2) goto L_ERR;
	Py_DECREF(R);
	R = _o2;
	_o2 = NULL;

	_o2 = PySequence_GetItem(fonts,0); if(!_o2) goto L_ERR;
	_o1 = PySequence_GetSlice(fonts, 1, 0x7fffffff); if(!_o1) goto L_ERR;
	Py_DECREF(font);
	font = _o2;
	Py_DECREF(fonts);
	fonts = _o1;
	_o1 = _o2 = NULL;

	_o2 = PyObject_GetAttrString(font, "encName"); if(!_o2) goto L_ERR;
	Py_DECREF(enc);
	enc = _o2;
	_o2 = NULL;

	_i1 = PySequence_Contains(enc, _k_UCS_2);
	if(_i1<0) goto L_ERR;
	else if(_i1){
		Py_DECREF(enc);
		enc = PyString_FromString("UTF16");
		}

	while(1){
		_i1 = PyObject_IsTrue(utext); if(_i1<0) goto L_ERR;
		if(!_i1) break;

		_o2 = PyObject_GetAttrString(utext, "encode"); if(!_o2) goto L_ERR;
		_o3 = PyTuple_New(1); if(!_o3) goto L_ERR;
		Py_INCREF(enc);
		PyTuple_SET_ITEM(_o3, 0, enc);
		_o4 = PyObject_CallObject(_o2, _o3); if(!_o4) goto L_FAIL;
		Py_DECREF(_o2); _o2 = 0;
		Py_DECREF(_o3); _o3 = 0;
		_o2 = PyTuple_New(2); if(!_o2) goto L_ERR;
		Py_INCREF(font);
		PyTuple_SET_ITEM(_o2, 0, font);
		PyTuple_SET_ITEM(_o2, 1, _o4);
		_o4 = NULL;
		if(PyList_Append(R, _o2)) goto L_ERR;
		Py_DECREF(_o2); _o2 = NULL;
		break;
L_FAIL:
		Py_XDECREF(_o2);
		Py_XDECREF(_o3);
		Py_XDECREF(_o4); _o2 = _o3 = _o4 = NULL;

		if(!PyErr_ExceptionMatches(PyExc_UnicodeEncodeError)) goto L_ERR;
		_o1 = _GetExcValue(); if(!_o1) goto L_ERR;
		Py_DECREF(e);
		e = _o1;
		_o1 = NULL;

		_o3 = PyObject_GetAttrString(e, "args"); if(!_o3) goto L_ERR;
		_o4 = PySequence_GetSlice(_o3, 2, 4); if(!_o4) goto L_ERR;
		Py_DECREF(_o3); _o3 = 0;
		_o2 = PySequence_GetItem(_o4, 0); if(!_o2) goto L_ERR;
		i = PyInt_AsLong(_o2); if(PyErr_Occurred()) goto L_ERR;
		Py_DECREF(_o2); _o2 = 0;
		_o1 = PySequence_GetItem(_o4, 1); if(!_o1) goto L_ERR;
		j = PyInt_AsLong(_o1); if(PyErr_Occurred()) goto L_ERR;
		Py_DECREF(_o1);
		Py_DECREF(_o4); _o1 = _o4 = 0;

		if(i){
			_o2 = PySequence_GetSlice(utext, 0, i); if(!_o2) goto L_ERR;
			_o1 = PyObject_GetAttrString(_o2, "encode"); if(!_o1) goto L_ERR;
			Py_DECREF(_o2); _o2 = NULL;
			_o4 = PyTuple_New(1); if(!_o4) goto L_ERR;
			Py_INCREF(enc);
			PyTuple_SET_ITEM(_o4, 0, enc);
			_o2 = PyObject_CallObject(_o1, _o4); if(!_o2) goto L_ERR;
			Py_DECREF(_o1);
			Py_DECREF(_o4); _o1 = _o4 = NULL;
			_o1 = PyTuple_New(2); if(!_o1) goto L_ERR;
			Py_INCREF(font);
			PyTuple_SET_ITEM(_o1, 0, font);
			PyTuple_SET_ITEM(_o1, 1, _o2);
			_o2 = NULL;
			if(PyList_Append(R, _o1)) goto L_ERR;
			Py_DECREF(_o1); _o1 = NULL;
			}

		_i2 = PyObject_IsTrue(fonts); if(_i2<0) goto L_ERR;
		if(_i2){
			_o4 = PySequence_GetSlice(utext, i, j); if(!_o4) goto L_ERR;
			_o2 = PyTuple_New(2); if(!_o2) goto L_ERR;
			PyTuple_SET_ITEM(_o2, 0, _o4);
			Py_INCREF(fonts);
			PyTuple_SET_ITEM(_o2, 1, fonts);
			_o4 = NULL;
			_o4 = unicode2T1(self,_o2,NULL); if(!_o4) goto L_ERR;
			Py_DECREF(_o2); _o2 = 0;
			_o3 = PyTuple_New(1); if(!_o3) goto L_ERR;
			PyTuple_SET_ITEM(_o3, 0, _o4);
			_o4 = NULL;
			_o1 = PyObject_GetAttrString(R, "extend"); if(!_o1) goto L_ERR;
			_o2 = PyObject_CallObject(_o1, _o3); if(!_o2) goto L_ERR;
			Py_DECREF(_o1);
			Py_DECREF(_o3);
			Py_DECREF(_o2); _o1 = _o2 = _o3 = NULL;
			}
		else{
			_o2 = PyInt_FromLong((j - i)); if(!_o2) goto L_ERR;
			_o4 = PyNumber_Multiply(_notdefChar, _o2); if(!_o4) goto L_ERR;
			Py_DECREF(_o2); _o2 = NULL;
			_o3 = PyTuple_New(2); if(!_o3) goto L_ERR;
			PyTuple_SET_ITEM(_o3, 0, _notdefFont);
			PyTuple_SET_ITEM(_o3, 1, _o4);
			Py_INCREF(_notdefFont);
			_o4 = NULL;
			if(PyList_Append(R, _o3)) goto L_ERR;
			Py_DECREF(_o3); _o3 = NULL;
			}

		_o4 = PySequence_GetSlice(utext, j, 0x7fffffff); if(!_o4) goto L_ERR;
		Py_DECREF(utext);
		utext = _o4;
		_o4 = NULL;
		}

	Py_INCREF(R);
	res = R;
	goto L_OK;

L_ERR:
	Py_XDECREF(_o1);
	Py_XDECREF(_o2);
	Py_XDECREF(_o3);
	Py_XDECREF(_o4);
	res = 0;
L_OK:
	Py_DECREF(R);
	Py_DECREF(font);
	Py_DECREF(enc);
	Py_DECREF(e);
	Py_DECREF(utext);
	Py_DECREF(fonts);
	return res;
	}
#endif

#if PY_VERSION_HEX>=0x02030000
#define HAVE_BOX
/*Box start**************/
typedef struct {
	PyObject_HEAD
	unsigned	is_box:1;
	unsigned	is_glue:1;
	unsigned	is_penalty:1;
	unsigned	is_none:1;
	double		width,stretch,shrink,penalty;
	int			flagged;
	char		character;
	} BoxObject;

static void BoxFree(BoxObject* self)
{
	PyMem_DEL(self);
}

static int Box_set_int(char* name, int* pd, PyObject *value)
{
	PyObject *v = PyNumber_Int(value);
	if(!v) return -1;
	*pd = PyInt_AsLong(v);
	Py_DECREF(v);
	return 0;
}

static int Box_set_double(char* name, double* pd, PyObject *value)
{
	PyObject *v = PyNumber_Float(value);
	if(!v) return -1;
	*pd = PyFloat_AsDouble(v);
	Py_DECREF(v);
	return 0;
}

static int Box_set_character(BoxObject *self, PyObject *value)
{
	if(value==Py_None){
		self->is_none = 1;
		}
	else {
		char *v = PyString_AsString(value);
		if(!v) return -1;
		if(PyString_GET_SIZE(value)!=1){
			PyErr_Format(PyExc_AttributeError,"Bad size %d('%s') for attribute character",PyString_GET_SIZE(value),v);
			return -1;
			}
		self->character = v[0];
		self->is_none = 0;
		}

	return 0;
}

static int Box_setattr(BoxObject *self, char *name, PyObject* value)
{
	if(!strcmp(name,"width")) return Box_set_double(name,&self->width,value);
	else if(!strcmp(name,"character")) return Box_set_character(self,value);
	else if(!strcmp(name,"stretch")) return Box_set_double(name,&self->stretch,value);
	else if(!strcmp(name,"shrink")) return Box_set_double(name,&self->shrink,value);
	else if(!strcmp(name,"penalty")) return Box_set_double(name,&self->penalty,value);
	else if(!strcmp(name,"flagged")) return Box_set_int(name,&self->flagged,value);
	else if(
			!strcmp(name,"is_penalty") ||
			!strcmp(name,"is_box") ||
			!strcmp(name,"is_glue")
			) PyErr_Format(PyExc_AttributeError, "readonly attribute %s", name);
	else PyErr_Format(PyExc_AttributeError, "no attribute %s", name);
	return -1;
}

static double _Glue_compute_width(BoxObject *self, double r)
{
	if(self->is_glue) return self->width+r*(r<0?self->shrink:self->stretch);
	return self->width;
}

static PyObject* Glue_compute_width(BoxObject *self, PyObject *args)
{
	double r;
	if(!PyArg_ParseTuple(args, "d:compute_width", &r)) return NULL;
	return PyFloat_FromDouble(_Glue_compute_width(self,r));
}

static struct PyMethodDef Box_methods[] = {
	{"compute_width", (PyCFunction)Glue_compute_width, METH_VARARGS|METH_KEYWORDS, "compute_width(r)"},
	{NULL, NULL}		/* sentinel */
	};

static PyObject* Box_get_character(unsigned is_none, char c)
{
	if(!is_none) return PyString_FromStringAndSize(&c,1);
	else {
		Py_INCREF(Py_None);
		return Py_None;
		}
}

static PyObject* Box_getattr(BoxObject *self, char *name)
{
	if(!strcmp(name,"width")) return PyFloat_FromDouble(self->width);
	else if(!strcmp(name,"character")) return Box_get_character(self->is_none,self->character);
	else if(!strcmp(name,"is_box")) return PyInt_FromLong(self->is_box);
	else if(!strcmp(name,"is_glue")) return PyInt_FromLong(self->is_glue);
	else if(!strcmp(name,"is_penalty")) return PyInt_FromLong(self->is_penalty);
	else if(!strcmp(name,"stretch")) return PyFloat_FromDouble(self->stretch);
	else if(!strcmp(name,"shrink")) return PyFloat_FromDouble(self->shrink);
	else if(!strcmp(name,"penalty")) return PyFloat_FromDouble(self->penalty);
	else if(!strcmp(name,"flagged")) return PyInt_FromLong(self->flagged);
	return Py_FindMethod(Box_methods, (PyObject *)self, name);
}

static PyTypeObject BoxType = {
	PyObject_HEAD_INIT(0)
	0,								/*ob_size*/
	"Box",							/*tp_name*/
	sizeof(BoxObject),				/*tp_basicsize*/
	0,								/*tp_itemsize*/
	/* methods */
	(destructor)BoxFree,			/*tp_dealloc*/
	(printfunc)0,					/*tp_print*/
	(getattrfunc)Box_getattr,		/*tp_getattr*/
	(setattrfunc)Box_setattr,		/*tp_setattr*/
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
	"Box instance, see doc string for details."
};

static BoxObject* Box(PyObject* module, PyObject* args, PyObject* kw)
{
	BoxObject* self;
	char	*kwlist[] = {"width","character",NULL};
	PyObject	*pC=NULL;
	double		w;

	if(!PyArg_ParseTupleAndKeywords(args,kw,"d|O:Box",kwlist,&w,&pC)) return NULL;
	if(!(self = PyObject_NEW(BoxObject, &BoxType))) return NULL;
	self->shrink = self->stretch = self->penalty = (double)(self->is_glue = self->is_penalty = self->flagged = 0);
	self->is_box = 1;
	self->width = w;
	if(Box_set_character(self, pC ? pC : Py_None)){
		BoxFree(self);
		return NULL;
		}

	return self;
}

static BoxObject* Glue(PyObject* module, PyObject* args, PyObject* kw)
{
	BoxObject* self;
	char	*kwlist[] = {"width","stretch","shrink",NULL};
	double		width,stretch,shrink;

	if(!PyArg_ParseTupleAndKeywords(args,kw,"ddd:Glue",kwlist,&width,&stretch,&shrink)) return NULL;
	if(!(self = PyObject_NEW(BoxObject, &BoxType))) return NULL;
	self->penalty = (double)(self->is_box = self->is_penalty = self->flagged = 0);
	self->is_glue = self->is_none = 1;
	self->width = width;
	self->stretch = stretch;
	self->shrink = shrink;

	return self;
}

static BoxObject* Penalty(PyObject* module, PyObject* args, PyObject* kw)
{
	BoxObject* self;
	char	*kwlist[] = {"width","penalty","flagged",NULL};
	double	width,penalty;
	int		flagged = 0;

	if(!PyArg_ParseTupleAndKeywords(args,kw,"dd|i:Penalty",kwlist,&width,&penalty,&flagged)) return NULL;
	if(!(self = PyObject_NEW(BoxObject, &BoxType))) return NULL;
	self->shrink = self->stretch = (double)(self->is_box = self->is_glue = 0);
	self->is_penalty = self->is_none = 1;
	self->width = width;
	self->penalty = penalty;
	self->flagged = flagged;
	return self;
}
/*Box end****************/
/* BoxList -- a list subtype */
typedef struct {
	PyListObject list;
	int state;
	} BoxListobject;

static PyObject *BoxList_getstate(BoxListobject *self, PyObject *args)
{
	if (!PyArg_ParseTuple(args, ":getstate")) return NULL;
	return PyInt_FromLong(self->state);
}

static PyObject *BoxList_setstate(BoxListobject *self, PyObject *args)
{
	int state;

	if (!PyArg_ParseTuple(args, "i:setstate", &state))
		return NULL;
	self->state = state;
	Py_INCREF(Py_None);
	return Py_None;
}

static PyObject *BoxList_specialmeth(PyObject *self, PyObject *args, PyObject *kw)
{
	PyObject *result = PyTuple_New(3);
	if(result!=NULL){
		if(self==NULL) self = Py_None;
		if(kw==NULL) kw = Py_None;
		Py_INCREF(self);
		PyTuple_SET_ITEM(result, 0, self);
		Py_INCREF(args);
		PyTuple_SET_ITEM(result, 1, args);
		Py_INCREF(kw);
		PyTuple_SET_ITEM(result, 2, kw);
		}
	return result;
}

static PyMethodDef BoxList_methods[] = {
	{"getstate", (PyCFunction)BoxList_getstate, METH_VARARGS, "getstate() -> state"},
	{"setstate", (PyCFunction)BoxList_setstate, METH_VARARGS, "setstate(state)"},
	/* These entries differ only in the flags; they are used by the tests in test.test_descr. */
	{"classmeth", (PyCFunction)BoxList_specialmeth, METH_VARARGS | METH_KEYWORDS | METH_CLASS, "classmeth(*args, **kw)"},
	{"staticmeth", (PyCFunction)BoxList_specialmeth, METH_VARARGS | METH_KEYWORDS | METH_STATIC, "staticmeth(*args, **kw)"},
	{NULL,	NULL},
	};

static PyTypeObject BoxList_type;

static int BoxList_init(BoxListobject *self, PyObject *args, PyObject *kwds)
{
	if(PyList_Type.tp_init((PyObject *)self, args, kwds)<0) return -1;
	self->state = 0;
	return 0;
}

static PyObject *BoxList_state_get(BoxListobject *self)
{
	return PyInt_FromLong(self->state);
}

static PyGetSetDef BoxList_getsets[] = {
	{"state", (getter)BoxList_state_get, NULL, PyDoc_STR("an int variable for demonstration purposes")},
	{0}
	};

static PyTypeObject BoxList_type = {
	PyObject_HEAD_INIT(DEFERRED_ADDRESS(&PyType_Type))
	0,
	"_rl_accel.BoxList",
	sizeof(BoxListobject),
	0,
	0,					/* tp_dealloc */
	0,					/* tp_print */
	0,					/* tp_getattr */
	0,					/* tp_setattr */
	0,					/* tp_compare */
	0,					/* tp_repr */
	0,					/* tp_as_number */
	0,					/* tp_as_sequence */
	0,					/* tp_as_mapping */
	0,					/* tp_hash */
	0,					/* tp_call */
	0,					/* tp_str */
	0,					/* tp_getattro */
	0,					/* tp_setattro */
	0,					/* tp_as_buffer */
	Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE, /* tp_flags */
	0,					/* tp_doc */
	0,					/* tp_traverse */
	0,					/* tp_clear */
	0,					/* tp_richcompare */
	0,					/* tp_weaklistoffset */
	0,					/* tp_iter */
	0,					/* tp_iternext */
	BoxList_methods,			/* tp_methods */
	0,					/* tp_members */
	BoxList_getsets,			/* tp_getset */
	DEFERRED_ADDRESS(&PyList_Type),		/* tp_base */
	0,					/* tp_dict */
	0,					/* tp_descr_get */
	0,					/* tp_descr_set */
	0,					/* tp_dictoffset */
	(initproc)BoxList_init,		/* tp_init */
	0,					/* tp_alloc */
	0,					/* tp_new */
};
#endif

static char *__doc__=
"_rl_accel contains various accelerated utilities\n\
\tstringWidth a fast string width function\n\
\t_instanceStringWidth a method version of stringWidth\n\
\tdefaultEncoding gets/sets the default encoding for stringWidth\n\
\tgetFonts gets font names from the internal table\n\
\tgetFontInfo gets font info from the internal table\n\
\tsetFontInfo adds a font to the internal table\n\
\t_SWRecover gets/sets a callback for stringWidth recovery\n\
\tescapePDF makes a string safe for PDF\n\
\t_instanceEscapePDF method equivalent of escapePDF\n\
\n\
\t_AsciiBase85Encode does what is says\n\
\t_AsciiBase85Decode does what is says\n\
\n\
\tfp_str converts numeric arguments to a single blank separated string\n"
"\tcalcChecksum calculate checksums for TTFs\n"
"\tadd32 32 bit unsigned addition\n"
"\thex32 32 bit unsigned to 0X8.8X string\n"
#ifdef	HAVE_BOX
"\tBox(width,character=None) creates a Knuth character Box with the specified width.\n"
"\tGlue(width,stretch,shrink) creates a Knuth glue Box with the specified width, stretch and shrink.\n"
"\tPenalty(width,penalty,flagged=0) creates a Knuth penalty Box with the specified width and penalty.\n"
"\tBoxList() creates a knuth box list.\n"
#endif
;

static struct PyMethodDef _methods[] = {
	{"defaultEncoding", _pdfmetrics_defaultEncoding, 1, "defaultEncoding([encoding])\ngets/sets the default encoding."},
	{"getFonts", _pdfmetrics_getFonts, 1, "getFonts()\nreturns font names."},
	{"getFontInfo", _pdfmetrics_getFontInfo, 1, "getFontInfo(fontName,encoding)\nreturns info ([widths],ascent,descent)."},
	{"setFontInfo", _pdfmetrics_setFontInfo, 1, "setFontInfo(fontName,encoding,ascent, descent, widths)\nadds the font to the table for encoding"},
	{"stringWidth", _pdfmetrics_stringWidth, 1, "stringWidth(text,fontName,fontSize,[encoding]) returns width of text in points"},
	{"_instanceStringWidth", _pdfmetrics_instanceStringWidth, 1, "_instanceStringWidth(text,fontSize) like stringWidth, but gets fontName from self"},
	{"_SWRecover", _pdfmetrics__SWRecover, 1,
					"_SWRecover([callable])\n"
					"get/set the string width recovery\n"
					"callback callable(text,font,size,encoding)\n"
					"return None to retry or the correct result."},
	{"_AsciiBase85Encode", _a85_encode, METH_VARARGS, "_AsciiBase85Encode(\".....\") return encoded string"},
	{"_AsciiBase85Decode", _a85_decode, METH_VARARGS, "_AsciiBase85Decode(\".....\") return decoded string"},
	{"escapePDF", escapePDF, METH_VARARGS, "escapePDF(s) return PDF safed string"},
	{"_instanceEscapePDF", _instanceEscapePDF, METH_VARARGS, "_instanceEscapePDF(s) return PDF safed string"},
	{"fp_str", _fp_str, METH_VARARGS, "fp_str(a0, a1,...) convert numerics to blank separated string"},
	{"_sameFrag", _sameFrag, 1, "_sameFrag(f,g) return 1 if fragments have same style"},
	{"calcChecksum", ttfonts_calcChecksum, METH_VARARGS, "calcChecksum(string) calculate checksums for TTFs"},
	{"add32", ttfonts_add32, METH_VARARGS, "add32(x,y)  32 bit unsigned x+y"},
	{"hex32", hex32, METH_VARARGS, "hex32(x)  32 bit unsigned-->0X8.8X string"},
#if PY_VERSION_HEX>=0x02040000
	{"unicode2T1", (PyCFunction)unicode2T1, METH_VARARGS|METH_KEYWORDS, "return a list of (font,string) pairs representing the unicode text"},
#endif
#ifdef	HAVE_BOX
	{"Box",	(PyCFunction)Box,	METH_VARARGS|METH_KEYWORDS, "Box(width,character=None) create a Knuth Box instance"},
	{"Glue", (PyCFunction)Glue,	METH_VARARGS|METH_KEYWORDS, "Glue(width,stretch,shrink) create a Knuth Glue instance"},
	{"Penalty", (PyCFunction)Penalty,	METH_VARARGS|METH_KEYWORDS, "Penalty(width,penalty,flagged=0) create a Knuth Penalty instance"},
#endif
	{NULL,		NULL}		/* sentinel */
	};

/*Initialization function for the module (*must* be called init_pdfmetrics)*/
void init_rl_accel(void)
{
	PyObject *m;
#if PY_VERSION_HEX<0x02000000
	PyObject *d;
#endif

	/*Create the module and add the functions and module doc string*/
	m = Py_InitModule3("_rl_accel", _methods,__doc__);

	/*Add some symbolic constants to the module */
	if(!ErrorObject){
		ErrorObject = PyErr_NewException("_rl_accel.error", NULL, NULL);
		if(!ErrorObject) goto err;
		}
	Py_INCREF(ErrorObject);
	moduleVersion = PyString_FromString(VERSION);
#if PY_VERSION_HEX>=0x02000000
	PyModule_AddObject(m, "error", ErrorObject);
	PyModule_AddObject(m, "version", moduleVersion );
#else
	d = PyModule_GetDict(m);
	PyDict_SetItemString(d, "error", ErrorObject );
	PyDict_SetItemString(d, "version", moduleVersion );
#endif

#ifdef	HAVE_BOX
	BoxType.ob_type = &PyType_Type;
	BoxList_type.tp_base = &PyList_Type;
	if(PyType_Ready(&BoxList_type)<0) goto err;
	Py_INCREF(&BoxList_type);
	if(PyModule_AddObject(m, "BoxList", (PyObject *)&BoxList_type)<0)goto err;
#endif

err:/*Check for errors*/
	if (PyErr_Occurred()) Py_FatalError("can't initialize module _rl_accel");
}
