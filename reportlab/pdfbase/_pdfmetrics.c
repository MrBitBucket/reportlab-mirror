#include <Python.h>
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
	for(;e;e=e->next) if(!stricmp(name,e->name)) return e;
	return (eI_t*)0;
}

static	fI_t* find_font(char* name, fI_t* f)
{
	for(;f;f=f->next) if(!stricmp(name,f->name)) return f;
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

static char *_pdfmetricsModuleDocString=
"_pdfmetrics contains a fast string width function\n\
defaultEncoding gets/sets the default encoding for stringWidth\n\
setFontInfo adds a font to the internal table\n\
_SWRecover gets/sets a callback for stringWidth recovery\n\
";

static struct PyMethodDef _pdfmetrics_methods[] = {
	{"defaultEncoding", _pdfmetrics_defaultEncoding, 1, "defaultEncoding([encoding])\ngets/sets the default encoding."},
	{"setFontInfo", _pdfmetrics_setFontInfo, 1, "setFontInfo(fontName,encoding,ascent, descent, widths)\nadds the font to the table for encoding"},
	{"stringWidth", _pdfmetrics_stringWidth, 1, "stringwidth(text,fontName,fontSize,[encoding]) returns width of text in points"},
	{"_SWRecover", _pdfmetrics__SWRecover, 1,
					"_SWRecover([callable])\n"
					"get/set the string width recovery\n"
					"callback callable(text,font,size,encoding)\n"
					"return None to retry or the correct result."},
	{NULL,		NULL}		/* sentinel */
	};

/*Initialization function for the module (*must* be called init_pdfmetrics)*/
void init_pdfmetrics()
{
	PyObject *m, *d, *v;
	int i=0;

	/*Create the module and add the functions */
	m = Py_InitModule("_pdfmetrics", _pdfmetrics_methods);

	/*Add some symbolic constants to the module */
	d = PyModule_GetDict(m);
	ErrorObject = PyString_FromString("_pdfmetrics.error");
	PyDict_SetItemString(d, "error", ErrorObject);

	/*add in the dosctring */
	v = Py_BuildValue("s", _pdfmetricsModuleDocString);
	PyDict_SetItemString(d, "__doc__", v);

	/* Check for errors */
	if (PyErr_Occurred()) Py_FatalError("can't initialize module _pdfmetrics");
}
