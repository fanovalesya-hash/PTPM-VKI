import unittest
from unittest.mock import Mock, patch
import sys
import os

# Добавляем путь к src для импортов
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from src.controller import TriangleController
from src.calculator import TriangleCalculator
from src.database import TriangleDatabase
from src.interactions import MockNotificationService


class TestTriangleIntegration(unittest.TestCase):

    def setUp(self):
        """
        Метод setUp выполняется перед каждым тестом.
        Создаем свежие экземпляры всех классов для изоляции тестов.
        """
        self.calculator = TriangleCalculator()
        self.database = TriangleDatabase(":memory:")  # БД в памяти для изоляции
        self.user_interaction = Mock()  # Заглушка для ввода пользователя
        self.external_service = Mock()  # Заглушка для внешнего сервиса

        self.controller = TriangleController(
            self.calculator,
            self.database,
            self.user_interaction,
            self.external_service
        )

    def tearDown(self):
        """
        Метод tearDown выполняется после каждого теста.
        Закрываем соединение с БД.
        """
        self.database.close()

    # ========== ИНТЕГРАЦИОННЫЕ ТЕСТЫ (3 штуки) ==========

    def test_integration_new_triangle_calculated_and_saved(self):
        """
        ИНТЕГРАЦИОННЫЙ ТЕСТ 1:
        Сценарий: Треугольника нет в БД.
        Ожидаемое поведение:
        1. Контроллер вызывает калькулятор
        2. Результат сохраняется в БД
        3. Результат отправляется во внешний сервис
        """
        # Выполняем обработку нового треугольника
        result = self.controller.process_triangle("3", "4", "5")

        # Проверяем, что результат корректный
        self.assertIn("разносторонний", result)

        # Проверяем, что запись появилась в БД
        db_record = self.database.get_record(3.0, 4.0, 5.0)
        self.assertIsNotNone(db_record)
        self.assertEqual(db_record[0], "разносторонний")

        # Проверяем, что внешний сервис был вызван
        self.external_service.send_data.assert_called_once()
        call_args = self.external_service.send_data.call_args[0][0]
        self.assertIn("разносторонний", call_args)

    def test_integration_existing_triangle_from_database(self):
        """
        ИНТЕГРАЦИОННЫЙ ТЕСТ 2:
        Сценарий: Треугольник уже есть в БД.
        Ожидаемое поведение:
        1. Контроллер НЕ вызывает калькулятор (берет из БД)
        2. Результат отправляется во внешний сервис
        """
        # Предварительно добавляем запись в БД
        self.database.add_record(10.0, 10.0, 10.0, "равносторонний", "")

        # Создаем Mock для калькулятора, чтобы отследить вызовы
        mock_calculator = Mock()
        controller_with_mock = TriangleController(
            mock_calculator,
            self.database,
            self.user_interaction,
            self.external_service
        )

        # Выполняем обработку треугольника, который уже есть в БД
        result = controller_with_mock.process_triangle("10", "10", "10")

        # Проверяем, что калькулятор НЕ вызывался (данные взяты из БД)
        mock_calculator.analyze.assert_not_called()

        # Проверяем, что результат корректный
        self.assertIn("равносторонний", result)

        # Проверяем, что внешний сервис был вызван
        self.external_service.send_data.assert_called_once()

    def test_integration_invalid_data_not_saved_to_database(self):
        """
        ИНТЕГРАЦИОННЫЙ ТЕСТ 3:
        Сценарий: Невалидные данные (строка вместо числа).
        Ожидаемое поведение:
        1. Контроллер НЕ идет в БД
        2. Формирует ошибку
        3. Отправляет ошибку во внешний сервис
        """
        # Выполняем обработку с невалидными данными
        result = self.controller.process_triangle("abc", "4", "5")

        # Проверяем, что результат содержит ошибку
        self.assertIn("Ошибка", result)

        # Проверяем, что в БД ничего не сохранилось
        # (пытаемся получить запись с float-значениями, но их там нет)
        db_record = self.database.get_record(0.0, 4.0, 5.0)
        self.assertIsNone(db_record)

        # Проверяем, что внешний сервис был вызван с ошибкой
        self.external_service.send_data.assert_called_once()
        call_args = self.external_service.send_data.call_args[0][0]
        self.assertIn("Ошибка", call_args)

    # ========== ЮНИТ-ТЕСТЫ ДЛЯ БД (2 штуки, не дублируют ЛР2) ==========

    def test_database_add_and_get_record(self):
        """
        ЮНИТ-ТЕСТ 1:
        Проверяем методы add_record и get_record класса TriangleDatabase.
        """
        # Добавляем запись
        self.database.add_record(5.0, 5.0, 8.0, "равнобедренный", "")

        # Получаем запись
        record = self.database.get_record(5.0, 5.0, 8.0)

        # Проверяем, что запись корректна
        self.assertIsNotNone(record)
        self.assertEqual(record[0], "равнобедренный")
        self.assertEqual(record[1], "")

    def test_database_delete_record(self):
        """
        ЮНИТ-ТЕСТ 2:
        Проверяем метод delete_record класса TriangleDatabase.
        """
        # Добавляем запись
        self.database.add_record(7.0, 7.0, 7.0, "равносторонний", "")

        # Проверяем, что запись есть
        record_before = self.database.get_record(7.0, 7.0, 7.0)
        self.assertIsNotNone(record_before)

        # Удаляем запись
        self.database.delete_record(7.0, 7.0, 7.0)

        # Проверяем, что запись удалена
        record_after = self.database.get_record(7.0, 7.0, 7.0)
        self.assertIsNone(record_after)


class TestControllerWithMockedInput(unittest.TestCase):
    """
    Дополнительные тесты с использованием patch для имитации пользовательского ввода.
    """

    def test_run_method_with_mocked_input(self):
        """
        Тест метода run() с подменой пользовательского ввода через patch.
        Проверяем, что контроллер корректно работает в интерактивном режиме.
        """
        calculator = TriangleCalculator()
        database = TriangleDatabase(":memory:")
        user_interaction = Mock()
        external_service = Mock()

        controller = TriangleController(
            calculator,
            database,
            user_interaction,
            external_service
        )

        # Настраиваем заглушку ввода: сначала "3", "4", "5", потом "q" для выхода
        user_interaction.get_input.side_effect = ["3", "4", "5", "q"]

        # Запускаем контроллер (он выйдет после ввода "q")
        controller.run()

        # Проверяем, что ввод запрашивался 4 раза (3 стороны + выход)
        self.assertEqual(user_interaction.get_input.call_count, 4)

        # Проверяем, что внешний сервис был вызван хотя бы один раз
        self.assertTrue(external_service.send_data.called)

        database.close()


if __name__ == "__main__":
    unittest.main()