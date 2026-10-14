import unittest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))
from src.delivery import calculate_delivery_cost


class TestDeliveryCost(unittest.TestCase):

    def test_standard_delivery_base_case(self):
        cost, date = calculate_delivery_cost(10, 1000, "обычный")
        self.assertEqual(cost, 6240)
        self.assertEqual(date, "2026-09-05")

    def test_delivery_cost_increases_with_distance(self):
        cost1, _ = calculate_delivery_cost(5, 500, "обычный")
        cost2, _ = calculate_delivery_cost(5, 1000, "обычный")
        self.assertGreater(cost2, cost1)

    def test_fragile_package_surcharge(self):
        cost_normal, _ = calculate_delivery_cost(3, 500, "обычный")
        cost_fragile, _ = calculate_delivery_cost(3, 500, "хрупкий")
        self.assertEqual(cost_fragile, cost_normal + 300)

    def test_dangerous_package_surcharge(self):
        cost_normal, _ = calculate_delivery_cost(3, 500, "обычный")
        cost_dangerous, _ = calculate_delivery_cost(3, 500, "опасный")
        self.assertEqual(cost_dangerous, cost_normal + 1000)

    def test_heavy_package_20kg_surcharge(self):
        cost, _ = calculate_delivery_cost(20, 1000, "обычный")
        self.assertEqual(cost, 7800)

    def test_medium_weight_5_to_20kg_surcharge(self):
        cost, _ = calculate_delivery_cost(10, 1000, "обычный")
        self.assertEqual(cost, 6240)

    def test_light_package_under_5kg_no_surcharge(self):
        cost, _ = calculate_delivery_cost(3, 1000, "обычный")
        self.assertEqual(cost, 5200)

    def test_express_delivery_should_increase_cost(self):
        cost_normal, _ = calculate_delivery_cost(10, 1000, "обычный", is_express=False)
        cost_express, _ = calculate_delivery_cost(10, 1000, "обычный", is_express=True)
        self.assertGreater(cost_express, cost_normal,
                           "Экспресс-доставка должна стоить дороже обычной")

    def test_express_delivery_reduces_days(self):
        _, date_normal = calculate_delivery_cost(10, 1000, "обычный", is_express=False)
        _, date_express = calculate_delivery_cost(10, 1000, "обычный", is_express=True)
        self.assertLess(date_express, date_normal,
                        "Экспресс-доставка должна быть быстрее обычной")

    def test_express_delivery_days_never_zero(self):
        _, date = calculate_delivery_cost(5, 100, "обычный", is_express=True)
        self.assertGreater(date, "2026-09-03",
                           "Дата доставки должна быть строго позже даты отправки")

    def test_invalid_weight_too_light(self):
        cost, date = calculate_delivery_cost(0.05, 100, "обычный")
        self.assertEqual(cost, -1)
        self.assertEqual(date, "0000-00-00")

    def test_invalid_weight_too_heavy(self):
        cost, date = calculate_delivery_cost(55, 100, "обычный")
        self.assertEqual(cost, -1)
        self.assertEqual(date, "0000-00-00")

    def test_invalid_distance_too_short(self):
        cost, date = calculate_delivery_cost(5, 0, "обычный")
        self.assertEqual(cost, -1)
        self.assertEqual(date, "0000-00-00")

    def test_invalid_distance_too_long(self):
        cost, date = calculate_delivery_cost(5, 5001, "обычный")
        self.assertEqual(cost, -1)
        self.assertEqual(date, "0000-00-00")

    def test_invalid_package_type(self):
        cost, date = calculate_delivery_cost(5, 100, "электроника")
        self.assertEqual(cost, -1)
        self.assertEqual(date, "0000-00-00")

    def test_boundary_weight_exactly_0_1(self):
        cost, date = calculate_delivery_cost(0.1, 100, "обычный")
        self.assertNotEqual(cost, -1)
        self.assertNotEqual(date, "0000-00-00")

    def test_boundary_weight_exactly_50(self):
        cost, date = calculate_delivery_cost(50.0, 100, "обычный")
        self.assertNotEqual(cost, -1)
        self.assertNotEqual(date, "0000-00-00")

    def test_boundary_distance_exactly_1(self):
        cost, date = calculate_delivery_cost(5, 1, "обычный")
        self.assertNotEqual(cost, -1)
        self.assertNotEqual(date, "0000-00-00")

    def test_boundary_distance_exactly_5000(self):
        cost, date = calculate_delivery_cost(5, 5000, "обычный")
        self.assertNotEqual(cost, -1)
        self.assertNotEqual(date, "0000-00-00")


if __name__ == "__main__":
    unittest.main()