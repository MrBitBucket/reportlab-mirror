#define SOCKETS_IMPLEMENTED

#define STD_API
#define XML_API
#define WIN_IMP
#define EXPRT
#ifdef _WIN32
#	ifndef WIN32
#		define WIN32
#	endif
#endif

void *Malloc(int bytes);
void *Realloc(void *mem, int bytes);
void Free(void *mem);
