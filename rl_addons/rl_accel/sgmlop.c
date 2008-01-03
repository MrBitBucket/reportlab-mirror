/*
 * SGMLOP
 * $Id$
 *
 * The sgmlop accelerator module
 *
 * This module provides a FastSGMLParser type, which is designed to
 * speed up the standard sgmllib and xmllib modules.  The parser can
 * be configured to support either basic SGML (enough of it to process
 * HTML documents, at least) or XML.  This module also provides an
 * Element type, useful for fast but simple DOM implementations.
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

} FastSGMLParserObject;

staticforward PyTypeObject FastSGMLParser_Type;

/* forward declarations */
static int fastfeed(FastSGMLParserObject* self);
static PyObject* attrparse(const CHAR_T *p, int len, int xml);


/* -------------------------------------------------------------------- */
/* create parser */

static PyObject*
_sgmlop_new(int xml)
{
    FastSGMLParserObject* self;

    self = PyObject_NEW(FastSGMLParserObject, &FastSGMLParser_Type);
    if (self == NULL)
        return NULL;

    self->xml = xml;

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
    if (!PyArg_NoArgs(args))
        return NULL;

    return _sgmlop_new(0);
}

static PyObject*
_sgmlop_xmlparser(PyObject* self, PyObject* args)
{
    if (!PyArg_NoArgs(args))
        return NULL;

    return _sgmlop_new(1);
}

static void
_sgmlop_dealloc(FastSGMLParserObject* self)
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
_sgmlop_register(FastSGMLParserObject* self, PyObject* args)
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
feed(FastSGMLParserObject* self, char* string, int stringlen, int last)
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

static PyObject*
_sgmlop_feed(FastSGMLParserObject* self, PyObject* args)
{
    /* feed a chunk of data to the parser */

    char* string;
    int stringlen;
    if (!PyArg_ParseTuple(args, "t#", &string, &stringlen))
        return NULL;

    return feed(self, string, stringlen, 0);
}

static PyObject*
_sgmlop_close(FastSGMLParserObject* self, PyObject* args)
{
    /* flush parser buffers */

    if (!PyArg_NoArgs(args))
        return NULL;

    return feed(self, "", 0, 1);
}

static PyObject*
_sgmlop_parse(FastSGMLParserObject* self, PyObject* args)
{
    /* feed a single chunk of data to the parser */

    char* string;
    int stringlen;
    if (!PyArg_ParseTuple(args, "t#", &string, &stringlen))
        return NULL;

    return feed(self, string, stringlen, 1);
}


/* -------------------------------------------------------------------- */
/* type interface */

static PyMethodDef _sgmlop_methods[] = {
    /* register callbacks */
    {"register", (PyCFunction) _sgmlop_register, 1},
    /* incremental parsing */
    {"feed", (PyCFunction) _sgmlop_feed, 1},
    {"close", (PyCFunction) _sgmlop_close, 0},
    /* one-shot parsing */
    {"parse", (PyCFunction) _sgmlop_parse, 1},
    {NULL, NULL}
};

static PyObject*  
_sgmlop_getattr(FastSGMLParserObject* self, char* name)
{
    return Py_FindMethod(_sgmlop_methods, (PyObject*) self, name);
}

statichere PyTypeObject FastSGMLParser_Type = {
    PyObject_HEAD_INIT(NULL)
    0, /* ob_size */
    "FastSGMLParser", /* tp_name */
    sizeof(FastSGMLParserObject), /* tp_size */
    0, /* tp_itemsize */
    /* methods */
    (destructor)_sgmlop_dealloc, /* tp_dealloc */
    0, /* tp_print */
    (getattrfunc)_sgmlop_getattr, /* tp_getattr */
    0 /* tp_setattr */
};

/* ====================================================================
/* element data type */

typedef struct {
    PyObject_HEAD

    /* an element has the following attributes: */
    PyObject* parent; /* back link (None for the root node) */
    PyObject* tag; /* element tag (a string) */
    PyObject* attrib; /* attributes (a dictionary object) */
    PyObject* text; /* text before first child */
    PyObject* suffix; /* text after this element, in parent */

    /* in addition, it can hold any number of child nodes: */
    int child_count; /* actual items */
    int child_total; /* allocated items */
    PyObject* *children;

    /* Note: the suffix attribute holds textual data that belongs to
       the parent.  on other words, each element represents the
       following XML snippet:

           "<tag attributes> text children </name> suffix"

       */

} ElementObject;

staticforward PyTypeObject Element_Type;

/* -------------------------------------------------------------------- */
/* element constructor and destructor */

static PyObject*
element_new(PyObject* _self, PyObject* args)
{
    ElementObject* self;

    PyObject* parent;
    PyObject* tag;
    PyObject* attrib = Py_None;
    PyObject* text = Py_None;
    PyObject* suffix = Py_None;
    if (!PyArg_ParseTuple(args, "OO|OOO", &parent, &tag,
                          &attrib, &text, &suffix))
        return NULL;

    if (parent != Py_None && parent->ob_type != &Element_Type) {
        PyErr_SetString(PyExc_TypeError, "parent must be Element or None");
        return NULL;
    }

    self = PyObject_NEW(ElementObject, &Element_Type);
    if (self == NULL)
        return NULL;

    Py_INCREF(parent);
    self->parent = parent;

    Py_INCREF(tag);
    self->tag = tag;

    Py_INCREF(attrib);
    self->attrib = attrib;

    Py_INCREF(text);
    self->text = text;

    Py_INCREF(suffix);
    self->suffix = suffix;

    self->child_count = 0;
    self->child_total = 0;
    self->children = NULL;

    ALLOC(sizeof(ElementObject), "create element");

    return (PyObject*) self;
}

static void
element_dealloc(ElementObject* self)
{
    int i;

    /* FIXME: the parent attribute means that a tree will contain
       circular references.  this will be fixed ("how?" is the big
       question...) */

    if (self->children) {
        for (i = 0; i < self->child_count; i++)
            Py_DECREF(self->children[i]);
        free(self->children);
    }

    /* break the backlink */
    Py_DECREF(self->parent);

    /* discard attributes */
    Py_DECREF(self->tag);
    Py_XDECREF(self->attrib);
    Py_XDECREF(self->text);
    Py_XDECREF(self->suffix);

    RELEASE(sizeof(ElementObject), "destroy element");

    PyObject_FREE(self);
}

/* -------------------------------------------------------------------- */
/* methods (in alphabetical order) */

static PyObject*
element_append(ElementObject* self, PyObject* args)
{
    int total;
    
    PyObject* element;
    if (!PyArg_ParseTuple(args, "O!", &Element_Type, &element))
        return NULL;

    if (!self->children) {
        total = 10;
        self->children = malloc(total * sizeof(PyObject*));
        self->child_total = total;
    } else if (self->child_count >= self->child_total) {
        total = self->child_total + 10;
        self->children = realloc(self->children, total * sizeof(PyObject*));
        self->child_total = total;
    }
    if (!self->children) {
        PyErr_NoMemory();
        return NULL;
    }

    Py_INCREF(element);
    self->children[self->child_count++] = element;

    Py_INCREF(Py_None);
    return Py_None;
}

static PyObject*
element_destroy(ElementObject* self, PyObject* args)
{
    int i;
    PyObject* res;
    
    if (!PyArg_NoArgs(args))
        return NULL;

    /* break the backlink */
    if (self->parent != Py_None) {
        Py_DECREF(self->parent);
        self->parent = Py_None;
        Py_INCREF(self->parent);
    }

    /* destroy element children */
    if (self->children) {
        for (i = 0; i < self->child_count; i++) {
            res = element_destroy((ElementObject*) self->children[i], args);
            Py_DECREF(res);
            Py_DECREF(self->children[i]);
        }
        self->child_count = 0;
    }

    /* leave the rest to the garbage collector... */

    Py_INCREF(Py_None);
    return Py_None;
}

static PyObject *
element_get(ElementObject* self, PyObject* args)
{
    PyObject* value;

    PyObject* key;
    PyObject* default_value = Py_None;
    if (!PyArg_ParseTuple(args, "O|O", &key, &default_value))
        return NULL;

    value = PyDict_GetItem(self->attrib, key);
    if (!value) {
        value = default_value;
        PyErr_Clear();
    }

    Py_INCREF(value);
    return value;
}

static PyObject*
element_getitem(ElementObject* self, Py_ssize_t index)
{
    if (index < 0 || index >= self->child_count) {
        PyErr_SetString(PyExc_IndexError, "child index out of range");
        return NULL;
    }

    Py_INCREF(self->children[index]);
    return self->children[index];
}

static Py_ssize_t
element_length(ElementObject* self)
{
    return self->child_count;
}

static PyObject*
element_repr(ElementObject* self)
{
    char buf[300];
    if (PyString_Check(self->tag))
        sprintf(
            buf, "<Element object '%.256s' at %lx>",
            PyString_AsString(self->tag),
            (long) self
            );
    else
        sprintf(
            buf, "<Element object at %lx>",
            (long) self
            );

    return PyString_FromString(buf);
}

/* -------------------------------------------------------------------- */
/* type descriptor */

static PyMethodDef element_methods[] = {
    {"get", (PyCFunction) element_get, 1},
    {"append", (PyCFunction) element_append, 1},
    {"destroy", (PyCFunction) element_destroy, 0},
    {NULL, NULL}
};

static PyObject*  
element_getattr(ElementObject* self, char* name)
{
    PyObject* res;

    res = Py_FindMethod(element_methods, (PyObject*) self, name);
    if (res)
	return res;

    PyErr_Clear();

    if (strcmp(name, "tag") == 0)
	res = self->tag;
    else if (strcmp(name, "text") == 0)
	res = self->text;
    else if (strcmp(name, "suffix") == 0)
        res = self->suffix;
    else if (strcmp(name, "attrib") == 0)
	res = self->attrib;
    else if (strcmp(name, "parent") == 0)
	res = self->parent;
    else {
        PyErr_SetString(PyExc_AttributeError, name);
        return NULL;
    }

    Py_INCREF(res);
    return res;
}

static int
element_setattr(ElementObject *self, const char* name, PyObject* value)
{
    if (value == NULL) {
        PyErr_SetString(PyExc_AttributeError,
                        "can't delete element attributes");
        return -1;
    }

    if (strcmp(name, "text") == 0) {

        Py_DECREF(self->text);
        self->text = value;
        Py_INCREF(self->text);

    } else if (strcmp(name, "suffix") == 0) {

        Py_DECREF(self->suffix);
        self->suffix = value;
        Py_INCREF(self->suffix);

    } else if (strcmp(name, "attrib") == 0) {

        Py_DECREF(self->attrib);
        self->attrib = value;
        Py_INCREF(self->attrib);

    } else {

        PyErr_SetString(PyExc_AttributeError, name);
        return -1;

    }

    return 0;
}

static PySequenceMethods element_as_sequence = {
    (lenfunc) element_length, /* sq_length */
    0, /* sq_concat */
    0, /* sq_repeat */
    (ssizeargfunc) element_getitem, /* sq_item */
    0, /* sq_slice */
    0, /* sq_ass_item */
    0, /* sq_ass_slice */
};

statichere PyTypeObject Element_Type = {
    PyObject_HEAD_INIT(NULL)
    0, /* ob_size */
    "Element", /* tp_name */
    sizeof(ElementObject), /*tp_size*/
    0, /* tp_itemsize */
    /* methods */
    (destructor)element_dealloc, /* tp_dealloc */
    0, /* tp_print */
    (getattrfunc)element_getattr, /* tp_getattr */
    (setattrfunc)element_setattr, /* tp_setattr */
    0, /* tp_compare */
    (reprfunc)element_repr, /* tp_repr */
    0, /* tp_as_number */
    &element_as_sequence, /* tp_as_sequence */
    0 /* tp_as_mapping */
};


/* ====================================================================
/* tree builder (not yet implemented) */

typedef struct {
    PyObject_HEAD

    PyObject* root; /* root node (first created node) */

    PyObject* this; /* current node */
    PyObject* last; /* most recently created node */
    PyObject* data; /* data collector */

} TreeBuilderObject;

staticforward PyTypeObject TreeBuilder_Type;

/* -------------------------------------------------------------------- */
/* constructor and destructor */

static PyObject*
treebuilder_new(PyObject* _self, PyObject* args)
{
    TreeBuilderObject* self;

    /* no arguments */
    if (!PyArg_NoArgs(args))
        return NULL;

    self = PyObject_NEW(TreeBuilderObject, &TreeBuilder_Type);
    if (self == NULL)
        return NULL;

    Py_INCREF(Py_None);
    self->root = Py_None;

    self->this = NULL;
    self->last = NULL;
    self->data = NULL;

    return (PyObject*) self;
}

static void
treebuilder_dealloc(TreeBuilderObject* self)
{
    Py_XDECREF(self->data);
    Py_XDECREF(self->last);
    Py_XDECREF(self->this);
    Py_DECREF(self->root);
    PyObject_FREE(self);
}

/* -------------------------------------------------------------------- */
/* methods (in alphabetical order) */

static PyObject*
treebuilder_start(TreeBuilderObject* self, PyObject* args)
{
    PyObject* tag;
    PyObject* attrib = Py_None;
    if (!PyArg_ParseTuple(args, "O|O", &tag, &attrib))
        return NULL;

    /* create a new node */

    Py_INCREF(Py_None);
    return Py_None;
}

static PyObject*
treebuilder_end(TreeBuilderObject* self, PyObject* args)
{
    PyObject* tag;
    if (!PyArg_ParseTuple(args, "O", &tag))
        return NULL;

    /* end current node */

    Py_INCREF(Py_None);
    return Py_None;
}

static PyObject *
treebuilder_data(TreeBuilderObject* self, PyObject* args)
{
    PyObject* data;
    if (!PyArg_ParseTuple(args, "O", &data))
        return NULL;

    /* add data to collector */

    Py_INCREF(Py_None);
    return Py_None;
}

/* -------------------------------------------------------------------- */
/* type descriptor */

static PyMethodDef treebuilder_methods[] = {
    {"data", (PyCFunction) treebuilder_data, 1},
    {"start", (PyCFunction) treebuilder_start, 1},
    {"end", (PyCFunction) treebuilder_end, 1},
    {NULL, NULL}
};

static PyObject*  
treebuilder_getattr(ElementObject* self, char* name)
{
    return Py_FindMethod(treebuilder_methods, (PyObject*) self, name);
}

statichere PyTypeObject TreeBuilder_Type = {
    PyObject_HEAD_INIT(NULL)
    0, /* ob_size */
    "TreeBuilder", /* tp_name */
    sizeof(TreeBuilderObject), /*tp_size*/
    0, /* tp_itemsize */
    /* methods */
    (destructor)treebuilder_dealloc, /* tp_dealloc */
    0, /* tp_print */
    (getattrfunc)treebuilder_getattr, /* tp_getattr */
    0, /* tp_setattr */
    0, /* tp_compare */
    0, /* tp_repr */
    0, /* tp_as_number */
    0, /* tp_as_sequence */
    0 /* tp_as_mapping */
};


/* ==================================================================== */
/* python module interface */

static PyMethodDef _functions[] = {
    {"SGMLParser", _sgmlop_sgmlparser, 0},
    {"XMLParser", _sgmlop_xmlparser, 0},
    {"Element", element_new, 1},
    {"TreeBuilder", treebuilder_new, 0},
    {NULL, NULL}
};

void
#ifdef WIN32
__declspec(dllexport)
#endif
initsgmlop()
{
    /* Patch object type */
    FastSGMLParser_Type.ob_type =
    Element_Type.ob_type =
    TreeBuilder_Type.ob_type = &PyType_Type;

    Py_InitModule("sgmlop", _functions);
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
fastfeed(FastSGMLParserObject* self)
{
    CHAR_T *end; /* tail */
    CHAR_T *p, *q, *s; /* scanning pointers */
    CHAR_T *b, *t, *e; /* token start/end */

    int token;

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
            PyObject* res;
            res = PyObject_CallFunction(self->handle_data,
                                        "s#", s, q-s);
            if (!res)
                return -1;
            Py_DECREF(res);
        }

        /* invoke callbacks */
        if (token & TAG) {
            if (token == TAG_END) {
                if (self->finish_endtag) {
                    PyObject* res;
                    res = PyObject_CallFunction(self->finish_endtag,
                                                "s#", b, t-b);
                    if (!res)
                        return -1;
                    Py_DECREF(res);
                }
            } else if (token == DIRECTIVE || token == DOCTYPE) {
                if (self->handle_special) {
                    PyObject* res;
                    res = PyObject_CallFunction(self->handle_special,
                                                "s#", b, e-b);
                    if (!res)
                        return -1;
                    Py_DECREF(res);
                }
            } else if (token == PI) {
                if (self->handle_proc) {
                    PyObject* res;
                    int len = t-b;
                    while (ISSPACE(*t))
                        t++;
                    res = PyObject_CallFunction(self->handle_proc,
                                                "s#s#", b, len, t, e-t);
                    if (!res)
                        return -1;
                    Py_DECREF(res);
                }
            } else if (self->finish_starttag) {
                PyObject* res;
                PyObject* attr;
                int len = t-b;
                while (ISSPACE(*t))
                    t++;
                attr = attrparse(t, e-t, self->xml);
                if (!attr)
                    return -1;
                res = PyObject_CallFunction(self->finish_starttag,
                                            "s#O", b, len, attr);
                Py_DECREF(attr);
                if (!res)
                    return -1;
                Py_DECREF(res);
                if (token == TAG_EMPTY && self->finish_endtag) {
                    res = PyObject_CallFunction(self->finish_endtag,
                                                "s#", b, len);
                    if (!res)
                        return -1;
                    Py_DECREF(res);
                }
            }
        } else if (token == ENTITYREF && self->handle_entityref) {
            PyObject* res;
            res = PyObject_CallFunction(self->handle_entityref,
                                        "s#", b, e-b);
            if (!res)
                return -1;
            Py_DECREF(res);
        } else if (token == CHARREF && (self->handle_charref ||
                                        self->handle_data)) {
            PyObject* res;
            if (self->handle_charref)
                res = PyObject_CallFunction(self->handle_charref,
                                            "s#", b, e-b);
            else {
                /* fallback: handle charref's as data */
                /* FIXME: hexadecimal charrefs? */
                CHAR_T ch;
                CHAR_T *p;
                ch = 0;
                for (p = b; p < e; p++)
                    ch = ch*10 + *p - '0';
                res = PyObject_CallFunction(self->handle_data,
                                            "s#", &ch, sizeof(CHAR_T));
            }
            if (!res)
                return -1;
            Py_DECREF(res);
        } else if (token == CDATA && (self->handle_cdata ||
                                      self->handle_data)) {
            PyObject* res;
            if (self->handle_cdata) {
                    res = PyObject_CallFunction(self->handle_cdata,
                                                "s#", b, e-b);
            } else {
                /* fallback: handle cdata as plain data */
                res = PyObject_CallFunction(self->handle_data,
                                            "s#", b, e-b);
            }
            if (!res)
                return -1;
            Py_DECREF(res);
        } else if (token == COMMENT && self->handle_comment) {
            PyObject* res;
            res = PyObject_CallFunction(self->handle_comment,
                                        "s#", b, e-b);
            if (!res)
                return -1;
            Py_DECREF(res);
        }
        
        q = p; /* start of token */
        s = p; /* start of span */
    }

  eol: /* end of line */
    if (q != s && self->handle_data) {
        PyObject* res;
        res = PyObject_CallFunction(self->handle_data,
                                    "s#", s, q-s);
        if (!res)
            return -1;
        Py_DECREF(res);
    }

    /* returns the number of bytes consumed in this pass */
    return ((char*) q) - self->buffer;
}

static PyObject*
attrparse(const CHAR_T* p, int len, int xml)
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

        key = PyString_FromStringAndSize(q, p-q);
        if (key == NULL)
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
                value = PyString_FromStringAndSize(q+1, p-q-1);
                if (p < end && *p == *q)
                    p++;
            } else {
                while (p < end && !ISSPACE(*p))
                    p++;
                value = PyString_FromStringAndSize(q, p-q);
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
