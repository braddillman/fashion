'''
Created on 2016-04-08

Generate different files to greet different worlds in different languages.

@author: bdillman
'''

import logging

from fashion.xformUtil import readModels
from fashion.xformUtil import generate

logging.debug("greetWorlds loaded")

def inputKinds():
    '''Inputs consumed by this xform'''
    return [ 'fashion_greetings', 'fashion_planets' ]

def outputKinds():
    '''Outputs generated by this xform'''
    return [ 'fashion_gen' ]

def police(fashion_planets=None, fashion_greetings=None):
    '''Validate input combinations.'''
    pass

def xform(fashion_planets=None, fashion_greetings=None):
    '''Generate many source files from 2 input models.'''
    logging.debug("greetWorlds xform running")
    
    planets   = readModels(fashion_planets)
    greetings = readModels(fashion_greetings)
    
    model = { 'planets'  : planets, 
              'greetings': greetings }
    
    generate(model, "fashion_template.txt", "fashion_greetWorld.txt")
