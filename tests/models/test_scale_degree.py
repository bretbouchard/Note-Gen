import unittest
from src.note_gen.models.scale_degree import ScaleDegree  # Replace 'your_module' with the actual module name

class TestScaleDegree(unittest.TestCase):
    def test_scale_degree_creation(self):
        degree = ScaleDegree(value=1)
        self.assertEqual(degree.value, 1)
        self.assertGreater(degree.value, 0, "Scale degree must be greater than 0")
        self.assertLessEqual(degree.value, 7, "Scale degree must be less than or equal to 7")
        
    def test_invalid_scale_degree(self):
        with self.assertRaises(ValueError):
            ScaleDegree(value=0)  # Scale degrees should be 1-based
        with self.assertRaises(ValueError):
            ScaleDegree(value=8)  # Scale degrees should not exceed 7

if __name__ == '__main__':
    unittest.main()