/*
 * SGMLOP
 * $Id$
 *
 * The sgmlop accelerator module
 *
 * This module provides a FastParser type, which is designed to
 * speed up the standard sgmllib and xmllib modules.  The parser can
 * be configured to support either basic SGML (enough of it to process
 * HTML documents, at least) or XML.
 *
 * History:
 * 1998-04-04 fl  Created (for coreXML)
 * 1998-04-05 fl  Added close method
 * 1998-04-06 fl  Added parse method, revised callback interface
 * 1998-04-14 fl  Fixed parsing of PI tags
 * 1998-05-14 fl  Cleaned up for first public release
 * 1998-05-19 fl  Fixed xmllib compatibility: handle_proc, handle_special
 * 1998-05-22 fl  Added attribute parser
 * 1999-06-20 fl  Added Element data type, various bug fixes.
 * 2000-05-28 fl  Fixed data truncation error (@SGMLOP1)
 * 2000-05-28 fl  Added temporary workaround for unicode problem (@SGMLOP2)
 * 2000-05-28 fl  Removed optional close argument (@SGMLOP3)
 * 2000-05-28 fl  Raise exception on recursive feed (@SGMLOP4)
 *
 * Copyright (c) 1998-2000 by Secret Labs AB
 * Copyright (c) 1998-2000 by Fredrik Lundh
 *
 * fredrik@pythonware.com
 * http://www.pythonware.com
 *
 * By obtaining, using, and/or copying this software and/or its
 * associated documentation, you agree that you have read, understood,
 * and will comply with the following terms and conditions:
 *
 * Permission to use, copy, modify, and distribute this software and its
 * associated documentation for any purpose and without fee is hereby
 * granted, provided that the above copyright notice appears in all
 * copies, and that both that copyright notice and this permission notice
 * appear in supporting documentation, and that the name of Secret Labs
 * AB or the author not be used in advertising or publicity pertaining to
 * distribution of the software without specific, written prior
 * permission.
 *
 * SECRET LABS AB AND THE AUTHOR DISCLAIMS ALL WARRANTIES WITH REGARD TO
 * THIS SOFTWARE, INCLUDING ALL IMPLIED WARRANTIES OF MERCHANTABILITY AND
 * FITNESS.  IN NO EVENT SHALL SECRET LABS AB OR THE AUTHOR BE LIABLE FOR
 * ANY SPECIAL, INDIRECT OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
 * WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN
 * ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT
 * OF OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.  */

#include "Python.h"
#if PY_MAJOR_VERSION >= 3
#	define isPy3
#	define PY2(X)
#	define PY3(X) X
#else
#	define	PyUnicode_FromStringAndSize(s,l) PyUnicode_DecodeUTF8(s, l, NULL)
#	define PY2(X) X
#	define PY3(X)
#endif
#ifdef RL_DEBUG
#	undef RL_DEBUG
#	define RL_DEBUG(a) fprintf(stderr,"sgmlop.c:%03d %s",__LINE__,a)
#endif
#if PY_VERSION_HEX < 0x02050000
#	define Py_ssize_t int
#	define lenfunc inquiry
#	define ssizeargfunc intargfunc
#endif

#include <ctype.h>

#ifdef SGMLOP_UNICODE_SUPPORT
/* wide character set (experimental) */
/* FIXME: under Python 1.6, the current version converts Unicode
   strings to UTF-8, and parses the result as if it was an ASCII
   string. */
#define CHAR_T  Py_UNICODE
#define ISALNUM Py_UNICODE_ISALNUM
#define ISSPACE Py_UNICODE_ISSPACE
#define TOLOWER Py_UNICODE_TOLOWER
#else
/* 8-bit character set */
#define CHAR_T  char
#define ISALNUM isalnum
#define ISSPACE isspace
#define TOLOWER tolower
#endif
#ifdef isPy3
static PyObject *Py_FindMethod(PyMethodDef *ml, PyObject *self, const char* name){
	for(;ml->ml_name!=NULL;ml++)
		if(name[0]==ml->ml_name[0] && strcmp(name+1,ml->ml_name+1)==0) return PyCFunction_New(ml, self);
	return NULL;
	}
#else
#   include "bytesobject.h"
#	ifndef PyVarObject_HEAD_INIT
#		define PyVarObject_HEAD_INIT(type, size) \
        	PyObject_HEAD_INIT(type) size,
#	endif
#endif

#if 0
static int memory = 0;
#define ALLOC(size, comment)\
do { memory += size; printf("%8d - %s\n", memory, comment); } while (0)
#define RELEASE(size, comment)\
do { memory -= size; printf("%8d - %s\n", memory, comment); } while (0)
#else
#define ALLOC(size, comment)
#define RELEASE(size, comment)
#endif

/* ====================================================================
/* parser data type */

/* state flags */
#define MAYBE 1
#define SURE 2

/* parser type definition */
typedef struct {
    PyObject_HEAD

    /* mode flags */
    int xml; /* 0=sgml/html 1=xml */
	int	returnUnicode;	/*return unicode*/

    /* state attributes */
    int feed;
    int shorttag; /* 0=normal 2=parsing shorttag */
    int doctype; /* 0=normal 1=dtd pending 2=parsing dtd */

    /* buffer (holds incomplete tags) */
    char* buffer;
    int bufferlen; /* current amount of data */
    int buffertotal; /* actually allocated */

    /* callbacks */
    PyObject* finish_starttag;
    PyObject* finish_endtag;
    PyObject* handle_proc;
    PyObject* handle_special;
    PyObject* handle_charref;
    PyObject* handle_entityref;
    PyObject* handle_data;
    PyObject* handle_cdata;
    PyObject* handle_comment;

} FastParserObject;

static PyTypeObject FastParser_Type;

/* forward declarations */
static int fastfeed(FastParserObject* self);
static PyObject* attrparse(int uniconv, const CHAR_T *p, int len, int xml);


/* -------------------------------------------------------------------- */
/* create parser */

static PyObject*
_sgmlop_new(int xml)
{
    FastParserObject* self;

    self = PyObject_NEW(FastParserObject, &FastParser_Type);
    if (self == NULL)
        return NULL;

    self->xml = xml;
	self->returnUnicode = 1;

    self->feed = 0;
    self->shorttag = 0;
    self->doctype = 0;

    self->buffer = NULL;
    self->bufferlen = 0;
    self->buffertotal = 0;

    self->finish_starttag = NULL;
    self->finish_endtag = NULL;
    self->handle_proc = NULL;
    self->handle_special = NULL;
    self->handle_charref = NULL;
    self->handle_entityref = NULL;
    self->handle_data = NULL;
    self->handle_cdata = NULL;
    self->handle_comment = NULL;

    return (PyObject*) self;
}

static PyObject*
_sgmlop_sgmlparser(PyObject* self, PyObject* args)
{
    if (!PyArg_ParseTuple(args, ":SGMLParser"))
        return NULL;

    return _sgmlop_new(0);
}

static PyObject*
_sgmlop_xmlparser(PyObject* self, PyObject* args)
{
    if (!PyArg_ParseTuple(args, ":XMLParser"))
        return NULL;

    return _sgmlop_new(1);
}

static void
_sgmlop_dealloc(FastParserObject* self)
{
    if (self->buffer)
        free(self->buffer);
    Py_XDECREF(self->finish_starttag);
    Py_XDECREF(self->finish_endtag);
    Py_XDECREF(self->handle_proc);
    Py_XDECREF(self->handle_special);
    Py_XDECREF(self->handle_charref);
    Py_XDECREF(self->handle_entityref);
    Py_XDECREF(self->handle_data);
    Py_XDECREF(self->handle_cdata);
    Py_XDECREF(self->handle_comment);
    PyObject_FREE(self);
}

#define GETCB(member, name)\
    Py_XDECREF(self->member);\
    self->member = PyObject_GetAttrString(item, name);

static PyObject*
_sgmlop_register(FastParserObject* self, PyObject* args)
{
    /* register a callback object */
    PyObject* item;
    if (!PyArg_ParseTuple(args, "O", &item))
        return NULL;

    GETCB(finish_starttag, "finish_starttag");
    GETCB(finish_endtag, "finish_endtag");
    GETCB(handle_proc, "handle_proc");
    GETCB(handle_special, "handle_special");
    GETCB(handle_charref, "handle_charref");
    GETCB(handle_entityref, "handle_entityref");
    GETCB(handle_data, "handle_data");
    GETCB(handle_cdata, "handle_cdata");
    GETCB(handle_comment, "handle_comment");

    PyErr_Clear();

    Py_INCREF(Py_None);
    return Py_None;
}


/* -------------------------------------------------------------------- */
/* feed data to parser.  the parser processes as much of the data as
   possible, and keeps the rest in a local buffer. */

static PyObject*
feed(FastParserObject* self, char* string, int stringlen, int last)
{
    /* common subroutine for SGMLParser.feed and SGMLParser.close */

    int length;

    if (self->feed) {
        /* dealing with recursive feeds isn's exactly trivial, so
           let's just bail out before the parser messes things up */
        PyErr_SetString(PyExc_AssertionError, "recursive feed");
        return NULL;
    }

    /* append new text block to local buffer */
    if (!self->buffer) {
        length = stringlen;
        self->buffer = malloc(length);
        self->buffertotal = stringlen;
    } else {
        length = self->bufferlen + stringlen;
        if (length > self->buffertotal) {
            self->buffer = realloc(self->buffer, length);
            self->buffertotal = length;
        }
    }
    if (!self->buffer) {
        PyErr_NoMemory();
        return NULL;
    }
    memcpy(self->buffer + self->bufferlen, string, stringlen);
    self->bufferlen = length;

    self->feed = 1;

    length = fastfeed(self);

    self->feed = 0;

    if (length < 0)
        return NULL;

    if (length > self->bufferlen) {
        /* ran beyond the end of the buffer (internal error)*/
        PyErr_SetString(PyExc_AssertionError, "buffer overrun");
        return NULL;
    }

    if (length > 0 && length < self->bufferlen)
        /* adjust buffer */
        memmove(self->buffer, self->buffer + length,
                self->bufferlen - length);

    self->bufferlen = self->bufferlen - length;

    /* FIXME: if data remains in the buffer even through this is the
       last call, do an extra handle_data to get rid of it */

    /* FIXME: if this is the last call, shut the parser down and
       release the internal buffers */

    return Py_BuildValue("i", self->bufferlen);
}

static PyObject* _feed(FastParserObject* self, PyObject* args, int last, const char *fmt){
    /* feed a chunk of data to the parser */

    char*		string;
    Py_ssize_t	stringlen;
	PyObject	*obj, *utf8=NULL, *r=NULL;
    if (!PyArg_ParseTuple(args, fmt, &obj)) return NULL;
	if(PyUnicode_Check(obj)){
#ifdef	isPy3
		if(!(string = PyUnicode_AsUTF8AndSize(obj,&stringlen))) return NULL;
#else
		utf8 = PyUnicode_AsUTF8String(obj);
		if(!utf8){
			PyErr_SetString(PyExc_ValueError,"argument not UTF8 encoded bytes");
			return NULL;
			}
		if(PyBytes_AsStringAndSize(utf8,&string,&stringlen)==-1) goto exit;
#endif
		}
	else if(PyBytes_Check(obj)){
		if(PyBytes_AsStringAndSize(obj,&string,&stringlen)==-1) goto exit;
		}
	else{
		PyErr_SetString(PyExc_ValueError,"argument not unicode or UTF8 encoded bytes");
		}
    r = feed(self, string, stringlen, last);
exit:
	Py_XDECREF(utf8);
	return r;
}
static PyObject* _sgmlop_feed(FastParserObject* self, PyObject* args){
    /* feed a chunk of data to the parser */
	return _feed(self, args, 0, "O:feed");
	}

static PyObject*
_sgmlop_close(FastParserObject* self, PyObject* args)
{
    /* flush parser buffers */
    if (!PyArg_ParseTuple(args, ":close"))
        return NULL;
    return feed(self, "", 0, 1);
}

static PyObject*
_sgmlop_parse(FastParserObject* self, PyObject* args)
{
	return _feed(self, args, 1, "O:parse");
}


/* -------------------------------------------------------------------- */
/* type interface */

static PyMethodDef _sgmlop_methods[] = {
    /* register callbacks */
    {"register", (PyCFunction) _sgmlop_register, METH_VARARGS},
    /* incremental parsing */
    {"feed", (PyCFunction) _sgmlop_feed, METH_VARARGS},
    {"close", (PyCFunction) _sgmlop_close, METH_VARARGS},
    /* one-shot parsing */
    {"parse", (PyCFunction) _sgmlop_parse, METH_VARARGS},
    {NULL, NULL}
};

static PyObject*
_sgmlop_getattr(FastParserObject* self, char* name)
{
	if(!strcmp(name,"returnUnicode")) return PyBool_FromLong(self->returnUnicode);
    return Py_FindMethod(_sgmlop_methods, (PyObject*) self, name);
}

static int _sgmlop_setattr(FastParserObject* self, char* name, PyObject *value)
{
	int i=0;
	if(!strcmp(name,"returnUnicode")){
		i = PyObject_IsTrue(value);
		if(i<0) return i;
		self->returnUnicode=i;
		i = 0;
		}
	else{
		PyErr_Format(PyExc_ValueError,"cannot setattr %s perhaps register should be used",name);
		i = -1;
		}
	return i;
}

static PyTypeObject FastParser_Type = {
    PyVarObject_HEAD_INIT(NULL,0)
    "FastParser", /* tp_name */
    sizeof(FastParserObject), /* tp_size */
    0, /* tp_itemsize */
    /* methods */
    (destructor)_sgmlop_dealloc, /* tp_dealloc */
    0, /* tp_print */
    (getattrfunc)_sgmlop_getattr, /* tp_getattr */
	(setattrfunc)_sgmlop_setattr	/*tp_setattr*/
};

/* ==================================================================== */
/* python module interface */
static PyMethodDef _functions[] = {
    {"SGMLParser", _sgmlop_sgmlparser, METH_VARARGS},
    {"XMLParser", _sgmlop_xmlparser, METH_VARARGS},
    {NULL, NULL}
};

#ifdef isPy3
static struct PyModuleDef moduledef = {
    PyModuleDef_HEAD_INIT,
    "sgmlop",
    0, /* module doc */
    -1,
    _functions,
    NULL,
    NULL,
    NULL,
    NULL
};

PyMODINIT_FUNC PyInit_sgmlop(void)
#else
void initsgmlop()
#endif
{
	PyObject	*module=NULL;
#ifdef isPy3
	module = PyModule_Create(&moduledef);
#else
	module = Py_InitModule3("sgmlop", _functions,NULL);
#endif
	if(!module) goto err;
#ifdef isPy3
	if(PyType_Ready(&FastParser_Type)<0) goto err;
	return module;
#else
    FastParser_Type.ob_type = &PyType_Type; /* Patch object type */
	return;
#endif
err:/*Check for errors*/
#ifdef isPy3
	Py_XDECREF(module);
	return NULL;
#else
	if (PyErr_Occurred()) Py_FatalError("can't initialize module sgmlop");
#endif
}

/* -------------------------------------------------------------------- */
/* the parser does it all in a single loop, keeping the necessary
   state in a few flag variables and the data buffer.  if you have
   a good optimizer, this can be incredibly fast. */

#define TAG 0x100
#define TAG_START 0x101
#define TAG_END 0x102
#define TAG_EMPTY 0x103
#define DIRECTIVE 0x104
#define DOCTYPE 0x105
#define PI 0x106
#define DTD_START 0x107
#define DTD_END 0x108
#define DTD_ENTITY 0x109
#define CDATA 0x200
#define ENTITYREF 0x400
#define CHARREF 0x401
#define COMMENT 0x800

static int
fastfeed(FastParserObject* self)
{
    CHAR_T *end; /* tail */
    CHAR_T *p, *q, *s; /* scanning pointers */
    CHAR_T *b, *t, *e; /* token start/end */
	char	*fmtS, *fmtSS, *fmtSO;
	PyObject* res;

    int token, returnUnicode=self->returnUnicode;
#ifdef	isPy3
	if(returnUnicode){
		fmtS="s#"; 
		fmtSS="s#s#";
		fmtSO="s#O";
		}
	else{
		fmtS="y#"; 
		fmtSS="y#y#";
		fmtSO="y#O";
		}
#else
	int		uniconv=0;
	PyObject	*_o1, *_o2;
	if(returnUnicode){
		fmtS="O"; 
		fmtSS="OO";
		fmtSO="OO";
		uniconv=1;
		}
	else{
		fmtS="s#"; 
		fmtSS="s#s#";
		fmtSO="s#O";
		}
#endif

    s = q = p = (CHAR_T*) self->buffer;
    end = (CHAR_T*) (self->buffer + self->bufferlen);

    while (p < end) {

        q = p; /* start of token */

        if (*p == '<') {
            int has_attr;

            /* <tags> */
            token = TAG_START;
            if (++p >= end)
                goto eol;

            if (*p == '!') {
                /* <! directive */
                if (++p >= end)
                    goto eol;
                token = DIRECTIVE;
                b = t = p;
                if (*p == '-') {
                    /* <!-- comment --> */
                    token = COMMENT;
                    b = p + 2;
                    for (;;) {
                        if (p+3 >= end)
                            goto eol;
                        if (p[1] != '-')
                            p += 2; /* boyer moore, sort of ;-) */
                        else if (p[0] != '-' || p[2] != '>')
                            p++;
                        else
                            break;
                    }
                    e = p;
                    p += 3;
                    goto eot;
                } else if (self->xml) {
                    /* FIXME: recognize <!ATTLIST data> ? */
                    /* FIXME: recognize <!ELEMENT data> ? */
                    /* FIXME: recognize <!ENTITY data> ? */
                    /* FIXME: recognize <!NOTATION data> ? */
                    if (*p == 'D' ) {
                        /* FIXME: make sure this really is a !DOCTYPE tag */
                        /* <!DOCTYPE data> or <!DOCTYPE data [ data ]> */
                        token = DOCTYPE;
                        self->doctype = MAYBE;
                    } else if (*p == '[') {
                        /* FIXME: make sure this really is a ![CDATA[ tag */
                        /* FIXME: recognize <![INCLUDE */
                        /* FIXME: recognize <![IGNORE */
                        /* <![CDATA[data]]> */
                        token = CDATA;
                        b = t = p + 7;
                        for (;;) {
                            if (p+3 >= end)
                                goto eol;
                            if (p[1] != ']')
                                p += 2;
                            else if (p[0] != ']' || p[2] != '>')
                                p++;
                            else
                                break;
                        }
                        e = p;
                        p += 3;
                        goto eot;
                    }
                }
            } else if (*p == '?') {
                token = PI;
                if (++p >= end)
                    goto eol;
            } else if (*p == '/') {
                /* </endtag> */
                token = TAG_END;
                if (++p >= end)
                    goto eol;
            }

            /* process tag name */
            b = p;
            if (!self->xml)
                while (ISALNUM(*p) || *p == '-' || *p == '.' ||
                       *p == ':' || *p == '?') {
                    *p = TOLOWER(*p);
                    if (++p >= end)
                        goto eol;
                }
            else
                while (ISALNUM(*p) || *p == '-' || *p == '.' || *p == '_' ||
                       *p == ':' || *p == '?') {
                    if (++p >= end)
                        goto eol;
                }

            t = p;

            has_attr = 0;

            if (*p == '/' && !self->xml) {
                /* <tag/data/ or <tag/> */
                token = TAG_START;
                e = p;
                if (++p >= end)
                    goto eol;
                if (*p == '>') {
                    /* <tag/> */
                    token = TAG_EMPTY;
                    if (++p >= end)
                        goto eol;
                } else
                    /* <tag/data/ */
                    self->shorttag = SURE;
                    /* we'll generate an end tag when we stumble upon
                       the end slash */

            } else {

                /* skip attributes */
                int quote = 0;
                int last = 0;
                while (*p != '>' || quote) {
                    if (!ISSPACE(*p)) {
                        has_attr = 1;
                        /* FIXME: note: end tags cannot have attributes! */
                    }
                    if (quote) {
                        if (*p == quote)
                            quote = 0;
                    } else {
                        if (*p == '"' || *p == '\'')
                            quote = *p;
                    }
                    if (*p == '[' && !quote && self->doctype) {
                        self->doctype = SURE;
                        token = DTD_START;
                        e = p++;
                        goto eot;
                    }
                    last = *p;
                    if (++p >= end)
                        goto eol;
                }

                e = p++;

                if (last == '/') {
                    /* <tag/> */
                    e--;
                    token = TAG_EMPTY;
                } else if (token == PI && last == '?')
                    e--;

                if (self->doctype == MAYBE)
                    self->doctype = 0; /* there was no dtd */

                if (has_attr)
                    ; /* FIXME: process attributes */

            }

        } else if (*p == '/' && self->shorttag) {

            /* end of shorttag. this generates an empty end tag */
            token = TAG_END;
            self->shorttag = 0;
            b = t = e = p;
            if (++p >= end)
                goto eol;

        } else if (*p == ']' && self->doctype) {

            /* end of dtd. this generates an empty end tag */
            token = DTD_END;
            /* FIXME: who handles the ending > !? */
            b = t = e = p;
            if (++p >= end)
                goto eol;
            self->doctype = 0;

        } else if (*p == '%' && self->doctype) {

            /* doctype entities */
            token = DTD_ENTITY;
            if (++p >= end)
                goto eol;
            b = t = p;
            while (ISALNUM(*p) || *p == '.')
                if (++p >= end)
                    goto eol;
            e = p;
            if (*p == ';')
                p++;

        } else if (*p == '&') {

            /* entities */
            token = ENTITYREF;
            if (++p >= end)
                goto eol;
            if (*p == '#') {
                token = CHARREF;
                if (++p >= end)
                    goto eol;
            }
            b = t = p;
            while (ISALNUM(*p) || *p == '.')
                if (++p >= end)
                    goto eol;
            e = p;
            if (*p == ';')
                p++;

        } else {

            /* raw data */
            if (++p >= end) {
                q = p;
                goto eol;
            }
            continue;

        }

      eot: /* end of token */

        if (q != s && self->handle_data) {
            /* flush any raw data before this tag */
#ifndef	isPy3
			if(uniconv){
				_o1=PyUnicode_DecodeUTF8(s, q-s,NULL);
				if(!_o1) return -1; 
            	res = PyObject_CallFunction(self->handle_data, fmtS, _o1);
				Py_DECREF(_o1);
				}
			else{
#endif
            	res = PyObject_CallFunction(self->handle_data, fmtS, s, q-s);
#ifndef isPy3
				}
#endif
            if (!res)
                return -1;
            Py_DECREF(res);
        }

        /* invoke callbacks */
        if (token & TAG) {
            if (token == TAG_END) {
                if (self->finish_endtag) {
#ifndef	isPy3
				if(uniconv){
					_o1=PyUnicode_DecodeUTF8(b, t-b,NULL);
					if(!_o1) return -1; 
            		res = PyObject_CallFunction(self->finish_endtag, fmtS, _o1);
					Py_DECREF(_o1);
					}
				else{
#endif
                    res = PyObject_CallFunction(self->finish_endtag, fmtS, b, t-b);
#ifndef isPy3
				}
#endif
                    if (!res) return -1;
                    Py_DECREF(res);
                }
            } else if (token == DIRECTIVE || token == DOCTYPE) {
                if (self->handle_special) {
#ifndef	isPy3
					if(uniconv){
						_o1=PyUnicode_DecodeUTF8(b, e-b,NULL);
						if(!_o1) return -1; 
            			res = PyObject_CallFunction(self->handle_special, fmtS, _o1);
						Py_DECREF(_o1);
						}
					else{
#endif
                    res = PyObject_CallFunction(self->handle_special, fmtS, b, e-b);
#ifndef isPy3
				}
#endif
                    if (!res) return -1;
                    Py_DECREF(res);
                }
            } else if (token == PI) {
                if (self->handle_proc) {
                    int len = t-b;
                    while (ISSPACE(*t))
                        t++;
#ifndef	isPy3
					if(uniconv){
						_o1=PyUnicode_DecodeUTF8(b, len,NULL);
						if(!_o1) return -1; 
						_o2=PyUnicode_DecodeUTF8(t, e-t,NULL);
						if(!_o2){
							Py_DECREF(_o1);
							return -1;
							}
            			res = PyObject_CallFunction(self->handle_proc, fmtSS, _o1, _o2);
						Py_DECREF(_o2);
						Py_DECREF(_o1);
						}
					else{
#endif
                    res = PyObject_CallFunction(self->handle_proc, fmtSS, b, len, t, e-t);
#ifndef isPy3
				}
#endif
                    if (!res)
                        return -1;
                    Py_DECREF(res);
                }
            } else if (self->finish_starttag) {
                PyObject* attr;
                int len = t-b;
                while (ISSPACE(*t))
                    t++;
                attr = attrparse(returnUnicode, t, e-t, self->xml);
                if (!attr)
                    return -1;
#ifndef	isPy3
					if(uniconv){
						_o1=PyUnicode_DecodeUTF8(b, len,NULL);
						if(!_o1) return -1; 
            			res = PyObject_CallFunction(self->finish_starttag, fmtSO, _o1, attr);
						Py_DECREF(_o1);
						}
					else{
#endif
                res = PyObject_CallFunction(self->finish_starttag, fmtSO, b, len, attr);
#ifndef isPy3
				}
#endif
                Py_DECREF(attr);
                if (!res)
                    return -1;
                Py_DECREF(res);
                if (token == TAG_EMPTY && self->finish_endtag) {
#ifndef	isPy3
					if(uniconv){
						_o1=PyUnicode_DecodeUTF8(b, len,NULL);
						if(!_o1) return -1; 
            			res = PyObject_CallFunction(self->finish_endtag, fmtS, _o1);
						Py_DECREF(_o1);
						}
					else{
#endif
                    res = PyObject_CallFunction(self->finish_endtag, fmtS, b, len);
#ifndef isPy3
				}
#endif
                    if (!res)
                        return -1;
                    Py_DECREF(res);
                }
            }
        } else if (token == ENTITYREF && self->handle_entityref) {
#ifndef	isPy3
					if(uniconv){
						_o1=PyUnicode_DecodeUTF8(b, e-b,NULL);
						if(!_o1) return -1; 
            			res = PyObject_CallFunction(self->handle_entityref, fmtS, _o1);
						Py_DECREF(_o1);
						}
					else{
#endif
            res = PyObject_CallFunction(self->handle_entityref, fmtS, b, e-b);
#ifndef isPy3
				}
#endif
            if (!res)
                return -1;
            Py_DECREF(res);
        } else if (token == CHARREF && (self->handle_charref ||
                                        self->handle_data)) {
            if (self->handle_charref)PY2({)
#ifndef	isPy3
					if(uniconv){
						_o1=PyUnicode_DecodeUTF8(b, e-b,NULL);
						if(!_o1) return -1; 
            			res = PyObject_CallFunction(self->handle_charref, fmtS, _o1);
						Py_DECREF(_o1);
						}
					else{
#endif
                res = PyObject_CallFunction(self->handle_charref, fmtS, b, e-b);
				PY2(}})
            else {
                /* fallback: handle charref's as data */
                /* FIXME: hexadecimal charrefs? */
                CHAR_T ch;
                CHAR_T *p;
                ch = 0;
                for (p = b; p < e; p++)
                    ch = ch*10 + *p - '0';
#ifndef	isPy3
					if(uniconv){
						_o1=PyUnicode_DecodeUTF8(&ch, sizeof(CHAR_T),NULL);
						if(!_o1) return -1; 
            			res = PyObject_CallFunction(self->handle_data, fmtS, _o1);
						Py_DECREF(_o1);
						}
					else{
#endif
                res = PyObject_CallFunction(self->handle_data, fmtS, &ch, sizeof(CHAR_T));
#ifndef isPy3
				}
#endif
            }
            if (!res)
                return -1;
            Py_DECREF(res);
        } else if (token == CDATA && (self->handle_cdata ||
                                      self->handle_data)) {
            if (self->handle_cdata) {
#ifndef	isPy3
					if(uniconv){
						_o1=PyUnicode_DecodeUTF8(b, e-b,NULL);
						if(!_o1) return -1; 
            			res = PyObject_CallFunction(self->handle_cdata, fmtS, _o1);
						Py_DECREF(_o1);
						}
					else{
#endif
                    res = PyObject_CallFunction(self->handle_cdata, fmtS, b, e-b);
#ifndef isPy3
				}
#endif
            } else {
                /* fallback: handle cdata as plain data */
#ifndef	isPy3
					if(uniconv){
						_o1=PyUnicode_DecodeUTF8(b, e-b,NULL);
						if(!_o1) return -1; 
            			res = PyObject_CallFunction(self->handle_data, fmtS, _o1);
						Py_DECREF(_o1);
						}
					else{
#endif
                res = PyObject_CallFunction(self->handle_data, fmtS, b, e-b);
#ifndef isPy3
				}
#endif
            }
            if (!res)
                return -1;
            Py_DECREF(res);
        } else if (token == COMMENT && self->handle_comment) {
#ifndef	isPy3
			if(uniconv){
				_o1=PyUnicode_DecodeUTF8(b, e-b,NULL);
				if(!_o1) return -1; 
           			res = PyObject_CallFunction(self->handle_comment, fmtS, _o1);
					Py_DECREF(_o1);
					}
				else{
#endif
            		res = PyObject_CallFunction(self->handle_comment, fmtS, b, e-b);
#ifndef isPy3
				}
#endif
            if (!res)
                return -1;
            Py_DECREF(res);
        }

        q = p; /* start of token */
        s = p; /* start of span */
    }

  eol: /* end of line */
    if (q != s && self->handle_data) {
#ifndef	isPy3
		if(uniconv){
			_o1=PyUnicode_DecodeUTF8(s, q-s,NULL);
			if(!_o1) return -1; 
         	res = PyObject_CallFunction(self->handle_data, fmtS, _o1);
			Py_DECREF(_o1);
			}
		else{
#endif
        	res = PyObject_CallFunction(self->handle_data, fmtS, s, q-s);
#ifndef isPy3
				}
#endif
        if (!res)
            return -1;
        Py_DECREF(res);
    }

    /* returns the number of bytes consumed in this pass */
    return ((char*) q) - self->buffer;
}

static PyObject*
attrparse(int uniconv, const CHAR_T* p, int len, int xml)
{
    PyObject* attrs;
    PyObject* key = NULL;
    PyObject* value = NULL;
    const CHAR_T* end = p + len;
    const CHAR_T* q;

    if (xml)
        attrs = PyDict_New();
    else
        attrs = PyList_New(0);

    while (p < end) {

        /* skip leading space */
        while (p < end && ISSPACE(*p))
            p++;
        if (p >= end)
            break;

        /* get attribute name (key) */
        q = p;
        while (p < end && *p != '=' && !ISSPACE(*p))
            p++;

       	key = uniconv? PyUnicode_FromStringAndSize(q, p-q):PyBytes_FromStringAndSize(q, p-q);
        if(!key)
            goto err;

        while (p < end && ISSPACE(*p))
            p++;

        if (p < end && *p != '=') {

            /* attribute value not specified: set value to name */
            value = key;
            Py_INCREF(value);

        } else {

            /* attribute value found */

            if (p < end)
                p++;
            while (p < end && ISSPACE(*p))
                p++;

            q = p;
            if (p < end && (*p == '"' || *p == '\'')) {
                p++;
                while (p < end && *p != *q)
                    p++;
               	value = uniconv?PyUnicode_FromStringAndSize(q+1, p-q-1):PyBytes_FromStringAndSize(q+1, p-q-1);
				if(!value)goto err;
                if (p < end && *p == *q)
                    p++;
            } else {
                while (p < end && !ISSPACE(*p))
                    p++;
               	value = uniconv?PyUnicode_FromStringAndSize(q, p-q):PyBytes_FromStringAndSize(q, p-q);
            	}

            if (value == NULL)
                goto err;

        }

        if (xml) {

            /* add to dictionary */

            /* PyString_InternInPlace(&key); */
            if (PyDict_SetItem(attrs, key, value) < 0)
                goto err;
            Py_DECREF(key);
            Py_DECREF(value);

        } else {

            /* add to list */

            PyObject* res;
            res = PyTuple_New(2);
            if (!res)
                goto err;
            PyTuple_SET_ITEM(res, 0, key);
            PyTuple_SET_ITEM(res, 1, value);
            if (PyList_Append(attrs, res) < 0) {
                Py_DECREF(res);
                goto err;
            }
            Py_DECREF(res);

        }

        key = NULL;
        value = NULL;

    }

    return attrs;

  err:
    Py_XDECREF(key);
    Py_XDECREF(value);
    Py_DECREF(attrs);
    return NULL;
}
