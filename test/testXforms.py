'''
Created on 2016-03-26

@author: bdillman
'''
import unittest
import os
import logging

import testUtils

import xforms
import project

class Test(unittest.TestCase):


    def setUp(self):
        testUtils.deleteTestApp()
        testUtils.copyTestApp()
        os.chdir(testUtils.testDest)
        p = project.Project(os.getcwd())
        p.create()
        testUtils.copyFashionStuff()
        logging.basicConfig(level=logging.DEBUG)

    def tearDown(self):
        os.chdir("..")
        testUtils.deleteTestApp()


    def testFindXformLocal(self):
        xfm = xforms.XformManager(["/bad/path", "fashion/xform"])
        self.assertIsNotNone(xfm, "found XformManager")
        xf = xfm.find("myXform")
        self.assertIsNotNone(xf, "found myXform")


    def testFindXformFashion(self):
        xfm = xforms.XformManager(["/bad/path", "fashion/xform", "../../xform"])
        self.assertIsNotNone(xfm, "found XformManager")
        xf = xfm.find("gen")
        self.assertIsNotNone(xf, "found myXform")


    def testXformExists(self):
        xf = xforms.Xform("fashion/xform/myXform.py")
        self.assertTrue(xf.exists(), "exists")
        xf = xforms.Xform("fashion/xform/notMyXform.py")
        self.assertFalse(xf.exists(), "exists")

    def testLoadXformLocal(self):
        xfm = xforms.XformManager(["/bad/path", "fashion/xform", "../../xform"])
        self.assertIsNotNone(xfm, "found XformManager")
        xf = xfm.find("myXform")
        self.assertIsNotNone(xf, "found myXform")
        xf.load()
        self.assertIsNotNone(xf.mod, "found python module")


    def testLoadXformFashion(self):
        xfm = xforms.XformManager(["/bad/path", "fashion/xform", "../../xform"])
        self.assertIsNotNone(xfm, "found XformManager")
        xf = xfm.find("gen")
        self.assertIsNotNone(xf, "found myXform")
        xf.load()
        self.assertIsNotNone(xf.mod, "found python module")


    def testFindAll(self):
        xfm = xforms.XformManager(["/bad/path", "fashion/xform", "../../xform"])
        self.assertIsNotNone(xfm, "found XformManager")
        xfList = xfm.findAll()
        self.assertIsNotNone(xfList, "found myXform")
        xfNames = [xf.modName for xf in xfList]
        self.assertIn("gen", xfNames)
        self.assertIn("myXform", xfNames)


    def testLoadAll(self):
        xfm = xforms.XformManager(["/bad/path", "fashion/xform", "../../xform"])
        self.assertIsNotNone(xfm, "found XformManager")
        xfm.loadAll()
        self.assertIsNotNone(xfm.xforms, "found myXform")
        self.assertEqual(len(xfm.xforms), 2, "number of xforms loaded")
        xfNames = [xf.modName for xf in xfm.xforms]
        self.assertIn("gen", xfNames)
        self.assertIn("myXform", xfNames)


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()