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

eI_t	*Encodings=NULL;

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
	char		*text, *fontName, *encoding;
	PyObject	*pS;
	double		fontSize;
	fI_t		*fI;
	eI_t		*e;
	int			w, *width, i, textLen;

	if (!PyArg_ParseTuple(args, "s#sOs", &text, &textLen, &fontName, &pS, &encoding)) return NULL;
	if((pS=PyNumber_Float(pS))) fontSize = PyFloat_AS_DOUBLE(pS);
	else{
		PyErr_SetString(ErrorObject,"bad fontSize");
		return NULL;
		}
	
	if(!(e=find_encoding(encoding))){
		PyErr_SetString(ErrorObject,"unknown encoding");
		return NULL;
		}

	if(!(fI=find_font(fontName,e->fonts))){
		PyErr_SetString(ErrorObject,"unknown font");
		return NULL;
		}

	width = fI->widths;
	for(i=w=0;i<textLen;i++)
		w += width[(unsigned)text[i]];


	return Py_BuildValue("f",0.001*fontSize*w);
}

static char *_pdfmetricsModuleDocString=
"_pdfmetrics contains a fast string width function\n\
addFont adds a font to the internal table\n\
";

static struct PyMethodDef _pdfmetrics_methods[] = {
	{"setFontInfo", _pdfmetrics_setFontInfo, 1, "setFontInfo(fontName,encoding,ascent, descent, widths)\nadds the font to the table for encoding"},
	{"stringWidth", _pdfmetrics_stringWidth, 1, "stringwidth(text,fontName,fontSize) returns width of text in points"},
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
