'''
Default xform module.

Multiple xform objects may be defined and configured in a single xform module
file.

Checklist:
- define xform objects
- configure and return them in a list in init(...)

for each xform object:
- assign a unique name
- define inputKinds and outputKinds lists
- define the execute(...) method
'''

import logging


# Module level code is executed when this file is loaded.
# Working directory is where segment file was loaded.


# init is called to produce xform objects from xform modules.
def init(config, mdb, verbose=False, tags=None):
    '''
    Create and return a list of xform objects.

    :param config: is the xformConfig object from the segment file.

    :param mdb: is a ModelAccess object, where inputKinds, outputKinds,
    templatePath, etc. are from the xformConfig object.

    :param tags: is a list of tags specified at init time, which might alter
    the init behavior.
    '''
    # Working directory is where segment file was loaded.
    logging.debug("module {0} init...".format(config.moduleName))

    # Create and return a list of xform objects.
    return [ MyXform(config, mdb, verbose, tags) ]


class MyXform(object):
    '''MyXform object.'''

    def __init__(self, config, mdb, verbose, tags):
        '''
        Constructor, called from init(...) above.

        :param config: is the xformConfig object from the segment file.

        :param mdb: is a ModelAccess object, where inputKinds, outputKinds,
        templatePath, etc. are from the xformConfig object.

        :param tags: is a list of tags specified at init time, which might alter
        the init behavior.
        '''
        # Working directory is where segment file was loaded.

        self.name = 'my.unique.xform.object.name'
        logging.debug("{0} __init___...".format(self.name))

        # Save tags for later, just in case.
        self.config = config
        self.tags = tags

        # Default to the inputKinds and outputKinds specified in the config,
        # or change them to anything. The config inputKinds and outputKinds
        # only affect the ModelAccess mdb in the module init() above and
        # this constructor.
        self.inputKinds = config.inputKinds
        self.outputKinds = config.outputKinds

    def execute(self, mdb, verbose=False, tags=None):
        '''
        execute is called to actually perform the xform.

        :param mdb: is a ModelAccess object, where inputKinds and outputKinds
        are from this object, set in the constructor above.

        :param tags: is a list of tags specified at init time, which might alter
        the init behavior.
        '''
        # Working directory is project root directory.
        logging.debug("{0} executing...".format(self.name))

        # xform code goes here.

        model = {}
        template = "{{ template }}"
        targetFile = "{{ targetFile }}}"
        mdb.generate(model, template, targetFile)
