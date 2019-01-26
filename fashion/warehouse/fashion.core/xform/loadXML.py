'''
Created on 2018-12-21

Copyright (c) 2018 Bradford Dillman

Load models from JSON files.
'''

import codecs
import glob
import json
import logging
import os

import xmltodict

from munch import munchify

# Module level code is executed when this file is loaded.
# cwd is where segment file was loaded.


def init(moduleConfig, codeRegistry, verbose=False, tags=None):
    '''
    Create 1 LoadXML object for each file.
    cwd is where segment file was loaded.
    '''
    param = munchify(moduleConfig.parameters)
    if isinstance(param.filename, list):
        filenames = param.filename
    else:
        filenames = glob.glob(param.filename)
    del param.filename
    for fn in filenames:
        codeRegistry.addXformObject(LoadXML(moduleConfig.moduleName, param, fn))


class LoadXML(object):
    '''
    Generate output by merging a model into a template to produce a file.
    '''

    def __init__(self, moduleName, cfg, filename):
        '''
        Constructor.
        cwd is where segment file was loaded.
        '''
        self.version = "1.0.0"
        self.templatePath = []
        self.config = cfg
        self.filename = os.path.abspath(filename)
        self.name = moduleName + "::" + self.filename
        self.tags = ["input"]
        self.inputKinds = []
        self.outputKinds = [ self.config.kind, 'fashion.core.input.file' ]

    def execute(self, codeRegistry, verbose=False, tags=None):
        '''
        Load the JSON file and insert it into the model database.
        cwd is project root.
        '''
        mdb = codeRegistry.getService('fashion.prime.modelAccess')
        with codecs.open(str(self.filename), 'r', 'utf_8', ) as fd:
            obj = munchify(xmltodict.parse(fd.read()))
            mdb.insert(self.config.kind, obj)
            mdb.inputFile(str(self.filename))
