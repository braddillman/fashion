'''
Portfolio - the project definition
===================================

The portfolio is the root of a fashion-enhanced project, located at the 
./fashion directory created during 'fashion init'.

It is normal and expected to directly edit files in the fashion directories,
so getting to know the directory structure will aid navigation.

project directory - your project
/fashion - added by 'fashion init'
/fashion/warehouse - contains local segments

Created on 2018-12-14 Copyright (c) 2018 Bradford Dillman
'''

import copy
import shutil
import logging
import json

from pathlib import Path

from munch import Munch, munchify

from fashion.databaseAccess import DatabaseAccess
from fashion.mirror import Mirror
from fashion.modelAccess import ModelAccess
from fashion.runway import Runway
from fashion.segment import Segment
from fashion.util import cd
from fashion.warehouse import Warehouse

#
# Get the FASHION_HOME directory.
#
FASHION_HOME = Path(__file__).resolve().parent
FASHION_WAREHOUSE_PATH = FASHION_HOME / "warehouse"


class Portfolio(object):
    '''Represents a fashion user project.'''

    def __init__(self, projDir):
        '''
        Initialize a portfolio mapped to the given directory, whether or not 
        the directory actually exists.

        :param str projDir: where the project is located. 
        '''
        self.projectPath = projDir.absolute()
        self.fashionPath = self.projectPath / 'fashion'
        self.mirrorPath = self.fashionPath / 'mirror'
        self.portfolioPath = self.fashionPath / 'portfolio.json'
        self.fashionDbPath = self.fashionPath / 'database.json'
        self.mirror = Mirror(self.projectPath, self.mirrorPath)
        if self.fashionDbPath.exists():
            self.load()
            self.db = DatabaseAccess(self.fashionDbPath)

    def __setDefaultProperties(self):
        self.properties = munchify({
            "name": "fashion",
            "defaultSegment": "local",
            "warehouses": [(self.fashionPath / 'warehouse').as_posix()]
        })

    def loadWarehouses(self):
        self.warehouse = None
        wl = copy.copy(self.properties.warehouses)
        wl.append(FASHION_WAREHOUSE_PATH.as_posix())
        wl.reverse()
        for wp in wl:
            self.warehouse = Warehouse(Path(wp), self.warehouse)

    def exists(self):
        '''Check if this project exists.'''
        return self.fashionPath.exists()

    def create(self):
        '''Create a new portfolio.'''
        if not self.exists():
            self.segments = {}
            self.__setDefaultProperties()
            self.fashionPath.mkdir(parents=True, exist_ok=True)
            (self.fashionPath / "warehouse").mkdir(parents=True, exist_ok=True)
            self.db = DatabaseAccess(self.fashionDbPath)
            self.loadWarehouses()
            self.warehouse.newSegment("local", self.db)
            self.save()

    def delete(self):
        '''Delete an existing project.'''
        if self.exists():
            self.db.close()
            shutil.rmtree(str(self.fashionPath))

    def save(self):
        '''Save the portfolio.'''
        with self.portfolioPath.open(mode="w") as pf:
            pf.write(self.properties.toJSON(sort_keys=True, indent=4))

    def load(self):
        '''Load a portfolio from a file.'''
        with self.portfolioPath.open(mode='r') as fd:
            dict = json.loads(fd.read())
            self.properties = munchify(dict)
        self.loadWarehouses()

    def defaultSegment(self):
        return self.warehouse.loadSegment(self.defaultSegmentName(), self.db)

    def defaultSegmentName(self):
        return self.properties.defaultSegment

    def setDefaultSegment(self, segname):
        self.properties.defaultSegment = segname

    def getRunway(self, tags=None):
        '''
        Get a Runway for this Portfolio.

        :param boolean verbose: True if the runway should be verbose.
        :param list tags: a list of tags for the Runway to include.
        :returns: a Runway object.
        :rtype: fashion.Runway
        '''
        self.warehouse.loadSegments(self.db)
        r = Runway(self.db, self.warehouse)
        r.loadModules()
        r.initModules()
        return r

    def normalizeFilename(self, filename):
        '''Convert filename to realtive to project directory.'''
        fn = Path(filename).absolute()
        return fn.relative_to(self.projectPath)


def findPortfolio(startDir=Path.cwd()):
    '''
    Find the root directory of a project by searching recursively upwards.

    :param str startDir: where to begin searching for project.
    :returns: the Portfolio object, if found; otherwise None.
    :rtype: Portfolio
    '''
    p = Portfolio(startDir)
    while True:
        if p.exists():
            logging.debug("Found portfolio: {0}".format(str(p.projectPath)))
            return p
        else:
            parent = p.projectPath.parent
            if parent == p.projectPath:
                break
            p = Portfolio(parent)
    logging.debug("No portfolio found: {0}".format(startDir))
    return None
