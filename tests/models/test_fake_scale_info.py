import unittest
from src.note_gen.models.fake_scale_info import FakeScaleInfo
from src.note_gen.models.note import Note
from src.note_gen.models.enums import ScaleType

class TestFakeScaleInfo(unittest.TestCase):
    def test_valid_initialization(self):
        note = Note(note_name='C', octave=4, duration=1.0, velocity=100)
        scale_info = FakeScaleInfo(root=note, scale_type=ScaleType.MAJOR, complexity=0.5)
        self.assertEqual(scale_info.root.note_name, 'C')
        self.assertEqual(scale_info.scale_type, ScaleType.MAJOR)
        self.assertEqual(scale_info.complexity, 0.5)

if __name__ == '__main__':
    unittest.main()
