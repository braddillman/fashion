from fashion.databaseAccess import DatabaseAccess

class TestDatabaseAccess(object):

    def test_init(self, tmp_path):
        fashionDbPath = tmp_path / 'fashion_database.json'
        db = DatabaseAccess(fashionDbPath)
        assert db is not None
