from fashion import databaseAccess

class TestDatabaseAccess(object):
    
    def test_init(self):
        db = databaseAccess.DatabaseAccess("fashion_database.json")
        assert db is not None