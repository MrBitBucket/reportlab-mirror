#include <stdio.h>
#include <stdlib.h>
#include <stdarg.h>
#if defined(WIN32) && ! defined(__CYGWIN__)
#include <io.h>
#include <fcntl.h>
#endif
#include "system.h"
#include "charset.h"
#include "string16.h"
#include "dtd.h"
#include "url.h"
#include "input.h"
#include "xmlparser.h"
#include "stdio16.h"
#include "version.h"
#include "namespaces.h"
#include "infoset-print.h"

int attr_compare(const void *a, const void *b);
void print_tree(Parser p, XBit bit);
void print_bit(Parser p, XBit bit);
void print_ns_attrs(NamespaceBinding ns, int count);
void print_namespaces(NamespaceBinding ns);
void print_attrs(ElementDefinition e, Attribute a);
void print_text(Char *text);
void print_text_bit(Char *text);
void dtd_cb(XBit bit, void *arg);
void dtd_cb2(XBit bit, void *arg);
void print_canonical_dtd(Parser p, const Char *name);
InputSource entity_open(Entity ent, void *arg);
static const char8 *minimal_uri(const char8 *uri, const char8 *base);

int verbose = 0, expand = 1, nsgml = 0,
    attr_defaults = 0, merge = 0, strict_xml = 0, tree = 0, validate = 0,
    xml_space = 0, namespaces = 0, simple_error = 0, experiment = 0,
    read_dtd = 0;
enum {o_unspec, o_none, o_bits, o_plain, o_can1, o_can2, o_can3, o_infoset} output_format = o_unspec;
char *enc_name = 0, *base_uri = 0;
CharacterEncoding encoding = CE_unknown;
InputSource source = 0;
int need_canonical_dtd = 0;

#define canonical_output (output_format >= o_can1)

Vector(XBit, bits);
Vector(XBit, dtd_bits);

int main(int argc, char **argv)
{
    int i;
    Parser p;
    char *s;
    Entity ent = 0;

    /* Sigh... guess which well-known system doesn't have getopt() */

    for(i = 1; i < argc; i++)
    {
	if(argv[i][0] != '-')
	    break;
	for(s = &argv[i][1]; *s; s++)
	    switch(*s)
	    {
	    case 'v':
		verbose = 1;
		break;
	    case 'V':
		validate++;
		break;
	    case 'a':
		attr_defaults = 1;
		break;
	    case 'e':
		fprintf(stderr, "warning: -e flag is obsolete, entities "
			        "are expanded unless -E is specified\n");
		break;
	    case 'E':
		expand = 0;
		break;
	    case 'b':
		output_format = o_bits;
		break;
	    case 'o':
		if(++i >= argc)
		{
		    fprintf(stderr, "-o requires argument\n");
		    return 1;
		}
		switch(argv[i][0])
		{
		case 'b':
		    output_format = o_bits;
		    break;
		case 'p':
		    output_format = o_plain;
		    break;
		case '0':
		    output_format = o_none;
		    break;
		case '1':
		    output_format = o_can1;
		    break;
		case '2':
		    output_format = o_can2;
		    need_canonical_dtd = 1;
		    break;
		case '3':
		    output_format = o_can3;
		    need_canonical_dtd = 1;
		    break;
		case 'i':
		    output_format = o_infoset;
		    namespaces = 1;
		    attr_defaults = 1;
		    merge = 0;
		    break;
		default:
		    fprintf(stderr, "bad output format %s\n", argv[i]);
		    return 1;
		}
		break;
	    case 's':
		output_format = o_none;
		break;
	    case 'n':
		nsgml = 1;
		break;
	    case 'N':
		namespaces = 1;
		break;
	    case 'c':
		if(++i >= argc)
		{
		    fprintf(stderr, "-c requires argument\n");
		    return 1;
		}
		enc_name = argv[i];
		break;
	    case 'm':
		merge = 1;
		break;
	    case 't':
		tree = 1;
		break;
	    case 'x':
		strict_xml = 1;
		attr_defaults = 1;
		break;
	    case 'S':
		xml_space = 1;
		break;
	    case 'z':
		simple_error = 1;
		break;
	    case 'u':
		if(++i >= argc)
		{
		    fprintf(stderr, "-u requires argument\n");
		    return 1;
		}
		base_uri = argv[i];
		break;
	    case 'd':
		read_dtd = 1;
		break;
	    case '.':
		experiment = 1;
		break;
	    default:
		fprintf(stderr, 
			"usage: rxp [-abemnNsStvVx] [-o b|0|1|2|3] [-c encoding] [-u base_uri] [url]\n");
		return 1;
	    }
    }

    init_parser();

    if(verbose)
	fprintf(stderr, "%s\n", rxp_version_string);

    if(i < argc)
    {
	ent = NewExternalEntity(0, 0, argv[i], 0, 0);
	if(ent)
	    source = EntityOpen(ent);
    }
    else
	source = SourceFromStream("<stdin>", stdin);

    if(base_uri)
    {
	/* Merge with default base URI so we can use a filename as base */
	base_uri = url_merge(base_uri, 0, 0, 0, 0, 0);
	EntitySetBaseURL(source->entity, base_uri);
	free(base_uri);
    }

    if(!source)
	return 1;

    p = NewParser();
    ParserSetEntityOpener(p, entity_open);

    if(validate)
	ParserSetFlag(p, Validate, 1);
    if(validate > 1)
	ParserSetFlag(p, ErrorOnValidityErrors, 1);

    if(read_dtd)
    {
	ParserSetFlag(p, TrustSDD, 0);
	ParserSetFlag(p, ProcessDTD, 1);
    }

    if(xml_space)
	ParserSetFlag(p, XMLSpace, 1);

    if(namespaces)
	ParserSetFlag(p, XMLNamespaces, 1);

    if(experiment)
    {
	ParserSetFlag(p, RelaxedAny, 1);
	ParserSetFlag(p, AllowUndeclaredNSAttributes, 1);
    }

    if(output_format == o_bits)
    {
	ParserSetDtdCallback(p, dtd_cb);
	ParserSetCallbackArg(p, p);
    }

    if(output_format == o_infoset)
    {
	ParserSetFlag(p, ReturnNamespaceAttributes, 1);
	ParserSetDtdCallback(p, dtd_cb2);
	ParserSetCallbackArg(p, p);
    }

    ParserSetFlag(p, SimpleErrorFormat, simple_error);

    if(attr_defaults)
	ParserSetFlag(p, ReturnDefaultedAttributes, 1);

    if(!expand)
    {
	ParserSetFlag(p, ExpandGeneralEntities, 0);
	ParserSetFlag(p, ExpandCharacterEntities, 0);
    }

    if(merge)
	ParserSetFlag(p, MergePCData, 1);

    if(nsgml)
    {
	ParserSetFlag(p, XMLSyntax, 0);
	ParserSetFlag(p, XMLPredefinedEntities, 0);
	ParserSetFlag(p, XMLExternalIDs, 0);
	ParserSetFlag(p, XMLMiscWFErrors, 0);
	ParserSetFlag(p, TrustSDD, 0);
	ParserSetFlag(p, ErrorOnUnquotedAttributeValues, 0);
	ParserSetFlag(p, ExpandGeneralEntities, 0);
	ParserSetFlag(p, ExpandCharacterEntities, 0);
/*	ParserSetFlag(p, TrimPCData, 1); */
    }

    if(strict_xml)
    {
	ParserSetFlag(p, ErrorOnBadCharacterEntities, 1);	
	ParserSetFlag(p, ErrorOnUndefinedEntities, 1);
	ParserSetFlag(p, XMLStrictWFErrors, 1);
	ParserSetFlag(p, WarnOnRedefinitions, 0);
	
    }

    if(ParserPush(p, source) == -1)
    {
	ParserPerror(p, &p->xbit);
	return 1;
    }

    if(enc_name)
    {
	encoding = FindEncoding(enc_name);

	if(encoding == CE_unknown)
	{
	    fprintf(stderr, "unknown encoding %s\n", enc_name);
	    return 1;
	}
    }
    else if(strict_xml)
	encoding = CE_UTF_8;
    else
	encoding = source->entity->encoding;

    SetFileEncoding(Stdout, encoding);

    if(output_format == o_unspec)
    {
	if(strict_xml)
	    output_format = o_can1;
	else
	    output_format = o_plain;
    }

    if(verbose)
	fprintf(stderr, "Input encoding %s, output encoding %s\n",
		CharacterEncodingNameAndByteOrder[source->entity->encoding],
		CharacterEncodingNameAndByteOrder[encoding]);

    if(source->entity->ml_decl == ML_xml && output_format == o_plain)
    {
	Printf("<?xml");

	if(source->entity->version_decl)
	    Printf(" version=\"%s\"", source->entity->version_decl);

	if(encoding == CE_unspecified_ascii_superset)
	{
	    if(source->entity->encoding_decl != CE_unknown)
		Printf(" encoding=\"%s\"", 
		       CharacterEncodingName[source->entity->encoding_decl]);
	}
	else
	    Printf(" encoding=\"%s\"",
		   CharacterEncodingName[encoding]);

	if(source->entity->standalone_decl != SDD_unspecified)
	    Printf(" standalone=\"%s\"", 
		   StandaloneDeclarationName[source->entity->standalone_decl]);

	Printf("?>\n");
    }

    VectorInit(bits);

    while(1)
    {
	XBit bit;

	if(output_format == o_infoset)
	{
	    bit = ReadXTree(p);
	    if(bit->type == XBIT_dtd)
	    {
		bit->children = dtd_bits;
		bit->nchildren = VectorCount(dtd_bits);
	    }
	    if(bit->type == XBIT_error)
		ParserPerror(p, bit);
	    else if(bit->type == XBIT_eof)
	    {
		infoset_print(Stdout, p, bits, VectorCount(bits));
		return 0;
	    }
	    else
		VectorPush(bits, bit);
	}
	else if(tree)
	{
	    bit = ReadXTree(p);
	    print_tree(p, bit);
	}
	else
	{
	    bit = ReadXBit(p);
	    print_bit(p, bit);
	}
	if(bit->type == XBIT_eof)
	{
	    int status = p->seen_validity_error ? 2 : 0;

	    if(output_format == o_plain)
		Printf("\n");

	    /* Not necessary, but helps me check for leaks */
	    if(tree)
		FreeXTree(bit);
	    else
		FreeXBit(bit);
	    FreeDtd(p->dtd);
	    FreeParser(p);
	    if(ent)
		FreeEntity(ent);
	    deinit_parser();

	    return status;
	}
	if(bit->type == XBIT_error)
	    return 1;
	if(tree)
	    FreeXTree(bit);
	else
	{
	    if(output_format != o_infoset)
		FreeXBit(bit);
	}
    }
}

void print_tree(Parser p, XBit bit)
{
    int i;
    struct xbit endbit;

    print_bit(p, bit);
    if(bit->type == XBIT_start)
    {
	for(i=0; i<bit->nchildren; i++)
	    print_tree(p, bit->children[i]);
	endbit.type = XBIT_end;
	endbit.element_definition = bit->element_definition;
	endbit.ns_element_definition = bit->ns_element_definition;
	print_bit(p, &endbit);
    }
}

void print_bit(Parser p, XBit bit)
{
    const char *sys, *pub;
    char *ws[] = {"u", "d", "p"};

    if(output_format == o_none && bit->type != XBIT_error)
	return;

    if(output_format == o_bits)
    {
	Printf("At %d: ", bit->byte_offset);
	switch(bit->type)
	{
	case XBIT_eof:
	    Printf("EOF\n");
	    break;
	case XBIT_error:
	    ParserPerror(p, bit);
	    break;
	case XBIT_dtd:
	    sys = pub = "<none>";
	    if(p->dtd->external_part)
	    {
		if(p->dtd->external_part->publicid)
		    pub = p->dtd->external_part->publicid;
		if(p->dtd->external_part->systemid)
		    sys = p->dtd->external_part->systemid;
	    }
	    Printf("doctype: %S pubid %s sysid %s\n", p->dtd->name, pub, sys);
	    break;
	case XBIT_start:
	    if(namespaces && bit->ns_element_definition)
		Printf("start: {%s}%S ",
		       bit->ns_element_definition->namespace->uri,
		       bit->element_definition->local);
	    else
		Printf("start: %S ", bit->element_definition->name);
	    if(xml_space)
		Printf("(ws=%s) ", ws[bit->wsm]);
	    print_attrs(0, bit->attributes);
	    print_namespaces(bit->ns_dict);
	    Printf("\n");
	    break;
	case XBIT_empty:
	    if(namespaces && bit->ns_element_definition)
		Printf("empty: {%s}%S ",
		       bit->ns_element_definition->namespace->uri,
		       bit->element_definition->local);
	    else
		Printf("empty: %S ", bit->element_definition->name);
	    if(xml_space)
		Printf("(ws=%s) ", ws[bit->wsm]);
	    print_attrs(0, bit->attributes);
	    print_namespaces(bit->ns_dict);
	    Printf("\n");
	    break;
	case XBIT_end:
	    if(namespaces && bit->ns_element_definition)
		Printf("end: {%s}%S ",
		       bit->ns_element_definition->namespace->uri,
		       bit->element_definition->local);
	    else
		Printf("end: %S ", bit->element_definition->name);
	    Printf("\n");
	    break;
	case XBIT_pi:
	    Printf("pi: %S: ", bit->pi_name);
	    print_text_bit(bit->pi_chars);
	    Printf("\n");
	    break;
	case XBIT_cdsect:
	    Printf("cdata: ");
	    print_text_bit(bit->cdsect_chars);
	    Printf("\n");
	    break;
	case XBIT_pcdata:
	    Printf("pcdata: ");
	    print_text_bit(bit->pcdata_chars);
	    Printf("\n");
	    break;
	case XBIT_comment:
	    Printf("comment: ");
	    print_text_bit(bit->comment_chars);
	    Printf("\n");
	    break;
	default:
	    fprintf(stderr, "***%s\n", XBitTypeName[bit->type]);
	    exit(1);
	    break;
	}
    }
    else
    {
	switch(bit->type)
	{
	case XBIT_eof:
	    break;
	case XBIT_error:
	    ParserPerror(p, bit);
	    break;
	case XBIT_dtd:
	    if(canonical_output)
		/* no doctype in canonical XML */
		break;
	    Printf("<!DOCTYPE %S", p->dtd->name);
	    if(p->dtd->external_part)
	    {
		if(p->dtd->external_part->publicid)
		    Printf(" PUBLIC \"%s\"", p->dtd->external_part->publicid);
		else if(p->dtd->external_part->systemid)
		    Printf(" SYSTEM");
		if(p->dtd->external_part->systemid)
		    Printf(" \"%s\"", p->dtd->external_part->systemid);
	    }
	    if(p->dtd->internal_part)
		Printf(" [%S]", p->dtd->internal_part->text);
	    Printf(">\n");
	    break;
	case XBIT_start:
	case XBIT_empty:
	    if(need_canonical_dtd)
		print_canonical_dtd(p, bit->element_definition->name);
	    Printf("<%S", bit->element_definition->name);
	    print_attrs(bit->element_definition, bit->attributes);
	    print_ns_attrs(bit->ns_dict, bit->nsc);
	    if(bit->type == XBIT_start)
		Printf(">");
	    else if(canonical_output)
		Printf("></%S>", bit->element_definition->name);
	    else
		Printf("/>");
	    break;
	case XBIT_end:
	    Printf("</%S>", bit->element_definition->name);
	    break;
	case XBIT_pi:
	    Printf("<?%S %S%s", 
		   bit->pi_name, bit->pi_chars, nsgml ? ">" : "?>");
	    if(p->state <= PS_prolog2 && !canonical_output)
		Printf("\n");
	    break;
	case XBIT_cdsect:
	    if(canonical_output)
		/* Print CDATA sections as plain PCDATA in canonical XML */
		print_text(bit->cdsect_chars);
	    else
		Printf("<![CDATA[%S]]>", bit->cdsect_chars);
	    break;
	case XBIT_pcdata:
	    if(output_format != o_can3 || !bit->pcdata_ignorable_whitespace)
		print_text(bit->pcdata_chars);
	    break;
	case XBIT_comment:
	    if(canonical_output)
		/* no comments in canonical XML */
		break;
	    Printf("<!--%S-->", bit->comment_chars);
	    if(p->state <= PS_prolog2)
		Printf("\n");
	    break;
	default:
	    fprintf(stderr, "\n***%s\n", XBitTypeName[bit->type]);
	    exit(1);
	    break;
	}
    }
}

int attr_compare(const void *a, const void *b)
{
    return Strcmp((*(Attribute *)a)->definition->name,
		  (*(Attribute *)b)->definition->name);
}

void print_attrs(ElementDefinition e, Attribute a)
{
    Attribute b;
    Attribute *aa;
    int i, n = 0;
    
    for(b=a; b; b=b->next)
	n++;

    if(n == 0)
	return;

    aa = malloc(n * sizeof(*aa));

    for(i=0, b=a; b; i++, b=b->next)
	aa[i] = b;

    if(canonical_output)
	qsort((void *)aa, n, sizeof(*aa), attr_compare);

    for(i=0; i<n; i++)
    {
	if(output_format == o_bits && namespaces && 
	   aa[i]->ns_definition && !aa[i]->ns_definition->element)
	    Printf(" {%s}%S=\"", 
		   aa[i]->ns_definition->namespace->uri,
		   aa[i]->definition->local);
	else
	    Printf(" %S=\"", aa[i]->definition->name);
	print_text(aa[i]->value);
	Printf("\"");
    }

    free(aa);
}

void print_text_bit(Char *text)
{
    int i;

    for(i=0; i<50 && text[i]; i++)
	if(text[i] == '\n' || text[i] == '\r')
	    text[i] = '~';
    Printf("%.50S", text);
}

void dtd_cb(XBit bit, void *arg)
{
    Printf("In DTD: ");
    print_bit(arg, bit);
    FreeXBit(bit);
}
	
void dtd_cb2(XBit bit, void *arg)
{
    XBit copy;

    if(bit->type == XBIT_comment)
	return;

    copy = malloc(sizeof(*copy));

    *copy = *bit;
    VectorPush(dtd_bits, copy);
}
	
void print_text(Char *text)
{
    Char *pc, *last;
    
    if(output_format == o_bits  || !expand)
    {
	Printf("%S", text);
	return;
    }

    for(pc = last = text; *pc; pc++)
    {
	if(*pc == '&' || *pc == '<' || *pc == '>' || *pc == '"' ||
	   (canonical_output && (*pc == 9 || *pc == 10 || *pc == 13)))
	{
	    if(pc > last)
		Printf("%.*S", pc - last, last);
	    switch(*pc)
	    {
	    case '<':
		Printf("&lt;");
		break;
	    case '>':
		Printf("&gt;");
		break;
	    case '&':
		Printf("&amp;");
		break;
	    case '"':
		Printf("&quot;");
		break;
	    case 9:
		Printf("&#9;");
		break;
	    case 10:
		Printf("&#10;");
		break;
	    case 13:
		Printf("&#13;");
		break;
	    }
	    last = pc+1;
	}
    }
	
    if(pc > last)
	Printf("%.*S", pc - last, last);
}

InputSource entity_open(Entity ent, void *arg)
{
    if(ent->publicid && 
       strcmp(ent->publicid, "-//RMT//DTD just a test//EN") == 0)
    {
	FILE *f;
	FILE16 *f16;

	if((f = fopen("/tmp/mydtd", "r")))
	{
	    if(!(f16 = MakeFILE16FromFILE(f, "r")))
		return 0;
	    SetCloseUnderlying(f16, 1);

	    return NewInputSource(ent, f16);
	}
    }

    return EntityOpen(ent);
}

void print_ns_attrs(NamespaceBinding ns, int count)
{
    NamespaceBinding n;

    if(!namespaces)
	return;

    for(n=ns; count>0; n=n->parent,--count)
    {
	/* Don't need to worry about duplicates, because that could only
	   happen if there were repeated attributes. */
	if(n->prefix)
	    Printf(" xmlns:%S=\"%s\"", n->prefix, n->namespace->uri);
	else
	    Printf(" xmlns=\"%s\"", n->namespace ? n->namespace->uri : "");
    }
}

void print_namespaces(NamespaceBinding ns)
{
    NamespaceBinding m, n;

    if(!namespaces)
	return;

    for(n=ns; n; n=n->parent)
    {
	for(m=ns; m!=n; m=m->parent)
	{
	    if(m->prefix == n->prefix)
		goto done;
	    if(m->prefix && n->prefix && Strcmp(m->prefix, n->prefix) == 0)
		goto done;
	}
	if(n->prefix)
	    Printf(" %S->%s", n->prefix, n->namespace->uri);
	else
	    Printf(" [default]->%s", n->namespace ? n->namespace->uri : "[null]");

    done:
	;
    }
}

int notation_compare(const void *a, const void *b)
{
    return Strcmp((*(NotationDefinition *)a)->name,
		  (*(NotationDefinition *)b)->name);
}

int entity_compare(const void *a, const void *b)
{
    return Strcmp((*(Entity *)a)->name, (*(Entity *)b)->name);
}

void print_canonical_dtd(Parser p, const Char *name)
{
    int i, nnot, nent;
    NotationDefinition not, *nots;
    Entity ent, *ents;
    const char8 *uri;

    need_canonical_dtd = 0;

    for(nnot=0, not=NextNotationDefinition(p->dtd, 0); not;
	not=NextNotationDefinition(p->dtd, not))
	if(!not->tentative)
	    nnot++;

    nots = malloc(nnot * sizeof(*nots));
    for(i=0, not=0; i<nnot; )
    {
	not = NextNotationDefinition(p->dtd, not);
	if(!not->tentative)
	    nots[i++] = not;
    }

    for(nent=0, ent=NextEntity(p->dtd, 0); ent; ent=NextEntity(p->dtd, ent))
	if(ent->notation)
	    nent++;

    ents = malloc(nent * sizeof(*ents));
    for(i=0, ent=0; i<nent; )
    {
	ent = NextEntity(p->dtd, ent);
	if(ent->notation)
	    ents[i++] = ent;
    }

    if((output_format != o_can3 && nnot == 0) ||
       (output_format == o_can3 && nnot + nent == 0))
	/* Don't produce a DOCTYPE if there's nothing to go in it.
	(The definition doesn't say this, but that's what the Oasis
	 test output has.) */
	return;

    qsort((void *)nots, nnot, sizeof(*nots), notation_compare);

    qsort((void *)ents, nent, sizeof(*ents), entity_compare);

    Printf("<!DOCTYPE %S [\n", name);

    /* NB the canonical forms definition says that double quotes should
       be used for the system/public ids, but the Oasis test output
       has single quotes, so we do that. */

    for(i=0; i<nnot; i++)
    {
	not = nots[i];

	if(not->systemid)
	    uri = minimal_uri(NotationURL(not), EntityURL(p->document_entity));
	else
	    uri = 0;

	Printf("<!NOTATION %S ", not->name);
	if(not->publicid)
	{
	    Printf("PUBLIC '%s'", not->publicid);
	    if(uri)
		Printf(" '%s'", uri);
	}
	else
	    Printf("SYSTEM '%s'", uri);
	Printf(">\n");
    }

    if(output_format == o_can3)
	for(i=0; i<nent; i++)
	{
	    ent = ents[i];

	    uri = minimal_uri(EntityURL(ent), EntityURL(p->document_entity));

	    Printf("<!ENTITY %S ", ent->name);
	    if(ent->publicid)
		Printf("PUBLIC '%s' '%s'", ent->publicid, uri);
	    else
		Printf("SYSTEM '%s'", uri);
	    Printf(" NDATA %S>\n", ent->notation->name);
	}
		
    Printf("]>\n");
}

/* 
 * Find minimal URI relative to some base URI.
 * This is a hack for the benefit of canonical forms, don't rely on it
 * for anything else.
 */
static const char8 *minimal_uri(const char8 *uri, const char8 *base)
{
    const char8 *u, *b;

    /* Find common prefix */

    for(u=uri, b=base; *u == *b; u++, b++)
	;

    /* Go back to a slash */

    while(u >= uri && *u != '/')
	u--, b--;

    if(*u != '/')
	return uri;		/* nothing in common */

    if(strchr(b+1, '/'))
	return uri;		/* too hard */

    return u+1;
}
