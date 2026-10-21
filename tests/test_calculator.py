import unittest
import sys
import os

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from src.calculator import TriangleCalculator


class TestAnalyzeTriangle(unittest.TestCase):

    def setUp(self):
        self.calculator = TriangleCalculator()

    def test_valid_equilateral_triangle(self):
        tri_type, coords = self.calculator.analyze_triangle("10", "10", "10")
        self.assertEqual(tri_type, "равносторонний")
        self.assertEqual(len(coords), 3)
        self.assertNotEqual(coords[0], (-1, -1))
        self.assertNotEqual(coords[0], (-2, -2))

    def test_valid_isosceles_triangle(self):
        tri_type, coords = self.calculator.analyze_triangle("5", "5", "8")
        self.assertEqual(tri_type, "равнобедренный")
        self.assertNotEqual(coords[0], (-1, -1))

    def test_valid_scalene_triangle(self):
        tri_type, coords = self.calculator.analyze_triangle("3", "4", "5")
        self.assertEqual(tri_type, "разносторонний")
        self.assertNotEqual(coords[0], (-1, -1))

    def test_invalid_string_data(self):
        tri_type, coords = self.calculator.analyze_triangle("5", "abc", "5")
        self.assertEqual(tri_type, "")
        self.assertEqual(coords, [(-2, -2), (-2, -2), (-2, -2)])

    def test_empty_string_data(self):
        tri_type, coords = self.calculator.analyze_triangle("", "4", "5")
        self.assertEqual(tri_type, "")
        self.assertEqual(coords, [(-2, -2), (-2, -2), (-2, -2)])

    def test_negative_side_length(self):
        tri_type, coords = self.calculator.analyze_triangle("-5", "5", "5")
        self.assertEqual(tri_type, "не треугольник")
        self.assertEqual(coords, [(-1, -1), (-1, -1), (-1, -1)])

    def test_zero_side_length(self):
        tri_type, coords = self.calculator.analyze_triangle("0", "10", "10")
        self.assertEqual(tri_type, "не треугольник")
        self.assertEqual(coords, [(-1, -1), (-1, -1), (-1, -1)])

    def test_triangle_inequality_violation(self):
        tri_type, coords = self.calculator.analyze_triangle("1", "1", "3")
        self.assertEqual(tri_type, "не треугольник")
        self.assertEqual(coords, [(-1, -1), (-1, -1), (-1, -1)])

    def test_float_precision_edge_case(self):
        tri_type, coords = self.calculator.analyze_triangle("0.1", "0.1", "0.1")
        self.assertEqual(tri_type, "равносторонний")
        self.assertNotEqual(coords[0], (-1, -1))

    def test_none_input_handling(self):
        tri_type, coords = self.calculator.analyze_triangle(None, "5", "5")
        self.assertEqual(tri_type, "")
        self.assertEqual(coords, [(-2, -2), (-2, -2), (-2, -2)])


if __name__ == "__main__":
    unittest.main()