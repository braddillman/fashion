'''
Created on 2018-12-29

Copyright (c) 2018 Bradford Dillman

@author: Bradford Dillman

Mirror a directory in a second directory.
'''

import shutil

from pathlib import Path, PurePath

from fashion.util import cd

class Mirror(object):
    '''Mirror a directory in a second directory.'''

    def __init__(self, projDir, mirrorDir, force=False):
        '''Constructor.'''
        self.projDir = projDir
        self.mirrorDir = mirrorDir
        self.force = force

    def getRelativePath(self, filename):
        '''Get path of filename relative to projDir.'''
        return filename.relative_to(self.projDir)

    def getMirrorPath(self, filename):
        '''Get path to mirror file given for a filename.'''
        return PurePath.joinpath(self.mirrorDir, self.getRelativePath(filename.absolute()))

    def copyToMirror(self, filename):
        '''Copy a file to its mirror path.'''
        mirPath = self.getMirrorPath(filename)
        destDir = mirPath.parent
        destDir.mkdir(parents=True, exist_ok=True)
        shutil.copy2(str(filename), str(mirPath))

    def isChanged(self, filename):
        '''Compare file to mirrored file, return True if filename is strictly newer.'''
        # Force overwrites by always returning no change.
        if self.force:
            return False
        mirFile = self.getMirrorPath(filename)
        if not mirFile.exists():
            return False
        if not filename.exists():
            return False
        mirrTime = mirFile.stat().st_mtime
        projTime = filename.stat().st_mtime
        return projTime > mirrTime
