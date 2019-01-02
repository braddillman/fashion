from fashion.databaseAccess import DatabaseAccess
from fashion.modelAccess import ModelAccess
from fashion.portfolio import FASHION_WAREHOUSE_PATH
from fashion.runway import Runway
from fashion.schema import SchemaRepository
from fashion.warehouse import Warehouse

class DummyXform(object):

    def __init__(self, tags=None):
        self.name = "dummy"
        self.tags = [] if tags is None else tags
        self.inputKinds = []
        self.outputKinds = []
        self.executed = False

    def execute(self, mdb, tags=None):
        self.executed = True

class TestRunway(object):

    def test_create(self, tmp_path):
        dba = DatabaseAccess(tmp_path / "db.json")
        fw = Warehouse(FASHION_WAREHOUSE_PATH)
        wh = Warehouse(tmp_path, fw)
        wh.loadSegments()
        r = Runway(dba, wh)
        assert r is not None
    
    def test_loadSchemas(self, tmp_path):
        dba = DatabaseAccess(tmp_path / "db.json")
        fw = Warehouse(FASHION_WAREHOUSE_PATH)
        wh = Warehouse(tmp_path, fw)
        wh.loadSegments()
        r = Runway(dba, wh)
        r.loadSchemas()

    def test_loadModules(self, tmp_path):
        dba = DatabaseAccess(tmp_path / "db.json")
        fw = Warehouse(FASHION_WAREHOUSE_PATH)
        wh = Warehouse(tmp_path, fw)
        wh.loadSegments()
        r = Runway(dba, wh)
        r.loadModules()
        r.initModules()
        r.plan()
        r.execute()

    # def test_noPlan(self, tmp_path):
    #     s = Schedule()
    #     s.plan(DatabaseAccess(tmp_path / "db.json"))

    # def test_emptyPlan(self, tmp_path):
    #     s = Schedule([])
    #     s.plan(DatabaseAccess(tmp_path / "db.json"))

    # def test_plan(self, tmp_path):
    #     s = Schedule([DummyXform()])
    #     s.plan(DatabaseAccess(tmp_path / "db.json"))

    # def test_cycleDetection(self, tmp_path):
    #     x1 = DummyXform()
    #     x1.name = "dummy1"
    #     x1.inputKinds = ["kind1"]
    #     x1.outputKinds = ["kind1"]
    #     x2 = DummyXform()
    #     x2.name = "dummy2"
    #     x2.inputKinds = ["kind1"]
    #     x1.outputKinds = ["kind1"]
    #     s = Schedule([x1, x2])
    #     s.plan(DatabaseAccess(tmp_path / "db.json"))
    #     assert s.valid == False

    # def test_simple2(self, tmp_path):
    #     x1 = DummyXform()
    #     x1.name = "dummy1"
    #     x1.outputKinds = ["kind1"]
    #     x2 = DummyXform()
    #     x2.name = "dummy2"
    #     x2.inputKinds = ["kind1"]
    #     s = Schedule([x1, x2])
    #     dba = DatabaseAccess(tmp_path / "db.json")
    #     s.plan(dba)
    #     assert s.valid == True
    #     assert x1.executed == False
    #     assert x2.executed == False
    #     schemaRepo = SchemaRepository()
    #     s.execute(dba, schemaRepo)
    #     assert x1.executed == True
    #     assert x2.executed == True
