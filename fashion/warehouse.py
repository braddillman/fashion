'''
Created on 2018-12-28

Copyright (c) 2018 Bradford Dillman

@author: Bradford Dillman

A collection of segments.
'''

import copy
import logging
import os
import shutil
import zipfile

from genson import SchemaBuilder
from munch import munchify

from fashion.segment import Segment
from fashion.util import cd
from fashion.xforms import matchTags


class Warehouse(object):
    '''A collection of segments.'''

    def __init__(self, dir, fallback=None):
        '''
        Constructor.
        :param dir: directory for segment subdirectories.
        :param fallback: another Warehouse to check for missing segments.
        '''
        self.dir = os.path.abspath(str(dir))
        self.fallback = fallback
        self.segmentCache = {}

    def listSegments(self):
        '''
        Return a list of segments in this warehouse.
        '''
        with cd(self.dir):
            return [os.path.basename(d) for d in os.listdir(self.dir) if os.path.isdir(d)]

    def loadSegment(self, segname):
        '''
        Load a segment by name from this or fallback Warehouse.
        :param segname: name of the segment to load.
        '''
        if segname in self.segmentCache:
            return self.segmentCache[segname]
        segfn = os.path.join(self.dir, segname, "segment.json")
        seg = None
        if os.path.exists(segfn):
            seg = Segment.load(segfn)
        elif self.fallback is not None:
            seg = self.fallback.loadSegment(segname)
        self.segmentCache[segname] = seg
        return seg

    def loadSegments(self):
        '''
        Load all segments in this and referenced warehouses.
        '''
        self.segments = [self.loadSegment(segname)
                         for segname in self.listSegments()]
        if self.fallback is None:
            return self.segments
        segNames = self.listSegments()
        for sn in self.fallback.listSegments():
            if sn not in segNames:
                self.segments.append(self.fallback.loadSegment(sn))

    def newSegment(self, segname):
        '''
        Create a new segment in this warehouse.
        :param segname: name of the new segment.
        '''
        if segname in self.listSegments():
            logging.error("segment {0} already exists".format(segname))
            return
        segdir = os.path.join(self.dir, segname)
        os.mkdir(segdir)
        Segment.create(segdir, segname)
        self.loadSegment(segname)

    def exportSegment(self, segname):
        '''Export a segment to a zip file.'''
        seg = self.loadSegment(segname)
        exportName = segname + "_v" + seg.properties.version + ".zip"
        dirName = os.path.abspath(os.path.join(seg.absDirname, ".."))
        with zipfile.ZipFile(exportName, mode='w') as zip:
            with cd(dirName):
                for root, dirs, files in os.walk(segname):
                    if os.path.basename(root) != '__pycache__':
                        for file in files:
                            zip.write(os.path.join(root, file))

    def importSegment(self, zipfilename):
        '''Import a segment from a zip file.'''
        with zipfile.ZipFile(zipfilename, mode='r') as zip:
            with cd(self.dir):
                zip.extractall()

    def deleteSegment(self, seg):
        '''
        Delete a segment from the warehouse.
        :param seg: the segment to delete.
        '''
        shutil.rmtree(str(seg.absDirname))

    def getModuleDefinitions(self, tags=None):
        '''
        Load all "xformModules" from all segments which match tags.
        :param tags: list of tags to match before loading.
        '''
        modDefs = {}
        for seg in self.segments:
            for m in seg.properties.xformModules:
                if m.moduleName in modDefs:
                    logging.error(
                        "xform module name collision: {0}".format(m.name))
                else:
                    if matchTags(tags, m.tags):
                        mod = munchify(m)
                        if "templatePath" not in mod:
                            if "templatePath" in seg.properties:
                                mod.templatePath = seg.properties.templatePath
                            else:
                                mod.templatePath = []
                        with cd(seg.absDirname):
                            mod.templatePath = [os.path.abspath(
                                p) for p in mod.templatePath]
                        mod.absDirname = seg.absDirname
                        mod.moduleRootName = m.moduleName
                        mod.moduleName = seg.properties.name + '.' + m.moduleName
                        modDefs[mod.moduleName] = mod
        return modDefs

    def getModuleConfigs(self, moduleDict):
        '''
        Load all "xformConfig" from all segments for modules in moduleDict.
        :param moduleDict: a dictionary of module definitions.
        '''
        cfgs = []
        for seg in self.segments:
            for c in seg.properties.xformConfig:
                if c.moduleName in moduleDict:
                    modDef = moduleDict[c.moduleName]
                    cfg = munchify(c)
                    cfg.name = cfg.moduleName
                    cfg.absDirname = seg.absDirname
                    # set defaults for omitted properties
                    if "inputKinds" not in cfg:
                        cfg.inputKinds = []
                    if "outputKinds" not in cfg:
                        cfg.outputKinds = []
                    if "tags" not in cfg:
                        cfg.tags = []
                    if "templatePath" not in cfg:
                        cfg.templatePath = modDef.properties.templatePath
                    cfgs.append(cfg)
        return cfgs

    def getUndefinedModuleConfigs(self, moduleDict):
        '''
        Load all "xformConfig" from all segments for modules NOT in moduleDict.
        :param moduleDict: a dictionary with keys of module names.
        '''
        cfgs = []
        for seg in self.segments:
            for cfg in seg.properties.xformConfig:
                if cfg.moduleName not in moduleDict:
                    cfg.properties.name = cfg.properties.moduleName
                    cfgs.append(cfg)
        return cfgs

    def getSchemaDefintions(self):
        '''Load all segment schemas.'''
        schemaDescrs = {}
        for seg in self.segments:
            for sch in seg.properties.schema:
                if sch.kind in schemaDescrs:
                    logging.error(
                        "duplicate schema definition: {0}".format(sch.kind))
                else:
                    sch.absDirname = seg.absDirname
                    schemaDescrs[sch.kind] = sch
        return schemaDescrs

    def guessSchema(self, dba, kind, existingSchema=None):
        objs = dba.table(kind).all()
        builder = SchemaBuilder()
        if existingSchema is not None:
            builder.add_schema(existingSchema)
        elif len(objs) == 0:
            logging.error("Can't guess with no schema and no examples of kind {0}".format(kind))
            return False
        for o in objs:
            builder.add_object(o)
        schema = builder.to_schema()
        localSeg = self.loadSegment("local")
        localSeg.createSchema(kind, schema)
        return True

    def getDefaultsTemplatePath(self):
        '''Get the templatePath to search for default implementations.'''
        localSeg = self.loadSegment("local")
        localPath = [localSeg.getAbsPath(p)
                     for p in localSeg.properties.templatePath]
        coreSeg = self.loadSegment("fashion.core")
        corePath = [coreSeg.getAbsPath(p)
                    for p in coreSeg.properties.templatePath]
        localPath.extend(corePath)
        return localPath
