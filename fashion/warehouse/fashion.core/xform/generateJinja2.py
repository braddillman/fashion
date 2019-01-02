'''
Created on 2018-12-21

Copyright (c) 2018 Bradford Dillman

Generate code from a model and a jinja2 template.
'''

import logging

from jinja2 import FileSystemLoader, Environment
from munch import munchify

from fashion.mirror import Mirror

# Module level code is executed when this file is loaded.
# cwd is where segment file was loaded.


def init(config, mdb, verbose=False, tags=None):
    '''cwd is where segment file was loaded.'''
    return [Generate(config)]


class Generate(object):
    '''Generate output by merging a model into a template to produce a file.'''

    def __init__(self, config):
        '''Constructor.'''
        self.name = config.moduleName
        self.tags = config.tags
        self.inputKinds = ["fashion.core.generate.jinja2.spec",
                           "fashion.core.mirror"]
        self.outputKinds = []

    def execute(self, mdb, verbose=False, tags=None):
        '''cwd is project root directory.'''
        # set up  mirrored directories
        mirCfg = munchify(mdb.getSingleton("fashion.core.mirror"))
        mirror = Mirror(mirCfg.projectPath, mirCfg.mirrorPath)
        genSpecs = mdb.getByKind(self.inputKinds[0])
        for genSpec in genSpecs:
            gs = munchify(genSpec)

            if mirror.isChanged(gs.targetFile):
                logging.error("Skipping {0}, file has changed.".format(gs.targetFile))
            else:
                env = Environment(loader=FileSystemLoader(gs.templatePath))
                template = env.get_template(gs.template)
                result = template.render(gs.model)
                with open(str(gs.targetFile), "w") as tf:
                    tf.write(result)
                mirror.copyToMirror(gs.targetFile)
