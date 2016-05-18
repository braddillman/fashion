'''
Created on 2016-05-01

Copyright (c) 2016 Bradford Dillman

@author: bdillman

Adapt mako templates for use by fashion application.
'''

import logging
import os.path
import pathlib
import shutil

from mako.lookup import TemplateLookup



#
# The list of directories used to lookup template files.
#
templateLookup = None

#
# Where to keep backups of the generated files.
# This is used to check for modification before overwrite.
#
mirrorDirectory = None

#
# The root project directory. All generation must be under this.
#
projectDirectory = None

#
# True if we force an overwrite (default to False).
#
overwrite = False


def setDirectories(projDir=None, mirrorDir=None, templateDirs=None, moduleDir=None):
    '''Set the directories where templates are found, for later lookup.'''
    global templateLookup
    global mirrorDirectory
    global projectDirectory
    projectDirectory = projDir
    mirrorDirectory = mirrorDir
    logging.debug(str(templateDirs))
    templateLookup = TemplateLookup(templateDirs, module_directory=moduleDir)

def generateFile(model=None, templateFile=None, targetFile=None, **kwargs):
    '''Generate a file using a model and a template.'''
    logging.debug("generateFile(model={0}, templateFile={1}, targetFile={2}".format(model, templateFile, targetFile))
    logging.debug("**kwargs={0}".format(kwargs))
    
    global overwrite
    
    # get the relative dir for target
    relFile = os.path.relpath(targetFile, str(projectDirectory))
    mirrorFile = os.path.join(mirrorDirectory, relFile)
    
    # check for file overwrite
    if os.path.exists(targetFile):
        if os.path.exists(mirrorFile):
            targetTime = os.path.getmtime(targetFile)
            mirrorTime = os.path.getmtime(mirrorFile)
            if targetTime > mirrorTime:
                if overwrite:
                    logging.warn("target modified - overwrite: {0}".format(relFile))
                else:
                    logging.warn("target modified - skipping: {0}".format(relFile))
                    return
       
    
    mytemplate = templateLookup.get_template(templateFile)
    pathlib.Path(os.path.dirname(targetFile)).mkdir(parents=True, exist_ok=True)
    with open(targetFile, 'w') as f:
        f.write(mytemplate.render(**model))

    # copy to mirror directory
    pathlib.Path(os.path.dirname(mirrorFile)).mkdir(parents=True, exist_ok=True)
    shutil.copy2(targetFile, mirrorFile)
    
def createDefaultFile(model=None, templateFile=None, targetFile=None, **kwargs):
    '''Create a default model, template, xform or other file.'''
    mytemplate = templateLookup.get_template(templateFile)
    pathlib.Path(os.path.dirname(targetFile)).mkdir(parents=True, exist_ok=True)
    with open(targetFile, 'w') as f:
        f.write(mytemplate.render(**model))
    