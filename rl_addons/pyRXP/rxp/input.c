#include <stdio.h>
#include <stdlib.h>
#include <assert.h>

#ifdef FOR_LT

#include "lt-memory.h"
#include "nsllib.h"

#define ERR(m) LT_ERROR(NECHAR,m)
#define ERR1(m,x) LT_ERROR1(NECHAR,m,x)
#define ERR2(m,x,y) LT_ERROR2(NECHAR,m,x,y)
#define ERR3(m,x,y,z) LT_ERROR3(NECHAR,m,x,y,z)

#define Malloc salloc
#define Realloc srealloc
#define Free sfree

#else

#include "system.h"
#define ERR(m) fprintf(stderr,m)
#define ERR1(m,x) fprintf(stderr,m,x)
#define ERR2(m,x,y) fprintf(stderr,m,x,y)
#define ERR3(m,x,y,z) fprintf(stderr,m,x,y,z)

#endif

#include "charset.h"
#include "string16.h"
#include "dtd.h"
#include "input.h"
#include "url.h"
#include "ctype16.h"

static int get_translated_line1(InputSource s);

InputSource SourceFromFILE16(const char8 *description, FILE16 *file16)
{
    Entity e;

    e = NewExternalEntity(0, 0, description, 0, 0);
    if(!strchr8(description, '/'))
    {
	char8 *base = default_base_url();
	EntitySetBaseURL(e, base);
	Free(base);
    }
    
    return NewInputSource(e, file16);
}

InputSource SourceFromStream(const char8 *description, FILE *file)
{
    FILE16 *file16;

    if(!(file16 = MakeFILE16FromFILE(file, "r")))
	return 0;

    return SourceFromFILE16(description, file16);
}

InputSource EntityOpen(Entity e)
{
    FILE16 *f16;
    char8 *r_url;

    if(e->type == ET_external)
    {
	const char8 *url = EntityURL(e);

	if(!url || !(f16 = url_open(url, 0, "r", &r_url)))
	    return 0;
	if(r_url && !e->base_url)
	    EntitySetBaseURL(e, r_url);
	Free(r_url);
    }
    else
    {
	f16 = MakeFILE16FromString((char *)e->text, -1, "r");
    }

    return NewInputSource(e, f16);
}


InputSource NewInputSource(Entity e, FILE16 *f16)
{
    InputSource source;

    if(!(source = Malloc(sizeof(*source))))
	return 0;

    source->line = 0;
    source->line_alloc = 0;
    source->line_length = 0;
    source->next = 0;
    source->seen_eoe = 0;

    source->entity = e;

    source->file16 = f16;

    source->bytes_consumed = 0;
    source->bytes_before_current_line = 0;
    source->line_end_was_cr = 0;
    source->line_number = 0;
    source->not_read_yet = 1;

    source->nextin = source->insize = 0;

    source->parent = 0;

    source->seen_error = 0;
    strcpy(source->error_msg, "no error (you should never see this)");

    return source;
}

void SourceClose(InputSource source)
{
    Fclose(source->file16);

    if(source->entity->type == ET_external)
	Free(source->line);
    Free(source);
}

int SourceLineAndChar(InputSource s, int *linenum, int *charnum)
{
    Entity e = s->entity, f = e->parent;

    if(e->type == ET_external)
    {
	*linenum = s->line_number;
	*charnum = s->next;
	return 1;
    }

    if(f && f->type == ET_external)
    {
	if(e->matches_parent_text)
	{
	    *linenum = e->line_offset + s->line_number;
	    *charnum = (s->line_number == 0 ? e->line1_char_offset : 0) +
		       s->next;
	    return 1;
	}
	else
	{
	    *linenum = e->line_offset;
	    *charnum = e->line1_char_offset;
	    return 0;
	}
    }

    if(f && f->matches_parent_text)
    {
	*linenum = f->line_offset + e->line_offset;
	*charnum = (e->line_offset == 0 ? f->line1_char_offset : 0) +
	    e->line1_char_offset;
	return 0;
    }

    return -1;
}

void SourcePosition(InputSource s, Entity *entity, int *byte_offset)
{
    *entity = s->entity;
    *byte_offset = SourceTell(s);
}

int SourceTell(InputSource s)
{
#if CHAR_SIZE == 8
    return s->bytes_before_current_line + s->next;
#else
    switch(s->entity->encoding)
    {
    case CE_ISO_10646_UCS_2B:
    case CE_UTF_16B:
    case CE_ISO_10646_UCS_2L:
    case CE_UTF_16L:
	return s->bytes_before_current_line + 2 * s->next;
    case CE_ISO_8859_1:
    case CE_ISO_8859_2:
    case CE_ISO_8859_3:
    case CE_ISO_8859_4:
    case CE_ISO_8859_5:
    case CE_ISO_8859_6:
    case CE_ISO_8859_7:
    case CE_ISO_8859_8:
    case CE_ISO_8859_9:
    case CE_unspecified_ascii_superset:
	return s->bytes_before_current_line + s->next;
    case CE_UTF_8:
	if(s->complicated_utf8_line)
	{
	    /* examine earlier chars in line to see how many bytes they used */
	    int i, c, n;

	    /* We cache the last result to avoid N^2 slowness on very
	       long lines.  Thanks to Gait Boxman for suggesting this. */

	    if(s->next < s->cached_line_char)
	    {
		/* Moved backwards in line; doesn't happen, I think */
		s->cached_line_char = 0;
		s->cached_line_byte = 0;
	    }

	    n = s->cached_line_byte;
	    for(i = s->cached_line_char; i < s->next; i++)
	    {
		c = s->line[i];
		if(c <= 0x7f)
		    n += 1;
		else if(c <= 0x7ff)
		    n += 2;
		else if(c >= 0xd800 && c <= 0xdfff)
		    /* One of a surrogate pair, count 2 each */
		    n += 2;
		else if(c <= 0xffff)
		    n += 3;
		else if(c <= 0x1ffff)
		    n += 4;
		else if(c <= 0x3ffffff)
		    n += 5;
		else
		    n += 6;

	    }

	    s->cached_line_char = s->next;
	    s->cached_line_byte = n;

	    return s->bytes_before_current_line + n;
	}
	else
	    return s->bytes_before_current_line + s->next;
    default:
	return -1;
    }
#endif
}

int SourceSeek(InputSource s, int byte_offset)
{
    s->line_length = 0;
    s->next = 0;
    s->seen_eoe = 0;
    s->bytes_consumed = s->bytes_before_current_line = byte_offset;
    s->nextin = s->insize = 0;
    /* XXX line number will be wrong! */
    s->line_number = -999999;
    return Fseek(s->file16, byte_offset, SEEK_SET);
}

static int get_translated_line(InputSource s)
{
    /* This is a hack, pending some reorganisation */

    struct _FILE16 {
	void *handle;
	int handle2, handle3;
	/* we don't need the rest here */
    };

    Entity e = s->entity;
    Char *p;
    struct _FILE16 *f16 = (struct _FILE16 *)s->file16;


    if(e->type == ET_external)
	return get_translated_line1(s);

    if(!*(Char *)((char *)f16->handle + f16->handle2))
    {
	s->line_length = 0;
	return 0;
    }

    s->line = (Char *)((char *)f16->handle + f16->handle2);
    for(p=s->line; *p && *p != '\n'; p++)
	;
    if(*p)
	p++;
    f16->handle2 = (char *)p - (char *)f16->handle;
    s->line_length = p - s->line;

    s->bytes_before_current_line = f16->handle2;

    return 0;
}

static int get_translated_line1(InputSource s)
{
    unsigned int c;		/* can't use Char, it might be >0x10000 */
    unsigned char *inbuf = s->inbuf;
    int nextin = s->nextin, insize = s->insize;
    int startin = s->nextin;
    Char *outbuf = s->line;
    int outsize = s->line_alloc;
    int nextout = 0;
    int remaining = 0;
    int ignore_linefeed = s->line_end_was_cr;

#if CHAR_SIZE == 16

    int expecting_low_surrogate = 0;
    int *to_unicode = 0;	/* initialize to shut gcc up */
    CharacterEncoding enc = s->entity->encoding;
    int more, i, mincode;
    s->complicated_utf8_line = 0;

    if(enc >= CE_ISO_8859_2 && enc <= CE_ISO_8859_9)
	to_unicode = iso_to_unicode[enc - CE_ISO_8859_2];

#endif

    if(s->seen_error)
	return -1;

    s->line_end_was_cr = 0;
    s->bytes_before_current_line = s->bytes_consumed;

    while(1)
    {
	/* There are never more characters than bytes in the input */
	if(outsize < nextout + (insize - nextin))
	{
	    outsize = nextout + (insize - nextin);
	    outbuf = Realloc(outbuf, outsize * sizeof(Char));
	}

	while(nextin < insize)
	{
#if CHAR_SIZE == 8
	    c = inbuf[nextin++];

	    if(!is_xml_legal(c))
	    {
		sprintf(s->error_msg,
			"Illegal character <0x%x> at file offset %d",
			c, s->bytes_consumed + nextin - startin - 1);
		c = (unsigned int)-1;
	    }
#else
	    switch(enc)
	    {
	    case CE_ISO_10646_UCS_2B:
	    case CE_UTF_16B:
		if(nextin+2 > insize)
		    goto more_bytes;
		c = (inbuf[nextin] << 8) + inbuf[nextin+1];
		nextin += 2;
		goto surr_check;
	    case CE_ISO_10646_UCS_2L:
	    case CE_UTF_16L:
		if(nextin+2 > insize)
		    goto more_bytes;
		c = (inbuf[nextin+1] << 8) + inbuf[nextin];
		nextin += 2;
	    surr_check:
		if(c >= 0xdc00 && c <= 0xdfff) /* low (2nd) surrogate */
		{
		    if(expecting_low_surrogate)
			expecting_low_surrogate = 0;
		    else
		    {
			sprintf(s->error_msg,
				"Unexpected low surrogate <0x%x> "
				"at file offset %d",
				c, s->bytes_consumed + nextin - startin - 2);
			c = (unsigned int)-1;
		    }
		}
		else if(expecting_low_surrogate)
		{
		    sprintf(s->error_msg,
			    "Expected low surrogate but got <0x%x> "
			    "at file offset %d",
			    c, s->bytes_consumed + nextin - startin - 2);
		    c = (unsigned int)-1;
		}
		if(c >= 0xd800 && c <= 0xdbff) /* high (1st) surrogate */
		    expecting_low_surrogate = 1;
		break;
	    case CE_ISO_646:	/* should really check for >127 in this case */
	    case CE_ISO_8859_1:
	    case CE_unspecified_ascii_superset:
		c = inbuf[nextin++];
		break;
	    case CE_ISO_8859_2:
	    case CE_ISO_8859_3:
	    case CE_ISO_8859_4:
	    case CE_ISO_8859_5:
	    case CE_ISO_8859_6:
	    case CE_ISO_8859_7:
	    case CE_ISO_8859_8:
	    case CE_ISO_8859_9:
		c = to_unicode[inbuf[nextin++]];
		if(c == (unsigned int)-1)
		    sprintf(s->error_msg, 
			    "Illegal %s character <0x%x> at file offset %d",
			    CharacterEncodingName[enc], inbuf[nextin-1],
			    s->bytes_consumed + nextin - 1 - startin);
		break;
	    case CE_UTF_8:
		c = inbuf[nextin++];
		if(c <= 0x7f)
		    break;
		if(c <= 0xc0 || c >= 0xfe)
		{
		    sprintf(s->error_msg,
			   "Illegal UTF-8 start byte <0x%x> at file offset %d",
			    c, s->bytes_consumed + nextin - 1 - startin);
		    c = (unsigned int)-1;
		    break;
		}
		if(c <= 0xdf)
		{
		    c &= 0x1f;
		    more = 1;
		    mincode = 0x80;
		}
		else if(c <= 0xef)
		{
		    c &= 0x0f;
		    more = 2;
		    mincode = 0x800;
		}
		else if(c <= 0xf7)
		{
		    c &= 0x07;
		    more = 3;
		    mincode = 0x10000;
		}
		else if(c <= 0xfb)
		{
		    c &= 0x03;
		    more = 4;
		    mincode = 0x200000;
		}
		else
		{
		    c &= 0x01;
		    more = 5;
		    mincode = 0x4000000;
		}
		if(nextin+more > insize)
		{
		    nextin--;
		    goto more_bytes;
		}
		s->complicated_utf8_line = 1;
		s->cached_line_char = 0;
		s->cached_line_byte = 0;
		
		for(i=0; i<more; i++)
		{
		    int t = inbuf[nextin++];
		    if((t & 0xc0) != 0x80)
		    {
			c = (unsigned int)-1;
			sprintf(s->error_msg,
			      "Illegal UTF-8 byte %d <0x%x> at file offset %d",
				i+2, t, 
				s->bytes_consumed + nextin - 1 - startin);
			break;
		    }
		    c = (c << 6) + (t & 0x3f);
		}
#if 0
		if(c < mincode)
		{
		    sprintf(s->error_msg,
			    "Illegal (non-shortest) UTF-8 sequence for "
			    "character <0x%x> "
			    "immediately before file offset %d",
			    c, s->bytes_consumed + nextin - startin);
		    c = (unsigned int)-1;
		}
#endif
		break;
	    default:
		sprintf(s->error_msg,
			"read from entity with unsupported encoding!");
		c = (unsigned int)-1;
		break;
	    }

	    if((c > 0x110000 || (c < 0x10000 && !is_xml_legal(c))) &&
	       c != (unsigned int)-1)
		if(!(enc == CE_UTF_16L || enc == CE_UTF_16B) ||
		   c < 0xd800 || c > 0xdfff)
		    /* We treat the surrogates as legal because we didn't
		       combine them when translating from UTF-16.  XXX */
		{
		    sprintf(s->error_msg,
			    "Illegal character <0x%x> "
			    "immediately before file offset %d",
			    c, s->bytes_consumed + nextin - startin);
		    c = (unsigned int)-1;
		}
#endif
	    if(c == (unsigned int)-1)
	    {
		/* There was an error.  Put a SUB character (ctl-Z) in
		   as a marker, and end the line. */
		outbuf[nextout++] = BADCHAR;
		s->seen_error = 1;

		/* copied from linefeed case below */

		s->nextin = nextin;
		s->insize = insize;
		s->bytes_consumed += (nextin - startin);
		s->line = outbuf;
		s->line_alloc = outsize;
		s->line_length = nextout;
		return 0;
	    }

	    if(c == '\n' && ignore_linefeed)
	    {
		/* Ignore lf at start of line if last line ended with cr */
		ignore_linefeed = 0;
		s->bytes_before_current_line += (nextin - startin);
	    }		
	    else
	    {
		ignore_linefeed = 0;
		if(c == '\r')
		{
		    s->line_end_was_cr = 1;
		    c = '\n';
		}

#if CHAR_SIZE == 16
		if(c >= 0x10000)
		{
		    /* Use surrogates */
		    outbuf[nextout++] = ((c - 0x10000) >> 10) + 0xd800;
		    outbuf[nextout++] = ((c - 0x10000) & 0x3ff) + 0xdc00;
		}
		else
		    outbuf[nextout++] = c;
#else
		outbuf[nextout++] = c;
#endif

		if(c == '\n')
		{
		    s->nextin = nextin;
		    s->insize = insize;
		    s->bytes_consumed += (nextin - startin);
		    s->line = outbuf;
		    s->line_alloc = outsize;
		    s->line_length = nextout;
		    return 0;
		}
	    }
	}

#if CHAR_SIZE == 16
    more_bytes:
	/* Copy down any partial character */

	remaining = insize - nextin;
	for(i=0; i<remaining; i++)
	    inbuf[i] = inbuf[nextin + i];
#endif

	/* Get another block */

	s->bytes_consumed += (nextin - startin);

	insize = Readu(s->file16,
			inbuf+insize-nextin, sizeof(s->inbuf)-remaining);
	nextin = startin = 0;

	if(insize <= 0)
	{
		s->nextin = nextin;
		s->insize = 0;
		s->line = outbuf;
		s->line_alloc = outsize;
		s->line_length = nextout;
		return insize;
	}

	insize += remaining;
    }
}

void determine_character_encoding(InputSource s)
{
    Entity e = s->entity;
    int nread;
    unsigned char *b = (unsigned char *)s->inbuf;

    b[0] = b[1] = b[2] = b[3] = 0;

    while(s->insize < 4)
    {
	nread = Readu(s->file16, s->inbuf + s->insize, 4 - s->insize);
	if(nread == -1)
	    return;
	if(nread == 0)
	    break;
	s->insize += nread;
    }

#if 0
    if(b[0] == 0 && b[1] == 0 && b[2] == 0 && b[3] == '<')
	e->encoding = CE_ISO_10646_UCS_4B;
    else if(b[0] == '<' && b[1] == 0 && b[2] == 0 && b[3] == 0)
	e->encoding = CE_ISO_10646_UCS_4L;
    else
#endif
    if(b[0] == 0xef && b[1] == 0xbb && b[2] == 0xbf)
    {
	e->encoding = CE_UTF_8;
	s->nextin = 3;
    }
    else
    if(b[0] == 0xfe && b[1] == 0xff)
    {
	e->encoding = CE_UTF_16B;
	s->nextin = 2;
    }
    else if(b[0] == 0 && b[1] == '<' && b[2] == 0 && b[3] == '?')
	e->encoding = CE_UTF_16B;
    else if(b[0] == 0xff && b[1] == 0xfe)
    {
	e->encoding = CE_UTF_16L;
	s->nextin = 2;
    }
    else if(b[0] == '<' && b[1] == 0 && b[2] == '?' && b[3] == 0)
	e->encoding = CE_UTF_16L;
    else
    {
#if CHAR_SIZE == 8	
	e->encoding = CE_unspecified_ascii_superset;
#else
        e->encoding = CE_UTF_8;
#endif
    }
}

int get_with_fill(InputSource s)
{
    assert(!s->seen_eoe);

    if(get_translated_line(s) != 0)
    {
	/* It would be nice to pass this up to the parser, but we don't
	   know anything about parsers here! */
      ERR1("I/O error on stream <%s>, ignore further errors\n",
	      EntityDescription(s->entity));

	/* Restore old line and return EOE (is this the best thing to do?) */
	s->line_length = s->next;
	s->seen_eoe = 1;
	return XEOE;
    }

    if(s->line_length == 0)
    {
	/* Restore old line */
	s->line_length = s->next;
	s->seen_eoe = 1;
	return XEOE;
    }

    s->next = 0;

    if(s->not_read_yet)
	s->not_read_yet = 0;
    else
	s->line_number++;

    return s->line[s->next++];
}
