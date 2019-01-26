'''
Created on 2018-12-19

Copyright (c) 2018 Bradford Dillman

@author: bdillman

Describe and manipulate xforms, which are python3 modules with specific
requirements.
'''

import importlib.util
import inspect
import logging
import os
import traceback

from packaging.specifiers import SpecifierSet
from packaging.version import Version


def matchTags(requestedTags, moduleTags):
    '''Check if module tags include requested tags.'''
    if requestedTags is None:
        return True
    req = set(requestedTags)
    if len(req) == 0 and len(moduleTags) == 0:
        return True
    has = set(moduleTags)
    inter = list(req & has)
    return len(inter) == len(req)


class XformModule():
    '''Represents a specific transform operation.'''

    def __init__(self, xfModDescr):
        '''Initialize a transform file a Python module filename.'''
        self.properties = xfModDescr
        self.isLoaded = False

    def loadModuleCode(self):
        '''
        Load the python module for this transform.
        :return: True if loaded
        '''
        if not self.isLoaded:
            try:
                self.spec = importlib.util.spec_from_file_location(
                    self.properties.moduleName, self.properties.filename)
                self.mod = importlib.util.module_from_spec(self.spec)
                self.spec.loader.exec_module(self.mod)
                self.isLoaded = True
            except FileNotFoundError:
                logging.error("FileNotFoundError: module {0} file {1}".format(
                    self.properties.moduleName, self.properties.filename))
            except AttributeError:
                logging.error("Failed to load module {0} from file {1}".format(
                    self.properties.moduleName, self.properties.filename))
        return self.isLoaded

    def init(self, xfModConfig, codeRegistry, tags=None):
        '''
        Initialize an xform module and get the xform objects.
        :return: a list of xform objects.
        '''
        if not self.isLoaded:
            logging.error("Can't init unloaded module: {0}".format(
                self.properties.moduleName))
        if matchTags(tags, xfModConfig.tags):
            try:
                self.mod.init(xfModConfig, codeRegistry, tags)
            except:
                logging.error("aborting, xform module init error: {0}".format(
                    xfModConfig.moduleName))
                traceback.print_exc()
                # TODO: add trace and debug info into mdb context
                # or insert object into mdb
