'''
Schema checking
===================================
Validates JSON objects.

Created on 2018-12-26 Copyright (c) 2018 Bradford Dillman
'''

import copy
import json
import logging

from jsonschema import validate, SchemaError


class Schema(object):
    '''Validates JSON objects against JSON schema.'''

    def __init__(self, schemaConfig):
        '''Constructor.'''
        self.config = copy.copy(schemaConfig)

    @staticmethod
    def load(schemaConfig):
        '''Load the JSON schema from a file.'''
        with open(str(schemaConfig.filename), 'r') as fd:
            s = Schema(schemaConfig)
            s.jsonschema = json.loads(fd.read())

    def validate(self, obj):
        '''Validate a JSON object against this schema.'''
        # raises SchemaError for bad schema
        # raises ValidationError on failure
        validate(obj, self.jsonschema)
        return True


class SchemaRepository(object):
    '''Registry of Schema objects.'''

    def __init__(self):
        '''Constructor.'''
        self.schemaByKind = {}

    def validate(self, kind, obj):
        '''
        Validate an object using the schema from this repository.

        :param kind: the kind of object to validate.
        :param obj: the object to validate.

        :raises: jsonschema.ValidationError on failure.
        '''
        if kind in self.schemaByKind:
            s = self.schemaByKind[kind]
            try:
                s.validate(obj)
            except SchemaError:
                logging.error(
                    "Schema error for kind: {0}".format(kind))
                self.removeByKind(kind)

    def addFromDescription(self, schemaConfig, overwrite=False):
        '''
        Create and add a Schema object from a schema description object.

        :param Schema schemaConfig: the configuration to add.
        '''
        if not overwrite and self.exists(schemaConfig.kind):
            return
        s = Schema.load(schemaConfig)
        if schemaConfig.kind not in self.schemaByKind:
            self.schemaByKind[schemaConfig.kind] = s

    def removeByKind(self, kind):
        '''
        Remove a schema for a kind.

        :param string kind: the model kind to remove.
        '''
        self.schemaByKind[kind]

    def exists(self, kind):
        '''
        Check if a schema exists for a model kind.

        :param string kind: the model kind to test.
        :returns: True if their is a schema for this model kind.
        :rtype: boolean
        '''
        return kind in self.schemaByKind
