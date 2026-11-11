import unittest
from converter import Converter

class MyTestCase(unittest.TestCase):
    def test_100_7_returns_1000(self):
        self.assertEqual(Converter.do(100.7), 1000)

    def test_large_returns_1000(self):
        self.assertEqual(Converter.do(9999.9), 1000)


    def test_106_returns_int(self):
        self.assertEqual(Converter.do(100.6), 100)

    def test_positive(self):
        self.assertEqual(Converter.do(65.7), 65)

    def test_small_positive(self):
        self.assertEqual(Converter.do(0.1), 0)

    def test_positive_integer_like(self):
        self.assertEqual(Converter.do(50.0), 50)


    def test_zero_error(self):
        with self.assertRaises(ValueError):
            Converter.do(0.0)


    def test_minus_30_4(self):
        self.assertEqual(Converter.do(-30.4), -35)

    def test_negative_close_zero(self):
        self.assertEqual(Converter.do(-0.1), -5)

    def test_negative_middle(self):
        self.assertEqual(Converter.do(-15.3), -20)

    def test_negative_integer_like(self):
        self.assertEqual(Converter.do(-10.0), -15)

    def test_minus_30_5(self):
        self.assertEqual(Converter.do(-30.5), -2000)

    def test_large_negative(self):
        self.assertEqual(Converter.do(-94.5), -2000)

    def test_very_large_negative(self):
        self.assertEqual(Converter.do(-9999.9), -2000)


if __name__ == '__main__':
    unittest.main()
