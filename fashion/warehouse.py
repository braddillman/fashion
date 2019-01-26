'''
Warehouse - a library of segments
===================================

A warehouse manages a library of fashion segments. Their is a local warehouse
for each fashion project under the ./fashion/warehouse directory in the 
project, created  by 'fashion init'.

There is also a shared global warehouse located where fashion is installed.

Each fashion project has access to all segments in its local warehouse and the
shared global warehouse.

Each segment is stored in a named subdirectory under the warehouse directory.
Each directory is named for the segment within.

A warehouse doesn't store anything about segments, so segment directories may
be deleted or copied freely, instead of using the command line functions.

/fashion/warehouse/* - segment directories
/fashion/warehouse/local - the default local segment

See the section on Segment for the directory layout under each segment
directory.

Created on 2018-12-28 Copyright (c) 2018 Bradford Dillman
'''

import copy
import logging
import os
import shutil
import zipfile

from pathlib import Path

from genson import SchemaBuilder
from munch import munchify
from tinydb import Query

from fashion.segment import Segment
from fashion.util import cd
from fashion.xforms import matchTags


class Warehouse(object):
    '''Manage collection of segments.'''

    def __init__(self, dir, fallback=None):
        '''
        Constructor.

        :param Path dir: directory for segment subdirectories.
        :param Warehouse fallback: another Warehouse to check for missing segments.
        '''

        # Location of this Warehouse.
        self.dir = dir.absolute()

        # Another Warehouse 2nd in priority to this one.
        self.fallback = fallback

        # A cache of already loaded segments.
        self.segmentCache = {}

    def listSegments(self):
        '''
        List names of segments in this warehouse.

        :returns: a list of segment names in this warehouse.
        :rtype: list(string)
        '''
        # Return the named subdirectories.
        with cd(self.dir):
            return [d.name for d in self.dir.iterdir() if d.is_dir()]

    def loadSegment(self, segname, db, cache=None):
        '''
        Load a segment by name from this or fallback Warehouse.

        :param string segname: name of the segment to load.
        :returns: the loaded segment or None.
        :rtype: Segment
        '''
        if cache is None:
            cache = self.segmentCache

        # Try the cache first.
        if segname in cache:
            return cache[segname]
        
        # Next check a named subdirectory.
        segfn = self.dir / segname / "segment.json"
        seg = None
        if segfn.exists():
            if db.isVerbose():
                print("Loading segment {0}".format(segname))
            seg = Segment.load(segfn)
        elif self.fallback is not None:
            # Try the fallback Warehouse if not found.
            seg = self.fallback.loadSegment(segname, db)

        # Update the cache.
        cache[segname] = seg
        Q = Query()

        # Make a note in the database.
        db.table('fashion.prime.segment').upsert(seg.properties, Q.name == segname)

        return seg

    def loadSegments(self, db):
        '''
        Load all segments in this and referenced warehouses.

        :returns: list of all Segment objects.
        :rtype: list(Segment)
        '''
        db.table('fashion.prime.segment').purge()
        return self.loadSegs(db, self.segmentCache)

    def loadSegs(self, db, cache):
        # Load all the segments in this Warehouse.
        self.segments = [self.loadSegment(segname, db)
                         for segname in self.listSegments()]
        if self.fallback is not None:
            # Append the fallback Warehouse segments.
            self.segments.extend(self.fallback.loadSegs(db, cache))
        return self.segments

    def newSegment(self, segname, db):
        '''
        Create a new segment in this warehouse.

        :param string segname: name of the new segment.
        :returns: the new Segment object.
        :rtype: Segment
        '''
        if segname in self.listSegments():
            logging.error("segment {0} already exists".format(segname))
            return
        segdir = self.dir / segname
        segdir.mkdir(parents=True, exist_ok=True)
        Segment.create(segdir, segname)
        self.loadSegment(segname, db)

    def exportSegment(self, segname, db):
        '''
        Export a segment to a zip file.

        :param string segname: name of segment to export.
        '''
        seg = self.loadSegment(segname, db)
        exportName = segname + "_v" + seg.properties.version + ".zip"
        dirName = seg.absDirname.parent.resolve()
        with zipfile.ZipFile(exportName, mode='w') as zip:
            with cd(dirName):
                for root, _, files in os.walk(segname):
                    if os.path.basename(root) != '__pycache__':
                        for file in files:
                            zip.write(os.path.join(root, file))

    def importSegment(self, zipfilename):
        '''
        Import a segment from a zip file.

        :param string zipfilename: filename of export.
        '''
        with zipfile.ZipFile(zipfilename, mode='r') as zip:
            with cd(self.dir):
                zip.extractall()

    def deleteSegment(self, segment):
        '''
        Delete a segment from this warehouse.

        :param Segment segment: the segment object to delete from this warehouse.
        '''
        shutil.rmtree(str(segment.absDirname))

    def getModuleDefinitions(self, dba, tags=None):
        '''
        Load all "xformModules" xform module defintions from all segments 
        which match tags. Does NOT load the modules.

        :param list(string) tags: list of tags to match before loading.
        :returns: a dictionary of module definions.
        :rtype: dictionary {moduleName:module}
        '''
        modDefs = {}
        dba.table('fashion.prime.module.definition').purge()
        for seg in self.segments:
            xformModules = munchify(seg.findModuleDefinitions())
            for m in xformModules:
                if m.moduleName in modDefs:
                    logging.error(
                        "xform module name collision: {0}".format(m.moduleName))
                else:
                    mod = munchify(m)
                    if "templatePath" not in mod:
                        if "templatePath" in seg.properties:
                            mod.templatePath = seg.properties.templatePath
                        else:
                            mod.templatePath = []
                    mod.absDirname = seg.absDirname.as_posix()
                    mod.moduleRootName = m.moduleName
                    mod.segmentName = seg.properties.name
                    dba.table('fashion.prime.module.definition').insert(mod)
                    modDefs[mod.moduleName] = mod
        return modDefs

    def getModuleConfigs(self, dba, moduleDict):
        '''
        Load all "xformConfig" xform module configurations from all segments 
        for modules in moduleDict. Does NOT load the modules or initialize them.

        :param moduleDict: a dictionary of module definitions.
        :returns: a list of xform modules configurations.
        :rtype: list(xform module configs)
        '''
        cfgs = []
        dba.table('fashion.prime.module.config').purge()
        for seg in self.segments:
            for c in seg.properties.xformConfig:
                if c.moduleName in moduleDict:
                    cfg = munchify(c)
                    cfg.name = cfg.moduleName
                    cfg.segmentName = seg.properties.name
                    cfg.absDirname = seg.absDirname.as_posix()
                    # set defaults for omitted properties
                    if "inputKinds" not in cfg:
                        cfg.inputKinds = []
                    if "outputKinds" not in cfg:
                        cfg.outputKinds = []
                    if "tags" not in cfg:
                        cfg.tags = []
                    if "templatePath" not in cfg:
                        if "templatePath" in seg.properties:
                            cfg.templatePath = seg.properties.templatePath
                        else:
                            cfg.templatePath = []
                    cfgs.append(cfg)
                    dba.table('fashion.prime.module.config').insert(cfg)
                else:
                    logging.error("No module for config: {0}".format(c.moduleName))
        return cfgs

    def getUndefinedModuleConfigs(self, moduleDict):
        '''
        Load all "xformConfig" from all segments for modules NOT in moduleDict.

        :param moduleDict: a dictionary with keys of module names.
        :returns: a list of xform modules configurations.
        :rtype: list(xform module configs)
        '''
        cfgs = []
        for seg in self.segments:
            for cfg in seg.properties.xformConfig:
                if cfg.moduleName not in moduleDict:
                    cfg.properties.name = cfg.properties.moduleName
                    cfgs.append(cfg)
        return cfgs

    def getSchemaDefintions(self):
        '''
        Load all segment schemas.
        :returns: a dictionary of schemas for models by kind.
        :rtype: dictionary {string kind:string schema filename}
        '''
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
        '''
        Guess a JSONSchema for a model kind from examples.

        :param DatabaseAccess dba: the fasion database to search.
        :param string kind: the model kind to guess.
        :param JSONobject existingSchema: starting schema, if any.
        :returns: True if the schema was guessed and created.
        :rtype: boolean
        '''
        objs = dba.table(kind).all()
        builder = SchemaBuilder()
        if existingSchema is not None:
            builder.add_schema(existingSchema)
        elif len(objs) == 0:
            logging.error(
                "Can't guess with no schema and no examples of kind {0}".format(kind))
            return False
        for o in objs:
            builder.add_object(o)
        schema = builder.to_schema()
        localSeg = self.loadSegment("local", dba)
        localSeg.createSchema(kind, schema)
        return True
