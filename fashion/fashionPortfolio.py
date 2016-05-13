'''
Created on 2016-04-17

Copyright (c) 2016 Bradford Dillman

@author: bdillman

Manage files using metadata stored in a database.
'''
import datetime
import logging
import os.path

import peewee
import playhouse.sqlite_ext
import ruamel.yaml



database_proxy = peewee.Proxy()
database = None

def init_db(filename):
    '''Initialize a connection to the database.'''
    logging.debug("init_db({})".format(filename))
    global database
    global database_proxy
    database = peewee.SqliteDatabase(filename)
    database_proxy.initialize(database)
    database.connect()
    return True

def create_db():
    '''Create a new database schema from an existing database connection.'''
    database.create_tables([FashionFile], safe=True)



class BaseModel(peewee.Model):
    '''Just for architectures' sake.'''
    class Meta:
        database = database_proxy




class FashionFile(BaseModel):
    '''Database record with metadata about a file in the filesystem.'''

    id = playhouse.sqlite_ext.PrimaryKeyAutoIncrementField(index=True,
                                                           unique=True,
                                                           null=False,
                                                           primary_key=True)
    
    # role target=1, template=2, model=3, xform=4
    role = peewee.IntegerField(index=True, unique=False, null=False)
    
    # (relative?) filename
    filename = peewee.CharField(index=True, unique=True, null=True)
    
    # last know timestamp of file
    timestamp = peewee.DateTimeField(index=True, unique=False, null=True)
    
    # model kind
    kind = peewee.CharField(index=True, unique=False, null=True)     
    
    # file format
    fileFormat = peewee.CharField(index=True, unique=False, null=True)
    
    # content of anonymous file
    content = peewee.BlobField(index=False, unique=False, null=True)
    
    # last time this record was modified
    lastModTime = peewee.DateTimeField(default=datetime.datetime.now)
    
    def loadFile(self):
        '''
        Load the file from the filesystem.
        Returns True for success, False for failure.
        '''
        if self.role == 3: # model
            if self.fileFormat == 'yaml': 
                if self.filename == None:
                    self.model = ruamel.yaml.load(self.content)
                    return self.model
                else:
                    with open(self.filename, 'r') as stream:
                        self.model = ruamel.yaml.load(stream)
                        return self.model
    
    def exists(self):
        '''Returns True iff filename exists on the filesystem.'''
        return os.path.exists(self.filename)
    
    def saveFile(self):
        '''Save self.model to filename.'''
        if self.content == None:
            raise("nothing to save")
        if self.filename == None:
            raise("no filename")
        with open(self.filename, 'w') as file:
            logging.debug("FashionFile.save({})".format(self.filename))
            file.write(self.content)
    


def importFile(**kwargs):
    '''Import a file with metadata.'''
    logging.debug("importFile({0})".format(kwargs))
    return FashionFile.get_or_create(**kwargs) 

def createModel(model, kind, fileFormat='yaml', filename=None):
    '''Create a new model with metadata.'''
    if fileFormat == 'yaml':
        content = ruamel.yaml.dump(model, default_flow_style = False)
    file = FashionFile.create(role=3, kind=kind, content=content, filename=filename, fileFormat=fileFormat)
    if filename != None:
        file.saveFile()
    return file

def getProjectModel():
    '''Get the project model for this project.'''
    pm = ruamel.yaml.load(FashionFile.get(kind='fashion_project').content)
    logging.debug("pm={0}".format(pm))
    return pm

def getModelFiles(kind):
    '''Get all models of the given kind.'''
    return FashionFile.select().where(FashionFile.role==3, FashionFile.kind==kind)
    
def clean():
    '''Delete model metadata for all but the project model.'''
    q = FashionFile.delete().where((FashionFile.role==3) & (FashionFile.kind != 'fashion_project'))
    q.execute()