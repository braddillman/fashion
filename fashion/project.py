'''
Created on 2016-04-29

Copyright (c) 2016 Bradford Dillman

@author: bdillman

Project class describes a fashion user project.
'''

import os
import shutil
import logging
import pathlib

import peewee

from . import fashionPortfolio
from . import library
from . import templates



#
# Get the FASHION_HOME directory.
#
FASHION_HOME = pathlib.Path(os.path.abspath(os.path.dirname(__file__)))



class Project:
	'''Represents a fashion user project.'''

	def __init__(self, projDir):
		'''
		Initialize a project mapped to the given directory, whether or not 
		the project or the directory actually exist.
		
		:param str projDir: where the project is located. 
		'''
		self.projectPath   = pathlib.Path(projDir)
		self.fashionPath   = self.projectPath / 'fashion'
		self.fashionDbPath = self.fashionPath / 'fashion.db'

	def exists(self):
		'''Check if this project exists.'''
		return self.fashionDbPath.exists()

	def findRelativePath(self, filename):
		'''
		Get a path or filename relative to the project path.
		
		:param str filename: input filename.
		'''
		return os.path.relpath(filename, str(self.projectPath))
	
	def create(self):
		'''Create a new fashion project.'''
		try:
			# create the project model
			projectModel = { 'projectPath'   : str(self.projectPath),
							 'fashionPath'   : str(self.fashionPath),
							 'fashionDbPath' : str(self.fashionDbPath),
							 'tmplMods'      : str(self.fashionPath / 'tmplMods'),
							 'bakPath'       : str(self.fashionPath / 'bak'),
							 'mirrorPath'    : str(self.fashionPath / 'mirror'),
							 'libraries'     : [str(self.fashionPath / 'library.yaml'),
											    str(FASHION_HOME     / 'library.yaml') ] }
			logging.debug("Creating fashion project: {0}".format(projectModel['projectPath']))
			
			tmplMods     = str(self.fashionPath / 'tmplMods')
			modelPath    = str(self.fashionPath / 'model')
			templatePath = str(self.fashionPath / 'template')
			xformPath    = str(self.fashionPath / 'xform')
			
			# create the ./fashion subdirs
			os.mkdir(projectModel['fashionPath'])
			os.mkdir(projectModel['bakPath'])
			os.mkdir(projectModel['mirrorPath'])
			os.mkdir(tmplMods)
			os.mkdir(modelPath)
			os.mkdir(templatePath)
			os.mkdir(xformPath)
			
			# create the database connection
			try:
				self.init_db()
			except peewee.OperationalError:
				# create the database schema
				fashionPortfolio.create_db()
				filename=os.path.join(projectModel['fashionPath'],"fashion.yaml")
				fashionPortfolio.createModel(projectModel, 'fashion_project', filename=filename)
				
			# default library
			lib = library.Library(projectModel['libraries'][0])
			lib.addGlob(glob="./model/", recursive=False,
					    role=3, kind='fashion_unknown', fileFormat='yaml')
			lib.addGlob(glob="./xform/", recursive=False,
					    role=4, fileFormat='python3')
			lib.addGlob(glob="./template/", recursive=False,
					    role=2, fileFormat='mako')
			lib.addGlob(glob="./xform/**/*.py", recursive=True,
					    role=4, fileFormat='python3')
			lib.save()
			
			self.projectModel = projectModel
			
			self.importModels()
				
		except FileExistsError:
			logging.warning("Can't create fashion project: {0} already exists".format(str(self.projectPath)))

	def importModels(self):
		'''Import all models from all libraries.'''
		for libFilename in self.projectModel['libraries']:
			l = library.Library(libFilename)
			l.load()
			l.importModels()
			
	def loadXforms(self):
		'''Import all xforms from all libraries.'''
		xfList = []
		for libFilename in self.projectModel['libraries']:
			l = library.Library(libFilename)
			l.load()
			xfList.extend(l.loadXforms())
		return xfList
	
	def loadTemplates(self):
		'''Load all template directories.'''
		dirs = []
		for libFilename in self.projectModel['libraries']:
			l = library.Library(libFilename)
			l.load()
			dirs.extend(l.getDirectories(2))
		templates.setDirectories(self.projectModel['projectPath'], self.projectModel['mirrorPath'], dirs, self.projectModel['tmplMods'])
		
	def getLocalLibrary(self):
		l = library.Library(self.projectModel['libraries'][0])
		l.load()
		return l
		
	def getLocalModelDir(self):
		return self.getLocalLibrary().getDirectories(3)[0]
		
	def getLocalTemplateDir(self):
		return self.getLocalLibrary().getDirectories(2)[0]
		
	def getLocalXformDir(self):
		return self.getLocalLibrary().getDirectories(4)[0]
	
	def destroy(self):
		'''Destroy an existing fashion project.''' 
		if self.exists():
			logging.debug("Destroying fashion project: {0}".format(str(self.projectPath)))
			shutil.rmtree(str(self.fashionPath))
		else:
			logging.debug("Can't destroy fashion project: {0} doesn't exist".format(str(self.projectPath)))
			
	def init_db(self):
		'''Initialize the fashion database.'''
		if fashionPortfolio.database == None:
			filename = str(self.fashionDbPath)
			fashionPortfolio.init_db(filename)
			
		self.projectModel = fashionPortfolio.getProjectModel()
		


def findProject(startDir):
	'''
	Find the root directory of a project by searching recursively upwards.
	
	:param str startDir: where to begin searching for project.
	:returns: the Project object, if found; otherwise None.
	:rtype: Project
	'''
	p = Project(startDir)
	while True:
		if p.exists():
			logging.debug("Found project: {0}".format(str(p.projectPath)))
			return p
		else:
			parent = p.projectPath.parent
			if parent == p.projectPath:
				break
			p = Project(parent)
	logging.debug("No project found: {0}".format(startDir))
	return None

