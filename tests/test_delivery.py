import unittest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))
from src.delivery import calculate_delivery_cost


class TestDeliveryCost(unittest.TestCase):

    def test_standard_delivery_base_case(self):
        # Базовый случай: обычная посылка 10 кг на 1000 км
        cost, date = calculate_delivery_cost(10, 1000, "обычный")
        # 200 + 1000*5 = 5200, *1.2 (вес 5-20 кг) = 6240
        self.assertEqual(cost, 6240)
        self.assertEqual(date, "2026-09-05")

    def test_delivery_cost_increases_with_distance(self):
        # Стоимость должна расти с увеличением расстояния
        cost1, _ = calculate_delivery_cost(5, 500, "обычный")
        cost2, _ = calculate_delivery_cost(5, 1000, "обычный")
        self.assertGreater(cost2, cost1)

    def test_fragile_package_surcharge(self):
        # Хрупкая посылка должна стоить дороже обычной на 300 руб
        cost_normal, _ = calculate_delivery_cost(3, 500, "обычный")
        cost_fragile, _ = calculate_delivery_cost(3, 500, "хрупкий")
        self.assertEqual(cost_fragile, cost_normal + 300)

    def test_dangerous_package_surcharge(self):
        # Опасная посылка должна стоить дороже обычной на 1000 руб
        cost_normal, _ = calculate_delivery_cost(3, 500, "обычный")
        cost_dangerous, _ = calculate_delivery_cost(3, 500, "опасный")
        self.assertEqual(cost_dangerous, cost_normal + 1000)

    def test_heavy_package_20kg_surcharge(self):
        # Посылка >= 20 кг должна иметь коэффициент 1.5
        cost, _ = calculate_delivery_cost(20, 1000, "обычный")
        # 200 + 5000 = 5200, *1.5 = 7800
        self.assertEqual(cost, 7800)

    def test_medium_weight_5_to_20kg_surcharge(self):
        # Посылка от 5 до 20 кг должна иметь коэффициент 1.2
        cost, _ = calculate_delivery_cost(10, 1000, "обычный")
        # 200 + 5000 = 5200, *1.2 = 6240
        self.assertEqual(cost, 6240)

    def test_light_package_under_5kg_no_surcharge(self):
        # Легкая посылка до 5 кг без весового коэффициента
        cost, _ = calculate_delivery_cost(3, 1000, "обычный")
        # 200 + 5000 = 5200, без коэффициента
        self.assertEqual(cost, 5200)

    def test_express_delivery_should_increase_cost(self):
        # ЭКСПРЕСС-ТЕСТ (упадет из-за бага): экспресс должен быть ДОРОЖЕ обычного
        cost_normal, _ = calculate_delivery_cost(10, 1000, "обычный", is_express=False)
        cost_express, _ = calculate_delivery_cost(10, 1000, "обычный", is_express=True)
        self.assertGreater(cost_express, cost_normal,
                           "Экспресс-доставка должна стоить дороже обычной")

    def test_express_delivery_reduces_days(self):
        # Экспресс должен сокращать срок доставки
        _, date_normal = calculate_delivery_cost(10, 1000, "обычный", is_express=False)
        _, date_express = calculate_delivery_cost(10, 1000, "обычный", is_express=True)
        self.assertLess(date_express, date_normal,
                        "Экспресс-доставка должна быть быстрее обычной")

    def test_express_delivery_days_never_zero(self):
        # КРАЙНИЙ СЛУЧАЙ (упадет из-за бага): дни доставки не могут быть 0
        # При расстоянии 100 км days_needed = max(1, 100//500) = 1
        # После is_express: 1 // 2 = 0 ← БАГ
        _, date = calculate_delivery_cost(5, 100, "обычный", is_express=True)
        self.assertGreater(date, "2026-09-03",
                           "Дата доставки должна быть строго позже даты отправки")

    def test_invalid_weight_too_light(self):
        # Вес меньше 0.1 кг — ошибка
        cost, date = calculate_delivery_cost(0.05, 100, "обычный")
        self.assertEqual(cost, -1)
        self.assertEqual(date, "0000-00-00")

    def test_invalid_weight_too_heavy(self):
        # Вес больше 50 кг — ошибка
        cost, date = calculate_delivery_cost(55, 100, "обычный")
        self.assertEqual(cost, -1)
        self.assertEqual(date, "0000-00-00")

    def test_invalid_distance_too_short(self):
        # Расстояние меньше 1 км — ошибка
        cost, date = calculate_delivery_cost(5, 0, "обычный")
        self.assertEqual(cost, -1)
        self.assertEqual(date, "0000-00-00")

    def test_invalid_distance_too_long(self):
        # Расстояние больше 5000 км — ошибка
        cost, date = calculate_delivery_cost(5, 5001, "обычный")
        self.assertEqual(cost, -1)
        self.assertEqual(date, "0000-00-00")

    def test_invalid_package_type(self):
        # Неверный тип посылки — ошибка
        cost, date = calculate_delivery_cost(5, 100, "электроника")
        self.assertEqual(cost, -1)
        self.assertEqual(date, "0000-00-00")

    def test_boundary_weight_exactly_0_1(self):
        # Граничное значение: вес ровно 0.1 кг — должно работать
        cost, date = calculate_delivery_cost(0.1, 100, "обычный")
        self.assertNotEqual(cost, -1)
        self.assertNotEqual(date, "0000-00-00")

    def test_boundary_weight_exactly_50(self):
        # Граничное значение: вес ровно 50 кг — должно работать
        cost, date = calculate_delivery_cost(50.0, 100, "обычный")
        self.assertNotEqual(cost, -1)
        self.assertNotEqual(date, "0000-00-00")

    def test_boundary_distance_exactly_1(self):
        # Граничное значение: расстояние ровно 1 км — должно работать
        cost, date = calculate_delivery_cost(5, 1, "обычный")
        self.assertNotEqual(cost, -1)
        self.assertNotEqual(date, "0000-00-00")

    def test_boundary_distance_exactly_5000(self):
        # Граничное значение: расстояние ровно 5000 км — должно работать
        cost, date = calculate_delivery_cost(5, 5000, "обычный")
        self.assertNotEqual(cost, -1)
        self.assertNotEqual(date, "0000-00-00")


if __name__ == "__main__":
    unittest.main()