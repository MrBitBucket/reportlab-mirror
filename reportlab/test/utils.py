"""Utilities for testing Python packages.
"""


import sys, os, string, fnmatch, copy

from reportlab.test import unittest


# Helper functions.

def getCVSEntries(folder, files=1, folders=0):
    """Returns a list of filenames as listed in the CVS/Entries file.

    'folder' is the folder that should contain the CVS subfolder.
    If there is no such subfolder an empty list is returned.
    'files' is a boolean; 1 and 0 means to return files or not.
    'folders' is a boolean; 1 and 0 means to return folders or not.
    """
    
    join = os.path.join
    split = string.split

    # If CVS subfolder doesn't exist return empty list.
    try:
        f = open(join(folder, 'CVS', 'Entries'))
    except IOError:
        return []

    # Return names of files and/or folders in CVS/Entries files. 
    allEntries = []
    for line in f.readlines():
        if folders and line[0] == 'D' \
           or files and line[0] != 'D':
            entry = split(line, '/')[1]
            if entry:
                allEntries.append(join(folder, entry))

    return allEntries


# This class as suggested by /F with an additional hook
# to be able to filter filenames.

class GlobDirectoryWalker:
    "A forward iterator that traverses a directory tree."

    def __init__(self, directory, pattern='*'):
        self.stack = [directory]
        self.pattern = pattern
        self.files = []
        self.index = 0


    def __getitem__(self, index):
        while 1:
            try:
                file = self.files[self.index]
                self.index = self.index + 1
            except IndexError:
                # pop next directory from stack
                self.directory = self.stack.pop()
                self.files = os.listdir(self.directory)
                # now call the hook
                self.files = self.filterFiles(self.directory, self.files)
                self.index = 0
            else:
                # got a filename
                fullname = os.path.join(self.directory, file)
                if os.path.isdir(fullname) and not os.path.islink(fullname):
                    self.stack.append(fullname)
                if fnmatch.fnmatch(file, self.pattern):
                    return fullname


    def filterFiles(self, folder, files):
        "Filter hook, overwrite in subclasses as needed."

        return files

    

class CVSGlobDirectoryWalker(GlobDirectoryWalker):
    "An directory tree iterator that checks for CVS data."

    def filterFiles(self, folder, files):
        """Filters files not listed in CVS subfolder.

        This will look in the CVS subfolder of 'folder' for
        a file named 'Entries' and filter all elements from
        the 'files' list that are not listed in 'Entries'.
        """

        join = os.path.join
        cvsFiles = getCVSEntries(folder)
        if cvsFiles:
            indicesToDelete = []
            for i in xrange(len(files)):
                f = files[i]
                if join(folder, f) not in cvsFiles:
                    indicesToDelete.append(i)
            indicesToDelete.reverse()
            for i in indicesToDelete:
                del files[i]

        return files


# An experimental untested base class with additional 'security'.

class SecureTestCase(unittest.TestCase):
    """Secure testing base class with additional pre- and postconditions.

    We try to ensure that each test leaves the environment it has
    found unchanged after the test is performed, successful or not.

    Currently we restore sys.path and the working directory, but more
    of this could be added easily, like removing temporary files or
    similar things.

    Use this as a base class replacing unittest.TestCase and call
    these methods in subclassed versions before doing your own
    business!
    """
    
    def setUp(self):
        "Remember sys.path and current working directory."

        self._initialPath = copy.copy(sys.path)
        self._initialWorkDir = os.getcwd()

        
    def tearDown(self):
        "Restore previous sys.path and working directory."

        sys.path = self._initialPath
        os.chdir(self._initialWorkDir)
    