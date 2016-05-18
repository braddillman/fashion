'''
Created on 2016-04-29

Copyright (c) 2016 Bradford Dillman

@author: bdillman

Describe and manipulate xforms, which are python3 modules with specific
requirements.
'''

import importlib.util
import inspect
import logging
import os.path
import traceback

from . import fashionPortfolio
from . import xformUtil



def loadModule(modName, filename):
	'''Load a python module from a file. Python 3.5+'''
	# spec = importlib.util.spec_from_file_location("module.name", "/path/to/file.py")
	spec = importlib.util.spec_from_file_location(modName, filename)
	mod = importlib.util.module_from_spec(spec)
	spec.loader.exec_module(mod)
	return mod

class Xform():
	'''Represents a specific transform operation.'''
	def __init__(self, filename):
		'''Initialize a transform file a Python module filename.'''
		self.filename = filename
		self.modName = os.path.basename(filename).split(".")[0]
		self.isLoaded = False
		
	def load(self):
		'''
		Load the python module for this transform.
		:return: True if loaded
		'''
		if not self.isLoaded:
			try:
				logging.debug("loading xform: {0}".format(self.filename))
				self.spec = importlib.util.spec_from_file_location(self.modName, self.filename)
				self.mod = importlib.util.module_from_spec(self.spec)
				self.spec.loader.exec_module(self.mod)
				try:
					self.outputKinds = self.mod.outputKinds()
				except:
					logging.error("outputKinds error: {0}".format(self.filename))
					traceback.print_exc()
					return False

				func = self.mod.xform
				self.xform_args = inspect.getargspec(func).args
				self.xformInputKinds = set(self.xform_args)
				if hasattr(self.mod, 'police'):
					func = self.mod.police
					self.police_args = inspect.getargspec(func).args
					self.policeInputKinds = set(self.police_args)
					self.inputKinds = self.xformInputKinds | self.policeInputKinds
					self.hasPolice = True
				else:
					self.inputKinds = self.xformInputKinds
					self.hasPolice = False
				self.isLoaded = True
			except AttributeError:
				logging.warning("Failed to load: {0}".format(self.filename))
		return self.isLoaded
	
	def exists(self):
		'''
		Tests for existence of this Xform.
		:returns: true if Xform exists.
		'''
		return os.path.exists(self.filename)
	
	def police(self, **inputs):
		xformUtil.current_xform_name = self.filename
		xformUtil.current_output_kinds = set() # no output for police
		if hasattr(self.mod, 'police'):
			return self.mod.police(**inputs)
	
	def execute(self, **inputs):
		xformUtil.current_xform_name = self.filename
		xformUtil.current_output_kinds = self.outputKinds
		self.mod.xform(**inputs)



class XformPlan(object):
	'''An execution plan for a set of xforms.'''
	def __init__(self, xfCollection = []):
		self.xfSet = set(xfCollection)
		
	def plan(self):
		'''Construction the xform execution plan.'''
		self.goodXforms  = {xf for xf in self.xfSet if xf.isLoaded}
		self.badXforms   = self.xfSet - self.goodXforms
		for xf in self.badXforms:
			logging.warn("bad xform: {0}".format(xf.filename))
		self.xfByName    = {xf.modName:xf for xf in self.goodXforms}
		self.xfNames     = set(self.xfByName)
		
		self.xfOutputs   = {xf.modName:set(xf.outputKinds) for xf in self.goodXforms}
		self.xfInputs    = {xf.modName:set(xf.inputKinds)  for xf in self.goodXforms}
		
		self.allOutputs  = {ok for _, outKinds in self.xfOutputs.items() 
						       for ok in outKinds}
		self.allInputs   = {ik for _, inKinds  in self.xfInputs.items()
						       for ik in inKinds}
		
		self.leafInputs  = self.allInputs  - self.allOutputs
		self.leafoutputs = self.allOutputs - self.allInputs
		self.intermed    = self.allInputs  & self.allOutputs
		
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
			
		self.xfPre = {}
		for xfName in self.xfNames:
			for inp in self.xfInputs[xfName]:
				if inp in self.xfByOutput.keys():
					self.xfPre[xfName] = self.xfByOutput[inp]
		
		self.xfPost = {}
		for xfName in self.xfNames:
			for outp in self.xfOutputs[xfName]:
				if outp in self.xfByInput.keys():
					self.xfPost[xfName] = self.xfByInput[outp]
				
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
			logging.warn("xform dependency cycle detected")
		for idx, xfName in enumerate(self.execList):
			logging.debug("{0}:{1}".format(idx, xfName))
			
	def execute(self):
		'''Execute all the xforms planned in self.execList.'''
		for xfName in self.execList:
			xf = self.xfByName[xfName]
			
			if xf.hasPolice:
				inputs = {inpKind:fashionPortfolio.getModelFiles(inpKind) 
						  for inpKind in xf.policeInputKinds}
				try:
					if xf.police(**inputs):
						# user verification failed
						logging.error("aborting, police failed: {0}".format(xf.filename))
						return
				except:
					logging.error("aborting, police error: {0}".format(xf.filename))
					traceback.print_exc()
				
			inputs = {inpKind:fashionPortfolio.getModelFiles(inpKind) 
					  for inpKind in xf.xformInputKinds}
			try:
				xf.execute(**inputs)
			except:
				logging.error("aborting, xform error: {0}".format(xf.filename))
				traceback.print_exc()
