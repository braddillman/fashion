'''
Created on 2018-12-31

Copyright (c) 2018 Bradford Dillman

@author: Bradford Dillman

A collection of xform modules and xform objects.
'''

import copy
import logging
import traceback

from munch import Munch, munchify
from tinydb import Query

from fashion.codeRegistry import CodeRegistry
from fashion.modelAccess import ModelAccess
from fashion.schema import SchemaRepository
from fashion.util import cd
from fashion.warehouse import Warehouse
from fashion.xforms import XformModule


class Runway(object):
    '''Loaded modules and objects.'''

    def __init__(self, dba, wh):
        '''Ctor.'''
        self.moduleDefs = {}
        self.moduleCfgs = []
        self.modules = {}
        self.schemaDefs = {}
        self.dba = dba
        self.warehouse = wh
        self.schemaRepo = SchemaRepository()
        self.codeRegistry = CodeRegistry(self.dba)

    def loadModules(self, tags=None):
        '''Load all xform module code.'''
        self.moduleDefs = self.warehouse.getModuleDefinitions(self.dba, tags)
        verbose = self.dba.isVerbose()
        self.dba.table('fashion.core.module.definition').purge()
        for modName, modDef in self.moduleDefs.items():
            with cd(modDef.absDirname):
                if verbose:
                    print("Loading module {0}".format(modDef.moduleName))
                mod = XformModule(modDef)
                if mod.loadModuleCode():
                    self.modules[modName] = mod
                    self.dba.table('fashion.core.module.definition').insert(modDef)
                else:
                    # TODO: file not found, etc.
                    pass

    def loadSchemas(self):
        '''Load all schemas from the warehouse.'''
        self.schemaDefs = self.warehouse.getSchemaDefintions()
        for _, schDef in self.schemaDefs.items():
            # TODO: insert schema definition record into database
            with cd(schDef.absDirname):
                self.schemaRepo.addFromDescription(schDef)

    def setMdb(self, mda):
        self.codeRegistry.removeService(mda.name, mda.version)
        self.codeRegistry.addService(mda)

    def initModules(self, tags=None):
        '''Initialize modules from their configs.'''
        self.moduleCfgs = self.warehouse.getModuleConfigs(self.dba, self.modules)
        verbose = self.dba.isVerbose()
        for cfg in self.moduleCfgs:
            with cd(cfg.absDirname):
                with ModelAccess(self.dba, self.schemaRepo, cfg) as mdb:
                    self.setMdb(mdb)
                    mod = self.modules[cfg.moduleName]
                    if verbose:
                        print("Initializing module {0}".format(
                            mod.properties.moduleName))
                    self.codeRegistry.setObjectConfig(cfg)
                    mod.init(cfg, self.codeRegistry, tags)

    def plan(self):
        '''Construction the xform execution plan.'''
        self.objects = self.codeRegistry.xformObjectsByName
        self.xfOutputs = {xf.name: set(xf.outputKinds)
                          for xf in self.objects.values()}
        self.xfInputs = {xf.name: set(xf.inputKinds)
                         for xf in self.objects.values()}
        self.xfNames = set([xf.name for xf in self.objects.values()])

        self.allOutputs = {ok for _, outKinds in self.xfOutputs.items()
                           for ok in outKinds}
        self.allInputs = {ik for _, inKinds in self.xfInputs.items()
                          for ik in inKinds}

        self.leafInputs = self.allInputs - self.allOutputs
        self.leafOutputs = self.allOutputs - self.allInputs
        self.intermed = self.allInputs & self.allOutputs

        self.xfByOutput = {}
        for xfName, xfOutKinds in self.xfOutputs.items():
            for outKind in xfOutKinds:
                self.xfByOutput.setdefault(outKind, set([]))
                self.xfByOutput[outKind].add(xfName)

        self.xfByInput = {}
        for xfName, xfInKinds in self.xfInputs.items():
            for inKind in xfInKinds:
                self.xfByInput.setdefault(inKind, set([]))
                self.xfByInput[inKind].add(xfName)

        # now flatten into an exec list
        availInp = self.leafInputs.copy()
        availXforms = self.xfNames.copy()
        self.execList = []
        while(availXforms):
            readyXforms = set()
            for xfName in availXforms:
                if self.xfInputs[xfName] <= availInp:
                    readyXforms.add(xfName)
            if readyXforms:
                availXforms = availXforms - readyXforms
                self.execList.extend(readyXforms)
                # readyOutputs might be ready, or only partly complete
                readyOutputs = set()
                for xfName in readyXforms:
                    readyOutputs.update(self.xfOutputs[xfName])
                for outp in readyOutputs:
                    for xfName in self.xfByOutput[outp]:
                        if xfName in availXforms:
                            break
                    else:
                        availInp.add(outp)
            else:
                break
        if availXforms:
            logging.warning("xform dependency cycle detected")
        else:
            self.valid = True

        for idx, xfName in enumerate(self.execList):
            logging.debug("{0}:{1}".format(idx, xfName))

    def execute(self, tags=None):
        '''Execute all the xforms planned in self.execList.'''
        verbose = self.dba.isVerbose()
        for xfName in self.execList:
            xfo = self.objects[xfName]
            try:
                with ModelAccess(self.dba, self.schemaRepo, xfo) as mdb:
                    self.setMdb(mdb)
                    if verbose:
                        print("Executing {0}".format(xfo.name))
                    cfg = self.codeRegistry.getObjectConfig(xfo.name)
                    Definition = Query()
                    defs = self.dba.table('fashion.prime.module.definition').search(Definition.moduleName == cfg.moduleName)
                    assert len(defs) == 1
                    defn = munchify(defs[0])
                    tplSvc = self.codeRegistry.getService('fashion.core.template')
                    tplSvc.setDefinitionPath(
                        defn.absDirname,
                        defn.templatePath)
                    tplSvc.setConfigurationPath(
                        cfg.absDirname,
                        cfg.templatePath)
                    xfo.execute(self.codeRegistry, verbose, tags)
            except:
                logging.error("aborting, xform error: {0}".format(xfName))
                traceback.print_exc()
