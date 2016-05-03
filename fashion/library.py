'''
Created on 2016-04-29

Copyright (c) 2016 Bradford Dillman

@author: bdillman

Describe and manipulate collections of metadata for models, templates and 
xforms.
'''
import glob
import logging
import os.path

import yaml

from . import fashionPortfolio
from . import xforms



class cd:
    '''Context manager for changing the current working directory'''
    def __init__(self, newPath):
        self.newPath = os.path.expanduser(newPath)

    def __enter__(self):
        self.savedPath = os.getcwd()
        logging.debug("cd {0} -> {1}".format(self.savedPath, self.newPath))
        os.chdir(self.newPath)

    def __exit__(self, etype, value, traceback):
        logging.debug("cd {1} -> {0}".format(self.savedPath, self.newPath))
        os.chdir(self.savedPath)



class Library(object):
    '''A collection of globs describing metadata for models, templates and xforms.'''

    def __init__(self, filename):
        '''Constructor'''
        self.filename = filename
        self.globs = []
        
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
        with cd(os.path.dirname(self.filename)):
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
        with cd(os.path.dirname(self.filename)):
            for g in xformGlobs:
                recursive = g.get('recursive', True)
                for f in glob.glob(g['glob'], recursive=recursive):
                    xf = xforms.Xform(f)
                    if xf.exists():
                        xf.load()
                        xfList.extend([xf])
        return xfList
    
    def getTemplateDirectories(self):
        '''Get the directories which contain template files.'''
        templateGlobs = [g for g in self.globs if g['role'] == 2]
        # globs are specified relative to library file
        with cd(os.path.dirname(self.filename)):
            for g in templateGlobs:
                recursive = g.get('recursive', True)
                return [os.path.abspath(d) for d in glob.glob(g['glob'], recursive=recursive)
                                           if os.path.isdir(d) ]
                
            
        
        
    def load(self):
        '''Load a library description file.'''
        with open(self.filename, "r") as stream:
            self.globs = yaml.load(stream)
            
    def save(self):
        '''Save a library description file.'''
        with open(self.filename, "a") as stream:
            yaml.dump(self.globs, stream, default_flow_style = False)
