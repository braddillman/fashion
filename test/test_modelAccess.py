from munch import munchify
from tinydb import Query

from fashion.databaseAccess import DatabaseAccess
from fashion.modelAccess import ModelAccess
from fashion.schema import SchemaRepository


class DummyContextOut(object):

    def __init__(self):
        self.name = "dummyContextOut"
        self.inputKinds = ["dummy.input"]
        self.outputKinds = ["dummy.output"]
        self.templatePath = []


class DummyContextIn(object):

    def __init__(self):
        self.name = "dummyContextIn"
        self.inputKinds = ["dummy.output"]
        self.outputKinds = []
        self.templatePath = []


class TestModelAccess(object):

    def test_create(self, tmp_path):
        dba = DatabaseAccess(tmp_path / "db.json")
        d = DummyContextOut()
        schemaRepo = SchemaRepository()
        with ModelAccess(dba, schemaRepo, d) as mdb:
            id = mdb.insert("dummy.output", {"name": "dummy model"})
            assert id is not None
        ctxs = dba.table('fashion.model.context').all()
        assert len(ctxs) == 1
        assert len(ctxs[0]["insert"]) == 1
        assert 'dummy.output' in ctxs[0]["insert"]
        assert id in ctxs[0]["insert"]['dummy.output']
        models = dba.table('dummy.output').all()
        assert len(models) == 1
        dba.close()

    def test_contextReset(self, tmp_path):
        '''
        Test that when a context is re-entered, the previous context data is
        reset.
        '''
        dba = DatabaseAccess(tmp_path / "db.json")
        d = DummyContextOut()
        schemaRepo = SchemaRepository()
        with ModelAccess(dba, schemaRepo, d) as mdb:
            id = mdb.insert("dummy.output", {"name": "dummy model"})
            assert id is not None
        ctxs = dba.table('fashion.model.context').all()
        assert len(ctxs) == 1
        models = dba.table('dummy.output').all()
        assert len(models) == 1
        # Now re-enter the same context
        with ModelAccess(dba, schemaRepo, d) as mdb:
            ctxs = dba.table('fashion.model.context').all()
            assert len(ctxs) == 0
            models = dba.table('dummy.output').all()
            assert len(models) == 0
            id = mdb.insert("dummy.output", {"name": "dummy model the second"})
            assert id is not None
        ctxs = dba.table('fashion.model.context').all()
        assert len(ctxs) == 1
        models = dba.table('dummy.output').all()
        assert len(models) == 1
        assert models[0]["name"] == "dummy model the second"
        dba.close()

    def test_reading(self, tmp_path):
        '''Test searching for models.'''
        dba = DatabaseAccess(tmp_path / "db.json")
        dOut = DummyContextOut()
        schemaRepo = SchemaRepository()
        with ModelAccess(dba, schemaRepo, dOut) as mdb:
            id = mdb.insert("dummy.output", {"name": "dummy model"})
        dIn = DummyContextIn()
        with ModelAccess(dba, schemaRepo, dIn) as mdb:
            m = mdb.getById("dummy.output", id)
            assert m is not None
            assert m["name"] == "dummy model"
            m = mdb.getByKind("dummy.output")
            assert m is not None
            assert len(m) == 1
            assert m[0]["name"] == "dummy model"
            dummyQ = Query()
            m = mdb.search("dummy.output", dummyQ.name == "dummy model")
            assert m is not None
            assert len(m) == 1
            assert m[0]["name"] == "dummy model"
        dba.close()
