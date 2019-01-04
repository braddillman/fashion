from pathlib import Path

from fashion.segment import Segment
from fashion.util import cd
from fashion.warehouse import Warehouse


class TestSegment(object):

    def test_ctor(self, tmp_path):
        '''Test Segment ctor.'''
        with cd(tmp_path):
            s1 = Segment(Path("segment.json"))
            assert s1.absFilename is not None
            assert s1.absDirname is not None
            assert s1.properties.templatePath[0] == "./template"
            assert len(s1.properties.segmentRefs) == 1
            s1.save()
            s2 = Segment.load(Path("segment.json"))
            assert s1.properties.templatePath == s2.properties.templatePath
            assert s1.properties.xformConfig == s2.properties.xformConfig
            assert s1.properties.segmentRefs == s2.properties.segmentRefs
            assert s1.properties.extraFiles == s2.properties.extraFiles
            assert s1.absFilename == s2.absFilename

    def test_create(self, tmp_path):
        '''Test creatinga new segment.'''
        with cd(tmp_path):
            s1 = Segment.create(tmp_path, "testseg")
            assert s1.absFilename is not None
            assert s1.absDirname is not None
            assert s1.absFilename.exists()
            p = s1.absDirname
            assert p.exists()
            modelDir = p / "model"
            assert modelDir.exists()

            s2 = Segment.load(Path("segment.json"))
            assert s1.properties.templatePath == s2.properties.templatePath
            assert s1.properties.xformConfig == s2.properties.xformConfig
            assert s1.properties.segmentRefs == s2.properties.segmentRefs
            assert s1.properties.extraFiles == s2.properties.extraFiles
            assert str(s1.absFilename) == str(s2.absFilename)
