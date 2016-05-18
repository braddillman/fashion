'''
Created on 2016-04-29

Copyright (c) 2016 Bradford Dillman

@author: bdillman

Describe and manipulate collections of metadata for models, templates and 
xforms.
'''

import fnmatch
import glob
import logging
import os.path

import ruamel.yaml

from . import fashionPortfolio
from . import xforms
from . import xformUtil



class Library(object):
    '''A collection of globs describing metadata for models, templates and xforms.'''

    def __init__(self, filename):
        '''Constructor'''
        self.filename = filename
        self.globs = []
        
    def matchGlobs(self, filename):
        return [g for g in self.globs
                  for path in glob.glob(g['glob'], recursive=g['recursive'])
                  if fnmatch.fnmatch(filename, path)]
        
    def addFile(self, filename, role, kind='fashion_unknown', fileFormat='yaml'):
        matchedGlobs = self.matchGlobs(filename)
        for g in matchedGlobs:
            raise("conflicting glob: {0}".format(g))
        else:
            self.addGlob(filename, role, kind, fileFormat, recursive=False)
            return True
        
    def addGlob(self, glob, role, kind='fashion_unknown', fileFormat='yaml', recursive=True):
        '''Add another glob to this library'''
        g = { 'glob': glob,
              'role': role,
              'kind': kind,
              'recursive': recursive,
              'fileFormat': fileFormat }
        self.globs.extend([g])
        
    def importModels(self):
        '''Import all models in this library into the fashion database.'''
        modelGlobs = [g for g in self.globs if g['role'] == 3]
        # globs are specified relative to library file
        with xformUtil.cd(os.path.dirname(self.filename)):
            for g in modelGlobs:
                recursive = g.get('recursive', True)
                for f in glob.glob(g['glob'], recursive=recursive):
                    fashionPortfolio.importFile(role=g['role'], 
                                                filename=os.path.abspath(f), 
                                                kind=g['kind'],
                                                fileFormat=g['fileFormat'])
        
    def loadXforms(self):
        '''Load all xforms in this library, returned as list.'''
        xfList = []
        xformGlobs = [g for g in self.globs if g['role'] == 4]
        # globs are specified relative to library file
        with xformUtil.cd(os.path.dirname(self.filename)):
            for g in xformGlobs:
                recursive = g.get('recursive', True)
                for f in glob.glob(g['glob'], recursive=recursive):
                    xf = xforms.Xform(f)
                    if xf.exists() and not os.path.isdir(f):
                        xf.load()
                        xfList.extend([xf])
        return xfList
    
    def getDirectories(self, role):
        '''Get the directories which contain model files.'''
        globs = [g for g in self.globs if g['role'] == role]
        # globs are specified relative to library file
        with xformUtil.cd(os.path.dirname(self.filename)):
            dirs = [os.path.abspath(d) for g in globs
                                       for d in glob.glob(g['glob'], recursive=g.get('recursive', True))
                                       if os.path.isdir(d) ]
            logging.debug("getDirectories({0})={1}".format(role, dirs))
            return dirs
        
    def load(self):
        '''Load a library description file.'''
        with open(self.filename, "r") as stream:
            self.globs = ruamel.yaml.load(stream)
            
    def save(self):
        '''Save a library description file.'''
        with open(self.filename, "w") as stream:
            ruamel.yaml.dump(self.globs, stream, default_flow_style = False)
