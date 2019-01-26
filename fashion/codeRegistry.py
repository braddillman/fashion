'''
ServiceRegistry
'''

import logging

from packaging.specifiers import SpecifierSet
from packaging.version import Version


class CodeRegistry(object):
    '''
    ServiceRegistry
    '''

    def __init__(self, dba):
        '''Constructor.'''
        self.dba = dba
        self.servicesByName = {}
        self.xformObjectsByName = {}
        self.cfgByName = {}

    def getService(self, serviceName, versionSpec=None):
        '''
        Look for a named service matching optional versionCriteria.
        If versionCriteria has multiple matches, the result is the newest match.
        If no service is located, result is None.
        '''
        if serviceName not in self.servicesByName:
            return None

        services = self.servicesByName[serviceName]
        versioned = [(Version(s.version), s) for s in services]
        ranked = sorted(versioned, key=lambda ver: ver[0], reverse=True)
        if versionSpec is None:
            return ranked[0][1]

        spec = SpecifierSet(versionSpec)
        matches = [vs for vs in ranked if vs[0] in spec]
        if len(matches) == 0:
            return None
        return matches[0][1]

    def addService(self, service):
        '''
        Add a new service with a unique version.
        Overwriting an existing version is rejected.
        Returns True on success.
        '''
        verbose = self.dba.isVerbose()
        name = service.name
        if name not in self.servicesByName:
            self.servicesByName[name] = [service]
            if verbose:
                print("Add service: {0} v{1}".format(name, service.version))
            return True
        testService = self.getService(name, "=="+service.version)
        if testService is not None:
            logging.error("Duplicate service registration: {0} v{1}".format(
                name, service.version))
            return False
        self.servicesByName[name].append(service)
        if verbose:
            print("Add service: {0}".format(name))
        return True

    def removeService(self, serviceName, version):
        '''
        Remove a specific service.
        Returns True only if service was removed.
        '''
        if serviceName not in self.servicesByName:
            return False
        verbose = self.dba.isVerbose()
        spec = SpecifierSet("!="+version)
        svcs = self.servicesByName[serviceName]
        shutdown = [s for s in svcs if Version(s.version) not in spec]
        remainder = [s for s in svcs if Version(s.version) in spec]
        self.servicesByName[serviceName] = remainder
        for s in shutdown:
            if verbose:
                print("Shutdown service {0} v{1}".format(s.name, s.version))
            if hasattr(s, "shutdown"):
                s.shutdown()
        return len(remainder) < len(svcs)

    def shutdownAllServices(self):
        '''Call shutdown on all services.'''
        verbose = self.dba.isVerbose()
        for _, svcs in self.servicesByName.items():
            for s in svcs:
                if verbose:
                    print("Shutdown service {0} v{1}".format(s.name, s.version))
                if hasattr(s, "shutdown"):
                    s.shutdown()

    def setObjectConfig(self, cfg):
        self.segmentConfig = cfg

    def getObjectConfig(self, objectName):
        '''
        Look for a named xform object.
        If no xform object is located, result is None.
        '''
        if objectName not in self.cfgByName:
            return None
        return self.cfgByName[objectName]

    def getXformObject(self, objectName):
        '''
        Look for a named xform object.
        If no xform object is located, result is None.
        '''
        if objectName not in self.xformObjectsByName:
            return None
        return self.xformObjectsByName[objectName]

    def addXformObject(self, newObj):
        '''
        Add a new xform object with a unique version.
        Newer versions overwrite strictly older versions.
        Returns True on success.
        '''
        verbose = self.dba.isVerbose()
        name = newObj.name
        if name not in self.xformObjectsByName:
            self.xformObjectsByName[name] = newObj
            self.cfgByName[name] = self.segmentConfig
            if verbose:
                print("Add xform object: {0} v{1}".format(name, newObj.version))
            return True

        existObj = self.xformObjectsByName[name]
        existVer = Version(existObj.version)
        newVer = Version(newObj.version)

        if existVer >= newVer:
            logging.error("Duplicate xform object registration: {0} v{1}".format(
                    name, newObj.version))
            return False

        self.xformObjectsByName[name] = newObj
        self.cfgByName[name] = self.segmentConfig
        if verbose:
            print("Add xform object: {0} v{1}".format(name, newObj.version))
        return True

    def removeXformObject(self, objectName):
        '''
        Remove a specific object.
        Returns True only if service was removed.
        '''
        if objectName not in self.xformObjectsByName:
            return False

        verbose = self.dba.isVerbose()
        if verbose:
            print("Remove xform object: {0} v{1}".format(objectName, self.xformObjectsByName[objectName].version))

        del self.xformObjectsByName[objectName]
        return True
