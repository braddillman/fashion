'''
Various utilities for fashion.

Created on 2018-12-19 Copyright (c) 2018 Bradford Dillman
'''

import logging
import os.path

class cd:
    '''Context manager for changing the current working directory'''
    def __init__(self, newPath):
        self.newPath = os.path.expanduser(str(newPath))

    def __enter__(self):
        self.savedPath = os.getcwd()
        logging.debug("cd {0} -> {1}".format(self.savedPath, self.newPath))
        os.chdir(self.newPath)

    def __exit__(self, etype, value, traceback):
        logging.debug("cd {1} -> {0}".format(self.savedPath, self.newPath))
        os.chdir(self.savedPath)
