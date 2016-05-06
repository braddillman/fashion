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

def xformCmd(args):
    '''Run a single transform.'''
    
    #
    # Pseudocode:
    #
    # Find the xform and load it
    # find all the inputs - done by xform or by fashion framework?
    # xform the inputs to outputs
    #
    
    pass

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

def versionCmd(args):
    '''Version of fashion'''
    print("version: unstable dev")

def main(args):
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

    xformParse = subparsers.add_parser('xform', help='transform models')
    xformParse.add_argument('xformName', help='xform name')

    buildParse = subparsers.add_parser('build', help='full build')
    buildParse.add_argument('-f', '--force', help="force overwrite", action='store_true')
    
    modelParse = subparsers.add_parser('model', help='work with models')

    versionParse = subparsers.add_parser('version', help='report version information')

    result = parser.parse_args(args);
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
        "xform": xformCmd,
        "build": buildCmd,
        "kill": killCmd,
        "version": versionCmd
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
