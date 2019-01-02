'''
Created on 2018-12-14

Copyright (c) 2018 Bradford Dillman

@author: Bradford Dillman

Portfolio class describes a fashion user project.
'''

import os
import shutil
import logging
import pathlib
import json

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
FASHION_HOME = pathlib.Path(os.path.abspath(os.path.dirname(__file__)))
FASHION_WAREHOUSE_PATH = FASHION_HOME / "warehouse"


class Portfolio(object):
    '''Represents a fashion user project.'''

    def __init__(self, projDir):
        '''
        Initialize a portfolio mapped to the given directory, whether or not 
        the directory actually exists.

        :param str projDir: where the project is located. 
        '''
        self.projectPath = pathlib.Path(str(projDir))
        self.fashionPath = self.projectPath / 'fashion'
        self.warehousePath = self.fashionPath / 'warehouse'
        self.warehouse = Warehouse(
            str(self.warehousePath), 
            Warehouse(str(FASHION_WAREHOUSE_PATH)))
        self.mirrorPath = self.fashionPath / 'mirror'
        self.portfolioPath = self.fashionPath / 'portfolio.json'
        self.fashionDbPath = self.fashionPath / 'database.json'
        self.mirror = Mirror(self.projectPath, self.mirrorPath)
        if self.fashionDbPath.exists():
            self.load()
            self.db = DatabaseAccess(self.fashionDbPath)

    def exists(self):
        '''Check if this project exists.'''
        return self.fashionPath.exists()

    def create(self):
        '''Create a new portfolio.'''
        if not self.exists():
            self.segments = {}
            self.properties = munchify({
                "name": "fashion",
                "defaultSegment": "local",
                "segments": ["local"]
            })
            os.mkdir(str(self.fashionPath))
            os.mkdir(str(self.warehousePath))
            self.db = DatabaseAccess(self.fashionDbPath)
            self.warehouse.newSegment("local")
            self.save()

    def delete(self):
        '''Delete an existing project.'''
        if self.exists():
            self.db.close()
            shutil.rmtree(str(self.fashionPath))

    def save(self):
        '''Save the portfolio.'''
        with open(str(self.portfolioPath), "w") as pf:
            pf.write(self.properties.toJSON(sort_keys=True, indent=4))

    def load(self):
        '''Load a portfolio from a file.'''
        with open(str(self.portfolioPath), 'r') as fd:
            dict = json.loads(fd.read())
            self.properties = munchify(dict)

    def getRunway(self, verbose=False, tags=None):
        '''Get a Runway for this Portfolio.'''
        self.warehouse.loadSegments()
        r = Runway(self.db, self.warehouse)
        r.loadModules(verbose=verbose)
        r.initModules(verbose=verbose)
        return r



def findPortfolio(startDir):
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
