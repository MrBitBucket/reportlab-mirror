/* 	$Id: xmlparser.h,v 1.3 2003/04/01 16:06:37 rgbecker Exp $    */

#ifndef XMLPARSER_H
#define XMLPARSER_H

#include "dtd.h"
#include "input.h"
#include "rxputil.h"
#include "namespaces.h"

#ifdef FOR_LT
#include "lt-hash.h"
typedef HashTab *HashTable;
#else
#include "hash.h"
#endif

/* Typedefs */

typedef struct parser_state *Parser;
typedef struct attribute *Attribute;
typedef struct xbit *XBit;
typedef void CallbackProc(XBit bit, void *arg);
typedef InputSource EntityOpenerProc(Entity e, void *arg);

/* Bits */

enum xbit_type {
    XBIT_dtd,
    XBIT_start, XBIT_empty, XBIT_end, XBIT_eof, XBIT_pcdata,
    XBIT_pi, XBIT_comment, XBIT_cdsect,
    XBIT_error, XBIT_warning, XBIT_none,
    XBIT_enum_count
};
typedef enum xbit_type XBitType;

extern XML_API const char8 *XBitTypeName[XBIT_enum_count];

enum white_space_mode {
    WSM_unspecified, WSM_default, WSM_preserve
};
typedef enum white_space_mode WhiteSpaceMode;

struct namespace_binding {
    const Char *prefix;		/* points into an attribute name, or is null */
    Namespace RXP_NAMESPACE;	/* that's namespace or name_space in C++ */
    struct namespace_binding *parent;
};
typedef struct namespace_binding *NamespaceBinding;

struct attribute {
    AttributeDefinition definition; /* The definition of this attribute */
    NSAttributeDefinition ns_definition;
    Char *value;		/* The (possibly normalised) value */
    int quoted;			/* Was it quoted? */
    int specified;		/* Was it not defaulted? */
    struct attribute *next;	/* The next attribute or null */
};

struct xbit {
    Entity entity;
    int byte_offset;
    enum xbit_type type;
    char8 *s1;
    Char *S1, *S2;
    int i1;
    Attribute attributes;
    ElementDefinition element_definition;
    WhiteSpaceMode wsm;
    NamespaceBinding ns_dict;	/* Linked list of namespace bindings */
    int nsc;			/* Count of local ns records */
    int nsowned;		/* True if ns recs should be freed with bit */
    NSElementDefinition ns_element_definition;
    				/* Null if no prefix and no default ns */
#ifndef FOR_LT
    int nchildren;
    struct xbit *parent;
    struct xbit **children;
#endif
};

#define pcdata_chars S1
#define pcdata_ignorable_whitespace i1

#define pi_name S1
#define pi_chars S2

#define comment_chars S1

#define cdsect_chars S1

#define error_message s1

/* Parser flags */

enum parser_flag {
    ExpandCharacterEntities,
    ExpandGeneralEntities,
    XMLSyntax,
    XMLPredefinedEntities,
    ErrorOnUnquotedAttributeValues,
    NormaliseAttributeValues,
    ErrorOnBadCharacterEntities,
    ErrorOnUndefinedEntities,
    ReturnComments,
    CaseInsensitive,
    ErrorOnUndefinedElements,
    ErrorOnUndefinedAttributes,
    WarnOnRedefinitions,
    TrustSDD,
    XMLExternalIDs,
    ReturnDefaultedAttributes,
    MergePCData,
    XMLMiscWFErrors,
    XMLStrictWFErrors,
    AllowMultipleElements,
    MaintainElementStack,
    IgnoreEntities,
    XMLLessThan,
    IgnorePlacementErrors,
    Validate,
    ErrorOnValidityErrors,
    XMLSpace,
    XMLNamespaces,
    NoNoDTDWarning,
    SimpleErrorFormat,
    AllowUndeclaredNSAttributes,
    RelaxedAny,
    ReturnNamespaceAttributes,
    ProcessDTD
};
typedef enum parser_flag ParserFlag;

#define NormalizeAttributeValues NormaliseAttributeValues

/* Parser */

enum parse_state 
    {PS_prolog1, PS_prolog2, PS_validate_dtd, 
     PS_body, PS_validate_final, PS_epilog, PS_end, PS_error};

struct element_info {
    ElementDefinition definition;
    NSElementDefinition ns_definition;
    Entity entity;
    FSMNode context;
    WhiteSpaceMode wsm;
    NamespaceBinding ns;
    int nsc;
};

struct parser_state {
    enum parse_state state;
    int seen_validity_error;
    Entity document_entity;
    int have_dtd;		/* True if dtd has been processed */
    StandaloneDeclaration standalone;
    struct input_source *source;
    Char *name, *pbuf, *save_pbuf;
    char8 *transbuf;
    char8 errbuf[400];		/* For error messages; fixed size is bad but
				   we don't want to fail if we can't malloc */
    char8 escbuf[2][15];
    int namelen, pbufsize, pbufnext, save_pbufsize, save_pbufnext;
    struct xbit xbit;
    int peeked;
    Dtd dtd;			/* The document's DTD */
    CallbackProc *dtd_callback;
    CallbackProc *warning_callback;
    EntityOpenerProc *entity_opener;
    unsigned int flags[2];	/* We now have >32 flags */
    Vector(struct element_info, element_stack);
    struct namespace_binding base_ns;
    void *callback_arg;
    int external_pe_depth;	/* To keep track of whether we're in the */
				/* internal subset: 0 <=> yes */
    HashTable id_table;
};

XML_API int init_parser(void);
XML_API void deinit_parser(void);
XML_API Parser NewParser(void);
XML_API void FreeParser(Parser p);

XML_API Entity ParserRootEntity(Parser p);
XML_API InputSource ParserRootSource(Parser p);

XML_API XBit ReadXBit(Parser p);
XML_API XBit PeekXBit(Parser p);
XML_API void FreeXBit(XBit xbit);

#ifndef FOR_LT
XBit ReadXTree(Parser p);
void FreeXTree(XBit tree);
#endif

XML_API XBit ParseDtd(Parser p, Entity e);

XML_API void ParserSetWarningCallback(Parser p, CallbackProc cb);
XML_API void ParserSetDtdCallback(Parser p, CallbackProc cb);
XML_API void ParserSetEntityOpener(Parser p, EntityOpenerProc opener);
XML_API void ParserSetCallbackArg(Parser p, void *arg);

XML_API int ParserPush(Parser p, InputSource source);
XML_API void ParserPop(Parser p);

XML_API void ParserSetFlag(Parser p,  ParserFlag flag, int value);
#define ParserGetFlag(p, flag) \
  (((flag) < 32) ? ((p)->flags[0] & (1u << (flag))) : ((p)->flags[1] & (1u << ((flag)-32))))

XML_API void _ParserPerror(FILE16 *f, Parser p, XBit bit);
XML_API void ParserPerror(Parser p, XBit bit);

#endif /* XMLPARSER_H */
