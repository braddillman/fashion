from fashion.portfolio import FASHION_WAREHOUSE_PATH
from fashion.warehouse import Warehouse


class TestWarehouse(object):
    '''Test the Warehouse class.'''

    def test_globalWarehouse(self):
        '''Test the default global warehouse.'''
        assert FASHION_WAREHOUSE_PATH is not None
        fw = Warehouse(FASHION_WAREHOUSE_PATH)
        globalSegNames = fw.listSegments()
        assert "fashion.core" in globalSegNames

    def test_defaultLocalWarehouse(self, tmp_path):
        '''Test the default local warehouse.'''
        lw = Warehouse(tmp_path)
        localSegNames = lw.listSegments()
        assert len(localSegNames) == 0

    def test_warehouseFallback(self, tmp_path):
        '''Test the local warehouse refers properly to another warehouse.'''
        fw = Warehouse(FASHION_WAREHOUSE_PATH)
        lw = Warehouse(tmp_path, fw)
        coreSeg = lw.loadSegment("fashion.core")
        assert coreSeg is not None

    def test_newSegment(self, tmp_path):
        '''Test creating a new segment in a warehouse.'''
        newSegName = "custom"
        wh = Warehouse(tmp_path)
        wh.newSegment(newSegName)
        segNames = wh.listSegments()
        assert len(segNames) == 1
        assert segNames[0] == newSegName
        seg = wh.loadSegment(segNames[0])
        assert seg is not None

    def test_loadSegments(self, tmp_path):
        '''Test loading all segments in a warehouse.'''
        wh = Warehouse(tmp_path)
        newSegName = "custom"
        wh.newSegment(newSegName)
        segs = wh.loadSegments()
        assert len(segs) == 1
        assert segs[0].properties.name == newSegName
