/****************************************************************************
#copyright ReportLab Inc. 2000
#see license.txt for license details
#history http://cvs.sourceforge.net/cgi-bin/cvsweb.cgi/rl_addons/pyRXP/pyRXP.c?cvsroot=reportlab
#$Header: /tmp/reportlab/rl_addons/pyRXP/pyRXP.c,v 1.2 2002/03/22 16:36:43 rgbecker Exp $
 ****************************************************************************/
static char* __version__=" $Id: pyRXP.c,v 1.2 2002/03/22 16:36:43 rgbecker Exp $ ";
#include <Python.h>
#include <stdio.h>
#include <stdlib.h>
#include <stdarg.h>

#ifndef CHAR_SIZE
#define CHAR_SIZE 8
#endif

#include "system.h"
#include "ctype16.h"
#include "charset.h"
#include "string16.h"
#include "dtd.h"
#include "input.h"
#include "xmlparser.h"
#include "stdio16.h"
#include "version.h"
#include "namespaces.h"
#define VERSION "0.51"
#define MODULE "pyRXP"
#define MAX_DEPTH 256
static PyObject *moduleError;
static PyObject *moduleVersion;
static PyObject *RXPVersion;
static PyObject *parser_flags;
static char *moduleDoc =
"\n\
This is pyRXP a python wrapper for RXP, a validating namespace-aware XML parser\n\
in C.\n\
\n\
RXP was written by Richard Tobin at the Language Technology Group,\n\
Human Communication Research Centre, University of Edinburgh.\n\
\n\
RXP is distributed under the GNU Public Licence, which is in the file\n\
COPYING.  RXP may be made available under other licensing terms;\n\
contact M.Moens@ed.ac.uk for details.\n\
\n\
RXP is based on the W3C XML 1.0 recommendation of 10th February 1998\n\
and the Namespaces recommendation of 14th January 1999.  Deviations\n\
from these recommendations should probably be considered as bugs.\n\
\n\
Interface summary:\n\
\n\
The python module exports the following\n\
	error			a python exception\n\
	version			the string version of the module\n\
	RXPVersion		the version string of the rxp library\n\
					embedded in the module\n\
	parser_flags	a dictionary of parser flags\n\
					the values are the defaults for parsers\n\
\n\
\n\
	Parser(*kw)		Create a parser\n\
\n\
\n\
	Parser() Attributes and Methods\n\
		parse(src)\n\
				The main interface to the parser. It returns Aaron Watter's\n\
				radxml encoding of the xml src.\n\
				The string src contains the xml.\n\
\n\
		srcName '<unknown>', name used to refer to the parser src\n\
				in error and warning messages.\n\
\n\
		warnCB	0, should either be None, 0, or a\n\
				callable method with a single argument which will\n\
				receive warning messages. If None is used then warnings\n\
				are thrown away. If the default 0 value is used then\n\
				warnings are written to the internal error message buffer\n\
				and will only be seen if an error occurs.\n\
\n\
		eoCB	argument should be None or a callable method with\n\
				a single argument. This method will be called when external\n\
				entities are opened. The method should return a possibly\n\
				modified URI.\n\
\n"
"		Flag attributes corresponding to the rxp flags;\n\
			the values are the module standard defaults.\n\
		ExpandCharacterEntities = 1\n\
		ExpandGeneralEntities = 1\n\
			If these are set, entity references are expanded.  If not, the\n\
			references are treated as text, in which case any text returned that\n\
			starts with an ampersand must be an entity reference (and provided\n\
			MergePCData is off, all entity references will be returned as separate\n\
			pieces).\n\
		XMLSyntax = 1\n\
		XMLPredefinedEntities = 1\n\
		ErrorOnUnquotedAttributeValues = 1\n\
		NormaliseAttributeValues = 1\n\
			If this is set, attributes are normalised according to the standard.\n\
			You might want to not normalise if you are writing something like an\n\
			editor.\n\
		ErrorOnBadCharacterEntities = 1\n\
			If this is set, character entities which expand to illegal values are\n\
			an error, otherwise they are ignored with a warning.\n\
		ErrorOnUndefinedEntities = 1\n\
			If this is set, undefined general entity references are an error,\n\
			otherwise a warning is given and a fake entity constructed whose value\n\
			looks the same as the entity reference.\n\
		ReturnComments = 0\n\
			If this is set, comments are returned, otherwise they are ignored.\n\
		CaseInsensitive = 0\n\
		ErrorOnUndefinedElements = 0\n\
		ErrorOnUndefinedAttributes = 0\n\
			If these are set and there is a DTD, references to undeclared elements\n\
			and attributes are an error.\n\
		WarnOnRedefinitions = 0\n\
			If this is on, a warning is given for redeclared elements, attributes,\n\
			entities and notations.\n"
"		TrustSDD = 1\n\
		ProcessDTD = 0\n\
			If TrustSDD is set and a DOCTYPE declaration is present, the internal\n\
			part is processed and if the document was not declared standalone or\n\
			if Validate is set the external part is processed.  Otherwise, whether\n\
			the DOCTYPE is automatically processed depends on ProcessDTD; if\n\
			ProcessDTD is not set the user must call ParseDtd() if desired.\n\
		XMLExternalIDs = 1\n\
		ReturnDefaultedAttributes = 1\n\
			If this is set, the returned attributes will include ones defaulted as\n\
			a result of ATTLIST declarations, otherwise missing attributes will not\n\
			be returned.\n\
		MergePCData = 1\n\
			If this is set, text data will be merged across comments and entity\n\
			references.\n\
		XMLMiscWFErrors = 1\n\
		XMLStrictWFErrors = 1\n\
			If this is set, various well-formedness errors will be reported as errors\n\
			rather than warnings.\n\
		AllowMultipleElements = 0\n\
		MaintainElementStack = 1\n\
		IgnoreEntities = 0\n\
		XMLLessThan = 0\n\
		IgnorePlacementErrors = 0\n"
"		Validate = 1\n\
			If this is on, the parser will validate the document.\n\
		ErrorOnValidityErrors = 1\n\
			If this is on, validity errors will be reported as errors rather than\n\
			warnings.  This is useful if your program wants to rely on the\n\
			validity of its input.\n\
		XMLSpace = 0\n\
			If this is on, the parser will keep track of xml:space attributes\n\
		XMLNamespaces = 0\n\
			If this is on, the parser processes namespace declarations (see\n\
			below).  Namespace declarations are *not* returned as part of the list\n\
			of attributes on an element.\n\
		NoNoDTDWarning = 1\n\
			Usually, if Validate is set, the parser will produce a warning if the\n\
			document has no DTD.  This flag suppresses the warning (useful if you\n\
			want to validate if possible, but not complain if not).\n\
		SimpleErrorFormat = 0\n\
		AllowUndeclaredNSAttributes = 0\n\
		RelaxedAny = 0\n\
		ReturnNamespaceAttributes = 0\n\
";

/*alter the integer values to change the module defaults*/
static struct {char* k;long v;} flag_vals[]={
	{"ExpandCharacterEntities",1},
	{"ExpandGeneralEntities",1},
	{"XMLSyntax",1},
	{"XMLPredefinedEntities",1},
	{"ErrorOnUnquotedAttributeValues",1},
	{"NormaliseAttributeValues",1},
	{"ErrorOnBadCharacterEntities",1},
	{"ErrorOnUndefinedEntities",1},
	{"ReturnComments",0},
	{"CaseInsensitive",0},
	{"ErrorOnUndefinedElements",0},
	{"ErrorOnUndefinedAttributes",0},
	{"WarnOnRedefinitions",0},
	{"TrustSDD",1},
	{"XMLExternalIDs",1},
	{"ReturnDefaultedAttributes",1},
	{"MergePCData",1},
	{"XMLMiscWFErrors",1},
	{"XMLStrictWFErrors",1},
	{"AllowMultipleElements",0},
	{"MaintainElementStack",1},
	{"IgnoreEntities",0},
	{"XMLLessThan",0},
	{"IgnorePlacementErrors",0},
	{"Validate",1},
	{"ErrorOnValidityErrors",1},
	{"XMLSpace",0},
	{"XMLNamespaces",0},
	{"NoNoDTDWarning",1},
	{"SimpleErrorFormat",0},
	{"AllowUndeclaredNSAttributes",0},
	{"RelaxedAny",0},
	{"ReturnNamespaceAttributes",0},
	{"ProcessDTD",0},
	{0}};

static	PyObject* get_attrs(ElementDefinition e, Attribute a)
{
	Attribute	b;
	int			n;
	for(n=0,b=a; b; b=b->next) n++;

	if(n){
		PyObject	*attrs=PyDict_New(), *t;
		for(; a; a=a->next){
			PyDict_SetItemString(attrs, (char*)a->definition->name, t=PyString_FromString(a->value));
			Py_DECREF(t);
			}
		return attrs;
		}
	else {
		Py_INCREF(Py_None);
		return Py_None;
		}
}

static	PyObject* make4tuple(char *name, PyObject* attr, int empty)
{
	PyObject	*t = PyTuple_New(4);
	PyTuple_SetItem(t,0,PyString_FromString(name));
	PyTuple_SetItem(t,1,attr);
	if(empty){
		attr = Py_None;
		Py_INCREF(Py_None);
		}
	else
		attr = PyList_New(0);
	PyTuple_SetItem(t,2,attr);
	PyTuple_SetItem(t,3,Py_None);
    Py_INCREF(Py_None);
	return t;
}

static	int handle_bit(Parser p, XBit bit, PyObject *stack[],int *depth)
{
	int	r = 0, empty;
	PyObject	*t;
	switch(bit->type) {
		case XBIT_eof: break;
		case XBIT_error:
			ParserPerror(p, bit);
			r = 1;
			break;
		case XBIT_start:
		case XBIT_empty:
			if(*depth==MAX_DEPTH){
				PyErr_SetString(moduleError,"Internal error, stack limit reached!");
				r = 2;
				break;
				}

			empty = bit->type == XBIT_empty;
			t = make4tuple((char*)bit->element_definition->name,
					get_attrs(bit->element_definition, bit->attributes), empty);
			if(empty){
				PyList_Append(PyTuple_GET_ITEM(stack[*depth],2),t);
				Py_DECREF(t);
				}
			else {
				*depth = *depth + 1;
				stack[*depth] = t;
				}
			break;
		case XBIT_end:
			if(*depth==0){
				PyErr_SetString(moduleError,"Internal error, stack underflow!");
				r = 2;
				break;
				}
			t = stack[*depth];
			*depth = *depth-1;
			PyList_Append(PyTuple_GET_ITEM(stack[*depth],2),t);
			Py_DECREF(t);
			break;
		case XBIT_pi:
#if			0
			bit->pi_name;
			bit->pi_chars;
#endif
			break;
		case XBIT_pcdata:
			t = PyString_FromString(bit->pcdata_chars);
			PyList_Append(PyTuple_GET_ITEM(stack[*depth],2),t);
			Py_DECREF(t);
			break;
		case XBIT_cdsect:
			t = PyString_FromString(bit->cdsect_chars);
			PyList_Append(PyTuple_GET_ITEM(stack[*depth],2),t);
			Py_DECREF(t);
			break;
		case XBIT_dtd:
			break;
		case XBIT_comment:
			if(ParserGetFlag(p,ReturnComments)){
				char* c = (char*)PyMem_Malloc(strlen(bit->comment_chars)+8);
				strcpy(c,"<!--");
				strcat(c,bit->comment_chars);
				strcat(c,"-->");
				t = PyString_FromString(c);
				PyList_Append(PyTuple_GET_ITEM(stack[*depth],2),t);
				Py_DECREF(t);
				PyMem_Free(c);
				}
			break;
		default:
			Fprintf(Stderr, "\nUnknown event type %s\n", XBitTypeName[bit->type]);
			ParserPerror(p, bit);
			r = 1;
			break;
		}
	return r;
}

typedef	struct {
		Parser		p;
		int			warnCBF;
		int			warnErr;
		PyObject*	warnCB;
		PyObject*	eoCB;
		} CB_info_t, *pCB_info_t;

static InputSource entity_open(Entity e, void *info)
{
	pCB_info_t	pInfo = (pCB_info_t)info;
	PyObject	*eoCB = pInfo->eoCB;

	if(e->type==ET_external){
		PyObject		*arglist;
		PyObject		*result;
		arglist = Py_BuildValue("(s)",e->systemid);
		result = PyEval_CallObject(eoCB, arglist);
		if(result){
			if(PyString_Check(result)){
				int	i;
				PyObject_Cmp(PyTuple_GET_ITEM(arglist,0),result,&i);
				if(i){
					/*not the same*/
					Free((void*)(e->systemid));
					e->systemid = strdup8(PyString_AS_STRING(result));
					}
				}
			Py_DECREF(result);
			}
		else {
			PyErr_Clear();
			}
		Py_DECREF(arglist);
		}
	return EntityOpen(e);
}

/*return non zero for error*/
PyObject *ProcessSource(Parser p, InputSource source)
{
	XBit		bit=0;
	int			r, depth, i;
	PyObject	*stack[MAX_DEPTH];
	PyObject	*retVal;

	if(ParserPush(p, source) == -1) {
		PyErr_SetString(moduleError,"Internal error, ParserPush failed!");
		return NULL;
		}

	depth = 0;
	stack[0] = make4tuple("",Py_None,0);	/*stealing a reference to Py_None*/
	Py_INCREF(Py_None);						/*so we must correct for it*/
	while(1){
		bit = ReadXBit(p);
		r = handle_bit(p, bit, stack, &depth);
		if(r) break;
		if (bit->type == XBIT_eof){
			r=0;
			break;
			}
		}
	if(!r && depth==0){
		retVal = PyList_GetItem(PyTuple_GetItem(stack[0],2),0);
		Py_INCREF(retVal);
		Py_DECREF(stack[0]);
		PyErr_Clear();
		}
	else {
		if(!r){
			PyErr_SetString(moduleError,"Internal error, stack not fully popped!");
			}
		else if(r==1){
			struct _FILE16 {
    			void *handle;
    			int handle2, handle3;
				};

			char *buf=((struct _FILE16*)Stderr)->handle;
			buf[((struct _FILE16*)Stderr)->handle2] = 0;
			PyErr_SetString(moduleError,buf);
			}
		for(i=0;i<=depth;i++){
			Py_DECREF(stack[depth]);
			}
		retVal = NULL;
		}
	FreeXBit(bit);
	return retVal;
}

static void myWarnCB(XBit bit, void *info)
{
	pCB_info_t	pInfo = (pCB_info_t)info;
	PyObject	*arglist;
	PyObject	*result;
	FILE16		*str;
	char		buf[512];

	pInfo->warnErr++;
	if(pInfo->warnCB==Py_None) return;

	str = MakeFILE16FromString(buf,sizeof(buf)-1,"w");
	_ParserPerror(str, pInfo->p, bit);
	Fclose(str);
	arglist = Py_BuildValue("(s)",buf);
	result = PyEval_CallObject(pInfo->warnCB, arglist);
	Py_DECREF(arglist);
	if(result){
		Py_DECREF(result);
		}
	else {
		pInfo->warnCBF++;
		PyErr_Clear();
		}
}

typedef struct {
	PyObject_HEAD
	char		*srcName;
	PyObject	*warnCB, *eoCB;
	int			flags[2];
	} pyRXPParserObject;

static void __SetFlag(pyRXPParserObject* p, ParserFlag flag, int value)
{
	int flagset;
	unsigned int flagbit;

	flagset = (flag >> 5);
	flagbit = (1u << (flag & 31));

	if(value) p->flags[flagset] |= flagbit;
	else p->flags[flagset] &= ~flagbit;
}

#define __GetFlag(p, flag) \
  ((((flag) < 32) ? ((p)->flags[0] & (1u << (flag))) : ((p)->flags[1] & (1u << ((flag)-32))))!=0)
static int _set_CB(char* name, PyObject** pCB, PyObject* value)
{
	if(value!=Py_None && !PyCallable_Check(value)){
		char buf[64];
		sprintf(buf,"%s value must be absent, callable or None", name);
		PyErr_SetString(PyExc_ValueError, buf);
		return -1;
		}
	else {
		if(*pCB) Py_DECREF(*pCB);
		*pCB = value;
		Py_INCREF(value);
		return 0;
		}
}

static PyObject* pyRXPParser_parse(pyRXPParserObject* self, PyObject* args)
{
	int			srcLen;
	char		*src;
	FILE16		*f;
	InputSource source;
	PyObject	*retVal;
	char		errBuf[512];
	CB_info_t	CB_info;
	Parser		p;

	if(!PyArg_ParseTuple(args, "s#", &src, &srcLen)) return NULL;

	if(self->warnCB){
		CB_info.warnCB = self->warnCB;
		CB_info.warnErr = 0;
		CB_info.warnCBF = 0;
		}
	if(self->eoCB){
		CB_info.eoCB = self->eoCB;
		}
	p = NewParser();
	p->flags[0] = self->flags[0];
	p->flags[1] = self->flags[1];
 	if((self->warnCB && self->warnCB!=Py_None) || (self->eoCB && self->eoCB!=Py_None)){
		CB_info.p = p;
 		ParserSetCallbackArg(p, &CB_info);
		if(self->warnCB && self->warnCB!=Py_None) ParserSetWarningCallback(p, myWarnCB);
		if(self->eoCB && self->eoCB!=Py_None) ParserSetEntityOpener(p, entity_open);
		}

	ParserSetFlag(p,XMLPredefinedEntities,__GetFlag(self,XMLPredefinedEntities));

	/*set up the parsers Stderr stream thing so we get it in a string*/
	Fclose(Stderr);
	Stderr = MakeFILE16FromString(errBuf,sizeof(errBuf)-1,"w");
	f = MakeFILE16FromString(src,srcLen,"r");
	source = SourceFromFILE16(self->srcName,f);
	retVal = ProcessSource(p,source);
	Fclose(Stderr);
	FreeDtd(p->dtd);
	FreeParser(p);
	deinit_parser();
	return retVal;
}

static struct PyMethodDef pyRXPParser_methods[] = {
	{"parse", (PyCFunction)pyRXPParser_parse, METH_VARARGS, "parse(src)"},
	{NULL, NULL}		/* sentinel */
};

static int pyRXPParser_setattr(pyRXPParserObject *self, char *name, PyObject* value)
{
	char buf[256];
	PyObject*	v;
	int i;

	if(!strcmp(name,"warnCB")) return _set_CB(name,&self->warnCB,value);
	else if(!strcmp(name,"eoCB")) return _set_CB(name,&self->eoCB,value);
	else if(!strcmp(name,"srcName")){
		if(!PyString_Check(value)){
			PyErr_SetString(PyExc_ValueError, "srcName value must be a string");
			return -1;
			}
		else {
			free(self->srcName);
			self->srcName = strdup(PyString_AsString(value));
			return 0;
			}
		}
	else {
		for(i=0;flag_vals[i].k;i++){
			if(!strcmp(flag_vals[i].k,name)){
				v = PyNumber_Int(value);
				if(v){
					__SetFlag(self,(ParserFlag)i,PyInt_AsLong(v));
					Py_DECREF(v);
					return 0;
					}
				else{
					sprintf(buf,"%s value must be int", name);
					PyErr_SetString(PyExc_ValueError, buf);
					return -1;
					}
				}
			}
		sprintf(buf,"Unknown attribute %s", name);
		PyErr_SetString(PyExc_AttributeError, buf);
		return -1;
		}
}

static PyObject* _get_OB(char* name,PyObject* ob)
{
	char	buf[128];
	if(ob){
		Py_INCREF(ob);
		return ob;
		}
	sprintf(buf,"Unknown attribute %s", name);
	PyErr_SetString(PyExc_AttributeError, buf);
	return NULL;
}

static PyObject* pyRXPParser_getattr(pyRXPParserObject *self, char *name)
{
	int	i;
	if(!strcmp(name,"warnCB")) return _get_OB(name,self->warnCB);
	else if(!strcmp(name,"eoCB")) return _get_OB(name,self->eoCB);
	else if(!strcmp(name,"srcName")) return PyString_FromString(self->srcName);
	else {
		for(i=0;flag_vals[i].k;i++)
			if(!strcmp(flag_vals[i].k,name))
				return PyInt_FromLong(__GetFlag(self,(ParserFlag)i));

		}
	return Py_FindMethod(pyRXPParser_methods, (PyObject *)self, name);
}

static void pyRXPParserFree(pyRXPParserObject* self)
{
	if(self->srcName) PyMem_Free(self->srcName);
	if(self->warnCB) Py_DECREF(self->warnCB);
	if(self->eoCB) Py_DECREF(self->eoCB);
#if	0
	/*this could be called if we're never going to use the parser again*/
	deinit_parser();
#endif
	PyMem_DEL(self);
}

static PyTypeObject pyRXPParserType = {
	PyObject_HEAD_INIT(0)
	0,								/*ob_size*/
	"pyRXPParser",					/*tp_name*/
	sizeof(pyRXPParserObject),		/*tp_basicsize*/
	0,								/*tp_itemsize*/
	/* methods */
	(destructor)pyRXPParserFree,	/*tp_dealloc*/
	(printfunc)0,					/*tp_print*/
	(getattrfunc)pyRXPParser_getattr,	/*tp_getattr*/
	(setattrfunc)pyRXPParser_setattr,	/*tp_setattr*/
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
	"pyRXPParser instance, see pyRXP doc string for details."
};

static pyRXPParserObject* pyRXPParser(PyObject* module, PyObject* args, PyObject* kw)
{
	pyRXPParserObject* self;
	int	i;

	if(!PyArg_ParseTuple(args, ":Parser")) return NULL;
	if(!(self = PyObject_NEW(pyRXPParserObject, &pyRXPParserType))) return NULL;
	self->warnCB = self->eoCB = (void*)self->srcName = NULL;
	if(!(self->srcName=strdup("[unknown]"))){
		PyErr_SetString(moduleError,"Internal error, memory limit reached!");
Lfree:	pyRXPParserFree(self);
		return NULL;
		}
	for(i=0;flag_vals[i].k;i++)
		__SetFlag(self,(ParserFlag)i,PyInt_AsLong(PyDict_GetItemString(parser_flags,flag_vals[i].k)));

	if(kw){
		PyObject *key, *value;
		i = 0;
		while(PyDict_Next(kw,&i,&key,&value))
			if(pyRXPParser_setattr(self, PyString_AsString(key), value)) goto Lfree;
		}

	return self;
}

static struct PyMethodDef moduleMethods[] = {
	{"Parser",	(PyCFunction)pyRXPParser,	METH_VARARGS|METH_KEYWORDS, "Parser(*kw) create a pyRXP parser instance"},
	{NULL,	NULL}	/*sentinel*/
};

DL_EXPORT(void) initpyRXP(void)
{
	PyObject *m, *d, *v, *t;
	int	i;

	/*set up the types by hand*/
	pyRXPParserType.ob_type = &PyType_Type;

	/* Create the module and add the functions */
	m = Py_InitModule(MODULE, moduleMethods);

	/* Add some symbolic constants to the module */
	d = PyModule_GetDict(m);
	moduleVersion = PyString_FromString(VERSION);
	PyDict_SetItemString(d, "version", moduleVersion );
	RXPVersion = PyString_FromString(rxp_version_string);
	PyDict_SetItemString(d, "RXPVersion", RXPVersion );
	moduleError = PyErr_NewException(MODULE ".Error",NULL,NULL);
	PyDict_SetItemString(d,"error",moduleError);
	parser_flags = PyDict_New();
	for(i=0;flag_vals[i].k;i++){
		PyDict_SetItemString(parser_flags, flag_vals[i].k, t=PyInt_FromLong(flag_vals[i].v));
		Py_DECREF(t);
		}
	PyDict_SetItemString(d,"parser_flags",parser_flags);
	
	/*add in the docstring*/
	v = PyString_FromString(moduleDoc);
	PyDict_SetItemString(d, "__doc__", v);
	Py_DECREF(v);
}
