'''
Created on 2016-03-26

@author: bdillman
'''
import unittest
import os
import logging

import testUtils
import project

class Test(unittest.TestCase):


    def setUp(self):
        testUtils.deleteTestApp()
        testUtils.copyTestApp()
        os.chdir(testUtils.testDest)
        logging.basicConfig(level=logging.DEBUG)

    def tearDown(self):
        os.chdir("..")
        testUtils.deleteTestApp()


    def testProjectExists(self):
        p = project.Project(os.getcwd())
        self.assertFalse(p.exists(), "found project in cwd")
        self.assertEqual(str(p.projectPath), os.getcwd())
        p.create()
        self.assertTrue(p.exists(), "found project in cwd")
        

    def testFindProjectInCwd(self):
        p = project.findProject(os.getcwd())
        self.assertIsNone(p, "found project in cwd")
        p = project.Project(os.getcwd())
        p.create()
        p = project.findProject(os.getcwd())
        self.assertIsNotNone(p, "found project in cwd")
        self.assertEqual(str(p.projectPath), os.getcwd())

    def testFindProjectInParent(self):
        p = project.findProject(os.getcwd())
        self.assertIsNone(p, "found project in cwd")
        p = project.Project(os.getcwd())
        p.create()
        os.chdir("bar")
        p = project.findProject(os.getcwd())
        self.assertIsNotNone(p, "found project in cwd")
        os.chdir("..")
        self.assertEqual(str(p.projectPath), os.getcwd())
        
        
    def testGetXformMgr(self):
        p = project.Project(os.getcwd())
        xm = p.getXformManager()
        self.assertIsNotNone(xm, "found xformMgr in project")
        

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()