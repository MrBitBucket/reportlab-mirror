/*
* Copyright ReportLab Europe Ltd. 2000-2007
* licensed under the same terms as the ReportLab Toolkit
* see http://www.reportlab.co.uk/svn/public/reportlab/trunk/reportlab/license.txt
* for details.
* history http://www.reportlab.co.uk/cgi-bin/viewcvs.cgi/public/reportlab/trunk/reportlab/lib/_rl_accel.c
*/
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
#define VERSION "0.64"
#define MODULE "_rl_accel"

static PyObject *moduleVersion;
static PyObject *moduleObject;
static int moduleLineno;

static PyObject *ErrorObject;

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
	static char *names[] = {"fontName", "fontSize", "textColor", "rise", "underline", "strike", "link", "backColor", NULL};
	int	r=0, t;
	char **p;
	if (!PyArg_ParseTuple(args, "OO:_sameFrag", &f, &g)) return NULL;
	if(PyObject_HasAttrString(f,"cbDefn")||PyObject_HasAttrString(g,"cbDefn")
		|| PyObject_HasAttrString(f,"lineBreak")||PyObject_HasAttrString(g,"lineBreak")) goto L0;
	for(p=names;*p;p++){
		PyObject *fa, *ga;
		fa = PyObject_GetAttrString(f,*p);
		ga = PyObject_GetAttrString(g,*p);
		if(fa && ga){
			t = PyObject_Compare(fa,ga);
			Py_DECREF(fa);
			Py_DECREF(ga);
			if(PyErr_Occurred()) goto L1;
			}
		else{
			t = fa==ga ? 0 : 1;
			Py_XDECREF(fa);
			Py_XDECREF(ga);
			PyErr_Clear();
			}
		if(t) goto L0;
		}
	r = 1;
L0:	return PyInt_FromLong((long)r);
L1:	return NULL;
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

static PyObject *ttfonts_calcChecksumL(PyObject *self, PyObject* args)
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

	return PyLong_FromUnsignedLong(Sum&0xFFFFFFFFU);
}

static PyObject *ttfonts_add32(PyObject *self, PyObject* args)
{
	unsigned long x, y;
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
	x += y;
	return PyInt_FromLong(x);
}

static PyObject *ttfonts_add32L(PyObject *self, PyObject* args)
{
	unsigned long x, y;
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
	x += y;
	return PyLong_FromUnsignedLong(x&0xFFFFFFFFU);
}

static PyObject *hex32(PyObject *self, PyObject* args)
{
	unsigned long x;
	char	buf[20];
	PyObject	*ox;
	if(!PyArg_ParseTuple(args, "O:hex32", &ox)) return NULL;
	if(PyLong_Check(ox)){
		x = PyLong_AsUnsignedLongMask(ox);
		}
	else{
		x = PyInt_AsLong(ox);
		if(PyErr_Occurred()) return NULL;
		}
	sprintf(buf,"0X%8.8X",x);
	return PyString_FromString(buf);
}

static PyObject *_notdefFont=NULL;	/*should only be used by older versions of reportlab*/
static PyObject *_notdefChar=NULL;
static PyObject *_GetExcValue(void)
{
	PyObject *type = NULL, *value = NULL, *tb = NULL, *result=NULL;
	PyErr_Fetch(&type, &value, &tb);
	PyErr_NormalizeException(&type, &value, &tb);
	if(PyErr_Occurred()) goto L_BAD;
	if(!value){
		value = Py_None;
		Py_INCREF(value);
		}
	Py_XINCREF(value);
	result = value;
L_BAD:
	Py_XDECREF(type);
	Py_XDECREF(value);
	Py_XDECREF(tb);
	return result;
}
static PyObject *_GetAttrString(PyObject *obj, char *name)
{
	PyObject *res = PyObject_GetAttrString(obj, name);
	if(!res) PyErr_SetString(PyExc_AttributeError, name);
	return res;
}

#define ERROR_EXIT() {moduleLineno=__LINE__;goto L_ERR;}
#define ADD_TB(name) _add_TB(name)
#include "compile.h"
#include "frameobject.h"
#include "traceback.h"
static void _add_TB(char *funcname)
{
	PyObject *py_srcfile = NULL, *py_funcname = NULL, *py_globals = NULL, *empty_tuple = NULL, *empty_string = NULL;
	PyCodeObject *py_code = NULL;
	PyFrameObject *py_frame = NULL;
	
	py_srcfile = PyString_FromString(__FILE__);
	if(!py_srcfile) goto bad;
	py_funcname = PyString_FromString(funcname);
	if(!py_funcname) goto bad;
	py_globals = PyModule_GetDict(moduleObject);
	if(!py_globals) goto bad;
	empty_tuple = PyTuple_New(0);
	if(!empty_tuple) goto bad;
	empty_string = PyString_FromString("");
	if(!empty_string) goto bad;
	py_code = PyCode_New(
						0,				/*int argcount,*/
						0,				/*int nlocals,*/
						0,				/*int stacksize,*/
						0,				/*int flags,*/
						empty_string,	/*PyObject *code,*/
						empty_tuple,	/*PyObject *consts,*/
						empty_tuple,	/*PyObject *names,*/
						empty_tuple,	/*PyObject *varnames,*/
						empty_tuple,	/*PyObject *freevars,*/
						empty_tuple,	/*PyObject *cellvars,*/
						py_srcfile,		/*PyObject *filename,*/
						py_funcname,	/*PyObject *name,*/
						moduleLineno,	/*int firstlineno,*/
						empty_string	/*PyObject *lnotab*/
						);
	if(!py_code) goto bad;
	py_frame = PyFrame_New(
		PyThreadState_Get(), /*PyThreadState *tstate,*/
		py_code,			 /*PyCodeObject *code,*/
		py_globals,			 /*PyObject *globals,*/
		0					 /*PyObject *locals*/
		);
	if(!py_frame) goto bad;
	py_frame->f_lineno = moduleLineno;
	PyTraceBack_Here(py_frame);
bad:
	Py_XDECREF(py_srcfile);
	Py_XDECREF(py_funcname);
	Py_XDECREF(empty_tuple);
	Py_XDECREF(empty_string);
	Py_XDECREF(py_code);
	Py_XDECREF(py_frame);
}
static PyObject *unicode2T1(PyObject *self, PyObject *args, PyObject *kwds)
{
	int			i, j, _i1, _i2;
	PyObject	*R, *font, *enc, *res, *utext=NULL, *fonts=NULL,
				*_o1 = NULL, *_o2 = NULL, *_o3 = NULL;
	static char *argnames[] = {"utext","fonts",NULL};
	char		*encStr;
	if (!PyArg_ParseTupleAndKeywords(args, kwds, "OO", argnames, &utext, &fonts)) return NULL;
	Py_INCREF(utext);
	Py_INCREF(fonts);
	R = Py_None; Py_INCREF(Py_None);
	font = Py_None; Py_INCREF(Py_None);
	enc = Py_None; Py_INCREF(Py_None);


	_o2 = PyList_New(0); if(!_o2) ERROR_EXIT();
	Py_DECREF(R);
	R = _o2;
	_o2 = NULL;

	_o2 = PySequence_GetItem(fonts,0); if(!_o2) ERROR_EXIT();
	_o1 = PySequence_GetSlice(fonts, 1, 0x7fffffff); if(!_o1) ERROR_EXIT();
	Py_DECREF(font);
	font = _o2;
	Py_DECREF(fonts);
	fonts = _o1;
	_o1 = _o2 = NULL;

	_o2 = _GetAttrString(font, "encName"); if(!_o2) ERROR_EXIT();
	Py_DECREF(enc);
	enc = _o2;
	_o2 = NULL;

	encStr = PyString_AsString(enc);
	if(PyErr_Occurred()) ERROR_EXIT();
	if(strstr(encStr,"UCS-2")) encStr = "UTF16";

	while((_i1=PyObject_IsTrue(utext))>0){
		if((_o1 = PyUnicode_AsEncodedString(utext, encStr, NULL))){
			_o2 = PyTuple_New(2); if(!_o2) ERROR_EXIT();
			Py_INCREF(font);
			PyTuple_SET_ITEM(_o2, 0, font);
			PyTuple_SET_ITEM(_o2, 1, _o1);
			_o1 = NULL;
			if(PyList_Append(R, _o2)) ERROR_EXIT();
			Py_DECREF(_o2); _o2 = NULL;
			break;
			}
		else{
			Py_XDECREF(_o1); _o1 = NULL;

			if(!PyErr_ExceptionMatches(PyExc_UnicodeEncodeError)) ERROR_EXIT();
			_o1 = _GetExcValue(); if(!_o1) ERROR_EXIT();
			PyErr_Clear();
			_o2 = _GetAttrString(_o1, "args"); if(!_o2) ERROR_EXIT();
			Py_DECREF(_o1);
			_o1 = PySequence_GetSlice(_o2, 2, 4); if(!_o1) ERROR_EXIT();
			Py_DECREF(_o2);
				_o2 = PySequence_GetItem(_o1, 0); if(!_o2) ERROR_EXIT();
				i = PyInt_AsLong(_o2); if(PyErr_Occurred()) ERROR_EXIT();
				Py_DECREF(_o2);

				_o2 = PySequence_GetItem(_o1, 1); if(!_o1) ERROR_EXIT();
				j = PyInt_AsLong(_o2); if(PyErr_Occurred()) ERROR_EXIT();
				Py_DECREF(_o2);

			Py_DECREF(_o1); _o2 = _o1 = 0;

			if(i){
				_o1 = PySequence_GetSlice(utext, 0, i); if(!_o1) ERROR_EXIT();
				_o2 = PyUnicode_AsEncodedString(_o1, encStr, NULL); if(!_o2) ERROR_EXIT();
				Py_DECREF(_o1);
				_o1 = PyTuple_New(2); if(!_o1) ERROR_EXIT();
				Py_INCREF(font);
				PyTuple_SET_ITEM(_o1, 0, font);
				PyTuple_SET_ITEM(_o1, 1, _o2);
				_o2 = NULL;
				if(PyList_Append(R, _o1)) ERROR_EXIT();
				Py_DECREF(_o1); _o1 = NULL;
				}

			_i2 = PyObject_IsTrue(fonts); if(_i2<0) ERROR_EXIT();
			if(_i2){
				_o1 = PySequence_GetSlice(utext, i, j); if(!_o1) ERROR_EXIT();
				_o2 = PyTuple_New(2); if(!_o2) ERROR_EXIT();
				PyTuple_SET_ITEM(_o2, 0, _o1);
				Py_INCREF(fonts);
				PyTuple_SET_ITEM(_o2, 1, fonts);
				_o1 = unicode2T1(self,_o2,NULL); if(!_o1) ERROR_EXIT();
				Py_DECREF(_o2); _o2 = 0;
				_o3 = PyTuple_New(1); if(!_o3) ERROR_EXIT();
				PyTuple_SET_ITEM(_o3, 0, _o1);
				_o1 = _GetAttrString(R, "extend"); if(!_o1) ERROR_EXIT();
				_o2 = PyObject_CallObject(_o1, _o3); if(!_o2) ERROR_EXIT();
				Py_DECREF(_o1);
				Py_DECREF(_o3);
				Py_DECREF(_o2); _o1 = _o2 = _o3 = NULL;
				}
			else{
				_o3 = _GetAttrString(font,"_notdefChar");
				if(!_o3){
					PyErr_Clear();
					_o2 = PyInt_FromLong((j - i)); if(!_o2) ERROR_EXIT();
					if(!_notdefFont){
						_o1 = PyImport_ImportModule("reportlab.pdfbase.pdfmetrics"); if(!_o1) ERROR_EXIT();
						_o2 = _GetAttrString(_o1,"_notdefFont");
						_o3 = _GetAttrString(_o1,"_notdefChar");
						if(!_o2 || !_o3 || !_o3) ERROR_EXIT();
						_notdefFont = _o2;
						_notdefChar = _o3;
						Py_DECREF(_o1);
						_o1 = _o2 = _o3 = NULL;
						}
					_o2 = PyInt_FromLong((j - i)); if(!_o2) ERROR_EXIT();
					_o1 = PyNumber_Multiply(_notdefChar, _o2); if(!_o1) ERROR_EXIT();
					Py_DECREF(_o2);
					_o2 = PyTuple_New(2); if(!_o2) ERROR_EXIT();
					PyTuple_SET_ITEM(_o2, 0, _notdefFont);
					PyTuple_SET_ITEM(_o2, 1, _o1);
					Py_INCREF(_notdefFont);
					}
				else{
					_o2 = PyInt_FromLong((j - i)); if(!_o2) ERROR_EXIT();
					_o1 = PyNumber_Multiply(_o3, _o2); if(!_o1) ERROR_EXIT();
					Py_DECREF(_o2); Py_DECREF(_o3); _o2=_o3=NULL;
					_o2 = PyTuple_New(2); if(!_o2) ERROR_EXIT();
					_o3 = _GetAttrString(font,"_notdefFont"); if(!_o3) ERROR_EXIT();
					PyTuple_SET_ITEM(_o2, 0, _o3);
					PyTuple_SET_ITEM(_o2, 1, _o1);
					Py_INCREF(_o3); _o3=NULL;
					}
				_o1 = NULL;
				if(PyList_Append(R, _o2)) ERROR_EXIT();
				Py_DECREF(_o2); _o2 = NULL;
				}

			_o1 = PySequence_GetSlice(utext, j, 0x7fffffff); if(!_o1) ERROR_EXIT();
			Py_DECREF(utext);
			utext = _o1;
			_o1 = NULL;
			}
		}
	if(_i1<0) ERROR_EXIT();

	Py_INCREF(R);
	res = R;
	goto L_OK;

L_ERR:
	ADD_TB("unicode2T1");
	Py_XDECREF(_o1);
	Py_XDECREF(_o2);
	Py_XDECREF(_o3);
	res = NULL;
L_OK:
	Py_DECREF(R);
	Py_DECREF(font);
	Py_DECREF(enc);
	Py_DECREF(utext);
	Py_DECREF(fonts);
	return res;
}
static PyObject *_instanceStringWidthU(PyObject *module, PyObject *args, PyObject *kwds)
{
	PyObject *L, *t, *f, *self, *text, *size, *res,
				*encoding = 0, *_o1 = 0, *_o2 = 0, *_o3 = 0;
	unsigned char *b;
	int n, m, i, j, s, _i1;
	static char *argnames[]={"self","text","size","encoding",0};
	if(!PyArg_ParseTupleAndKeywords(args, kwds, "OOO|O", argnames, &self, &text, &size, &_o1)) return 0;
	Py_INCREF(self);
	Py_INCREF(text);
	Py_INCREF(size);
	if(_o1){
		encoding = _o1;
		_o1 = NULL;
		Py_INCREF(encoding);
		}
	else{
		_o1 = PyString_FromString("utf8"); if(!_o1) ERROR_EXIT();
		encoding = _o1;
		_o1 = NULL;
		}
	L = Py_None; Py_INCREF(Py_None);
	t = Py_None; Py_INCREF(Py_None);
	f = Py_None; Py_INCREF(Py_None);

	if(!PyUnicode_Check(text)){
		_o1 = _GetAttrString(text, "decode"); if(!_o1) ERROR_EXIT();
		_o3 = PyTuple_New(1); if(!_o3) ERROR_EXIT();
		Py_INCREF(encoding);
		PyTuple_SET_ITEM(_o3, 0, encoding);
		_o2 = PyObject_CallObject(_o1, _o3); if(!_o2) ERROR_EXIT();
		Py_DECREF(_o1);
		Py_DECREF(_o3); _o1 = _o3 = NULL;
		Py_DECREF(text);
		text = _o2;
		_o2 = NULL;
		}

	_o3 = PyList_New(1); if(!_o3) ERROR_EXIT();
	Py_INCREF(self);
	PyList_SET_ITEM(_o3, 0, self);
	_o2 = _GetAttrString(self, "substitutionFonts"); if(!_o2) ERROR_EXIT();
	_o1 = PyNumber_Add(_o3, _o2); if(!_o1) ERROR_EXIT();
	Py_DECREF(_o3); _o3 = 0;
	Py_DECREF(_o2); _o2 = NULL;
	_o3 = PyTuple_New(2); if(!_o3) ERROR_EXIT();
	Py_INCREF(text);
	PyTuple_SET_ITEM(_o3, 0, text);
	PyTuple_SET_ITEM(_o3, 1, _o1);
	_o1 = NULL;
	_o2 = unicode2T1(module,_o3,NULL); if(!_o2) ERROR_EXIT();
	Py_DECREF(_o3); _o3 = NULL;
	Py_DECREF(L);
	L = _o2;
	_o2 = NULL;

	n = PyList_GET_SIZE(L);

	for(s=i=0;i<n;++i){
		_o1 = PyList_GetItem(L,i); if(!_o1) ERROR_EXIT();
		Py_INCREF(_o1);

		_o2 = PySequence_GetItem(_o1, 0); if(!_o2) ERROR_EXIT();
		Py_DECREF(f);
		f = _o2;
		_o2 = NULL;

		_o2 = _GetAttrString(f, "widths"); if(!_o2) ERROR_EXIT();
		Py_DECREF(f);
		f = _o2;
		_o2 = NULL;

		_o2 = PySequence_GetItem(_o1, 1); if(!_o2) ERROR_EXIT();
		Py_DECREF(t);
		t = _o2;
		Py_DECREF(_o1);
		_o1 = _o2 = NULL;

		m = PyString_Size(t);
		b = PyString_AS_STRING(t);

		for(j=0;j<m;++j){
			_i1 = (long)(b[j]);
			_o2 = PyList_GetItem(f,_i1); if(!_o2) {PyErr_Format(PyExc_IndexError,"widths index %d out of range",_i1);ERROR_EXIT();}
			_i1 = PyInt_AsLong(_o2);
			_o2 = NULL;	/*we borrowed this*/
			if(PyErr_Occurred()) ERROR_EXIT();
			s += _i1;
			}
		}

	_o1 = PyFloat_FromDouble((s * 0.001)); if(!_o1) ERROR_EXIT();
	res = PyNumber_Multiply(_o1, size); if(!res) ERROR_EXIT();
	Py_DECREF(_o1);
	goto L_OK;
L_ERR:
	ADD_TB("_instanceStringWidthU");
	Py_XDECREF(_o1);
	Py_XDECREF(_o2);
	Py_XDECREF(_o3);
	res = NULL;
L_OK:
	Py_DECREF(L);
	Py_DECREF(t);
	Py_DECREF(f);
	Py_DECREF(self);
	Py_DECREF(text);
	Py_DECREF(size);
	Py_DECREF(encoding);
	return res;
}
static PyObject *_instanceStringWidthTTF(PyObject *module, PyObject *args, PyObject *kwds)
{
	PyObject *self, *text, *size, *res,
				*encoding = 0, *_o1=NULL, *_o2=NULL, *_o3=NULL;
	Py_UNICODE *b;
	int n, i;
	double s, _d1, dw;
	static char *argnames[]={"self","text","size","encoding",0};
	if(!PyArg_ParseTupleAndKeywords(args, kwds, "OOO|O", argnames, &self, &text, &size, &_o1)) return 0;
	Py_INCREF(text);
	if(_o1){
		encoding = _o1;
		_o1 = NULL;
		Py_INCREF(encoding);
		}
	else{
		_o1 = PyString_FromString("utf8"); if(!_o1) ERROR_EXIT();
		encoding = _o1;
		_o1 = NULL;
		}

	if(!PyUnicode_Check(text)){
		i = PyObject_IsTrue(encoding); if(i<0) ERROR_EXIT();
		if(!i){
			Py_DECREF(encoding);
			encoding = PyString_FromString("utf8"); if(!encoding) ERROR_EXIT();
			}
		_o1 = _GetAttrString(text, "decode"); if(!_o1) ERROR_EXIT();
		_o3 = PyTuple_New(1); if(!_o3) ERROR_EXIT();
		Py_INCREF(encoding);
		PyTuple_SET_ITEM(_o3, 0, encoding);
		_o2 = PyObject_CallObject(_o1, _o3); if(!_o2) ERROR_EXIT();
		Py_DECREF(_o1);
		Py_DECREF(_o3); _o1 = _o3 = NULL;
		Py_DECREF(text);
		text = _o2; /*no _o2=NULL as we assign there straight away*/ 
		}

	/*self.face.charWidths --> _o1, self.face.defaultWidth --> _o3*/
	_o2 = _GetAttrString(self, "face"); if(!_o2) ERROR_EXIT();
	_o1 = _GetAttrString(_o2, "charWidths"); if(!_o1) ERROR_EXIT(); if(!PyDict_Check(_o1)){PyErr_SetString(PyExc_TypeError, "TTFontFace instance charWidths is not a dict");ERROR_EXIT();}
	_o3 = _GetAttrString(_o2, "defaultWidth"); if(!_o3) ERROR_EXIT();
	Py_DECREF(_o2); _o2 = NULL;
	dw = PyFloat_AsDouble(_o3);
	if(PyErr_Occurred()) ERROR_EXIT();
	Py_DECREF(_o3);	_o3=NULL;

	n = PyUnicode_GET_SIZE(text);
	b = PyUnicode_AS_UNICODE(text);

	for(s=i=0;i<n;++i){
		_o3 = PyInt_FromLong((long)b[i]); if(!_o3) ERROR_EXIT();
		_o2 = PyDict_GetItem(_o1,_o3);
		Py_DECREF(_o3); _o3 = NULL;
		if(!_o2) _d1 = dw;
		else{
			_d1 = PyFloat_AsDouble(_o2);
			_o2=NULL;	/*no decref as we borrowed it*/
			if(PyErr_Occurred()) ERROR_EXIT();
			}
		s += _d1;
		}
	Py_DECREF(_o1);
	_o1 = PyFloat_FromDouble((s * 0.001)); if(!_o1) ERROR_EXIT();
	res = PyNumber_Multiply(_o1, size); if(!res) ERROR_EXIT();
	Py_DECREF(_o1);
	goto L_OK;
L_ERR:
	ADD_TB("_instanceStringWidthTTF");
	Py_XDECREF(_o1);
	Py_XDECREF(_o2);
	Py_XDECREF(_o3);
	res = NULL;
L_OK:
	Py_DECREF(text);
	Py_DECREF(encoding);
	return res;
}
/*we may need to reload pdfmtrics etc etc*/
static PyObject *_reset(PyObject *module)
{
	if(_notdefFont){
		Py_DECREF(_notdefFont); _notdefFont = NULL;
		Py_DECREF(_notdefChar);	_notdefChar = NULL;
		}
	Py_INCREF(Py_None);
	return Py_None;
}

#define HAVE_BOX
#ifdef HAVE_BOX
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
\n\
\tescapePDF makes a string safe for PDF\n\
\t_instanceEscapePDF method equivalent of escapePDF\n\
\n\
\t_AsciiBase85Encode does what is says\n\
\t_AsciiBase85Decode does what is says\n\
\n\
\tfp_str converts numeric arguments to a single blank separated string\n"
"\tcalcChecksum calculate checksums for TTFs (legacy)\n"
"\tcalcChecksumL calculate checksums for TTFs (returns long)\n"
"\tadd32 32 bit unsigned addition (legacy)\n"
"\tadd32L 32 bit unsigned addition (returns long)\n"
"\thex32 32 bit unsigned to 0X8.8X string\n"
"\t_instanceStringWidthU version2 Font instance stringWidth\n\
\t_instanceStringWidthTTF version2 TTFont instance stringWidth\n\
\tunicode2T1 version2 pdfmetrics.unicode2T1\n\
\t_reset() version2 clears _rl_accel state\n"
#ifdef	HAVE_BOX
"\tBox(width,character=None) creates a Knuth character Box with the specified width.\n"
"\tGlue(width,stretch,shrink) creates a Knuth glue Box with the specified width, stretch and shrink.\n"
"\tPenalty(width,penalty,flagged=0) creates a Knuth penalty Box with the specified width and penalty.\n"
"\tBoxList() creates a knuth box list.\n"
#endif
;

static struct PyMethodDef _methods[] = {
	{"_AsciiBase85Encode", _a85_encode, METH_VARARGS, "_AsciiBase85Encode(\".....\") return encoded string"},
	{"_AsciiBase85Decode", _a85_decode, METH_VARARGS, "_AsciiBase85Decode(\".....\") return decoded string"},
	{"escapePDF", escapePDF, METH_VARARGS, "escapePDF(s) return PDF safed string"},
	{"_instanceEscapePDF", _instanceEscapePDF, METH_VARARGS, "_instanceEscapePDF(s) return PDF safed string"},
	{"fp_str", _fp_str, METH_VARARGS, "fp_str(a0, a1,...) convert numerics to blank separated string"},
	{"_sameFrag", _sameFrag, 1, "_sameFrag(f,g) return 1 if fragments have same style"},
	{"calcChecksum", ttfonts_calcChecksum, METH_VARARGS, "calcChecksum(string) calculate checksums for TTFs (legacy)"},
	{"calcChecksumL", ttfonts_calcChecksumL, METH_VARARGS, "calcChecksumL(string) calculate checksums for TTFs (returns long)"},
	{"add32", ttfonts_add32, METH_VARARGS, "add32(x,y)  32 bit unsigned x+y (legacy)"},
	{"add32L", ttfonts_add32L, METH_VARARGS, "add32L(x,y)  32 bit unsigned x+y (returns long)"},
	{"hex32", hex32, METH_VARARGS, "hex32(x)  32 bit unsigned-->0X8.8X string"},
	{"unicode2T1", (PyCFunction)unicode2T1, METH_VARARGS|METH_KEYWORDS, "return a list of (font,string) pairs representing the unicode text"},
	{"_instanceStringWidthU", (PyCFunction)_instanceStringWidthU, METH_VARARGS|METH_KEYWORDS, "Font.stringWidth(self,text,fontName,fontSize,encoding='utf8') --> width"},
	{"_instanceStringWidthTTF", (PyCFunction)_instanceStringWidthTTF, METH_VARARGS|METH_KEYWORDS, "TTFont.stringWidth(self,text,fontName,fontSize,encoding='utf8') --> width"},
	{"_reset", (PyCFunction)_reset, METH_NOARGS, "_rl_accel._reset() reset _rl_accel state"},
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

	/*Create the module and add the functions and module doc string*/
	moduleObject = Py_InitModule3("_rl_accel", _methods,__doc__);

	/*Add some symbolic constants to the module */
	if(!ErrorObject){
		ErrorObject = PyErr_NewException("_rl_accel.error", NULL, NULL);
		if(!ErrorObject) goto err;
		}
	Py_INCREF(ErrorObject);
	moduleVersion = PyString_FromString(VERSION);
	PyModule_AddObject(moduleObject, "error", ErrorObject);
	PyModule_AddObject(moduleObject, "version", moduleVersion );

#ifdef	HAVE_BOX
	BoxType.ob_type = &PyType_Type;
	BoxList_type.tp_base = &PyList_Type;
	if(PyType_Ready(&BoxList_type)<0) goto err;
	Py_INCREF(&BoxList_type);
	if(PyModule_AddObject(moduleObject, "BoxList", (PyObject *)&BoxList_type)<0)goto err;
#endif

err:/*Check for errors*/
	if (PyErr_Occurred()) Py_FatalError("can't initialize module _rl_accel");
}
