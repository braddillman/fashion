'''
Created on 2016-04-29

Copyright (c) 2016 Bradford Dillman

@author: bdillman

Utilities used by user xforms.
'''

from . import fashionPortfolio



def readModels(modelFashioFiles):
    '''Read a list of models.'''
    return [p for f in modelFashioFiles for p in f.loadFile()]
    
def writeModel(model=None, kind=None, fileFormat='yaml', filename=None):
    '''Write a single model.'''
    fashionPortfolio.createModel(model, kind, fileFormat, filename)

def generate(model=None, templateFile=None, targetFile=None):
    '''Write a generation model for a single file.'''
    genModel = { 'model'       : model,
                 'templateFile': templateFile,
                 'targetFile'  : targetFile }    
    writeModel(genModel, 'fashion_gen')
