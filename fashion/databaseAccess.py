from tinydb import TinyDB
from tinydb.storages import JSONStorage
from tinydb.middlewares import CachingMiddleware

import os

class DatabaseAccess(object):
    '''
    Raw database access. This module might be unnecessary, it's just a simple 
    wrapper around TinyDB. It doesn't isolate the Query abstractions of TinyDB
    so we don't get any portability or independence from TinyDB. But it is a
    place to change storage, middleware, etc.
    '''

    def __init__(self, filename):
        '''
        Initialize a database with a file.
        :param filename: database filename.
        '''
        self.filename = str(filename)
        self.db = TinyDB(self.filename, storage=CachingMiddleware(JSONStorage))

    def close(self):
        '''Close the database file.'''
        self.db.close()

    def table(self, tableName):
        return self.db.table(tableName)

    def insert(self, *args, **kwargs):
        '''Insert an object into the database.'''
        return self.db.insert(*args, **kwargs)

    def get(self, *args, **kwargs):
        '''Get an object from the database.'''
        return self.db.Get(*args, **kwargs)

    def contains(self, *args, **kwargs):
        '''Test an object from the database.'''
        return self.db.Get(*args, **kwargs)

    def search(self, *args, **kwargs):
        '''Query for objects.'''
        return self.db.search(*args, **kwargs)

    def remove(self, *args, **kwargs):
        '''Remove objects by query.'''
        return self.db.remove(*args, **kwargs)
