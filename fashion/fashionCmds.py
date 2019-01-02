'''
Created on 2016-04-29

Copyright (c) 2016 Bradford Dillman

@author: bdillman

Command line parser for fashion project.
'''

import argparse
import json
import logging
import os
import pathlib
import shutil
import sys
import zipfile

from munch import Munch

from fashion.portfolio import FASHION_HOME, Portfolio
from fashion.runway import Runway
from fashion.schema import SchemaRepository
from fashion.util import cd

alwaysYes = False

portfolio = None


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
            return True
        choice = input().lower()
        if default is not None and choice == '':
            return valid[default]
        elif choice in valid:
            return valid[choice]
        else:
            sys.stdout.write("Please respond with 'yes' or 'no' "
                             "(or 'y' or 'n').\n")


def setup(args):
    global portfolio
    portfolio = Portfolio(args.project)
    if not portfolio.exists():
        print("No project found.")
        return False
    return True


def init(args):
    '''Initialize a new fashion project.'''
    global portfolio
    portfolio = Portfolio(args.project)
    if portfolio.exists():
        print("project already exists")
    else:
        portfolio.create()


def kill(args):
    '''Delete a fashion project.'''
    global portfolio
    portfolio = Portfolio(args.project)
    if portfolio.exists():
        if query_yes_no("Are you sure you want to delete the fashion project", "no"):
            portfolio.delete()
    else:
        print("project doesn't exist")


def version(args):
    '''Version of fashion'''
    print(str(FASHION_HOME))
    print("version: 0.2.0 unstable dev")


def build(args):
    '''Build the output.'''
    global portfolio
    if not setup(args):
        return
    print("building...")
    with cd(portfolio.projectPath):
        r = portfolio.getRunway()
        r.initMirror(portfolio.projectPath, portfolio.mirrorPath)
        r.plan()
        r.execute()


def create(args):
    global portfolio
    if not setup(args):
        return
    print("creating new {0}...".format(args.element))
    if args.element == 'xform':
        tp = portfolio.warehouse.getDefaultsTemplatePath()
        localSeg = portfolio.warehouse.loadSegment("local")
        localSeg.createXform(args.name, tp)
    else:
        print("unknown element type '{0}'".format(args.element))


def guessSchema(args):
    global portfolio
    if not setup(args):
        return
    portfolio.warehouse.loadSegments()
    schemaDefs = portfolio.warehouse.getSchemaDefintions()
    if args.kind in schemaDefs:
        if not query_yes_no("Are you sure you want to overwrite the schema?", "no"):
            return
    portfolio.warehouse.guessSchema(portfolio.db, args.kind)


def dump(args):
    global portfolio
    if not setup(args):
        return
    print(json.dumps(portfolio.db.table(args.kind).get(doc_id=args.id), indent=4))


def dumpAll(args):
    global portfolio
    if not setup(args):
        return
    print(json.dumps(portfolio.db.table(args.kind).all(), indent=4))


def segmentList(args):
    global portfolio
    if not setup(args):
        return
    segNames = portfolio.warehouse.listSegments()
    if portfolio.warehouse.fallback is not None:
        segNames.extend(portfolio.warehouse.fallback.listSegments())
    if len(segNames) == 0:
        print("No segments found.")
        return
    for sn in segNames:
        seg = portfolio.warehouse.loadSegment(sn)
        print("{0} v{1} - {2}".format(seg.properties.name,
                                      seg.properties.version, seg.absDirname))


def segmentNew(args):
    global portfolio
    if not setup(args):
        return
    seg = portfolio.warehouse.loadSegment(args.segname)
    if seg is not None:
        if query_yes_no("Are you sure you want to overwrite the segment?", "no"):
            portfolio.warehouse.deleteSegment(seg)
        else:
            return
    portfolio.warehouse.newSegment(args.segname)


def segmentExport(args):
    global portfolio
    if not setup(args):
        return
    seg = portfolio.warehouse.loadSegment(args.segname)
    if seg is None:
        print("Segment not found: {0}".format(args.segname))
        return
    print("exporting segment {0}".format(args.segname))
    portfolio.warehouse.exportSegment(args.segname)


def segmentImport(args):
    global portfolio
    if not setup(args):
        return
    if not os.path.exists(args.filename):
        print("{0} not found.".format(args.filename))
        return
    segname = os.path.basename(args.filename).split("_v")[0]
    version = os.path.basename(args.filename).split("_v")[1].split(".zip")[0]
    seg = portfolio.warehouse.loadSegment(segname)
    if seg is not None:
        if query_yes_no("Are you sure you want to overwrite the segment?", "no"):
            portfolio.warehouse.deleteSegment(seg)
        else:
            return
    print("importing segment {0} v{1}".format(segname, version))
    portfolio.warehouse.importSegment(args.filename)


# TODO: nab command

# TODO: pojo segment
# TODO: pocppo segment
# TODO: pocso segment
# TODO: SISO segment (HLA, DIS)


def main():
    '''Parse command from command line args, then delegate.'''
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', '--project',   help='project directory', nargs=1)
    parser.add_argument('-y', '--alwaysYes',
                        help="answer 'y' to all prompts", action='store_true')
    parser.add_argument('-v', '--verbose',
                        help="verbose output", action='store_true')
    parser.add_argument('-d', '--debug',
                        help="debug logging", action='store_true')

    subparsers = parser.add_subparsers(dest='command',
                                       title='commands',
                                       description='valid commands',
                                       help='command help',
                                       prog='fashion')

    initParser = subparsers.add_parser(
        'init', help='initialize a new fashion project in current directory')
    initParser.set_defaults(func=init)

    killParser = subparsers.add_parser(
        'kill', help='delete all fashion contents from project directory')
    killParser.set_defaults(func=kill)

    versionParser = subparsers.add_parser(
        'version', help='display fashion version')
    versionParser.set_defaults(func=version)

    buildParser = subparsers.add_parser(
        'build', help='build the plan of xforms and generate output')
    buildParser.set_defaults(func=build)

    createParser = subparsers.add_parser(
        'create', help='create a default xform, schema, model, etc.')
    createParser.add_argument(
        'element', help='element type: xform, schema, model, template')
    createParser.add_argument('name',    help='name of new element')
    createParser.set_defaults(func=create)

    guessSchemaParser = subparsers.add_parser(
        'guess_schema', help='create a default schema for a model kind')
    guessSchemaParser.add_argument('kind', help='kind of model for schema')
    guessSchemaParser.set_defaults(func=guessSchema)

    dumpParser = subparsers.add_parser(
        'dump', help='print model contents')
    dumpParser.add_argument('kind', help='kind of model')
    dumpParser.add_argument('id', help='id of model')
    dumpParser.set_defaults(func=dump)

    dumpAllParser = subparsers.add_parser(
        'dump_all', help='print model contents')
    dumpAllParser.add_argument('kind', help='kind of model')
    dumpAllParser.set_defaults(func=dumpAll)

    segmentParser = subparsers.add_parser(
        'segment', help='list, import, export, update segments')
    segmentSubParser = segmentParser.add_subparsers(dest='segmentCommand',
                                                    title='segment subcommands',
                                                    description='valid segment subcommands',
                                                    help='segment subcommand help')
    segmentListParser = segmentSubParser.add_parser(
        'list', help='list segments')
    segmentListParser.set_defaults(func=segmentList)
    segmentExportParser = segmentSubParser.add_parser(
        'export', help='export a segment')
    segmentExportParser.add_argument(
        'segname', help='name of segment to export')
    segmentExportParser.set_defaults(func=segmentExport)
    segmentImportParser = segmentSubParser.add_parser(
        'import', help='import a segment')
    segmentImportParser.add_argument(
        'filename', help='filename of segment to import')
    segmentImportParser.set_defaults(func=segmentImport)
    segmentNewParser = segmentSubParser.add_parser(
        'new', help='create a new segment')
    segmentNewParser.add_argument(
        'segname', help='name of new segment')
    segmentNewParser.set_defaults(func=segmentNew)

    result = parser.parse_args(sys.argv[1:])
    if result.project == None:
        result.project = os.getcwd()

    global alwaysYes
    if result.alwaysYes:
        alwaysYes = result.alwaysYes

    if result.debug:
        logging.basicConfig(level=logging.DEBUG)

    logging.debug(result)

    result.func(result)

    global portfolio
    if portfolio is not None:
        portfolio.db.close()


#
# Main entry point
#
if __name__ == "__main__":
    main(sys.argv[1:])
