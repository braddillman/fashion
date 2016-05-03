'''
Created on 2016-03-26

@author: bdillman
'''

import os
import shutil

testDest = "testBox"
testSrc  = "testApp"

def copyTestApp():
    shutil.copytree(testSrc, testDest)

def deleteTestApp():
    try:
        shutil.rmtree(testDest)
    except FileNotFoundError:
        pass

def mergeTree(srcDir, destDir):
    if not os.path.isdir(srcDir):
        shutil.copy(srcDir, destDir)
        return
    for src in os.listdir(srcDir):
        srcFile  = "{0}/{1}".format(srcDir,  src)
        destFile = "{0}/{1}".format(destDir, src)
        if(os.path.isdir(srcFile)):
            mergeTree(srcFile, destFile)
        else:
            shutil.copy(srcFile, destFile)
    
def copyFashionStuff():
    mergeTree("../testFashion/fashion/model",    "./fashion/model")
    mergeTree("../testFashion/fashion/template", "./fashion/template")
    mergeTree("../testFashion/fashion/xform",    "./fashion/xform")
