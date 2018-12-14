from tinydb import TinyDB
from tinydb.storages import JSONStorage
from tinydb.middlewares import CachingMiddleware

class DatabaseAccess:
    '''Raw database access.'''

    def __init__(self, filename):
        ''' Initialize a database with a file.'''
        self.filename = filename
        # TODO: set up caching middleware
        self.db = TinyDB(self.filename, storage=CachingMiddleware(JSONStorage))

    def insert(self, *args, **kwargs):
        '''Insert an object into the database.'''
        self.db.insert(*args, **kwargs)

    def search(self, *args, **kwargs):
        '''Query for objects.'''
        self.db.search(*args, **kwargs)

    def remove(self, *args, **kwargs):
        '''Remove objects by query.'''
        self.db.remove(*args, **kwargs)
