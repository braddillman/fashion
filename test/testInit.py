'''
Created on 2016-03-25

@author: bdillman
'''
import unittest

import os
import logging

import testUtils
import fashionCmds


class Test(unittest.TestCase):
    """
    Test commands for initializing and deleting a project.
    """
    
    def setUp(self):
        testUtils.deleteTestApp()
        testUtils.copyTestApp()
        os.chdir(testUtils.testDest)
        logging.basicConfig(level=logging.DEBUG)

    def tearDown(self):
        os.chdir("..")
        testUtils.deleteTestApp()
        
    def runCmd(self, args):
        args = ["-y"] + args
        fashionCmds.main(args)

    def testInit(self):
        self.runCmd(["init"])

    def testInit2(self):
        self.runCmd(["init"])
        self.runCmd(["init"])
 
    def testKill(self):
        self.runCmd(["init"])
        self.runCmd(["kill"])
 
    def testKill2(self):
        self.runCmd(["kill"])

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()