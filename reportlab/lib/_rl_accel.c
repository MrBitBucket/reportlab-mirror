/****************************************************************************
#copyright ReportLab Inc. 2000
#see license.txt for license details
#history http://cvs.sourceforge.net/cgi-bin/cvsweb.cgi/reportlab/lib/_rl_accel.c?cvsroot=reportlab
#$Header: /tmp/reportlab/reportlab/lib/_rl_accel.c,v 1.28 2002/10/19 18:06:07 rgbecker Exp $
 ****************************************************************************/
#if 0
static __version__=" $Id: _rl_accel.c,v 1.28 2002/10/19 18:06:07 rgbecker Exp $ "
#endif
#include <Python.h>
#include <stdlib.h>
#include <math.h>
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
#define VERSION "0.38"
#define MODULE "_rl_accel"
#ifndef	ATTRDICT
	#if PY_MAJOR_VERSION>=2
	#	define ATTRDICT 1
	#endif
#endif
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
			PyObject *arglist = Py_BuildValue("(s#sd)",text,textLen,fontName,fontSize);
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

static	char* _fp_fmts[]={"%.0f", "%.1f", "%.2f", "%.3f", "%.4f", "%.5f", "%.6f"};
static	char *_fp_one(PyObject *pD)
{
	double	d;
	static	char s[30];
	int l;
	char*	dot;
	if((pD=PyNumber_Float(pD))) d = PyFloat_AS_DOUBLE(pD);
	else {
		PyErr_SetString(ErrorObject, "bad numeric value");
		return NULL;
		}
	if(fabs(d)<=1.0e-7){
		s[0]='0';
		s[1]=0;
		}
	else{
		if(fabs(d)>1) l = min(max(0,6-(int)log10(fabs(d))),6);
		else l = 6;
		sprintf(s,_fp_fmts[l], d);
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
			}
		buf=malloc(31*aL);
		pB = buf;
		for(i=0;i<aL;i++){
			if(!(pD = _fp_one(PySequence_GetItem(args,i)))){
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

#ifdef	ATTRDICT
static PyTypeObject _AttrDictType = {
	PyObject_HEAD_INIT(0)
	0,								/*ob_size*/
	0,								/*tp_name*/
	0,								/*tp_basicsize*/
	0,								/*tp_itemsize*/
	/* methods */
	0,								/*tp_dealloc*/
	0,								/*tp_print*/
	0,								/*tp_getattr*/
	0,								/*tp_setattr*/
	0,								/*tp_compare*/
	0,								/*tp_repr*/
	0,								/*tp_as_number*/
	0,								/*tp_as_sequence*/
	0,								/*tp_as_mapping*/
	0,								/*tp_hash*/
	0,								/*tp_call*/
	0,								/*tp_str*/

	/* Space for future expansion */
	0L,0L,0L,0L,
	/* Documentation string */
	NULL
};
static char* _AttrDict_tp_doc=
	"_AttrDict instance\n\
\n\
";

static PyObject * _AttrDict_copy(register PyObject *self, PyObject *args)
{
	PyObject *r;
	if (!PyArg_NoArgs(args)) return NULL;
	self->ob_type=&PyDict_Type;
	r = PyDict_Copy((PyObject*)self);
	self->ob_type=&_AttrDictType;
	if(r) r->ob_type=&_AttrDictType;
	return r;
}
static PyObject * _AttrDict_clear(register PyObject *self, PyObject *args)
{
	if (!PyArg_NoArgs(args)) return NULL;
	self->ob_type=&PyDict_Type;
	PyDict_Clear(self);
	self->ob_type=&_AttrDictType;
	Py_INCREF(Py_None);
	return Py_None;
}

static PyMethodDef mapp_methods[] = {
	{"clear",	(PyCFunction)_AttrDict_clear, METH_OLDARGS, "D.clear() -> None.  Remove all items from D."},
	{"copy",	(PyCFunction)_AttrDict_copy, METH_OLDARGS, "D.copy() -> a shallow copy of D"},
	{NULL,		NULL}		/* sentinel */
	};
static PyMethodChain _AttrDict_MethodChain[2];

static	PyObject *_AttrDict_getattr(PyObject* self, char* name)
{
	PyObject* r;
	self->ob_type=&PyDict_Type;
	r = PyDict_GetItemString(self,name);
	if(!r) r = Py_FindMethodInChain(&_AttrDict_MethodChain[0],self,name);
	self->ob_type=&_AttrDictType;
	return r;
}

static int _AttrDict_setattr(PyObject* self, char *name, PyObject* value)
{
	int	r;
	self->ob_type=&PyDict_Type;
	if(value){
		r = PyDict_SetItemString(self,name,value);
		}
	else {
		r = PyDict_DelItemString(self,name);
		}
	self->ob_type=&_AttrDictType;
	return r;
}

static PyObject *_AttrDict(PyObject *self, PyObject *args)
{
	PyObject *r;
	if (!PyArg_ParseTuple(args,":_attrDict")) return NULL;

	r = PyDict_New();
	if(!r) return NULL;
	r->ob_type = &_AttrDictType;
	return r;
}

static binaryfunc dict_subscript;
static objobjargproc dict_ass_sub;
static PyObject * _AttrDict_subscript(PyObject *self, register PyObject *key)
{
	PyObject* r;
	self->ob_type=&PyDict_Type;
	r = dict_subscript(self,key);
	self->ob_type=&_AttrDictType;
	return r;
}

static int _AttrDict_ass_sub(PyObject *self, PyObject *v, PyObject *w)
{
	int r;
	self->ob_type=&PyDict_Type;
	r = dict_ass_sub(self,v,w);
	self->ob_type=&_AttrDictType;
	return r;
}

static PyMappingMethods _AttrDict_as_mapping = {
	(inquiry)0, /*mp_length*/
	(binaryfunc)_AttrDict_subscript, /*mp_subscript*/
	(objobjargproc)_AttrDict_ass_sub, /*mp_ass_subscript*/
};
#endif

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
	static char *names[] = {"fontName", "fontSize", "textColor", "rise", NULL};
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


static char *__doc__=
"_rl_accel contains various accelerated utilities\n\
	stringWidth a fast string width function\n\
	_instanceStringWidth a method version of stringWidth\n\
	defaultEncoding gets/sets the default encoding for stringWidth\n\
	getFontInfo gets font info from the internal table\n\
	setFontInfo adds a font to the internal table\n\
	_SWRecover gets/sets a callback for stringWidth recovery\n\
	escapePDF makes a string safe for PDF\n\
	_instanceEscapePDF method equivalent of escapePDF\n\
	\n\
	_AsciiBase85Encode does what is says\n\
	\n\
	fp_str converts numeric arguments to a single blank separated string\n"

#ifdef	ATTRDICT
"	_AttrDict creates a dict object which can do setattr/getattr type things\n"
#endif
	"calcChecksum calculate checksums for TTFs\n"
;

static struct PyMethodDef _methods[] = {
	{"defaultEncoding", _pdfmetrics_defaultEncoding, 1, "defaultEncoding([encoding])\ngets/sets the default encoding."},
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
	{"escapePDF", escapePDF, METH_VARARGS, "escapePDF(s) return PDF safed string"},
	{"_instanceEscapePDF", _instanceEscapePDF, METH_VARARGS, "_instanceEscapePDF(s) return PDF safed string"},
	{"fp_str", _fp_str, METH_VARARGS, "fp_str(a0, a1,...) convert numerics to blank separated string"},
	{"_sameFrag", _sameFrag, 1, "_sameFrag(f,g) return 1 if fragments have same style"},
#ifdef	ATTRDICT
	{"_AttrDict", _AttrDict, METH_VARARGS, "_AttrDict() create a dict which can use attribute notation"},
#endif
	{"calcChecksum", ttfonts_calcChecksum, METH_VARARGS, "calcChecksum(string) calculate checksums for TTFs"},
	{NULL,		NULL}		/* sentinel */
	};

/*Initialization function for the module (*must* be called init_pdfmetrics)*/
void init_rl_accel(void)
{
	PyObject *m, *d, *v;

	/*Create the module and add the functions */
	m = Py_InitModule("_rl_accel", _methods);

	/*Add some symbolic constants to the module */
	d = PyModule_GetDict(m);

#ifdef	ATTRDICT
	/*set up our modified dictionary type*/
	_AttrDictType = PyDict_Type;
	_AttrDictType.tp_doc = _AttrDict_tp_doc;
	_AttrDictType.tp_name = "_AttrDict";
	_AttrDictType.tp_getattr = _AttrDict_getattr;
	_AttrDictType.tp_setattr = _AttrDict_setattr;
	_AttrDict_as_mapping.mp_length = _AttrDictType.tp_as_mapping->mp_length;
	dict_subscript = _AttrDictType.tp_as_mapping->mp_subscript;
	dict_ass_sub = _AttrDictType.tp_as_mapping->mp_ass_subscript;
	_AttrDictType.tp_as_mapping = &_AttrDict_as_mapping;
	v = PyObject_GetAttrString(d,"has_key");
	_AttrDict_MethodChain[0].methods = mapp_methods;
	_AttrDict_MethodChain[0].link = &_AttrDict_MethodChain[1];
	_AttrDict_MethodChain[1].methods = (PyMethodDef*)(((PyCFunctionObject*)v)->m_ml);
	_AttrDict_MethodChain[1].link = NULL;
	Py_DECREF(v);
#endif
	ErrorObject = PyString_FromString("_rl_accel.error");
	PyDict_SetItemString(d, "error", ErrorObject);
	moduleVersion = PyString_FromString(VERSION);
	PyDict_SetItemString(d, "version", moduleVersion );

	/*add in the docstring */
	PyDict_SetItemString(d, "__doc__", Py_BuildValue("s", __doc__));

	/* Check for errors */
	if (PyErr_Occurred()) Py_FatalError("can't initialize module _rl_accel");
}
