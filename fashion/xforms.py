'''
Created on 2016-04-29

Copyright (c) 2016 Bradford Dillman

@author: bdillman

Describe and manipulate xforms, which are python3 modules with specific
requirements.
'''

import os.path
import importlib.util
import logging
import inspect

from . import fashionPortfolio



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
				self.isLoaded = True
				func = self.mod.xform
				self.args = inspect.getargspec(func).args
			except AttributeError:
				logging.warning("Failed to load: {0}".format(self.filename))
		return self.isLoaded
		
	def exists(self):
		'''
		Tests for existence of this Xform.
		:returns: true if Xform exists.
		'''
		return os.path.exists(self.filename)
	
	def verify(self):
		'''Verify the xform is well formed and could be executed.'''
		if not hasattr(self.mod, 'inputKinds'):
			logging.debug("missing inputKinds xform: {0}".format(self.modName))
			return False
		if not hasattr(self.mod, 'outputKinds'):
			logging.debug("missing outputKinds xform: {0}".format(self.modName))
			return False
		if not hasattr(self.mod, 'xform'):
			logging.debug("missing xform xform: {0}".format(self.modName))
			return False
		return True



class XformPlan(object):
	'''An execution plan for a set of xforms.'''
	def __init__(self, xfCollection = []):
		self.xfSet = set(xfCollection)
		
	def plan(self):
		'''Construction the xform execution plan.'''
		self.goodXforms = set()
		for xf in self.xfSet:
			logging.debug("verify xform: {0}".format(xf.modName))
			if hasattr(xf, 'mod'):
				if xf.verify():
					self.goodXforms.add(xf)
			else:
				logging.debug("no module skipping xform: {0}".format(xf.modName))
		self.badXforms   = self.xfSet - self.goodXforms
		for xf in self.badXforms:
			logging.warn("bad xform: {0}".format(xf.modName))
		self.xfByName    = {xf.modName:xf for xf in self.goodXforms}
		self.xfNames     = set(self.xfByName)
		
		self.xfOutputs   = {xf.modName:set(xf.mod.outputKinds()) for xf in self.goodXforms}
		self.xfInputs    = {xf.modName:set(xf.mod.inputKinds())  for xf in self.goodXforms}
		
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
			# fetch inputs
			inputs = {}
			for inpKind in self.xfInputs[xfName]:
				# fetch inp
				inputs[inpKind] = fashionPortfolio.getModelFiles(inpKind)
			xf.mod.police(**inputs)
			xf.mod.xform(**inputs)
