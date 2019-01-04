'''
Created on 2018-12-16

Copyright (c) 2018 Bradford Dillman

@author: Bradford Dillman

A segment of fashion models, templates and xforms.
'''

import json
import logging
import shutil

from pathlib import Path

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
    if targetFile.exists():
        logging.error(
            "xform module file already exists: {0}".format(targetFile))
        return False
    env = Environment(loader=FileSystemLoader(templatePath))
    template = env.get_template(templateFile)
    result = template.render(model)
    try:
        targetFile.makedir(parents=True, exist_ok=True)
    except:
        pass
    with targetFile.open(mode="w") as tf:
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
        self.absFilename = self.filename.absolute()
        self.absDirname = self.absFilename.parent

    @staticmethod
    def load(filename):
        '''
        Load a segment description from a JSON file.
        :param filename: the location of the segment JSON file.
        '''
        with filename.open(mode='r') as fd:
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
        newSeg = Segment(segdir / "segment.json")
        newSeg.properties.name = segname
        newSeg.createDirectories()
        newSeg.save()
        return newSeg

    def getAbsPath(self, filename):
        '''Translate filename relative to this segment.'''
        with cd(self.absDirname):
            return filename.absolute()

    def save(self):
        '''
        Save a segment description to a JSON file.
        '''
        self.validate()
        with self.absFilename.open(mode="w") as sf:
            sf.write(self.properties.toJSON(indent=4))

    def createDirectories(self):
        '''
        Create default directories.
        '''
        self.absDirname.mkdir(parents=True, exist_ok=True)
        (self.absDirname / "model").mkdir(parents=True, exist_ok=True)
        (self.absDirname / "schema").mkdir(parents=True, exist_ok=True)
        (self.absDirname / "template").mkdir(parents=True, exist_ok=True)
        (self.absDirname / "xform").mkdir(parents=True, exist_ok=True)

    def xformExists(self, xformName):
        '''Test if an xform exists.'''
        filename = Path(xformName + ".py")
        targetFile = Path(self.properties.defaultXformPath) / filename
        with cd(self.absDirname):
            return targetFile.exists()
        
    def deleteXform(self, xformName):
        '''Delete an xform'''
        filename = Path(xformName + ".py")
        targetFile = Path(self.properties.defaultXformPath) / filename
        with cd(self.absDirname):
            if targetFile.exists():
               targetFile.unlink()
        moduleName = xformName
        modDefs = [x for x in self.properties.xformModules if x.moduleName != moduleName]
        self.properties.xformModules = modDefs
        moduleName = self.properties.name + "." + xformName
        modCfgs = [x for x in self.properties.xformConfig if x.moduleName != moduleName]
        self.properties.xformConfig = modCfgs
        self.save()
        
    def createXform(self, xformName, templatePath, templateFile="defaultXformTemplate.py", model={}, moduleName=None):
        with cd(self.absDirname):
            filename = Path(xformName + ".py")
            targetFile = Path(self.properties.defaultXformPath) / filename
            if moduleName is None:
                moduleName = filename.stem
            if not createDefaultXform(templatePath, targetFile, templateFile=templateFile, model=model):
                print("Failed!")
            else:
                self.properties.xformModules.append({
                    "moduleName": moduleName,
                    "filename": targetFile.as_posix(),
                    "inputKinds": [],
                    "outputKinds": [],
                    "tags": []
                })
                self.properties.xformConfig.append({
                    "moduleName": self.properties.name + "." + moduleName,
                    "parameters": {},
                    "tags": []
                })
                self.save()
        return True

    def templateExists(self, filename):
        with cd(self.absDirname):
            with cd(self.properties.defaultTemplatePath):
                absDst = filename.absolute()
        return absDst.exists()

    def deleteTemplate(self, filename):
        with cd(self.absDirname):
            with cd(self.properties.defaultTemplatePath):
                absDst = filename.absolute()
        if absDst.exists():
            absDst.unlink()
        return True

    def createTemplate(self, filename):
        '''Create a template from a file.'''
        absFn =  filename.absolute()
        with cd(self.absDirname):
            with cd(self.properties.defaultTemplatePath):
                absDst = filename.absolute()
        try:
            absDst.parent.mkdir(parents=True, exist_ok=True)
        except:
            pass
        shutil.copy(absFn.as_posix(), absDst.as_posix())
        return True

    def createSchema(self, kind, schema):
        filename = Path(self.properties.defaultSchemaPath) / Path(kind + ".json")
        with cd(self.absDirname):
            with filename.open(mode="w") as fp:
                json.dump(schema, fp, indent=4)
        self.properties.schema.append({
            "kind": kind,
            "filename": str(filename)
        })
        self.save()

    def validate(self):
        '''
        Validate this object against a schema.
        '''
        validate(self.properties, segmentSchema)
