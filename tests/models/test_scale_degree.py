import unittest
from src.note_gen.models.scale_degree import ScaleDegree  
from note_gen.models.note import Note  # Add this import at the top

def test_scale_degree_creation(self):
    degree = ScaleDegree(
        degree="1",
        note=Note(note_name="C", octave=4),
        value="1",
        midi_number=60
    )
        
    def test_invalid_scale_degree(self):
        with self.assertRaises(ValueError):
            ScaleDegree(value=0)  # Scale degrees should be 1-based
        with self.assertRaises(ValueError):
            ScaleDegree(value=8)  # Scale degrees should not exceed 7

if __name__ == '__main__':
    unittest.main()