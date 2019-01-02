import logging

from fashion.portfolio import Portfolio
from fashion.util import cd

class TestPortfolio(object):

    def test_init(self, tmp_path):
        logging.basicConfig(level=logging.DEBUG)
        with cd(tmp_path):
            pf = Portfolio(tmp_path)
            assert pf is not None
            assert pf.exists() == False

    def test_createDelete(self, tmp_path):
        logging.basicConfig(level=logging.DEBUG)
        with cd(tmp_path):
            pf = Portfolio(tmp_path)
            assert pf is not None
            assert pf.exists() == False
            pf.create()
            assert pf.exists() == True
            pf.delete()
            assert pf.exists() == False

    def test_saveLoad(self, tmp_path):
        logging.basicConfig(level=logging.DEBUG)
        with cd(tmp_path):
            pf = Portfolio(tmp_path)
            pf.create()
            pf.save()
            pf.db.close()
            pf2 = Portfolio(tmp_path)
            assert pf2.properties.name == "fashion"
