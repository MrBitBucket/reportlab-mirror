"""Get useful information from live Python objects.

This module encapsulates the interface provided by the internal special
attributes (func_*, co_*, im_*, tb_*, etc.) in a friendlier fashion.
It also provides some help for examining source code and class layout.

Here are some of the useful functions provided by this module:

    getdoc(), getcomments() - get documentation on an object
    getclasstree() - arrange classes so as to represent their hierarchy
    getfile(), getsourcefile(), getsource() - find an object's source code
    getargspec(), getargvalues() - get info about function arguments
    formatargspec(), formatargvalues() - format an argument spec
    stack(), trace() - get info about frames on the stack or in a traceback
"""

# This module is in the public domain.  No warranties.

__version__ = 'Ka-Ping Yee <ping@lfw.org>, 1 Jan 2001'

import sys, types, string, dis, imp

# ----------------------------------------------------------- type-checking
def ismodule(object):
    """Return true if the object is a module.

    Module objects provide these attributes:
        __doc__         documentation string
        __file__        filename (missing for built-in modules)"""
    return type(object) is types.ModuleType

def isclass(object):
    """Return true if the object is a class.

    Class objects provide these attributes:
        __doc__         documentation string
        __module__      name of module in which this class was defined"""
    return type(object) is types.ClassType

def ismethod(object):
    """Return true if the object is an instance method.

    Instance method objects provide these attributes:
        __doc__         documentation string
        __name__        name with which this method was defined
        im_class        class object in which this method belongs
        im_func         function object containing implementation of method
        im_self         instance to which this method is bound, or None"""
    return type(object) is types.MethodType

def isfunction(object):
    """Return true if the object is a user-defined function.

    Function objects provide these attributes:
        __doc__         documentation string
        __name__        name with which this function was defined
        func_code       code object containing compiled function bytecode
        func_defaults   tuple of any default values for arguments
        func_doc        (same as __doc__)
        func_globals    global namespace in which this function was defined
        func_name       (same as __name__)"""
    return type(object) in [types.FunctionType, types.LambdaType]

def istraceback(object):
    """Return true if the object is a traceback.

    Traceback objects provide these attributes:
        tb_frame        frame object at this level
        tb_lasti        index of last attempted instruction in bytecode
        tb_lineno       current line number in Python source code
        tb_next         next inner traceback object (called by this level)"""
    return type(object) is types.TracebackType

def isframe(object):
    """Return true if the object is a frame object.

    Frame objects provide these attributes:
        f_back          next outer frame object (this frame's caller)
        f_builtins      built-in namespace seen by this frame
        f_code          code object being executed in this frame
        f_exc_traceback traceback if raised in this frame, or None
        f_exc_type      exception type if raised in this frame, or None
        f_exc_value     exception value if raised in this frame, or None
        f_globals       global namespace seen by this frame
        f_lasti         index of last attempted instruction in bytecode
        f_lineno        current line number in Python source code
        f_locals        local namespace seen by this frame
        f_restricted    0 or 1 if frame is in restricted execution mode
        f_trace         tracing function for this frame, or None"""
    return type(object) is types.FrameType

def iscode(object):
    """Return true if the object is a code object.

    Code objects provide these attributes:
        co_argcount     number of arguments (not including * or ** args)
        co_code         string of raw compiled bytecode
        co_consts       tuple of constants used in the bytecode
        co_filename     name of file in which this code object was created
        co_firstlineno  number of first line in Python source code
        co_flags        bitmap: 1=optimized | 2=newlocals | 4=*arg | 8=**arg
        co_lnotab       encoded mapping of line numbers to bytecode indices
        co_name         name with which this code object was defined
        co_names        tuple of names of local variables
        co_nlocals      number of local variables
        co_stacksize    virtual machine stack space required
        co_varnames     tuple of names of arguments and local variables"""
    return type(object) is types.CodeType

def isbuiltin(object):
    """Return true if the object is a built-in function or method.

    Built-in functions and methods provide these attributes:
        __doc__         documentation string
        __name__        original name of this function or method
        __self__        instance to which a method is bound, or None"""
    return type(object) in [types.BuiltinFunctionType,
                            types.BuiltinMethodType]

def isroutine(object):
    """Return true if the object is any kind of function or method."""
    return type(object) in [types.FunctionType, types.LambdaType,
                            types.MethodType, types.BuiltinFunctionType,
                            types.BuiltinMethodType]

def getmembers(object, predicate=None):
    """Return all members of an object as (key, value) pairs sorted by key.
    Optionally, only return members that satisfy a given predicate."""
    results = []
    for key in dir(object):
        value = getattr(object, key)
        if not predicate or predicate(value):
            results.append((key, value))
    results.sort()
    return results

# -------------------------------------------------- source code extraction
def indentsize(line):
    """Return the indent size, in spaces, at the start of a line of text."""
    expline = string.expandtabs(line)
    return len(expline) - len(string.lstrip(expline))

def getdoc(object):
    """Get the documentation string for an object.

    All tabs are expanded to spaces.  To clean up docstrings that are
    indented to line up with blocks of code, any whitespace than can be
    uniformly removed from the second line onwards is removed."""
    if hasattr(object, '__doc__') and object.__doc__:
        lines = string.split(string.expandtabs(object.__doc__), '\n')
        margin = None
        for line in lines[1:]:
            content = len(string.lstrip(line))
            if not content: continue
            indent = len(line) - content
            if margin is None: margin = indent
            else: margin = min(margin, indent)
        if margin is not None:
            for i in range(1, len(lines)): lines[i] = lines[i][margin:]
        return string.join(lines, '\n')

def getfile(object):
    """Try to guess which (text or binary) file an object was defined in."""
    if ismodule(object):
        if hasattr(object, '__file__'):
            return object.__file__
        raise TypeError, 'arg is a built-in module'
    if isclass(object):
        object = sys.modules[object.__module__]
        if hasattr(object, '__file__'):
            return object.__file__
        raise TypeError, 'arg is a built-in class'
    if ismethod(object):
        object = object.im_func
    if isfunction(object):
        object = object.func_code
    if istraceback(object):
        object = object.tb_frame
    if isframe(object):
        object = object.f_code
    if iscode(object):
        return object.co_filename
    raise TypeError, 'arg is not a module, class, method, ' \
                     'function, traceback, frame, or code object'

modulesbyfile = {}

def getmodule(object):
    """Try to guess which module an object was defined in."""
    if isclass(object):
        return sys.modules[object.__module__]
    try:
        file = getsourcefile(object)
    except TypeError:
        return None
    if modulesbyfile.has_key(file):
        return sys.modules[modulesbyfile[file]]
    for module in sys.modules.values():
        if hasattr(module, '__file__'):
            modulesbyfile[getsourcefile(module)] = module.__name__
    if modulesbyfile.has_key(file):
        return sys.modules[modulesbyfile[file]]
    main = sys.modules['__main__']
    try:
        mainobject = getattr(main, object.__name__)
        if mainobject is object: return main
    except AttributeError: pass
    builtin = sys.modules['__builtin__']
    try:
        builtinobject = getattr(builtin, object.__name__)
        if builtinobject is object: return builtin
    except AttributeError: pass

def getsourcefile(object):
    """Try to guess which Python source file an object was defined in."""
    filename = getfile(object)
    if filename[-4:] == '.pyc':
        filename = filename[:-4] + '.py'
    return filename

def findsource(object):
    """Find the first line of code corresponding to a given module, class,
    method, function, traceback, frame, or code object; return the entire
    contents of the source file and the starting line number.  An IOError
    exception is raised if the source code cannot be retrieved."""
    try:
        file = open(getsourcefile(object))
        lines = file.readlines()
        file.close()
    except (TypeError, IOError):
        raise IOError, 'could not get source code'

    if ismodule(object):
        return lines, 0

    if isclass(object):
        name = object.__name__
        matches = (['class', name], ['class', name + ':'])
        for i in range(len(lines)):
            if string.split(lines[i])[:2] in matches:
                return lines, i
        else: raise IOError, 'could not find class definition'

    if ismethod(object):
        object = object.im_func
    if isfunction(object):
        object = object.func_code
    if istraceback(object):
        object = object.tb_frame
    if isframe(object):
        object = object.f_code
    if iscode(object):
        try:
            lnum = object.co_firstlineno - 1
        except AttributeError:
            raise IOError, 'could not find function definition'
        else:
            while lnum > 0:
                if string.split(lines[lnum])[:1] == ['def']: break
                lnum = lnum - 1
            return lines, lnum

def getcomments(object):
    """Get lines of comments immediately preceding an object's source code."""
    try: lines, lnum = findsource(object)
    except: return None

    if ismodule(object):
        # Look for a comment block at the top of the file.
        start = 0
        if lines[0][:2] == '#!': start = 1
        while start < len(lines) and string.strip(lines[start]) in ['', '#']:
            start = start + 1
        if lines[start][:1] == '#':
            comments = []
            end = start
            while end < len(lines) and lines[end][:1] == '#':
                comments.append(string.expandtabs(lines[end]))
                end = end + 1
            return string.join(comments, '')

    # Look for a preceding block of comments at the same indentation.
    elif lnum > 0:
        indent = indentsize(lines[lnum])
        end = lnum - 1
        if string.strip(lines[end]) == '':
            while end >= 0 and string.strip(lines[end]) == '':
                end = end - 1
        else:
            while string.lstrip(lines[end])[:1] != '#' and \
                indentsize(lines[end]) == indent:
                end = end - 1
        if end >= 0 and string.lstrip(lines[end])[:1] == '#' and \
            indentsize(lines[end]) == indent:
            comments = [string.lstrip(string.expandtabs(lines[end]))]
            if end > 0:
                end = end - 1
                comment = string.lstrip(string.expandtabs(lines[end]))
                while comment[:1] == '#' and indentsize(lines[end]) == indent:
                    comments[:0] = [comment]
                    end = end - 1
                    if end < 0: break
                    comment = string.lstrip(string.expandtabs(lines[end]))
            return string.join(comments, '')

import tokenize

class ListReader:
    """Provide a readline() method to return lines from a list of strings."""
    def __init__(self, lines):
        self.lines = lines
        self.index = 0

    def readline(self):
        i = self.index
        if i < len(self.lines):
            self.index = i + 1
            return self.lines[i]
        else: return ''

class EndOfBlock(Exception): pass

class BlockFinder:
    """Provide a tokeneater() method to detect the end of a code block."""
    def __init__(self):
        self.indent = 0
        self.started = 0
        self.last = 0

    def tokeneater(self, type, token, (srow, scol), (erow, ecol), line):
        if not self.started:
            if type == tokenize.NAME: self.started = 1
        elif type == tokenize.NEWLINE:
            self.last = srow
        elif type == tokenize.INDENT:
            self.indent = self.indent + 1
        elif type == tokenize.DEDENT:
            self.indent = self.indent - 1
            if self.indent == 0: raise EndOfBlock, self.last

def getblock(lines):
    """Extract the block of code at the top of the given list of lines."""
    try:
        tokenize.tokenize(ListReader(lines).readline, BlockFinder().tokeneater)
    except EndOfBlock, eob:
        return lines[:eob.args[0]]

def getsourcelines(object):
    """Try to get the source code corresponding to a module, class, method,
    function, traceback, frame, or code object.  Return a list of lines and
    the line number of the first line, or raise an IOError exception if the
    source code cannot be retrieved."""
    lines, lnum = findsource(object)

    if ismodule(object): return lines, 0
    else: return getblock(lines[lnum:]), lnum

def getsource(object):
    """Try to get the source code corresponding to a module, class, method,
    function, traceback, frame, or code object.  Return a string, or raise
    an IOError exception if the source code cannot be retrieved."""
    lines, lnum = getsourcelines(object)
    return string.join(lines, '')

# --------------------------------------------------- class tree extraction
def walktree(classes, children, parent):
    """Recursive helper function for getclasstree()."""
    results = []
    classes.sort(lambda a, b: cmp(a.__name__, b.__name__))
    for c in classes:
        results.append((c, c.__bases__))
        if children.has_key(c):
            results.append(walktree(children[c], children, c))
    return results

def getclasstree(classes, unique=0):
    """Arrange the given list of classes into a hierarchy of nested lists.
    Where a nested list appears, it contains classes derived from the class
    whose entry immediately precedes the list.  Each entry is a 2-tuple
    containing a class and a tuple of its base classes.  If the 'unique'
    argument is true, exactly one entry appears in the returned structure
    for each class in the given list.  Otherwise, classes that multiply
    inherit, and their descendants, will appear multiple times."""
    children = {}
    roots = []
    for c in classes:
        if c.__bases__:
            for parent in c.__bases__:
                if not children.has_key(parent):
                    children[parent] = []
                children[parent].append(c)
                if unique and parent in classes: break
        elif c not in roots:
            roots.append(c)
    for parent in children.keys():
        if parent not in classes:
            roots.append(parent)
    return walktree(roots, children, None)

# ------------------------------------------------ argument list extraction
# These constants are from Python's compile.h.
CO_OPTIMIZED, CO_NEWLOCALS, CO_VARARGS, CO_VARKEYWORDS = 1, 2, 4, 8

def getargs(co):
    """Get information about the arguments accepted by a code object.
    Three things are returned: (args, varargs, varkw), where 'args' is
    a list of argument names (possibly containing nested lists), and
    'varargs' and 'varkw' are the names of the * and ** arguments or None."""
    if not iscode(co): raise TypeError, 'arg is not a code object'

    code = co.co_code
    nargs = co.co_argcount
    names = co.co_varnames
    args = list(names[:nargs])
    step = 0

    # The following acrobatics are for anonymous (tuple) arguments.
    for i in range(nargs):
        if args[i][:1] in ['', '.']:
            stack, remain, count = [], [], []
            while step < len(code):
                op = ord(code[step])
                step = step + 1
                if op >= dis.HAVE_ARGUMENT:
                    opname = dis.opname[op]
                    value = ord(code[step]) + ord(code[step+1])*256
                    step = step + 2
                    if opname in ['UNPACK_TUPLE', 'UNPACK_SEQUENCE']:
                        remain.append(value)
                        count.append(value)
                    elif opname == 'STORE_FAST':
                        stack.append(names[value])
                        remain[-1] = remain[-1] - 1
                        while remain[-1] == 0:
                            remain.pop()
                            size = count.pop()
                            stack[-size:] = [stack[-size:]]
                            if not remain: break
                            remain[-1] = remain[-1] - 1
                        if not remain: break
            args[i] = stack[0]

    varargs = None
    if co.co_flags & CO_VARARGS:
        varargs = co.co_varnames[nargs]
        nargs = nargs + 1
    varkw = None
    if co.co_flags & CO_VARKEYWORDS:
        varkw = co.co_varnames[nargs]
    return args, varargs, varkw

def getargspec(func):
    """Get the names and default values of a function's arguments.
    A tuple of four things is returned: (args, varargs, varkw, defaults).
    'args' is a list of the argument names (it may contain nested lists).
    'varargs' and 'varkw' are the names of the * and ** arguments or None.
    'defaults' is an n-tuple of the default values of the last n arguments."""
    if not isfunction(func): raise TypeError, 'arg is not a Python function'
    args, varargs, varkw = getargs(func.func_code)
    return args, varargs, varkw, func.func_defaults

def getargvalues(frame):
    """Get information about arguments passed into a particular frame.
    A tuple of four things is returned: (args, varargs, varkw, locals).
    'args' is a list of the argument names (it may contain nested lists).
    'varargs' and 'varkw' are the names of the * and ** arguments or None.
    'locals' is the locals dictionary of the given frame."""
    args, varargs, varkw = getargs(frame.f_code)
    return args, varargs, varkw, frame.f_locals

def strseq(object, convert=str):
    """Recursively walk a sequence, stringifying each element."""
    if type(object) in [types.ListType, types.TupleType]:
        results = map(lambda o, c=convert: strseq(o, c), object)
        if len(results) == 1:
            return '(' + results[0] + ',)'
        else:
            return '(' + string.join(results, ', ') + ')'
    else:
        return convert(object)

def formatargspec(args, varargs=None, varkw=None, defaults=None,
                  argformat=str, defaultformat=lambda x: '=' + repr(x),
                  varargsformat=lambda name: '*' + name,
                  varkwformat=lambda name: '**' + name):
    """Format a pretty argument spec from the 4-tuple returned by getargspec.
    The arguments are (args, varargs, varkw, defaults)."""
    specs = []
    if defaults:
        firstdefault = len(args) - len(defaults)
    for i in range(len(args)):
        spec = strseq(args[i], argformat)
        if defaults and i >= firstdefault:
            spec = spec + defaultformat(defaults[i - firstdefault])
        specs.append(spec)
    if varargs:
        specs.append(varargsformat(varargs))
    if varkw:
        specs.append(varkwformat(varkw))
    return '(' + string.join(specs, ', ') + ')'

def formatargvalues(args, varargs, varkw, locals,
                    argformat=str, valueformat=repr,
                    varargsformat=lambda name: '*' + name,
                    varkwformat=lambda name: '**' + name):
    """Format a pretty argument spec from the 4-tuple returned by getargvalues.
    The arguments are (args, varargs, varkw, locals)."""
    def convert(name, locals=locals,
                argformat=argformat, valueformat=valueformat):
        return argformat(name) + '=' + valueformat(locals[name])
    specs = []
    for i in range(len(args)):
        specs.append(strseq(args[i], convert))
    if varargs:
        specs.append(varargsformat(varargs) + '=' +
                     valueformat(locals[varargs]))
    if varkw:   
        specs.append(varkwformat(varkw) + '=' + valueformat(locals[varkw]))
    return '(' + string.join(specs, ', ') + ')'

# -------------------------------------------------- stack frame extraction
def getframe(frame, context=1):
    """For a given frame or traceback object, return the filename, line
    number, function name, a given number of lines of context from the
    source code, and the index of the line within the lines of context."""
    if istraceback(frame):
        frame = frame.tb_frame
    if not isframe(frame):
        raise TypeError, 'arg is not a frame or traceback object'

    filename = getsourcefile(frame)
    if context > 0:
        start = frame.f_lineno - 1 - context/2
        try:
            lines, lnum = findsource(frame)
            start = max(start, 1)
            start = min(start, len(lines) - context)
            lines = lines[start:start+context]
            index = frame.f_lineno - 1 - start
        except:
            lines = index = None
    else:
        lines = index = None

    return (filename, frame.f_lineno, frame.f_code.co_name, lines, index)

def getouterframes(frame, context=1):
    """Get a list of records for a frame and all higher (calling) frames.
    Each record contains a frame object, filename, line number, function
    name, the requested amount of context, and index within the context."""
    framelist = []
    while frame:
        framelist.append((frame,) + getframe(frame, context))
        frame = frame.f_back
    return framelist

def getinnerframes(traceback, context=1):
    """Get a list of records for a traceback's frame and all lower frames.
    Each record contains a frame object, filename, line number, function
    name, the requested amount of context, and index within the context."""
    traceback = traceback.tb_next
    framelist = []
    while traceback:
        framelist.append((traceback.tb_frame,) + getframe(traceback, context))
        traceback = traceback.tb_next
    return framelist

def currentframe():
    """Return the frame object for the caller's stack frame."""
    try:
        raise 'catch me'
    except:
        return sys.exc_traceback.tb_frame.f_back

if hasattr(sys, '_getframe'): currentframe = sys._getframe

def stack(context=1):
    """Return a list of records for the stack above the caller's frame."""
    return getouterframes(currentframe().f_back, context)

def trace(context=1):
    """Return a list of records for the stack below the current exception.""" 
    return getinnerframes(sys.exc_traceback, context)
