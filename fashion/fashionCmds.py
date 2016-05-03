'''
Created on 2016-04-29

Copyright (c) 2016 Bradford Dillman

@author: bdillman

Command line parser for fashion project.
'''

import argparse
import os
import sys
import shutil
import logging

from . import project
from . import xforms
from . import fashionPortfolio
from . import templates

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
    proj = project.Project(args.project)
    if proj.exists():
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
    '''Nab a file and turn it into a fashionTemplate + xform + genrec'''
    proj = project.Project(args.directory)
    targetFile = args.filename
    rel = os.path.relpath(targetFile, str(proj.projPath))

    # back up file to mirror
    mirrorDest = proj.projPath / 'fashion' / 'mirror' / rel
    shutil.copyfile(targetFile, str(mirrorDest))

    # create fashionTemplate by copying target file
    templateDest = proj.projPath / 'fashion' / 'fashionTemplate' / rel
    if os.path.exists(str(templateDest)):
        print("Template already exists: " + str(templateDest))
        return
    shutil.copyfile(targetFile, str(templateDest))
    print("Created fashionTemplate: " + str(templateDest))
    
    # create default model
    modelDest = proj.projPath / 'fashion' / 'model' / rel
    
    # create xform
    # create genrec

def banCmd(args):
    '''Undo a nab.'''
    pass

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

    banParse = subparsers.add_parser('ban', help='ban a file and remove it from generation')
    banParse.add_argument('filename', help='file to ban')

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
        "ban": banCmd,
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
