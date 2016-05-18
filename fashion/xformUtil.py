'''
Created on 2016-04-29

Copyright (c) 2016 Bradford Dillman

@author: bdillman

Utilities used by user xforms.
'''

import logging
import os.path

from . import fashionPortfolio

#
# Name of current executing xform
#
current_xform_name = ""

#
# Set of current output kinds
#
current_output_kinds = set()

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



def readModels(modelFashionFiles, flatten=False):
    '''Read a list of models.'''
    modelList = [f.loadFile() for f in modelFashionFiles]
    if flatten:
        models = [item for sublist in modelList for item in sublist]
    else:
        models = modelList
    return models
    
def writeModel(model=None, kind=None, fileFormat='yaml', filename=None):
    '''Write a single model.'''
    if kind not in current_output_kinds:
        logging.warn("xform {0} didn't declare output kind: {1}".format(current_xform_name, current_output_kinds))
    fashionPortfolio.createModel(model, kind, fileFormat, filename)

def generate(model=None, templateFile=None, targetFile=None):
    '''Write a generation model for a single file.'''
    genModel = { 'model'       : model,
                 'templateFile': templateFile,
                 'targetFile'  : targetFile }    
    writeModel(genModel, 'fashion_gen')
