/****************************************************************************
#copyright ReportLab Inc. 2000
#see license.txt for license details
#history http://cvs.sourceforge.net/cgi-bin/cvsweb.cgi/reportlab/lib/_rl_accel.c?cvsroot=reportlab
#$Header: /tmp/reportlab/reportlab/lib/_rl_accel.c,v 1.4 2000/10/25 08:57:45 rgbecker Exp $
 ****************************************************************************/
static __version__=" $Id: _rl_accel.c,v 1.4 2000/10/25 08:57:45 rgbecker Exp $ "
#include <Python.h>
#include <stdlib.h>
#include <math.h>
#if defined(__GNUC__) || defined(sun)
#	define STRICMP strcasecmp
#elif defined(_MSC_VER)
#	define STRICMP stricmp
#else
#	error "Don't know how to define STRICMP"
#endif
#ifndef max
#	define max(a,b) ((a)>(b)?(a):(b))
#endif
#ifndef min
#	define min(a,b) ((a)<(b)?(a):(b))
#endif
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
			Py_INCREF(temp);         			/* Add a reference to new callback */
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
			PyErr_SetString(ErrorObject,"Unknown encoding");
			return NULL;
			}
		else defaultEncoding = e;
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

static PyObject *_pdfmetrics_stringWidth(PyObject *self, PyObject* args)
{
	char		*text, *fontName, *encoding=NULL;
	PyObject	*pS;
	double		fontSize;
	fI_t		*fI;
	eI_t		*e;
	int			w, *width, i, textLen;
	static int	recover=1;

	if (!PyArg_ParseTuple(args, "s#sO|s", &text, &textLen, &fontName, &pS, &encoding)) return NULL;
	if((pS=PyNumber_Float(pS))) fontSize = PyFloat_AS_DOUBLE(pS);
	else{
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
			if(result==Py_None){
				Py_DECREF(result);
				if(!(fI=find_font(fontName,e->fonts))) goto L_ufe;
				}
			else return result;
			}
L_ufe:	PyErr_SetString(ErrorObject,"unknown font");
		return NULL;
		}

	width = fI->widths;
	for(i=w=0;i<textLen;i++)
		w += width[(unsigned)text[i]];

	return Py_BuildValue("f",0.001*fontSize*w);
}

static const unsigned long _a85_nums[5] = {1L, 85L, 7225L, 614125L, 52200625L};

PyObject *_a85_encode(PyObject *self, PyObject *args)
{
	unsigned char	*inData;
	int				length, blocks, extra, i, j, k, lim;
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
		else
			for (j=4; j>=0; j--) {
				res = block / _a85_nums[j];
				buf[k++] = (char)(res+33);
				block -= res * _a85_nums[j];
				}
		}
	
	block = 0L;

	for (i=0; i<extra; i++)
		block += (unsigned long)inData[length-extra+i] << (24-8*i);

	for (j=4; j>=4-extra; j--){
		res = block / _a85_nums[j];
		buf[k++] = (char)(res+33);
		block -= res * _a85_nums[j];
		}

	buf[k++] = '~';
	buf[k++] = '>';
	retVal = PyString_FromStringAndSize(buf, k);
	free(buf);
	return retVal;
}

static	char* _fp_fmts[]={"%.0f", "%.1f", "%.2f", "%.3f", "%.4f", "%.5f", "%.6f", "%.8f", "%.9f"};
static	char *_fp_one(PyObject *pD)
{
	double d;
	static	char s[30];
	int l;
	if((pD=PyNumber_Float(pD))) d = PyFloat_AS_DOUBLE(pD);
	else {
		PyErr_SetString(ErrorObject, "bad numeric value");
		return NULL;
		}
	l = min(max(0,6-(int)log10(fabs(d))),6);
	sprintf(s,_fp_fmts[l], d);
	l = strlen(s)-1;
	while(l && s[l]=='0') l--;
	if(s[l]=='.') s[l]=0;
	else {
		s[l+1]=0;
		if(s[0]=='0' && s[1]=='.') return s+1;
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

static char *__doc__=
"_rl_accel contains various accelerated utilities\n\
    a fast string width function\n\
    defaultEncoding gets/sets the default encoding for stringWidth\n\
    setFontInfo adds a font to the internal table\n\
    _SWRecover gets/sets a callback for stringWidth recovery\n\
	\n\
	_AsciiBase85Encode does what is says\n\
	\n\
	fp_str converts numeric arguments to a single blank separated string\n\
";

static struct PyMethodDef _methods[] = {
	{"defaultEncoding", _pdfmetrics_defaultEncoding, 1, "defaultEncoding([encoding])\ngets/sets the default encoding."},
	{"setFontInfo", _pdfmetrics_setFontInfo, 1, "setFontInfo(fontName,encoding,ascent, descent, widths)\nadds the font to the table for encoding"},
	{"stringWidth", _pdfmetrics_stringWidth, 1, "stringwidth(text,fontName,fontSize,[encoding]) returns width of text in points"},
	{"_SWRecover", _pdfmetrics__SWRecover, 1,
					"_SWRecover([callable])\n"
					"get/set the string width recovery\n"
					"callback callable(text,font,size,encoding)\n"
					"return None to retry or the correct result."},
	{"_AsciiBase85Encode", _a85_encode, METH_VARARGS, "_AsciiBase85Encode(\".....\") return encoded string"},
	{"fp_str", _fp_str, METH_VARARGS, "fp_str(a0, a1,...) convert numerics to blank separated string"},
	{NULL,		NULL}		/* sentinel */
	};

/*Initialization function for the module (*must* be called init_pdfmetrics)*/
void init_rl_accel()
{
	PyObject *m, *d;
	int i=0;

	/*Create the module and add the functions */
	m = Py_InitModule("_rl_accel", _methods);

	/*Add some symbolic constants to the module */
	d = PyModule_GetDict(m);
	ErrorObject = PyString_FromString("_rl_accel.error");
	PyDict_SetItemString(d, "error", ErrorObject);

	/*add in the docstring */
	PyDict_SetItemString(d, "__doc__", Py_BuildValue("s", __doc__));

	/* Check for errors */
	if (PyErr_Occurred()) Py_FatalError("can't initialize module _rl_accel");
}
