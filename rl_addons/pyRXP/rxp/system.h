#ifndef _RXP_SYSTEM_H
#define _RXP_SYSTEM_H
#define SOCKETS_IMPLEMENTED

#define STD_API
#define XML_API
#define WIN_IMP
#define EXPRT
#ifdef _WIN32
#	ifndef WIN32
#		define WIN32
#	endif
#	ifndef PY_LONG_LONG
#		define PY_LONG_LONG __int64
#	endif
#endif
#ifndef PY_LONG_LONG
#	if defined(__GNUC__)
#		define PY_LONG_LONG long long
#	endif
#endif

void *Malloc(int bytes);
void *Realloc(void *mem, int bytes);
void Free(void *mem);
void CFree(void *mem);
#endif
