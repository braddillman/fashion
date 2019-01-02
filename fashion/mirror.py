'''
Created on 2018-12-29

Copyright (c) 2018 Bradford Dillman

@author: Bradford Dillman

Mirror a directory in a second directory.
'''

import os
import shutil

from fashion.util import cd

class Mirror(object):
    '''Mirror a directory in a second directory.'''

    def __init__(self, projDir, mirrorDir, force=False):
        '''Constructor.'''
        self.projDir = str(projDir)
        self.mirrorDir = str(mirrorDir)
        self.force = force

    def getRelativePath(self, filename):
        '''Get path of filename relative to projDir.'''
        return os.path.relpath(filename, self.projDir)

    def getMirrorPath(self, filename):
        '''Get path to mirror file given for a filename.'''
        return os.path.join(self.mirrorDir, self.getRelativePath(filename))

    def copyToMirror(self, filename):
        '''Copy a file to its mirror path.'''
        mirPath = self.getMirrorPath(filename)
        destDir = os.path.dirname(mirPath)
        os.makedirs(str(destDir), exist_ok=True)
        shutil.copy2(filename, mirPath)

    def isChanged(self, filename):
        '''Compare file to mirrored file, return True if filename is strictly newer.'''
        # Force overwrites by always returning no change.
        if self.force:
            return False
        mirFile = self.getMirrorPath(filename)
        if not os.path.exists(mirFile):
            return False
        if not os.path.exists(filename):
            return False
        mirrTime = os.stat(mirFile).st_mtime
        projTime = os.stat(filename).st_mtime
        return projTime > mirrTime
