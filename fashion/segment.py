'''
Created on 2018-12-16

Copyright (c) 2018 Bradford Dillman

@author: Bradford Dillman

A segment of fashion models, templates and xforms.
'''

import json
import logging
import os
import pathlib
import shutil

from jinja2 import FileSystemLoader, Environment
from jsonschema import validate
from munch import munchify

from fashion.util import cd

# JSON schema to validate a segment object/file.
segmentSchema = {
    "definitions": {},
    "$schema": "http://json-schema.org/draft-07/schema#",
    "$id": "http://fashion.com/segment.json",
    "type": "object",
            "title": "Segment Schema",
            "required": [
                "name",
                "version",
    ],
    "properties": {
                "name": {
                    "$id": "#/properties/name",
                    "type": "string",
                    "minLength": 1,
                    "title": "Name of the segment",
                    "default": "",
                    "examples": [
                        "fashion.core"
                    ],
                    "pattern": "^(.*)$"
                },
                "version": {
                    "$id": "#/properties/version",
                    "type": "string",
                    "minLength": 1,
                    "title": "Version of the segment",
                    "default": "",
                    "examples": [
                        "1.0.0"
                    ],
                    "pattern": "^(.*)$"
                },
                "description": {
                    "$id": "#/properties/description",
                    "type": "string",
                    "title": "A description of the segment",
                    "default": "",
                    "examples": [
                        "fashion core segment"
                    ],
                    "pattern": "^(.*)$"
                },
                "templatePath": {
                    "$id": "#/properties/templatePath",
                    "type": "array",
                    "title": "Template path list relative to segment file directory",
                    "items": {
                        "$id": "#/properties/templatePath/items",
                        "type": "string",
                        "title": "A template path",
                        "default": "",
                        "examples": [
                            "./template"
                        ],
                        "pattern": "^(.*)$"
                    }
                },
                "schema": {
                    "$id": "#/properties/schema",
                    "type": "array",
                    "title": "A list of schemas for this segment",
                    "items": {
                        "$id": "#/properties/schema/items",
                        "type": "object",
                        "title": "The Items Schema",
                        "required": [
                            "kind",
                            "filename"
                        ],
                        "properties": {
                            "kind": {
                                "$id": "#/properties/schema/items/properties/kind",
                                "type": "string",
                                "title": "The Kind Schema",
                                "default": "",
                                "examples": [
                                    "fashion.core.generate.jinja2.spec"
                                ],
                                "pattern": "^(.*)$"
                            },
                            "filename": {
                                "$id": "#/properties/schema/items/properties/filename",
                                "type": "string",
                                "title": "The Filename Schema",
                                "default": "",
                                "examples": [
                                    "./schema/generateJinja2.json"
                                ],
                                "pattern": "^(.*)$"
                            }
                        }
                    }
                },
                "xformModules": {
                    "$id": "#/properties/xformModules",
                    "type": "array",
                    "title": "The Xformmodules Schema",
                    "items": {
                        "$id": "#/properties/xformModules/items",
                        "type": "object",
                        "title": "The Items Schema",
                        "required": [
                            "moduleName",
                            "filename"
                        ],
                        "properties": {
                            "moduleName": {
                                "$id": "#/properties/xformModules/items/properties/moduleName",
                                "type": "string",
                                "title": "The Modulename Schema",
                                "default": "",
                                "examples": [
                                    "fashion.core.generate.jinja2"
                                ],
                                "pattern": "^(.*)$"
                            },
                            "filename": {
                                "$id": "#/properties/xformModules/items/properties/filename",
                                "type": "string",
                                "title": "The Filename Schema",
                                "default": "",
                                "examples": [
                                    "./xform/generateJinja2.py"
                                ],
                                "pattern": "^(.*)$"
                            },
                            "tags": {
                                "$id": "#/properties/xformModules/items/properties/tags",
                                "type": "array",
                                "title": "The Tags Schema",
                                "items": {
                                    "$id": "#/properties/xformModules/items/properties/tags/items",
                                    "type": "string",
                                    "title": "The Items Schema",
                                    "default": "",
                                    "examples": [
                                        "output"
                                    ],
                                    "pattern": "^(.*)$"
                                }
                            }
                        }
                    }
                },
                "xformConfig": {
                    "$id": "#/properties/xformConfig",
                    "type": "array",
                    "title": "The Xformconfig Schema",
                    "items": {
                        "$id": "#/properties/xformConfig/items",
                        "type": "object",
                        "title": "The Items Schema",
                        "required": [
                            "moduleName",
                        ],
                        "properties": {
                            "moduleName": {
                                "$id": "#/properties/xformConfig/items/properties/moduleName",
                                "type": "string",
                                "title": "The Modulename Schema",
                                "default": "",
                                "examples": [
                                    "fashion.core.generate.jinja2"
                                ],
                                "pattern": "^(.*)$"
                            },
                            "tags": {
                                "$id": "#/properties/xformConfig/items/properties/tags",
                                "type": "array",
                                "title": "The Tags Schema",
                                "items": {
                                    "$id": "#/properties/xformConfig/items/properties/tags/items",
                                    "type": "string",
                                    "title": "The Items Schema",
                                    "default": "",
                                    "examples": [
                                        "output"
                                    ],
                                    "pattern": "^(.*)$"
                                }
                            },
                            "parameters": {
                                "$id": "#/properties/xformConfig/items/properties/parameters",
                                "type": "object",
                                "title": "The Parameters Schema"
                            }
                        }
                    }
                },
                "segmentRefs": {
                    "$id": "#/properties/segmentRefs",
                    "type": "array",
                    "title": "The Segmentrefs Schema",
                    "items": {
                        "$id": "#/properties/segmentRefs/items",
                        "type": "string",
                        "title": "A reference to another required segment",
                        "default": "",
                        "examples": [
                            "fashion.core"
                        ],
                        "pattern": "^(.*)$"
                    }
                },
                "extraFiles": {
                    "$id": "#/properties/extraFiles",
                    "type": "array",
                    "title": "The Extrafiles Schema",
                    "items": {
                        "$id": "#/properties/extraFiles/items",
                        "type": "string",
                        "title": "The Items Schema",
                        "default": "",
                        "examples": [
                            "./model/fashionPrime.json"
                        ],
                        "pattern": "^(.*)$"
                    }
                }
    }
}


def createDefaultXform(templatePath, targetFile, templateFile="defaultXformTemplate.py", model={}):
    '''Create a default xform module file.'''
    if os.path.exists(targetFile):
        logging.error(
            "xform module file already exists: {0}".format(targetFile))
        return False
    env = Environment(loader=FileSystemLoader(templatePath))
    template = env.get_template(templateFile)
    result = template.render(model)
    with open(str(targetFile), "w") as tf:
        tf.write(result)
    return True


class Segment(object):
    '''A collection of fashion resources.'''

    def __init__(self, filename):
        '''
        Initialize a new local segment.
        :param filename: the location of the segment JSON file.
        '''
        self.properties = munchify({
            "name": "local",
            "version": "1.0.0",
            "description": "fashion segment",
            "templatePath": ['./template'],
            "defaultModelPath": './model',
            "defaultSchemaPath": './schema',
            "defaultTemplatePath": './template',
            "defaultXformPath": './xform',
            "libPath": "./lib",
            "schema": [],
            "segmentRefs": ["fashion.core"],
            "xformModules": [],
            "xformConfig": [],
            "extraFiles": []
        })
        self.filename = filename
        self.absFilename = os.path.abspath(self.filename)
        self.absDirname = os.path.dirname(self.absFilename)

    @staticmethod
    def load(filename):
        '''
        Load a segment description from a JSON file.
        :param filename: the location of the segment JSON file.
        '''
        with open(str(filename), 'r') as fd:
            segment = Segment(filename)
            segment.properties = munchify(json.loads(fd.read()))
            if "templatePath" not in segment.properties:
                segment.properties.templatePath = []
        segment.validate()
        return segment

    @staticmethod
    def create(segdir, segname):
        '''
        Create a new segment.
        :param segdir: the location of the segment JSON file.
        :param segname: the name of the segment.
        '''
        newSeg = Segment(os.path.join(segdir, "segment.json"))
        newSeg.properties.name = segname
        newSeg.createDirectories()
        newSeg.save()
        return newSeg

    def getAbsPath(self, filename):
        '''Translate filename relative to this segment.'''
        absFn = filename
        with cd(self.absDirname):
            absFn = os.path.abspath(absFn)
        return absFn

    def save(self):
        '''
        Save a segment description to a JSON file.
        '''
        self.validate()
        with open(str(self.absFilename), "w") as sf:
            sf.write(self.properties.toJSON(indent=4))

    def createDirectories(self):
        '''
        Create default directories.
        '''
        p = pathlib.Path(self.absDirname)
        with cd(p):
            os.makedirs(str(p),              exist_ok=True)
            os.makedirs(str(p / "model"),    exist_ok=True)
            os.makedirs(str(p / "schema"),   exist_ok=True)
            os.makedirs(str(p / "template"), exist_ok=True)
            os.makedirs(str(p / "xform"),    exist_ok=True)

    def xformExists(self, xformName):
        '''Test if an xform exists.'''
        filename = xformName + ".py"
        targetFile = self.properties.defaultXformPath + '/' + filename
        with cd(self.absDirname):
            return os.path.exists(targetFile)
        
    def deleteXform(self, xformName):
        '''Delete an xform'''
        filename = xformName + ".py"
        targetFile = self.properties.defaultXformPath + '/' + filename
        with cd(self.absDirname):
            if os.path.exists(targetFile):
                os.remove(targetFile)
        moduleName = xformName
        modDefs = [x for x in self.properties.xformModules if x.moduleName != moduleName]
        self.properties.xformModules = modDefs
        moduleName = self.properties.name + "." + xformName
        modCfgs = [x for x in self.properties.xformConfig if x.moduleName != moduleName]
        self.properties.xformConfig = modCfgs
        self.save()
        
    def createXform(self, xformName, templatePath, templateFile="defaultXformTemplate.py", model={}):
        with cd(self.absDirname):
            filename = xformName + ".py"
            targetFile = self.properties.defaultXformPath + '/' + filename
            if not createDefaultXform(templatePath, targetFile, templateFile=templateFile, model=model):
                print("Failed!")
            else:
                self.properties.xformModules.append({
                    "moduleName": xformName,
                    "filename": targetFile,
                    "inputKinds": [],
                    "outputKinds": [],
                    "tags": []
                })
                self.properties.xformConfig.append({
                    "moduleName": self.properties.name + "." + xformName,
                    "parameters": {},
                    "tags": []
                })
                self.save()
        return True

    def templateExists(self, filename):
        with cd(self.absDirname):
            with cd(self.properties.defaultTemplatePath):
                absDst = os.path.abspath(filename)
        return os.path.exists(absDst)

    def deleteTemplate(self, filename):
        with cd(self.absDirname):
            with cd(self.properties.defaultTemplatePath):
                absDst = os.path.abspath(filename)
        if os.path.exists(absDst):
            os.remove(absDst)
        return True

    def createTemplate(self, filename):
        '''Create a template from a file.'''
        absFn =  os.path.abspath(filename)
        with cd(self.absDirname):
            with cd(self.properties.defaultTemplatePath):
                absDst = os.path.abspath(filename)
        shutil.copy(absFn, absDst)
        return True

    def createSchema(self, kind, schema):
        filename = self.properties.defaultSchemaPath + "/" + kind + ".json"
        with cd(self.absDirname):
            with open(filename, "w") as fp:
                json.dump(schema, fp, indent=4)
        self.properties.schema.append({
            "kind": kind,
            "filename": filename
        })
        self.save()

    def validate(self):
        '''
        Validate this object against a schema.
        '''
        validate(self.properties, segmentSchema)
