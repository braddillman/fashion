import logging
import shutil

from pathlib import Path, PurePath

from jinja2 import ChoiceLoader, FileSystemLoader, Environment
from jinja2.exceptions import TemplateNotFound
from munch import munchify

from fashion.util import cd

def init(config, codeRegistry, verbose=False, tags=None):
    '''cwd is where segment file was loaded.'''
    mdb = codeRegistry.getService('fashion.prime.modelAccess')
    args = munchify(mdb.getSingleton("fashion.prime.args"))
    if "force" in args:
        f = args.force
    else:
        f = False
    pf = munchify(mdb.getSingleton("fashion.prime.portfolio"))
    codeRegistry.addService(MirrorService(Path(pf.projectPath), Path(pf.mirrorPath), force=f))
    codeRegistry.addService(TemplateService())
    codeRegistry.addService(GenerateService(codeRegistry))
    # identifier service

class MirrorService(object):

    def __init__(self, projDir, mirrorDir, force=False):
        self.name = "fashion.core.mirror"
        self.version = "1.0.0"
        self.projDir = projDir
        self.mirrorDir = mirrorDir
        self.force = force

    def getRelativePath(self, filename):
        '''Get path of filename relative to projDir.'''
        return filename.relative_to(self.projDir)

    def getMirrorPath(self, filename):
        '''Get path to mirror file given for a filename.'''
        return PurePath.joinpath(self.mirrorDir, self.getRelativePath(filename.absolute()))

    def copyToMirror(self, filename):
        '''Copy a file to its mirror path.'''
        mirPath = self.getMirrorPath(filename)
        destDir = mirPath.parent
        destDir.mkdir(parents=True, exist_ok=True)
        shutil.copy2(str(filename), str(mirPath))

    def isChanged(self, filename):
        '''Compare file to mirrored file, return True if filename is strictly newer.'''
        # Force overwrites by always returning no change.
        if self.force:
            return False
        mirFile = self.getMirrorPath(filename)
        if not mirFile.exists():
            return False
        if not filename.exists():
            return False
        mirrTime = mirFile.stat().st_mtime
        projTime = filename.stat().st_mtime
        return projTime > mirrTime

class TemplateService(object):

    def __init__(self):
        self.name = "fashion.core.template"
        self.version = "1.0.0"

        self.defPath = []
        self.defAbsDir = None
        self.cfgPath = []
        self.cfgAbsDir = None

    def getDefaultLoader(self):
        with cd(self.defAbsDir):
            defPath = [Path(p).absolute().as_posix() for p in self.defPath]
        with cd(self.cfgAbsDir):
            cfgPath = [Path(p).absolute().as_posix() for p in self.cfgPath]
        loader = ChoiceLoader([
            FileSystemLoader(cfgPath),
            FileSystemLoader(defPath)])
        return loader

    def setDefinitionPath(self, absDir, pathList):
        self.defPath = pathList
        self.defAbsDir = absDir

    def setConfigurationPath(self, absDir, pathList):
        self.cfgPath = pathList
        self.cfgAbsDir = absDir

class GenerateService(object):
    '''Generate output by merging a model into a template to produce a file.'''
    def __init__(self, codeRegistry):
        '''Constructor.'''
        self.name = "fashion.core.generate"
        self.version = "1.0.0"
        self.codeRegistry = codeRegistry

    def generate(self, model, template, targetFile, templateLoader=None):
        mdb = self.codeRegistry.getService('fashion.prime.modelAccess')
        mirror = self.codeRegistry.getService('fashion.core.mirror')
        loader = templateLoader
        if loader is None:
            templateSvc = self.codeRegistry.getService('fashion.core.template')
            loader = templateSvc.getDefaultLoader()
        if mirror.isChanged(Path(targetFile)):
            logging.warning("Skipping {0}, file has changed.".format(targetFile))
        else:
            try:
                env = Environment(loader=loader)
                template = env.get_template(template)
                result = template.render(model)
                targetPath = Path(targetFile)
                with targetPath.open(mode="w") as tf:
                    tf.write(result)
                mirror.copyToMirror(targetPath)
                mdb.outputFile(targetPath)
            except TemplateNotFound:
                logging.error("TemplateNotFound: {0}".format(template))
