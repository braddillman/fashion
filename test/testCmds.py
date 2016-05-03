'''
Created on 2016-03-25

@author: bdillman
'''
import unittest

import os
import logging

import testUtils
import fashionCmds
import project


class Test(unittest.TestCase):
    """
    Test commands.
    """

    def setUp(self):
        testUtils.deleteTestApp()
        testUtils.copyTestApp()
        os.chdir(testUtils.testDest)
        logging.basicConfig(level=logging.DEBUG)
        self.runCmd(["init"])
        testUtils.copyFashionStuff()

    def tearDown(self):
        os.chdir("..")
        testUtils.deleteTestApp()
        
    def runCmd(self, args):
        args = ["-y"] + args
        fashionCmds.main(args)


#     def testVersion(self):
#         self.runCmd(["version"])
        
    @unittest.skip("not yet")
    def testXformGen(self):
        p = project.Project(os.getcwd())
        p.init_db()
        tgtMgr = p.getTargetManager()
        tgtMgr.createTarget("test.txt", "hello_world.tlt", "hello_world.yaml")
        self.runCmd(["xform", "gen"])

    def testXformGreetWorlds(self):
        p = project.Project(os.getcwd())
        p.init_db()
        tgtMgr = p.getTargetManager()
        tgtMgr.createTarget("test.txt", "hello_world.tlt", "hello_world.yaml")
        self.runCmd(["xform", "greetWorlds"])
        
if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testVersion']
    unittest.main()