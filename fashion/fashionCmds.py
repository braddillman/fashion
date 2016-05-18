'''
Created on 2016-04-29

Copyright (c) 2016 Bradford Dillman

@author: bdillman

Command line parser for fashion project.
'''

import argparse
import logging
import os
import pathlib
import shutil
import sys

from . import fashionPortfolio
from . import project
from . import templates
from . import xforms
from . import xformUtil
from fashion.project import FASHION_HOME

alwaysYes = False

def query_yes_no(question, default="yes"):
    '''
    Ask a yes/no question via input() and return their answer.

    "question" is a string that is presented to the user.
    "default" is the presumed answer if the user just hits <Enter>.
        It must be "yes" (the default), "no" or None (meaning
        an answer is required of the user).

    The "answer" return value is True for "yes" or False for "no".
    '''
    valid = {"yes": True, "y": True, "ye": True,
             "no": False, "n": False}
    if default is None:
        prompt = " [y/n] "
    elif default == "yes":
        prompt = " [Y/n] "
    elif default == "no":
        prompt = " [y/N] "
    else:
        raise ValueError("invalid default answer: '%s'" % default)

    while True:
        sys.stdout.write(question + prompt)
        if alwaysYes:
            sys.stdout.write("y\n")
            return True;
        choice = input().lower()
        if default is not None and choice == '':
            return valid[default]
        elif choice in valid:
            return valid[choice]
        else:
            sys.stdout.write("Please respond with 'yes' or 'no' "
                             "(or 'y' or 'n').\n")

def initCmd(args):
    '''Initialize a new fashion project.'''
    proj = project.Project(args.project)
    if proj.exists():
        print("project already exists")
    else:
        proj.create()

def killCmd(args):
    '''Delete a fashion project.'''
    proj = project.Project(args.project)
    if proj.exists():
        if query_yes_no("Are you sure you want to delete the fashion project", "no"):
            proj.destroy()
    else:
        print("project doesn't exist")

def buildCmd(args):
    '''Perform a full build.'''
    proj = project.findProject(args.project)
    if proj.exists():
        with xformUtil.cd(str(proj.projectPath)):
            proj.init_db()
            fashionPortfolio.clean()
            proj.importModels()
            xfs = proj.loadXforms()
            plan = xforms.XformPlan(xfs)
            plan.plan()
            proj.loadTemplates()
            templates.overwrite = args.force
            plan.execute()
    else:
        print("project doesn't exist")
    
def nabCmd(args):
    '''Nab a file and turn it into a template + xform.'''
    proj = project.findProject(args.project)
    if proj.exists():
        proj.init_db()
        
        targetFile = args.filename
        relTarget = os.path.relpath(targetFile, str(proj.projectPath))

        # create template by copying target file
        templateDir = proj.getLocalTemplateDir()
        templateDest = os.path.join(templateDir, relTarget)
        relTemplate = os.path.relpath(templateDest, str(templateDir))
        if os.path.exists(str(templateDest)):
            print("Template already exists: " + str(templateDest))
            return
        pathlib.Path(os.path.dirname(templateDest)).mkdir(parents=True, exist_ok=True)
        shutil.copyfile(targetFile, str(templateDest))
        print("Created template: " + str(templateDest))
        
        # create a corresponding default xform
        xfName = os.path.basename(os.path.splitext(targetFile)[0])
        if args.name != None:
            xfName = args.name
        xfFilename = xfName + ".py"
        xformDest = os.path.join(proj.getLocalXformDir(), os.path.dirname(relTarget), xfFilename)
        model = { 'name'    : xfName,
                  'template': relTemplate,
                  'target'  : relTarget }
        defaultXformTemplateFile = "defaultXform.py"
        proj.loadTemplates()
        templates.createDefaultFile(model, defaultXformTemplateFile, xformDest)
        print("Created xform: " + str(xformDest))
        
    else:
        print("project doesn't exist")    

def homeCmd(args):
    '''fashion install home'''
    print(str(FASHION_HOME))
    
def infoCmd(args):
    '''fashion install info'''
    print("not implemented")
    
def versionCmd(args):
    '''Version of fashion'''
    print(str(FASHION_HOME))
    print("version: unstable dev")
    
def create_model(args):
    '''Create a new model'''
    proj = project.findProject(args.project)
    if proj.exists():
        proj.init_db()
        targetFile = os.path.join(proj.getLocalModelDir(), args.filename)
        kind = args.kind
        if args.format == None:
            fileFormat = 'yaml'
        else:
            fileFormat = args.format
        lib = proj.getLocalLibrary()
        if lib.addFile(targetFile, 3, kind, fileFormat):
            lib.save()
            if not os.path.exists(targetFile):
                proj.loadTemplates()
                templates.createDefaultFile({}, "defaultModel.yaml", targetFile)
                print("Created new model {0}".format(targetFile))
                return True
            else:
                print("Added existing model {0}".format(targetFile))
                return True
        print("Failed to create model {0}".format(targetFile))
    else:
        print("project doesn't exist")    

def create_xform(args):
    '''Create a new xform'''
    proj = project.findProject(args.project)
    if proj.exists():
        proj.init_db()
        targetFile = os.path.join(proj.getLocalXformDir(), args.filename+'.py')
        lib = proj.getLocalLibrary()
        if lib.addFile(targetFile, 4, fileFormat='python3'):
            lib.save()
            if not os.path.exists(targetFile):
                proj.loadTemplates()
                xfName = os.path.basename(os.path.splitext(targetFile)[0])
                model = { 'name'    : xfName,
                          'template': 'myTemplate',
                          'target'  : 'myTarget' }
                templates.createDefaultFile(model, "defaultXform.py", targetFile)
                print("Created new xform {0}".format(targetFile))
                return True
            else:
                print("Added existing xform {0}".format(targetFile))
                return True
        print("Failed to create xform {0}".format(targetFile))
    else:
        print("project doesn't exist")    

def main():
    '''Parse command from command line args, then delegate.'''
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', '--project',   help='project directory', nargs=1)
    parser.add_argument('-y', '--alwaysYes', help="answer 'y' to all prompts", action='store_true')
    parser.add_argument('-v', '--verbose',   help="verbose output", action='store_true')
    parser.add_argument('-d', '--debug',     help="debug logging", action='store_true')

    subparsers = parser.add_subparsers(dest='command',
                                       title='commands', 
                                       description='valid commands', 
                                       help='command help')

    initParse = subparsers.add_parser('init', help='initialize a new fashion project in the current directory')

    killParse = subparsers.add_parser('kill', help='delete a fashion project and all contents from the current directory')

    nabParse = subparsers.add_parser('nab', help='nab a file and turn it into a fashionTemplate')
    nabParse.add_argument('filename', help='file to nab')
    nabParse.add_argument('-n', '--name',   help='xform name', nargs=1)

    buildParse = subparsers.add_parser('build', help='full build')
    buildParse.add_argument('-f', '--force', help="force overwrite", action='store_true')
    
    createModelParse = subparsers.add_parser('create-model', help='create a new model')
    createModelParse.add_argument('filename', help='filename for new model')
    createModelParse.add_argument('kind',     help='kind of model to create')
    createModelParse.add_argument('-f', '--format', help="file format", nargs=1)

    createXformParse = subparsers.add_parser('create-xform', help='create a new xform')
    createXformParse.add_argument('filename', help='filename for new xform')

    homeParse = subparsers.add_parser('home', help='report install directory')
    infoParse = subparsers.add_parser('info', help='show info, not implemented')
    versionParse = subparsers.add_parser('version', help='report version information')

    result = parser.parse_args(sys.argv[1:]);
    if result.project == None:
        result.project = os.getcwd()
        
    global alwaysYes        
    if result.alwaysYes:
        alwaysYes = result.alwaysYes

    if result.debug:        
        logging.basicConfig(level=logging.DEBUG)

    logging.debug(result)

    cmds = {
        "init": initCmd,
        "nab": nabCmd,
        "build": buildCmd,
        "kill": killCmd,
        "home": homeCmd,
        "info": infoCmd,
        "version": versionCmd,
        "create-model": create_model,
        "create-xform": create_xform
    }

    try:
        cmds[result.command](result)
    except KeyError:
        if result.command == None:
            parser.print_help()
        else:
            print("unknown command "+result.command);

#
# Main entry point
#
if __name__ == "__main__":
    main(sys.argv[1:])
